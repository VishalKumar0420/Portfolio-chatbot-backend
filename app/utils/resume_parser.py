"""
Resume parser utilities: extract text from PDF/DOCX and parse with LLM.
"""

import io
import json

from docx import Document
from PyPDF2 import PdfReader

from app.config.groq import groq_client


def extract_text_from_pdf(content: bytes) -> str:
    """
    Extract plain text from a PDF file.

    Raises:
        ValueError: If extraction fails.
    """
    try:
        reader = PdfReader(io.BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages).strip()
    except Exception as exc:
        raise ValueError(f"Failed to extract text from PDF: {exc}")


def extract_text_from_docx(content: bytes) -> str:
    """
    Extract plain text from a DOCX file.

    Raises:
        ValueError: If extraction fails.
    """
    try:
        doc = Document(io.BytesIO(content))
        return "\n".join(p.text for p in doc.paragraphs).strip()
    except Exception as exc:
        raise ValueError(f"Failed to extract text from DOCX: {exc}")


def extract_text_from_resume(content: bytes, filename: str) -> str:
    """
    Dispatch to the correct extractor based on file extension.

    Raises:
        ValueError: If the file format is unsupported.
    """
    ext = filename.lower().rsplit(".", 1)[-1]

    if ext == "pdf":
        return extract_text_from_pdf(content)
    elif ext in ("docx", "doc"):
        return extract_text_from_docx(content)
    else:
        raise ValueError(f"Unsupported format '{ext}'. Only PDF and DOCX are supported.")


def _empty_resume() -> dict:
    """Return an empty resume structure matching the ResumeData schema."""
    return {
        "aboutMe": "",
        "personalInfo": {
            "fullName": "", "email": "", "phone": "",
            "location": "", "linkedin": "", "github": "", "portfolio": "",
        },
        "educations": [],
        "skills": [],
        "experience": [],
        "certifications": [],
        "achievements": [],
    }


def parse_resume_with_llm(resume_text: str) -> dict:
    """
    Use the Groq LLM to extract structured data from raw resume text.

    Returns a dict matching the ResumeData schema.
    Falls back to an empty structure on JSON parse failure.
    """
    prompt = f"""You are an expert resume parser. Extract structured information from the resume below.

Resume:
{resume_text}

Return ONLY a valid JSON object — no markdown, no explanation — with this exact structure:
{{
  "aboutMe": "professional summary",
  "personalInfo": {{
    "fullName": "", "email": "", "phone": "",
    "location": "", "linkedin": "", "github": "", "portfolio": ""
  }},
  "educations": [
    {{"institution": "", "degree": "", "fieldOfStudy": "", "startDate": "", "endDate": "", "percentage": ""}}
  ],
  "skills": ["skill1", "skill2"],
  "experience": [
    {{"company": "", "position": "", "location": "", "startDate": "", "endDate": "", "description": "", "isCurrentlyWorking": false}}
  ],
  "certifications": [
    {{"certificateName": "", "issuingOrganization": "", "issueDate": "", "expiryDate": "", "credentialId": ""}}
  ],
  "achievements": [
    {{"title": "", "date": "", "description": ""}}
  ]
}}

Rules:
- Return ONLY valid JSON
- Use empty string for missing text fields, empty array for missing lists
- Set isCurrentlyWorking to true if endDate is "Present"
- Dates should be YYYY-MM or YYYY format"""

    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise resume parser. Return only valid JSON without markdown or explanations.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            max_tokens=4000,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```", 2)[-1] if raw.count("```") >= 2 else raw.lstrip("`")
            raw = raw.lstrip("json").strip()
        if raw.endswith("```"):
            raw = raw[:-3].strip()

        return json.loads(raw)

    except (json.JSONDecodeError, Exception):
        return _empty_resume()

import io
import json
from PyPDF2 import PdfReader
from docx import Document
from app.core.llm.groq_client import client


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file"""
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting text from PDF: {str(e)}")


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file"""
    try:
        docx_file = io.BytesIO(file_content)
        doc = Document(docx_file)
        
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error extracting text from DOCX: {str(e)}")


def extract_text_from_resume(file_content: bytes, filename: str) -> str:
    """
    Extract text from resume file (PDF or DOCX)
    
    Args:
        file_content: Binary content of the file
        filename: Name of the file with extension
        
    Returns:
        Extracted text from the resume
    """
    file_extension = filename.lower().split('.')[-1]
    
    if file_extension == 'pdf':
        return extract_text_from_pdf(file_content)
    elif file_extension in ['docx', 'doc']:
        return extract_text_from_docx(file_content)
    else:
        raise ValueError(f"Unsupported file format: {file_extension}. Only PDF and DOCX are supported.")


def parse_resume_with_llm(resume_text: str) -> dict:
    """
    Parse resume text using Groq LLM to extract structured data
    
    Args:
        resume_text: Extracted text from resume
        
    Returns:
        Structured resume data as dictionary
    """
    
    prompt = f"""You are an expert resume parser. Extract and structure the following resume information into a JSON format.

Resume Text:
{resume_text}

Extract the following information and return ONLY a valid JSON object (no markdown, no explanation):

{{
  "aboutMe": "Brief professional summary or objective (if available)",
  "personalInfo": {{
    "fullName": "Full name of the person",
    "email": "Email address",
    "phone": "Phone number",
    "location": "City, State/Country",
    "linkedin": "LinkedIn profile URL",
    "github": "GitHub profile URL",
    "portfolio": "Portfolio website URL"
  }},
  "educations": [
    {{
      "institution": "University/College name",
      "degree": "Degree type (e.g., Bachelor's, Master's)",
      "fieldOfStudy": "Major/Field of study",
      "startDate": "Start date (YYYY-MM or YYYY)",
      "endDate": "End date (YYYY-MM or YYYY) or 'Present'",
      "percentage": "GPA/Percentage/Grade"
    }}
  ],
  "skills": ["skill1", "skill2", "skill3"],
  "experience": [
    {{
      "company": "Company name",
      "position": "Job title/position",
      "location": "City, State/Country",
      "startDate": "Start date (YYYY-MM or YYYY)",
      "endDate": "End date (YYYY-MM or YYYY) or 'Present'",
      "description": "Job responsibilities and achievements",
      "isCurrentlyWorking": true or false
    }}
  ],
  "certifications": [
    {{
      "certificateName": "Name of certification",
      "issuingOrganization": "Organization that issued",
      "issueDate": "Issue date (YYYY-MM or YYYY)",
      "expiryDate": "Expiry date (YYYY-MM or YYYY) or empty if no expiry",
      "credentialId": "Credential ID if available"
    }}
  ],
  "achievements": [
    {{
      "title": "Achievement title",
      "date": "Date (YYYY-MM or YYYY)",
      "description": "Description of achievement"
    }}
  ]
}}

IMPORTANT RULES:
1. Return ONLY valid JSON, no markdown code blocks, no explanations
2. If information is not found, use empty string "" for strings, empty array [] for arrays, or false for booleans
3. For dates, use format YYYY-MM or YYYY
4. For isCurrentlyWorking, set to true if endDate is "Present" or similar
5. Extract all skills mentioned (technical, soft skills, tools, languages)
6. Be thorough but accurate - don't make up information
7. Ensure all JSON keys match exactly as specified above"""

    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a precise resume parser that extracts structured data from resumes. You always return valid JSON without any markdown formatting or explanations."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,
            max_tokens=4000,
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Remove markdown code blocks if present
        if result_text.startswith("```json"):
            result_text = result_text[7:]
        if result_text.startswith("```"):
            result_text = result_text[3:]
        if result_text.endswith("```"):
            result_text = result_text[:-3]
        
        result_text = result_text.strip()
        
        # Parse JSON
        parsed_data = json.loads(result_text)
        
        return parsed_data
        
    except json.JSONDecodeError as e:
        # Return empty structure if parsing fails
        return get_empty_resume_structure()
    except Exception as e:
        print(f"Error parsing resume with LLM: {e}")
        return get_empty_resume_structure()


def get_empty_resume_structure() -> dict:
    """Return empty resume structure"""
    return {
        "aboutMe": "",
        "personalInfo": {
            "fullName": "",
            "email": "",
            "phone": "",
            "location": "",
            "linkedin": "",
            "github": "",
            "portfolio": ""
        },
        "educations": [],
        "skills": [],
        "experience": [],
        "certifications": [],
        "achievements": []
    }

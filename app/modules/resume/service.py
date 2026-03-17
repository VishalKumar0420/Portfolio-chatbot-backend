"""
Resume service: validate the uploaded file, extract text, and parse with LLM.
"""

from fastapi import HTTPException, UploadFile, status

from app.utils.resume_parser import extract_text_from_resume, parse_resume_with_llm

_ALLOWED_EXTENSIONS = {"pdf", "docx", "doc"}
_MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


async def parse_resume(file: UploadFile) -> dict:
    """
    Validate, extract text from, and parse a resume file using the LLM.

    Args:
        file: Uploaded PDF or DOCX resume file.

    Returns:
        Structured resume data dict matching the ResumeData schema.

    Raises:
        HTTPException 400: Invalid file type, oversized file, or insufficient text.
        HTTPException 500: Unexpected LLM processing error.
    """
    # Validate file extension
    extension = file.filename.lower().rsplit(".", 1)[-1]
    if extension not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{extension}'. Only PDF and DOCX are accepted.",
        )

    # Read and validate file size
    content = await file.read()
    if len(content) > _MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File exceeds the 10 MB size limit.",
        )

    # Extract raw text from the file
    try:
        resume_text = extract_text_from_resume(content, file.filename)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    if not resume_text or len(resume_text.strip()) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract enough text. Ensure the file is not empty or corrupted.",
        )

    # Parse structured data with LLM
    try:
        return parse_resume_with_llm(resume_text)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while parsing the resume.",
        )

from fastapi import UploadFile,File,UploadFile, HTTPException
from app.shares.resume_parser import extract_text_from_resume, parse_resume_with_llm
async def parse_resume_service(file: UploadFile = File(..., description="Resume file (PDF or DOCX)")):
    """
    Parse resume file and extract structured data
    
    - **file**: Upload a resume file (PDF or DOCX format, max 10MB)
    
    Returns structured resume data including:
    - Personal information (name, email, phone, etc.)
    - Education history
    - Work experience
    - Skills
    - Certifications
    - Achievements
    """
    
    try:
        # Process the resume file
        resume_data = await process_resume_file(file)
        
        return resume_data
        
    except HTTPException as e:
        raise e
    except Exception as e:
        
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the resume"
        )





async def process_resume_file(file: UploadFile) -> dict:
    """
    Process uploaded resume file and extract structured data
    
    Args:
        file: Uploaded resume file (PDF or DOCX)
        
    Returns:
        Structured resume data
    """
    
    # Validate file type
    allowed_extensions = ['pdf', 'docx', 'doc']
    file_extension = file.filename.lower().split('.')[-1]
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Only PDF and DOCX files are supported. Got: {file_extension}"
        )
    
    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    file_content = await file.read()
    
    if len(file_content) > max_size:
        raise HTTPException(
            status_code=400,
            detail="File size exceeds 10MB limit"
        )
    
    try:
        # Extract text from resume
        resume_text = extract_text_from_resume(file_content, file.filename)
        
        if not resume_text or len(resume_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Could not extract sufficient text from the resume. Please ensure the file is not corrupted or empty."
            )
        
        
        # Parse resume with LLM
        structured_data = parse_resume_with_llm(resume_text)
        
        
        return structured_data
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error processing resume: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing resume: {str(e)}"
        )

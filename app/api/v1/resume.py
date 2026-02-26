from fastapi import APIRouter, UploadFile, File, HTTPException

from app.schemas.resume import ResumeData, ResumeResponse
from app.services.resume_service import process_resume_file

router = APIRouter()




@router.post("/parse_resume/", response_model=ResumeResponse)
async def parse_resume(file: UploadFile = File(..., description="Resume file (PDF or DOCX)")):
    """
    Parse resume file and extract structured data
    
    - *file*: Upload a resume file (PDF or DOCX format, max 10MB)
    
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
        
        return ResumeResponse(
            success=True,
            message="Resume parsed successfully",
            data=ResumeData(**resume_data)
        )
        
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unexpected error in parse_resume route: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing the resume"
        )
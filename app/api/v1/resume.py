
from fastapi import APIRouter,UploadFile,File
from app.schemas.parse_resume import ParseResume,ResumeData
from app.services.resume_service import parse_resume_service

router = APIRouter(prefix="/resume", tags=["RESUME"])

@router.post("/parse_resume/",response_model=ParseResume)
async def parse_resume(file: UploadFile = File(..., description="Resume file (PDF or DOCX)")):
    response= await parse_resume_service(file=file)
    return ParseResume(
            success=True,
            message="Resume parsed successfully",
            data=ResumeData(**response)
    ) 
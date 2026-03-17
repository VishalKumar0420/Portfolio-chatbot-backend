"""
Resume controller: wraps the resume service in an APIResponse envelope.
"""

from fastapi import UploadFile

from app.modules.resume import service
from app.modules.resume.schema import ResumeData
from app.schemas.response import APIResponse


async def handle_parse_resume(file: UploadFile) -> APIResponse[ResumeData]:
    """Parse the uploaded resume and return structured data."""
    resume_dict = await service.parse_resume(file=file)
    return APIResponse(
        message="Resume parsed successfully",
        data=ResumeData(**resume_dict),
    )

"""
Resume router: parse uploaded resume files.

All routes require a valid JWT Bearer token.
"""

from fastapi import APIRouter, Depends, File, UploadFile, status

from app.middleware.auth import verify_token
from app.modules.resume import controller
from app.modules.resume.schema import ResumeData
from app.schemas.response import APIResponse

router = APIRouter(prefix="/resume", tags=["Resume"])

_BEARER_SECURITY = [{"BearerAuth": []}]


@router.post(
    "/parse",
    response_model=APIResponse[ResumeData],
    status_code=status.HTTP_200_OK,
    summary="Parse a resume file",
    description=(
        "Accepts a PDF or DOCX resume (max 10 MB), extracts text, "
        "and uses an LLM to return structured resume data."
    ),
    operation_id="parse_resume",
    openapi_extra={"security": _BEARER_SECURITY},
)
async def parse_resume(
    file: UploadFile = File(..., description="Resume file — PDF or DOCX, max 10 MB"),
):
    """Upload a resume and receive structured JSON extracted by the LLM."""
    return await controller.handle_parse_resume(file=file)

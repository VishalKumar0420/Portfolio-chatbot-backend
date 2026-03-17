"""
Health check router — used by load balancers and monitoring tools.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", summary="Health check", operation_id="health_check")
def health_check():
    """Confirm the service is running."""
    return {"success": True, "status": "ok", "service": "backend"}

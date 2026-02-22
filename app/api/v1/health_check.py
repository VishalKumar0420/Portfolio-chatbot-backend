from fastapi import APIRouter

router = APIRouter( prefix="/health", tags=["health"] )

@router.get( "", summary="health", operation_id="health_check")
def health_check():
    return {
        "status": "ok",
        "service": "backend",
    }
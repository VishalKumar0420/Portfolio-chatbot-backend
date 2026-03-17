"""
Shared response schema and JSONResponse helpers used across all modules.

Every endpoint returns this shape:
  {
    "success": bool,
    "status_code": int,
    "message": str,
    "data": <any> | null,
    "errors": <any> | null
  }
"""

from typing import Any, Generic, Optional, TypeVar

from fastapi.responses import JSONResponse
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard response envelope for all API endpoints."""

    success: bool = True
    status_code: int = 200
    message: str
    data: Optional[T] = None
    errors: Optional[dict] = None


# ── JSONResponse helpers (used in exception handlers) ─────────────────────────

def error_response(message: str, status_code: int = 400, errors: Optional[Any] = None) -> JSONResponse:
    """Return a standard error JSONResponse."""
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "status_code": status_code, "message": message, "data": None, "errors": errors},
    )


def validation_response(errors: dict, status_code: int = 422) -> JSONResponse:
    """Return a standard validation-error JSONResponse."""
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "status_code": status_code, "message": "Validation failed", "data": None, "errors": errors},
    )

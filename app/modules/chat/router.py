"""
Chat router: add, search, and delete chat sessions.

All routes require a valid JWT Bearer token.
"""

from fastapi import APIRouter, BackgroundTasks, Depends, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.middleware.auth import verify_token
from app.modules.chat import controller
from app.modules.chat.schema import AddChatRequest, ChatResponse, DeleteChatRequest, SearchChatRequest
from app.schemas.response import APIResponse

router = APIRouter(prefix="/chat", tags=["Chat"])

_BEARER_SECURITY = [{"BearerAuth": []}]


@router.post(
    "/add",
    response_model=APIResponse[ChatResponse],
    status_code=status.HTTP_201_CREATED,
    summary="Add or update a chat session",
    description=(
        "Saves the chat record to the database and asynchronously indexes "
        "the resume content into Pinecone for semantic search."
    ),
    operation_id="add_chat",
    openapi_extra={"security": _BEARER_SECURITY},
)
async def add_chat(
    data: AddChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: str = Depends(verify_token),
):
    """Save chat to DB and queue vector indexing."""
    return controller.handle_add_chat(
        data=data, user_id=user_id, db=db, background_tasks=background_tasks
    )


@router.post(
    "/search",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Search chat content with AI",
    description=(
        "Performs a semantic vector search over the indexed chat content "
        "and returns an AI-generated answer with matched context chunks."
    ),
    operation_id="search_chat",
)
async def search_chat(
    data: SearchChatRequest
):
    """Semantic search and LLM-generated answer."""
    return controller.handle_search_chat(data=data)


@router.delete(
    "/delete",
    response_model=APIResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete a chat session",
    description="Removes all Pinecone vectors associated with the given chat ID.",
    operation_id="delete_chat",
    openapi_extra={"security": _BEARER_SECURITY},
)
async def delete_chat(
    data: DeleteChatRequest,
    user_id: str = Depends(verify_token),
):
    """Delete all indexed vectors for a chat session."""
    return controller.handle_delete_chat(data=data)

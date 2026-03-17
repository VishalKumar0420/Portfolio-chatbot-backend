"""
Chat controller: wraps service calls in APIResponse envelopes.
"""

from fastapi import BackgroundTasks, status
from sqlalchemy.orm import Session

from app.modules.chat import service
from app.modules.chat.schema import AddChatRequest, ChatResponse, DeleteChatRequest, SearchChatRequest
from app.schemas.response import APIResponse


def handle_add_chat(
    data: AddChatRequest,
    user_id: str,
    db: Session,
    background_tasks: BackgroundTasks,
) -> APIResponse:
    """
    Persist the chat to DB synchronously, then index vectors in the background.

    The DB write is synchronous so failures surface immediately.
    Vector indexing is deferred to avoid blocking the HTTP response.
    """
    service.save_chat(db, data.chat_id, user_id, data.chat_name, data.content)
    background_tasks.add_task(service.index_chat_content, data.chat_id, data.content)

    return APIResponse(
        status_code=status.HTTP_201_CREATED,
        message="Chat saved and indexing started",
        data=ChatResponse(
            chat_id=data.chat_id,
            chat_name=data.chat_name,
            content=data.content,
        ),
    )


def handle_search_chat(data: SearchChatRequest) -> APIResponse:
    """Run semantic search and return the LLM answer with context."""
    results = service.search_chat(data.chat_id, data.query)
    return APIResponse(message="Search completed successfully", data=results)


def handle_delete_chat(data: DeleteChatRequest) -> APIResponse:
    """Delete all vectors for the given chat session."""
    service.delete_chat_vectors(data.chat_id)
    return APIResponse(message=f"Chat '{data.chat_id}' deleted successfully")

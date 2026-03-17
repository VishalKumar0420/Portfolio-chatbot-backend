"""
Chat Pydantic schemas: request bodies for chat operations.
"""

from pydantic import BaseModel, Field
from pydantic import constr

from app.modules.resume.schema import ResumeData

class AddChatRequest(BaseModel):
    """Request body for POST /chat/add."""

    chat_id: constr(min_length=3, max_length=50) = Field(..., description="Unique chat session ID")  # type: ignore
    chat_name: constr(min_length=3, max_length=100) = Field(..., description="Display name for the chat")  # type: ignore
    content: ResumeData


class SearchChatRequest(BaseModel):
    """Request body for POST /chat/search."""

    chat_id: constr(min_length=3, max_length=50) = Field(..., description="Chat session ID to search within")  # type: ignore
    query: constr(min_length=3) = Field(..., description="Natural-language query")  # type: ignore


class DeleteChatRequest(BaseModel):
    """Request body for DELETE /chat/delete."""

    chat_id: constr(min_length=3, max_length=50) = Field(..., description="Chat session ID to delete")  # type: ignore


class ChatResponse(BaseModel):
    """Data returned after a chat is saved or updated."""

    chat_id: str
    chat_name: str
    content: ResumeData

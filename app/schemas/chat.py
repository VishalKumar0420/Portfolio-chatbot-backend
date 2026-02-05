from pydantic import BaseModel, Field, constr
from typing import Dict, Literal

SectionType = Literal[
    "ABOUTME",
    "EDUCATIONS",
    "SKILLS",
    "EXPERIENCE",
    "CERTIFICATION",
    "PERSONALINFO",
    "ACHIEVEMENTS",
]


class ChatInput(BaseModel):
    chat_id: constr(min_length=3, max_length=50) = Field(..., description="Unique user chat ID")  # type: ignore
    chat_name: constr(min_length=3, max_length=100) = Field(..., description="Name of the chat")  # type: ignore
    content: Dict[SectionType, str] = Field(
        ..., description="Content as dictionary with section names as keys"
    )


class ChatQuery(BaseModel):
    chat_id: constr(min_length=3, max_length=50) = Field(..., description="Unique user chat ID")  # type: ignore
    query: constr(min_length=3) = Field(..., description="Query text to search")  # type: ignore


class ChatDelete(BaseModel):
    chat_id: constr(min_length=3, max_length=50) = Field(..., description="Unique user chat ID to delete")  # type: ignore

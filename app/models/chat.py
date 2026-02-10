from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, ForeignKey, String
from app.core.db.base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid

# from sqlalchemy.orm import


class Chat(Base):
    __tablename = "chat"
    chat_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id"), nullable=False)
    chat_name = Column(String, nullable=False)
    created_at = (
        Column(
            DateTime(timezone=True),
            default=lambda: datetime.now(timezone.utc),
            nullable=False,
        ),
    )
    user = relationship("User", back_populates="chat")

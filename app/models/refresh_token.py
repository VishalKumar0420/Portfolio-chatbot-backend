import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.db.base import Base


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    token = Column(String(255), unique=True, nullable=False)

    is_revoked = Column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
    )

    user = relationship(
        "User",
        back_populates="refresh_tokens",
    )

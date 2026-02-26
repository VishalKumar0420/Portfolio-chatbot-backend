import uuid
from sqlalchemy import ARRAY, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from app.core.db.base import Base
from sqlalchemy.dialects.postgresql import UUID


class Achievement(Base):
    __tableName__ = "achievement"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        defual=uuid.uuid4,
        index=True,
        nullable=False,
    )
    resume_id = Column(
        UUID(as_uuid=True), ForeignKey("resume.id", ondelete="CASCADE"), index=True
    )
    title = Column(ARRAY(String), nullable=False, default=dict)
    date = Column(ARRAY(String), nullable=False, default=dict)
    description = Column(ARRAY(String), nullable=False, default=dict)

    resume = relationship("Resume", back_populates="achievement")

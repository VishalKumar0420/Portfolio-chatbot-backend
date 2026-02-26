import uuid
from sqlalchemy import ARRAY, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from app.core.db.base import Base
from sqlalchemy.dialects.postgresql import UUID


class Experience(Base):
    __tableName__ = "education"

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
    company = Column(ARRAY(String), nullable=False, default=dict)
    position = Column(ARRAY(String), nullable=False, default=dict)
    location = Column(ARRAY(String), nullable=False, default=dict)
    startDate = Column(ARRAY(String), nullable=False, default=dict)
    endDate = Column(ARRAY(String), nullable=False, default=dict)
    description = Column(ARRAY(String), nullable=False, default=dict)
    isCurrentlyWorking = Column(ARRAY(String), nullable=False, default=dict)


    resume = relationship("Resume", back_populates="experience")

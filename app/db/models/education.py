import uuid
from sqlalchemy import ARRAY, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from app.core.db.base import Base
from sqlalchemy.dialects.postgresql import UUID


class Education(Base):
    __tableName__ = "education"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        defual=uuid.uuid4,
        index=True,
        nullable=False,
    )
    resume_id = Column(
        UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), index=True
    )
    institution = Column(ARRAY(String), nullable=False, default=dict)
    degree = Column(ARRAY(String), nullable=False, default=dict)
    fieldOfStudy = Column(ARRAY(String), nullable=False, default=dict)
    startDate = Column(ARRAY(String), nullable=False, default=dict)
    endDate = Column(ARRAY(String), nullable=False, default=dict)
    percentage = Column(ARRAY(String), nullable=False, default=dict)

    resume = relationship("Resume", back_populates="education")

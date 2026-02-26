import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.core.db.base import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="resumes")

    personal_info = relationship(
        "PersonalInfo",
        back_populates="resume",
        cascade="all, delete-orphan",
        uselist=False,
    )

    educations = relationship(
        "Education",
        back_populates="resume",
        cascade="all, delete-orphan",
    )

    experiences = relationship(
        "Experience",
        back_populates="resume",
        cascade="all, delete-orphan",
    )

    certifications = relationship(
        "Certification",
        back_populates="resume",
        cascade="all, delete-orphan",
    )

    achievements = relationship(
        "Achievement",
        back_populates="resume",
        cascade="all, delete-orphan",
    )

    skills = relationship(
        "Skill",
        back_populates="resume",
        cascade="all, delete-orphan",
    )

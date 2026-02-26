import uuid
from sqlalchemy import ARRAY, Column, ForeignKey, String
from sqlalchemy.orm import relationship
from app.core.db.base import Base
from sqlalchemy.dialects.postgresql import UUID


class Certification(Base):
    __tableName__ = "certification"

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
    certificateName = Column(ARRAY(String), nullable=False, default=dict)
    issuingOrganization = Column(ARRAY(String), nullable=False, default=dict)
    issueDate = Column(ARRAY(String), nullable=False, default=dict)
    expiryDate = Column(ARRAY(String), nullable=False, default=dict)
    credentialId = Column(ARRAY(String), nullable=False, default=dict)

    resume = relationship("Resume", back_populates="certification")

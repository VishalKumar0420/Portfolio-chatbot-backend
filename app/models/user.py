import enum
from sqlalchemy import Column,String,Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.core.db.base import Base
import uuid


class RoleEnum(enum.Enum):
    admin="admin"
    user="user"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True),primary_key=True,default=uuid.uuid4,unique=True,nullable=False)
    name = Column(String,nullable=False)
    email = Column(String, unique=True,nullable=False)
    password = Column(String,nullable=False)
    role=Column(Enum(RoleEnum),default=RoleEnum.user,nullable=False)
    refresh_tokens = relationship(
        "RefreshToken",
        back_populates="user",
        cascade="all, delete"
    )
    otps = relationship("OTP", back_populates="user")

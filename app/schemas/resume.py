from pydantic import BaseModel, Field
from typing import List, Optional


class PersonalInfo(BaseModel):
    fullName: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    portfolio: str = ""


class Education(BaseModel):
    institution: str = ""
    degree: str = ""
    fieldOfStudy: str = ""
    startDate: str = ""
    endDate: str = ""
    percentage: str = ""


class Experience(BaseModel):
    company: str = ""
    position: str = ""
    location: str = ""
    startDate: str = ""
    endDate: str = ""
    description: str = ""
    isCurrentlyWorking: bool = False


class Certification(BaseModel):
    certificateName: str = ""
    issuingOrganization: str = ""
    issueDate: str = ""
    expiryDate: str = ""
    credentialId: str = ""


class Achievement(BaseModel):
    title: str = ""
    date: str = ""
    description: str = ""


class ResumeData(BaseModel):
    aboutMe: str = ""
    personalInfo: PersonalInfo
    educations: List[Education] = []
    skills: List[str] = []
    experience: List[Experience] = []
    certifications: List[Certification] = []
    achievements: List[Achievement] = []


class ResumeResponse(BaseModel):
    success: bool
    message: str
    data: Optional[ResumeData] = None
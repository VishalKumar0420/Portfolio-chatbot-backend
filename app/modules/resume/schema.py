"""
Resume Pydantic schemas: structured data extracted from a resume file.

All fields are optional with empty defaults so partial data never causes
validation errors. List items accept both object and plain-string forms.
"""

from typing import List, Union

from pydantic import BaseModel


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
    # accept both 'fieldOfStudy' and 'field'
    fieldOfStudy: str = ""
    field: str = ""
    startDate: str = ""
    startYear: str = ""
    endDate: str = ""
    endYear: str = ""
    percentage: str = ""

    class Config:
        extra = "allow"  # ignore unknown keys silently


class Experience(BaseModel):
    company: str = ""
    position: str = ""
    role: str = ""        # alias used by some clients
    location: str = ""
    startDate: str = ""
    endDate: str = ""
    description: str = ""
    isCurrentlyWorking: bool = False

    class Config:
        extra = "allow"


class Certification(BaseModel):
    certificateName: str = ""
    title: str = ""       # alias used by some clients
    issuingOrganization: str = ""
    issuer: str = ""      # alias used by some clients
    issueDate: str = ""
    year: str = ""        # alias used by some clients
    expiryDate: str = ""
    credentialId: str = ""

    class Config:
        extra = "allow"


class Achievement(BaseModel):
    title: str = ""
    date: str = ""
    description: str = ""

    class Config:
        extra = "allow"


class ResumeData(BaseModel):
    """
    Full structured resume data.

    Each list field accepts either objects or plain strings so the schema
    works regardless of how the client formats the data.
    """

    aboutMe: str = ""
    personalInfo: PersonalInfo = PersonalInfo()
    educations: List[Union[Education, str]] = []
    skills: List[str] = []
    experience: List[Union[Experience, str]] = []
    certifications: List[Union[Certification, str]] = []
    achievements: List[Union[Achievement, str]] = []

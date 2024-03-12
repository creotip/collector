from pydantic import BaseModel, Field, HttpUrl, field_validator


class JobPromotion(BaseModel):
    job_title: str
    raw_date: str = Field(
        description="Raw date field that appears below job title",
        example="Jan 2020 - Present  4 yrs 2 mos",
    )


class Experience(BaseModel):
    title: str
    company_url: HttpUrl | None = Field(description="URL of the company's LinkedIn page")
    promotions: list[JobPromotion]

    @field_validator("company_url")
    @classmethod
    def validate_company_link(cls, v):
        if not v:
            return v
        if "?" in v.path:
            raise ValueError("company_link must not contain '?'")
        return v


class EducationHistory(BaseModel):
    title: str


class Certification(BaseModel):
    title: str
    issuer: str


class Accomplishments(BaseModel):
    certifications: list[Certification]
    languages: list[str]


class ContactInfo(BaseModel):
    title: str
    value: str


class UserProfileMetadata(BaseModel):
    profile_name: str
    profile_image: str
    profile_url: str = Field(description="LinkedIn profile URL", pattern="https://www.linkedin.com/in/.+")
    open_to_work: bool
    education: str
    current_company: str
    location: str | None
    about: str
    experiences: list[Experience]
    skills: list[str]
    education_history: list[EducationHistory]
    accomplishments: Accomplishments
    contact_info: list[ContactInfo]

    class Config:
        str_strip_whitespace = True

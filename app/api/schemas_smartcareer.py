from pydantic import BaseModel, Field

class StudentProfileIn(BaseModel):
    sphere: str = "IT"
    full_name: str | None = None
    github: str | None = None
    resume_url: str | None = None

    skills: list[str] = Field(default_factory=list)
    technologies: list[str] = Field(default_factory=list)
    projects: list[dict] = Field(default_factory=list)
    interests: list[str] = Field(default_factory=list)
    experience_years: int = 0

class StudentProfileOut(StudentProfileIn):
    id: int
    user_id: int

class EmployerProfileIn(BaseModel):
    company_name: str
    website: str | None = None

class EmployerProfileOut(EmployerProfileIn):
    id: int
    user_id: int

class JobIn(BaseModel):
    title: str
    description: str
    level: str = "junior"
    location: str | None = None
    sphere: str = "IT"
    required_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)

class JobOut(JobIn):
    id: int
    employer_id: int

class MatchOut(BaseModel):
    job_id: int
    score: int
    missing_skills: list[str]
    explanation: str
    roadmap: list[str]

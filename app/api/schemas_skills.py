from pydantic import BaseModel, Field

class SkillIn(BaseModel):
    name: str
    level: int = Field(ge=1, le=5)

class SkillOut(SkillIn):
    id: int
    verified: bool

class ResumeStatsOut(BaseModel):
    sphere: str
    fit_percent: int
    strong_skills: list[str]
    weak_skills: list[str]
    all_skills: list[dict]  # [{name, level, verified}]
    matching_jobs_count: int
    matching_roles_count: int

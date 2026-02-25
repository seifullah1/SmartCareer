from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.roles import require_role
from app.models.models import User
from app.models.smartcareer import StudentProfile, Job
from app.api.schemas_smartcareer import StudentProfileIn, StudentProfileOut, MatchOut
from app.services.ai_matching import match

router = APIRouter(prefix="/student", tags=["student"])

@router.get("/profile", response_model=StudentProfileOut)
def get_profile(current: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    prof = db.query(StudentProfile).filter(StudentProfile.user_id == current.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Profile not found")
    return StudentProfileOut(
        id=prof.id, user_id=prof.user_id,
        sphere=prof.sphere,
        full_name=prof.full_name,
        github=prof.github,
        resume_url=prof.resume_url,
        skills=prof.skills or [], technologies=prof.technologies or [],
        projects=prof.projects or [], interests=prof.interests or [],
        experience_years=prof.experience_years or 0,
    )

@router.post("/profile", response_model=StudentProfileOut)
def upsert_profile(data: StudentProfileIn, current: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    prof = db.query(StudentProfile).filter(StudentProfile.user_id == current.id).first()
    if not prof:
        prof = StudentProfile(user_id=current.id)
        db.add(prof)

    prof.sphere = data.sphere
    prof.full_name = data.full_name
    prof.github = data.github
    prof.resume_url = data.resume_url

    prof.skills = data.skills
    prof.technologies = data.technologies
    prof.projects = data.projects
    prof.interests = data.interests
    prof.experience_years = data.experience_years

    db.commit()
    db.refresh(prof)

    return StudentProfileOut(
        id=prof.id, user_id=prof.user_id,
        sphere=prof.sphere,
        full_name=prof.full_name,
        github=prof.github,
        resume_url=prof.resume_url,
        skills=prof.skills or [], technologies=prof.technologies or [],
        projects=prof.projects or [], interests=prof.interests or [],
        experience_years=prof.experience_years or 0,
    )

@router.post("/match/{job_id}", response_model=MatchOut)
def match_to_job(job_id: int, current: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    prof = db.query(StudentProfile).filter(StudentProfile.user_id == current.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Profile not found")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    result = match((prof.skills or []) + (prof.technologies or []), job.required_skills or [])
    return MatchOut(job_id=job.id, score=result["score"], missing_skills=result["missing_skills"],
                    explanation=result["explanation"], roadmap=result["roadmap"])

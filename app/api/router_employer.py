from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.roles import require_role
from app.models.models import User
from app.models.smartcareer import EmployerProfile, Job, StudentProfile
from app.api.schemas_smartcareer import EmployerProfileIn, EmployerProfileOut, JobIn, JobOut
from app.services.ai_matching import match

router = APIRouter(prefix="/employer", tags=["employer"])

@router.post("/profile", response_model=EmployerProfileOut)
def upsert_employer_profile(data: EmployerProfileIn, current: User = Depends(require_role("employer")), db: Session = Depends(get_db)):
    prof = db.query(EmployerProfile).filter(EmployerProfile.user_id == current.id).first()
    if not prof:
        prof = EmployerProfile(user_id=current.id, company_name=data.company_name, website=data.website)
        db.add(prof)
    else:
        prof.company_name = data.company_name
        prof.website = data.website

    db.commit()
    db.refresh(prof)
    return EmployerProfileOut(id=prof.id, user_id=prof.user_id, company_name=prof.company_name, website=prof.website)

@router.post("/jobs", response_model=JobOut)
def create_job(data: JobIn, current: User = Depends(require_role("employer")), db: Session = Depends(get_db)):
    job = Job(
        employer_id=current.id,
        title=data.title,
        description=data.description,
        level=data.level,
        location=data.location,
        sphere=data.sphere,
        required_skills=data.required_skills,
        soft_skills=data.soft_skills,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return JobOut(
        id=job.id, employer_id=job.employer_id, title=job.title, description=job.description,
        level=job.level, location=job.location, sphere=job.sphere,
        required_skills=job.required_skills or [], soft_skills=job.soft_skills or []
    )

@router.get("/jobs", response_model=list[JobOut])
def my_jobs(current: User = Depends(require_role("employer")), db: Session = Depends(get_db)):
    jobs = db.query(Job).filter(Job.employer_id == current.id).order_by(Job.id.desc()).all()
    return [
        JobOut(
            id=j.id, employer_id=j.employer_id, title=j.title, description=j.description,
            level=j.level, location=j.location, sphere=j.sphere,
            required_skills=j.required_skills or [], soft_skills=j.soft_skills or []
        ) for j in jobs
    ]

@router.get("/jobs/{job_id}/candidates")
def candidates(job_id: int, current: User = Depends(require_role("employer")), db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id, Job.employer_id == current.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    profiles = db.query(StudentProfile).all()
    results = []
    for p in profiles:
        r = match((p.skills or []) + (p.technologies or []), job.required_skills or [])
        results.append({
            "student_user_id": p.user_id,
            "full_name": p.full_name,
            "score": r["score"],
            "missing_skills": r["missing_skills"][:8],
            "explanation": r["explanation"],
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return {"job_id": job_id, "candidates": results[:50]}

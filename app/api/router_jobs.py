from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.models.smartcareer import Job
from app.api.schemas_smartcareer import JobOut

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("", response_model=list[JobOut])
def list_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).order_by(Job.id.desc()).limit(50).all()
    return [
        JobOut(
            id=j.id, employer_id=j.employer_id, title=j.title, description=j.description,
            level=j.level, location=j.location, required_skills=j.required_skills or [],
            soft_skills=j.soft_skills or []
        ) for j in jobs
    ]

@router.get("/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    j = db.query(Job).filter(Job.id == job_id).first()
    if not j:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobOut(
        id=j.id, employer_id=j.employer_id, title=j.title, description=j.description,
        level=j.level, location=j.location, required_skills=j.required_skills or [],
        soft_skills=j.soft_skills or []
    )

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.roles import require_role
from app.models.models import User
from app.models.smartcareer import Job
from app.models.applications import Application

router = APIRouter(prefix="/apply", tags=["apply"])

@router.post("/jobs/{job_id}")
def apply_to_job(
    job_id: int,
    current: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # unique constraint защищает от дублей
    app = Application(job_id=job.id, student_id=current.id, employer_id=job.employer_id, status="sent")
    db.add(app)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=409, detail="Already applied")

    return {"application_id": app.id, "status": app.status}

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.roles import require_role
from app.models.models import User
from app.models.applications import Application
from app.models.smartcareer import Job
from app.models.skills import StudentSkill
from app.models.smartcareer import StudentProfile

router = APIRouter(prefix="/employer/applications", tags=["employer"])

@router.get("")
def list_applications(
    current: User = Depends(require_role("employer")),
    db: Session = Depends(get_db),
):
    apps = db.query(Application).filter(Application.employer_id == current.id).order_by(Application.id.desc()).limit(100).all()

    job_ids = list({a.job_id for a in apps})
    jobs = {j.id: j for j in db.query(Job).filter(Job.id.in_(job_ids)).all()} if job_ids else {}

    student_ids = list({a.student_id for a in apps})
    profiles = {p.user_id: p for p in db.query(StudentProfile).filter(StudentProfile.user_id.in_(student_ids)).all()} if student_ids else {}

    # skills кратко для просмотра
    skill_rows = db.query(StudentSkill).filter(StudentSkill.user_id.in_(student_ids)).all() if student_ids else []
    skills_map = {}
    for r in skill_rows:
        skills_map.setdefault(r.user_id, []).append({"name": r.name, "level": r.level, "verified": r.verified})

    out = []
    for a in apps:
        j = jobs.get(a.job_id)
        p = profiles.get(a.student_id)
        out.append({
            "application_id": a.id,
            "status": a.status,
            "job": {"id": a.job_id, "title": j.title if j else None},
            "student": {
                "user_id": a.student_id,
                "full_name": p.full_name if p else None,
                "skills": skills_map.get(a.student_id, [])[:12],
            },
            "created_at": str(a.created_at),
        })

    return {"count": len(out), "applications": out}

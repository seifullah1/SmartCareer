from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.roles import require_role
from app.models.models import User
from app.models.smartcareer import StudentProfile, Job
from app.models.skills import StudentSkill
from app.services.ai_matching import match
from app.services.ai_plans import what_if, learning_plan

router = APIRouter(prefix="/student/ai", tags=["student-ai"])

@router.post("/what-if", summary="What-if: improve selected skills")
def what_if_endpoint(payload: dict, current: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    """
    Input:
    - skills_to_improve: list of skills
    - target_job_id: optional job id to compute current fit
    - lang: ru|kz|en
    """
    lang = payload.get("lang", "ru")
    skills_to_improve = payload.get("skills_to_improve", [])
    target_job_id = payload.get("target_job_id")

    prof = db.query(StudentProfile).filter(StudentProfile.user_id == current.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Profile not found")

    skills_rows = db.query(StudentSkill).filter(StudentSkill.user_id == current.id).all()
    profile_skills = (prof.skills or []) + (prof.technologies or []) + [r.name for r in skills_rows]

    target_role = prof.sphere
    current_fit = 50

    if target_job_id:
        job = db.query(Job).filter(Job.id == int(target_job_id)).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        target_role = job.title
        res = match(profile_skills, job.required_skills or [], job_title=job.title)
        current_fit = int(res.get("score", 0))

    return what_if(skills_to_improve=skills_to_improve, current_fit=current_fit, target_role=target_role, lang=lang)

@router.post("/learning-plan", summary="Generate learning plan")
def learning_plan_endpoint(payload: dict, current: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    """
    Input:
    - skills: optional list (if empty -> take from profile+skills table)
    - target_role: desired role name
    - lang: ru|kz|en
    """
    lang = payload.get("lang", "ru")
    target_role = payload.get("target_role", "Junior Developer")
    skills = payload.get("skills", [])

    if not skills:
        prof = db.query(StudentProfile).filter(StudentProfile.user_id == current.id).first()
        skills_rows = db.query(StudentSkill).filter(StudentSkill.user_id == current.id).all()
        skills = (prof.skills or []) + (prof.technologies or []) + [r.name for r in skills_rows]

    return learning_plan(skills=skills, target_role=target_role, lang=lang)

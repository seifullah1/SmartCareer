from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.roles import require_role
from app.models.models import User
from app.models.smartcareer import StudentProfile, Job
from app.models.skills import StudentSkill
from app.services.ai_matching import match

router = APIRouter(prefix="/student", tags=["student"])

@router.get("/stats")
def student_stats(
    current: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    prof = db.query(StudentProfile).filter(StudentProfile.user_id == current.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Profile not found")

    skills_rows = db.query(StudentSkill).filter(StudentSkill.user_id == current.id).all()
    all_skills = [{"name": r.name, "level": r.level, "verified": r.verified} for r in skills_rows]

    strong = [r.name for r in skills_rows if (r.verified or r.level >= 4)]
    weak = [r.name for r in skills_rows if ((not r.verified) and r.level <= 2)]

    # вакансии по сфере профиля
    jobs = db.query(Job).filter(Job.sphere == prof.sphere).order_by(Job.id.desc()).limit(50).all()

    # считаем средний мэтч по первым N вакансиям
    profile_skill_list = (prof.skills or []) + (prof.technologies or []) + [s["name"] for s in all_skills]
    scores = []
    for j in jobs[:15]:
        res = match(profile_skill_list, j.required_skills or [], job_title=j.title)
        scores.append(int(res.get("score", 0)))

    fit = int(round(sum(scores) / max(1, len(scores)))) if scores else 0

    matching_jobs = sum(1 for s in scores if s >= 60)
    roles = len(set([j.title for j in jobs]))  # грубо: разные профессии по title

    return {
        "sphere": prof.sphere,
        "fit_percent": fit,
        "matching_jobs_count": matching_jobs,
        "matching_roles_count": roles,
        "strong_skills": strong[:10],
        "weak_skills": weak[:10],
        "all_skills": all_skills
    }

@router.get("/jobs")
def student_jobs(
    current: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    prof = db.query(StudentProfile).filter(StudentProfile.user_id == current.id).first()
    if not prof:
        raise HTTPException(status_code=404, detail="Profile not found")

    skills_rows = db.query(StudentSkill).filter(StudentSkill.user_id == current.id).all()
    profile_skill_list = (prof.skills or []) + (prof.technologies or []) + [r.name for r in skills_rows]

    jobs = db.query(Job).filter(Job.sphere == prof.sphere).order_by(Job.id.desc()).limit(50).all()

    items = []
    scores = []
    for j in jobs:
        res = match(profile_skill_list, j.required_skills or [], job_title=j.title)
        score = int(res.get("score", 0))
        scores.append(score)
        items.append({
            "job_id": j.id,
            "title": j.title,
            "level": j.level,
            "location": j.location,
            "match_percent": score,
            "missing_skills": res.get("missing_skills", [])[:8],
            "recommendation": (res.get("roadmap", [])[:3] or []),
        })

    items.sort(key=lambda x: x["match_percent"], reverse=True)
    avg = int(round(sum(scores) / max(1, len(scores)))) if scores else 0

    return {
        "sphere": prof.sphere,
        "total_jobs": len(items),
        "avg_match": avg,
        "jobs": items
    }

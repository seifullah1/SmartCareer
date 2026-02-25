from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.roles import require_role
from app.models.models import User
from app.models.skills import Resume, StudentSkill
from app.models.smartcareer import StudentProfile
from app.services.ai_resume import analyze_resume

router = APIRouter(prefix="/resume", tags=["resume"])

@router.post("/{resume_id}/analyze")
def analyze(
    resume_id: int,
    current: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    res = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current.id).first()
    if not res:
        raise HTTPException(status_code=404, detail="Resume not found")
    if not res.extracted_text:
        raise HTTPException(status_code=400, detail="Resume text is empty")

    prof = db.query(StudentProfile).filter(StudentProfile.user_id == current.id).first()
    sphere = prof.sphere if prof else "IT"

    summary = analyze_resume(res.extracted_text, sphere=sphere)
    res.ai_summary = summary
    db.commit()

    # авто-апдейт skills
    skills = summary.get("skills", []) or []
    upserted = 0
    for s in skills:
        name = (s.get("name") or "").strip()
        level = int(s.get("level") or 1)
        if not name:
            continue
        row = db.query(StudentSkill).filter(StudentSkill.user_id == current.id, StudentSkill.name == name).first()
        if not row:
            row = StudentSkill(user_id=current.id, name=name, level=max(1, min(5, level)), verified=False)
            db.add(row)
            upserted += 1
        else:
            # повышаем уровень, но не понижаем
            row.level = max(row.level, max(1, min(5, level)))

    db.commit()
    return {"resume_id": resume_id, "ai_summary": summary, "skills_upserted": upserted}

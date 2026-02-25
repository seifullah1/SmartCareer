from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.db.deps import get_db
from app.api.roles import require_role
from app.models.models import User
from app.models.skills import StudentSkill, SkillTest, SkillTestAttempt
from app.api.schemas_skills import SkillIn, SkillOut

router = APIRouter(prefix="/skills", tags=["skills"])

@router.get("", response_model=list[SkillOut])
def list_skills(current: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    rows = db.query(StudentSkill).filter(StudentSkill.user_id == current.id).order_by(StudentSkill.name.asc()).all()
    return [SkillOut(id=r.id, name=r.name, level=r.level, verified=r.verified) for r in rows]

@router.post("", response_model=SkillOut)
def upsert_skill(data: SkillIn, current: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    row = db.query(StudentSkill).filter(StudentSkill.user_id == current.id, StudentSkill.name == data.name).first()
    if not row:
        row = StudentSkill(user_id=current.id, name=data.name, level=data.level, verified=False)
        db.add(row)
    else:
        row.level = data.level
    db.commit()
    db.refresh(row)
    return SkillOut(id=row.id, name=row.name, level=row.level, verified=row.verified)

@router.post("/tests/{skill_name}")
def create_skill_test(skill_name: str, current: User = Depends(require_role("student")), db: Session = Depends(get_db)):
  
    questions = {
        "skill": skill_name,
        "questions": [
            {"id":"q1","type":"mcq","prompt":f"{skill_name}: sample question 1","options":["A","B","C","D"],"answer":"A"},
            {"id":"q2","type":"mcq","prompt":f"{skill_name}: sample question 2","options":["A","B","C","D"],"answer":"B"},
            {"id":"q3","type":"mcq","prompt":f"{skill_name}: sample question 3","options":["A","B","C","D"],"answer":"C"},
            {"id":"q4","type":"mcq","prompt":f"{skill_name}: sample question 4","options":["A","B","C","D"],"answer":"D"},
            {"id":"q5","type":"mcq","prompt":f"{skill_name}: sample question 5","options":["A","B","C","D"],"answer":"A"},
        ]
    }
    test = SkillTest(user_id=current.id, skill_name=skill_name, questions=questions)
    db.add(test)
    db.commit()
    db.refresh(test)
    safe = {**questions, "questions":[{k:v for k,v in q.items() if k!="answer"} for q in questions["questions"]]}
    return {"test_id": test.id, "test": safe}

@router.post("/tests/{test_id}/submit")
def submit_skill_test(test_id: int, payload: dict, current: User = Depends(require_role("student")), db: Session = Depends(get_db)):
    test = db.query(SkillTest).filter(SkillTest.id == test_id, SkillTest.user_id == current.id).first()
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    answers = payload.get("answers", {})
    qs = test.questions.get("questions", [])
    total = len(qs)
    correct = 0
    for q in qs:
        if answers.get(q["id"]) == q.get("answer"):
            correct += 1

    score = int(round(100 * correct / max(1,total)))
    passed = score >= 70

    attempt = SkillTestAttempt(test_id=test.id, user_id=current.id, answers=answers, score=score, passed=passed, feedback={})
    db.add(attempt)

    # если passed — отмечаем skill verified
    if passed:
        skill_name = test.skill_name
        row = db.query(StudentSkill).filter(StudentSkill.user_id == current.id, StudentSkill.name == skill_name).first()
        if not row:
            row = StudentSkill(user_id=current.id, name=skill_name, level=3, verified=True, verified_at=datetime.now(timezone.utc))
            db.add(row)
        else:
            row.verified = True
            row.verified_at = datetime.now(timezone.utc)

    db.commit()
    return {"score": score, "passed": passed}

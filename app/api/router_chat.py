from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.deps_auth import get_current_user
from app.models.models import User
from app.models.smartcareer import Job
from app.models.chat import ChatThread, ChatMessage

router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/threads/{job_id}")
def start_thread(job_id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current.role != "student":
        raise HTTPException(status_code=403, detail="Only student can start a chat")

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    thread = db.query(ChatThread).filter(ChatThread.job_id == job_id, ChatThread.student_id == current.id).first()
    if thread:
        return {"thread_id": thread.id}

    thread = ChatThread(job_id=job_id, student_id=current.id, employer_id=job.employer_id)
    db.add(thread)
    try:
        db.commit()
    except Exception:
        db.rollback()
        thread = db.query(ChatThread).filter(ChatThread.job_id == job_id, ChatThread.student_id == current.id).first()
        if thread:
            return {"thread_id": thread.id}
        raise

    db.refresh(thread)
    return {"thread_id": thread.id}

@router.get("/threads/{thread_id}")
def list_messages(thread_id: int, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    thread = db.query(ChatThread).filter(ChatThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    if current.role == "student" and thread.student_id != current.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if current.role == "employer" and thread.employer_id != current.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    msgs = db.query(ChatMessage).filter(ChatMessage.thread_id == thread_id).order_by(ChatMessage.id.asc()).all()
    return {
        "thread_id": thread_id,
        "messages": [{"id": m.id, "sender_role": m.sender_role, "text": m.text, "created_at": str(m.created_at)} for m in msgs]
    }

@router.post("/threads/{thread_id}/send")
def send_message(thread_id: int, payload: dict, current: User = Depends(get_current_user), db: Session = Depends(get_db)):
    text = (payload.get("text") or "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Empty text")

    thread = db.query(ChatThread).filter(ChatThread.id == thread_id).first()
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    if current.role == "student" and thread.student_id != current.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if current.role == "employer" and thread.employer_id != current.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    msg = ChatMessage(thread_id=thread_id, sender_role=current.role, text=text)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return {"message_id": msg.id}

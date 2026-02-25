import os
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from pypdf import PdfReader
import docx

from app.db.deps import get_db
from app.api.roles import require_role
from app.models.models import User
from app.models.skills import Resume

router = APIRouter(prefix="/resume", tags=["resume"])

STORAGE_DIR = "/app/storage/resumes"

def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    parts = []
    for page in reader.pages:
        parts.append(page.extract_text() or "")
    return "\n".join(parts).strip()

def extract_text_from_docx(path: str) -> str:
    d = docx.Document(path)
    return "\n".join([p.text for p in d.paragraphs]).strip()

@router.post("/upload")
def upload_resume(
    file: UploadFile = File(...),
    current: User = Depends(require_role("student")),
    db: Session = Depends(get_db),
):
    os.makedirs(STORAGE_DIR, exist_ok=True)
    fname = file.filename or "resume"
    ext = os.path.splitext(fname)[1].lower()
    if ext not in [".pdf", ".docx"]:
        raise HTTPException(status_code=400, detail="Only PDF or DOCX allowed")

    save_path = os.path.join(STORAGE_DIR, f"user_{current.id}_{fname}")
    content = file.file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    if ext == ".pdf":
        text = extract_text_from_pdf(save_path)
    else:
        text = extract_text_from_docx(save_path)

    rec = Resume(user_id=current.id, filename=fname, file_path=save_path, extracted_text=text, ai_summary={})
    db.add(rec)
    db.commit()
    db.refresh(rec)

    return {"resume_id": rec.id, "filename": rec.filename, "chars": len(text)}

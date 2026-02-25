from fastapi import APIRouter, Depends
from app.api.roles import require_role
from app.models.models import User
from app.services.ai_plans import learning_plan

router = APIRouter(prefix="/soft-skills", tags=["soft-skills"])

VIDEOS = {
    "ru": [
        "https://www.youtube.com/watch?v=6u8Yq1v2z6A",
        "https://www.youtube.com/watch?v=1mHjMNZZvFo",
        "https://www.youtube.com/watch?v=H14bBuluwB8",
    ],
    "en": [
        "https://www.youtube.com/watch?v=HG68Ymazo18",
        "https://www.youtube.com/watch?v=1G4isv_Fylg",
        "https://www.youtube.com/watch?v=V8eFv2nF3Ck",
    ],
    "kz": [
        "https://www.youtube.com/watch?v=6u8Yq1v2z6A",
        "https://www.youtube.com/watch?v=1mHjMNZZvFo",
        "https://www.youtube.com/watch?v=H14bBuluwB8",
    ],
}

@router.get("/recommend")
def recommend(lang: str = "ru", current: User = Depends(require_role("student"))):
    # короткий AI-план по soft skills
    plan = learning_plan(
        skills=["Interview communication", "Self-presentation", "Negotiation", "Teamwork"],
        target_role="Interview / workplace success",
        lang=lang
    )
    return {
        "lang": lang,
        "videos": VIDEOS.get(lang, VIDEOS["ru"]),
        "ai_plan": plan
    }

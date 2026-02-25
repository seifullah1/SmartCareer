from fastapi import APIRouter, Depends
from app.api.roles import require_role
from app.models.models import User

router = APIRouter(prefix="/courses", tags=["courses"])

COURSES = {
    "Python": [
        "https://www.youtube.com/watch?v=_uQrJ0TkZlc",
        "https://www.coursera.org/learn/python",
    ],
    "Docker": [
        "https://www.youtube.com/watch?v=fqMOX6JJhGo",
    ],
    "SQL": [
        "https://www.youtube.com/watch?v=HXV3zeQKqGY",
    ],
}

@router.get("")
def get_courses(skill: str = "Python", current: User = Depends(require_role("student"))):
    return {
        "skill": skill,
        "videos": COURSES.get(skill, []),
    }

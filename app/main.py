from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router_auth import router as auth_router
from app.api.router_student import router as student_router
from app.api.router_student_stats import router as student_stats_router
from app.api.router_student_ai import router as student_ai_router
from app.api.router_courses import router as courses_router
from app.api.router_employer import router as employer_router
from app.api.router_jobs import router as jobs_router
from app.api.router_resume import router as resume_router
from app.api.router_resume_analyze import router as resume_analyze_router
from app.api.router_skills import router as skills_router
from app.api.router_apply import router as apply_router
from app.api.router_employer_applications import router as employer_apps_router
from app.api.router_chat import router as chat_router
from app.api.router_softskills import router as softskills_router
from app.api.router_trends import router as trends_router

app = FastAPI(title="Smart Career Backend")


tags_metadata = [
    {"name": "auth", "description": "Registration/login (JWT)."},
    {"name": "student", "description": "Student profile, stats, job matching."},
    {"name": "student-ai", "description": "AI features: what-if, learning plan."},
    {"name": "resume", "description": "Resume upload + AI analysis (PDF/DOCX)."},
    {"name": "skills", "description": "Skills CRUD + skill verification tests."},
    {"name": "jobs", "description": "Public jobs feed and job details."},
    {"name": "apply", "description": "Student applications to jobs."},
    {"name": "employer", "description": "Employer profile + jobs management + analytics."},
    {"name": "chat", "description": "Job chat between student and employer."},
    {"name": "soft-skills", "description": "Soft skills recommendations + videos."},
    {"name": "trends", "description": "Trending skills daily + cached in DB."},
]

app = FastAPI(
    title="CareerMatch AI API",
    description=(
        "API for bridging education ↔ job market.\n\n"
        "Roles:\n"
        "- student\n"
        "- employer\n\n"
        "Auth: Bearer JWT in `Authorization: Bearer <token>`."
    ),
    version="1.0.0",
    openapi_tags=tags_metadata,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(student_router)
app.include_router(student_stats_router)
app.include_router(student_ai_router)

app.include_router(employer_router)
app.include_router(jobs_router)

app.include_router(resume_router)
app.include_router(resume_analyze_router)
app.include_router(skills_router)

app.include_router(apply_router)
app.include_router(employer_apps_router)

app.include_router(chat_router)
app.include_router(softskills_router)
app.include_router(trends_router)
app.include_router(courses_router)

@app.get("/health")
def health():
    return {"status": "ok"}

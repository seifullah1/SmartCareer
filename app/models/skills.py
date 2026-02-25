from sqlalchemy import Integer, ForeignKey, DateTime, func, String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from app.db.session import Base

class Resume(Base):
    __tablename__ = "resumes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    file_path: Mapped[str] = mapped_column(String(512))
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_summary: Mapped[dict] = mapped_column(JSONB, default=dict)  # skills, roles, etc
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class StudentSkill(Base):
    __tablename__ = "student_skills"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    name: Mapped[str] = mapped_column(String(128), index=True)
    level: Mapped[int] = mapped_column(Integer, default=1)  # 1..5
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class SkillTest(Base):
    __tablename__ = "skill_tests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    skill_name: Mapped[str] = mapped_column(String(128), index=True)
    questions: Mapped[dict] = mapped_column(JSONB)  # {questions:[...]}
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class SkillTestAttempt(Base):
    __tablename__ = "skill_test_attempts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("skill_tests.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    answers: Mapped[dict] = mapped_column(JSONB)   # {q1:"A",...}
    score: Mapped[int] = mapped_column(Integer, default=0)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    feedback: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

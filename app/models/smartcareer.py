from sqlalchemy import String, Integer, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from app.db.session import Base

class StudentProfile(Base):
    __tablename__ = "student_profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)

    sphere: Mapped[str] = mapped_column(String(64), default="IT")  # IT/Finance/etc
    full_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    github: Mapped[str | None] = mapped_column(String(255), nullable=True)
    resume_url: Mapped[str | None] = mapped_column(String(255), nullable=True)

    skills: Mapped[list] = mapped_column(JSONB, default=list)
    technologies: Mapped[list] = mapped_column(JSONB, default=list)
    projects: Mapped[list] = mapped_column(JSONB, default=list)
    interests: Mapped[list] = mapped_column(JSONB, default=list)
    experience_years: Mapped[int] = mapped_column(Integer, default=0)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class EmployerProfile(Base):
    __tablename__ = "employer_profiles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, index=True)

    company_name: Mapped[str] = mapped_column(String(255))
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    level: Mapped[str] = mapped_column(String(64), default="junior")
    location: Mapped[str | None] = mapped_column(String(128), nullable=True)

    sphere: Mapped[str] = mapped_column(String(64), default="IT")
    required_skills: Mapped[list] = mapped_column(JSONB, default=list)
    soft_skills: Mapped[list] = mapped_column(JSONB, default=list)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

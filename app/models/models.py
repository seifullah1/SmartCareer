from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from app.db.session import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="student")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class Subject(Base):
    __tablename__ = "subjects"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), unique=True, index=True)

class Test(Base):
    __tablename__ = "tests"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"))
    difficulty: Mapped[str] = mapped_column(String(32))
    generated_payload: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class TestAttempt(Base):
    __tablename__ = "test_attempts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    test_id: Mapped[int] = mapped_column(ForeignKey("tests.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    answers: Mapped[dict] = mapped_column(JSONB)
    score: Mapped[int] = mapped_column(Integer, default=0)
    feedback: Mapped[dict] = mapped_column(JSONB, default={})
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

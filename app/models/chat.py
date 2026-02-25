from sqlalchemy import Integer, ForeignKey, DateTime, func, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class ChatThread(Base):
    __tablename__ = "chat_threads"
    __table_args__ = (UniqueConstraint("job_id","student_id", name="uq_thread_job_student"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    employer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    thread_id: Mapped[int] = mapped_column(ForeignKey("chat_threads.id"), index=True)
    sender_role: Mapped[str] = mapped_column(String(16))  # student/employer
    text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

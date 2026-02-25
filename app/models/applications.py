from sqlalchemy import Integer, ForeignKey, DateTime, func, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base

class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (
        UniqueConstraint("job_id", "student_id", name="uq_application_job_student"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), index=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)     # user.id with role=student
    employer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)    # job.employer_id

    status: Mapped[str] = mapped_column(String(32), default="sent")  # sent/reviewed/accepted/rejected
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

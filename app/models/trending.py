from sqlalchemy import Integer, Date, DateTime, func, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from app.db.session import Base

class TrendingCache(Base):
    __tablename__ = "trending_cache"
    __table_args__ = (
        UniqueConstraint("day", "sphere", "lang", "country", name="uq_trending_day_sphere_lang_country"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    day: Mapped["Date"] = mapped_column(Date, index=True)
    sphere: Mapped[str] = mapped_column(String(64), index=True)
    lang: Mapped[str] = mapped_column(String(8), index=True)
    country: Mapped[str] = mapped_column(String(8), index=True)

    data: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

from datetime import date
from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session
from app.db.deps import get_db

from app.models.trending import TrendingCache
from app.services.ai_trends import trending

router = APIRouter(prefix="/trends", tags=["trends"])

@router.get("")
def get_trends(sphere: str = "IT", lang: str = "ru", country: str = "KZ", db: Session = Depends(get_db)):
    today = date.today()

    row = (
        db.query(TrendingCache)
        .filter(
            TrendingCache.day == today,
            TrendingCache.sphere == sphere,
            TrendingCache.lang == lang,
            TrendingCache.country == country,
        )
        .first()
    )
    if row and row.data:
        return {"cached": True, **row.data}

    data = trending(sphere=sphere, lang=lang, country=country)
    row = TrendingCache(day=today, sphere=sphere, lang=lang, country=country, data=data)
    db.add(row)
    db.commit()
    return {"cached": False, **data}

@router.post("/refresh")
def refresh_trends(sphere: str = "IT", lang: str = "ru", country: str = "KZ", db: Session = Depends(get_db)):
    today = date.today()
    data = trending(sphere=sphere, lang=lang, country=country)

    row = (
        db.query(TrendingCache)
        .filter(
            TrendingCache.day == today,
            TrendingCache.sphere == sphere,
            TrendingCache.lang == lang,
            TrendingCache.country == country,
        )
        .first()
    )
    if row:
        row.data = data
    else:
        row = TrendingCache(day=today, sphere=sphere, lang=lang, country=country, data=data)
        db.add(row)

    db.commit()
    return {"refreshed": True, **data}

from __future__ import annotations
import json
import httpx
from datetime import datetime, timezone
from app.core.config import settings

def trending(sphere: str, lang: str, country: str = "KZ") -> dict:
    if not settings.openai_api_key:
        return {"sphere": sphere, "lang": lang, "country": country, "skills": ["Python","SQL","Docker"], "note": "Fallback trends."}

    system = "You are a labor market analyst. Output ONLY valid JSON. No markdown. No extra keys."
    user_payload = {
        "lang": lang,
        "sphere": sphere,
        "country": country,
        "time_window": "next 30 days",
        "task": "Return top trending skills and a short note for students."
    }

    schema = {
        "type":"object",
        "properties":{
            "sphere":{"type":"string"},
            "lang":{"type":"string"},
            "country":{"type":"string"},
            "skills":{"type":"array","items":{"type":"string"}},
            "note":{"type":"string"},
            "generated_at":{"type":"string"}
        },
        "required":["sphere","lang","country","skills","note","generated_at"],
        "additionalProperties": False
    }

    body = {
        "model": settings.openai_model,
        "input": [
            {"role":"system","content": system},
            {"role":"user","content": json.dumps(user_payload, ensure_ascii=False)}
        ],
        "text": {"format":{"type":"json_schema","name":"trends","schema": schema, "strict": True}},
        "store": False
    }

    with httpx.Client(timeout=35.0) as client:
        r = client.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {settings.openai_api_key}", "Content-Type":"application/json"},
            json=body
        )
        r.raise_for_status()
        data = r.json()
        out = (data.get("output_text") or "").strip()
        if not out:
            return {"sphere": sphere, "lang": lang, "country": country, "skills": [], "note": "", "generated_at": datetime.now(timezone.utc).isoformat()}
        return json.loads(out)

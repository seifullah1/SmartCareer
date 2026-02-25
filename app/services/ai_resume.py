from __future__ import annotations
import json
import httpx
from app.core.config import settings

def analyze_resume(text: str, sphere: str) -> dict:
    # fallback, если ключа нет
    if not settings.openai_api_key:
        return {
            "sphere": sphere,
            "suggested_roles": ["Junior Developer"],
            "skills": [{"name":"Python","level":3},{"name":"SQL","level":2}],
            "strong_skills": ["Python"],
            "weak_skills": ["SQL"],
            "summary": "Fallback resume analysis (no AI key)."
        }

    system = (
        "You are an HR resume analyzer. Output ONLY valid JSON according to schema. "
        "No markdown. No extra keys."
    )

    user_payload = {
        "sphere": sphere,
        "resume_text": text[:12000],  # ограничим чтобы не улететь по токенам
        "task": "Extract skills with levels 1-5, suggest roles, identify strong/weak skills and give a short summary."
    }

    schema = {
        "type": "object",
        "properties": {
            "sphere": {"type": "string"},
            "suggested_roles": {"type": "array", "items": {"type": "string"}},
            "skills": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "level": {"type": "integer", "minimum": 1, "maximum": 5}
                    },
                    "required": ["name", "level"],
                    "additionalProperties": False
                }
            },
            "strong_skills": {"type": "array", "items": {"type": "string"}},
            "weak_skills": {"type": "array", "items": {"type": "string"}},
            "summary": {"type": "string"}
        },
        "required": ["sphere", "suggested_roles", "skills", "strong_skills", "weak_skills", "summary"],
        "additionalProperties": False
    }

    body = {
        "model": settings.openai_model,
        "input": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)}
        ],
        "text": {"format": {"type": "json_schema", "name": "resume_analysis", "schema": schema, "strict": True}},
        "store": False
    }

    with httpx.Client(timeout=30.0) as client:
        r = client.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {settings.openai_api_key}", "Content-Type": "application/json"},
            json=body,
        )
        r.raise_for_status()
        data = r.json()
        out_text = (data.get("output_text") or "").strip()
        return json.loads(out_text) if out_text else {}

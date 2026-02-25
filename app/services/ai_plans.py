from __future__ import annotations
import json
import httpx
from app.core.config import settings

def _fallback(lang: str):
    return {
        "lang": lang,
        "time_weeks": 4,
        "expected_fit_increase_percent": 15,
        "plan": [
            "Week 1: Learn basics + notes",
            "Week 2: Practice tasks",
            "Week 3: Build mini project",
            "Week 4: Polish portfolio + interview prep",
        ],
        "resources": []
    }

def what_if(skills_to_improve: list[str], current_fit: int, target_role: str, lang: str) -> dict:
    if not settings.openai_api_key:
        return _fallback(lang)

    system = "You are a career coach. Output ONLY valid JSON. No markdown. No extra keys."
    user_payload = {
        "lang": lang,
        "task": "Estimate time and fit increase if user improves selected skills. Provide a short plan.",
        "current_fit_percent": current_fit,
        "target_role": target_role,
        "skills_to_improve": skills_to_improve
    }

    schema = {
        "type": "object",
        "properties": {
            "lang": {"type":"string"},
            "time_weeks": {"type":"integer","minimum":1,"maximum":52},
            "expected_fit_increase_percent": {"type":"integer","minimum":0,"maximum":80},
            "plan": {"type":"array","items":{"type":"string"}},
            "resources": {"type":"array","items":{"type":"string"}}
        },
        "required": ["lang","time_weeks","expected_fit_increase_percent","plan","resources"],
        "additionalProperties": False
    }

    body = {
        "model": settings.openai_model,
        "input": [
            {"role":"system","content": system},
            {"role":"user","content": json.dumps(user_payload, ensure_ascii=False)}
        ],
        "text": {"format": {"type":"json_schema","name":"what_if", "schema": schema, "strict": True}},
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
        return json.loads(out) if out else _fallback(lang)

def learning_plan(skills: list[str], target_role: str, lang: str) -> dict:
    if not settings.openai_api_key:
        return _fallback(lang)

    system = "You are a learning planner. Output ONLY valid JSON. No markdown. No extra keys."
    user_payload = {
        "lang": lang,
        "task": "Create a structured learning plan with time estimate and concrete actions.",
        "target_role": target_role,
        "skills": skills
    }

    schema = {
        "type":"object",
        "properties":{
            "lang":{"type":"string"},
            "time_weeks":{"type":"integer","minimum":1,"maximum":52},
            "plan":{"type":"array","items":{"type":"string"}},
            "projects":{"type":"array","items":{"type":"string"}},
            "resources":{"type":"array","items":{"type":"string"}}
        },
        "required":["lang","time_weeks","plan","projects","resources"],
        "additionalProperties": False
    }

    body = {
        "model": settings.openai_model,
        "input": [
            {"role":"system","content": system},
            {"role":"user","content": json.dumps(user_payload, ensure_ascii=False)}
        ],
        "text": {"format":{"type":"json_schema","name":"learning_plan","schema": schema, "strict": True}},
        "store": False
    }

    with httpx.Client(timeout=40.0) as client:
        r = client.post(
            "https://api.openai.com/v1/responses",
            headers={"Authorization": f"Bearer {settings.openai_api_key}", "Content-Type":"application/json"},
            json=body
        )
        r.raise_for_status()
        data = r.json()
        out = (data.get("output_text") or "").strip()
        return json.loads(out) if out else _fallback(lang)

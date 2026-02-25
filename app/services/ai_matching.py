from __future__ import annotations
import os, json
import httpx

def _norm(s: str) -> str:
    return s.strip().lower()

def _fallback_match(profile_skills: list[str], job_skills: list[str]) -> dict:
    ps = set(_norm(x) for x in profile_skills)
    js = set(_norm(x) for x in job_skills)
    if not js:
        return {"score": 50, "missing_skills": [], "explanation": "No required skills listed.", "roadmap": []}
    overlap = ps.intersection(js)
    missing = list(sorted(js - ps))
    score = int(round(100 * (len(overlap) / max(1, len(js)))))
    score = max(5, min(100, score))
    roadmap = [f"Learn {m} (course + mini project)" for m in missing[:5]] or ["Improve portfolio and soft skills."]
    return {"score": score, "missing_skills": missing, "explanation": f"Matched {len(overlap)} of {len(js)} required skills.", "roadmap": roadmap}

def match(profile_skills: list[str], job_skills: list[str], job_title: str | None = None) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5.1-chat-latest")
    if not api_key:
        return _fallback_match(profile_skills, job_skills)

    # жёстко просим JSON, без лишнего текста
    system = (
        "You are a career matching engine. Output ONLY valid JSON. "
        "No markdown, no comments, no extra keys."
    )
    user = {
        "job_title": job_title or "",
        "job_required_skills": job_skills,
        "candidate_skills": profile_skills,
        "task": "Return a match score, missing skills, short explanation, and a 5-step roadmap."
    }

    schema = {
        "type": "object",
        "properties": {
            "score": {"type": "integer", "minimum": 0, "maximum": 100},
            "missing_skills": {"type": "array", "items": {"type": "string"}},
            "explanation": {"type": "string"},
            "roadmap": {"type": "array", "items": {"type": "string"}}
        },
        "required": ["score", "missing_skills", "explanation", "roadmap"],
        "additionalProperties": False
    }

    payload = {
        "model": model,
        "input": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps(user, ensure_ascii=False)}
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "match_result",
                "schema": schema,
                "strict": True
            }
        },
        "store": False
    }

    try:
        with httpx.Client(timeout=20.0) as client:
            r = client.post(
                "https://api.openai.com/v1/responses",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            r.raise_for_status()
            data = r.json()
            out_text = (data.get("output_text") or "").strip()
            if not out_text:
                # иногда текст лежит внутри output items — fallback на простой парсинг
                return _fallback_match(profile_skills, job_skills)
            return json.loads(out_text)
    except Exception:
        return _fallback_match(profile_skills, job_skills)

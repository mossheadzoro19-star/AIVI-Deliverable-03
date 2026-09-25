import json
import random
import time

from google import genai
from google.genai import types
from models import MatchResult
from prompt import SYSTEM_PROMPT

def sanitize_json(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:] if lines and lines[0].strip().startswith("```") else lines
        lines = lines[:-1] if lines and lines[-1].strip() == "```" else lines
        text = "\n".join(lines).strip()
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("No JSON object found")
    return text[start:end + 1]

GEMINI_RESPONSE_SCHEMA = {
    "type": "OBJECT",
    "properties": {
        "status": {"type": "STRING", "enum": ["success", "invalid_input", "insufficient_evidence", "rate_limited", "timeout", "evaluation_unavailable"]},
        "match_score": {"type": "INTEGER"},
        "top_strengths": {"type": "ARRAY", "items": {"type": "STRING"}},
        "missing_skills": {"type": "ARRAY", "items": {"type": "STRING"}},
        "summary": {"type": "STRING"},
    },
    "required": ["status", "match_score", "top_strengths", "missing_skills", "summary"],
}

def evaluate(resume: str, jd: str, api_key: str, model: str = "gemini-2.5-flash") -> MatchResult:
    if len(resume.strip()) < 40:
        return MatchResult(status="insufficient_evidence", match_score=0, top_strengths=[], missing_skills=[], summary="The resume does not contain enough evidence.\nNo score was produced.")
    client = genai.Client(api_key=api_key)
    user_prompt = "RESUME START\n" + resume + "\nRESUME END\n\nJOB DESCRIPTION START\n" + jd + "\nJOB DESCRIPTION END"
    config = types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT, response_mime_type="application/json", response_json_schema=GEMINI_RESPONSE_SCHEMA, temperature=0.0)
    last_error = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(model=model, contents=user_prompt, config=config)
            data = json.loads(sanitize_json(response.text))
            return MatchResult.model_validate(data)
        except Exception as exc:
            last_error = exc
            msg = str(exc).lower()
            rate_limited = "429" in msg or ("rate" in msg and "limit" in msg)
            timed_out = "timeout" in msg or "timed out" in msg
            if attempt < 2 and (rate_limited or timed_out):
                time.sleep((2**attempt) + random.uniform(0, 0.5))
                continue
            if rate_limited:
                return MatchResult(status="rate_limited", match_score=0, top_strengths=[], missing_skills=[], summary="The API rate limit was reached.\nNo score was produced after bounded retries.")
            if timed_out:
                return MatchResult(status="timeout", match_score=0, top_strengths=[], missing_skills=[], summary="The model request timed out.\nNo score was produced after bounded retries.")
            if isinstance(exc, (json.JSONDecodeError, ValueError)):
                if attempt < 2:
                    time.sleep(0.25)
                    continue
                return MatchResult(status="evaluation_unavailable", match_score=0, top_strengths=[], missing_skills=[], summary="The model response failed validation.\nNo score was produced.")
            break
    raise RuntimeError(f"Evaluation failed: {last_error}")
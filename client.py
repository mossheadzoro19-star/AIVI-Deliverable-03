import json
import os
import random
import time

from google import genai
from google.genai import types
from models import MatchResult
from prompt import SYSTEM_PROMPT

DEFAULT_MODEL = "gemini-3.8-flash"
DEFAULT_FALLBACK_MODELS = ["gemini-3.7-flash", "gemini-3.5-flash"]
MAX_ATTEMPTS_PER_MODEL = 2

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

def evaluate(resume: str, jd: str, api_key: str, model: str = DEFAULT_MODEL) -> MatchResult:
    if len(resume.strip()) < 40:
        return MatchResult(
            status="insufficient_evidence",
            match_score=0,
            top_strengths=[],
            missing_skills=[],
            summary="The resume does not contain enough evidence.\nNo score was produced.",
        )

    client = genai.Client(api_key=api_key)
    user_prompt = (
        "RESUME START\n" + resume +
        "\nRESUME END\n\nJOB DESCRIPTION START\n" + jd +
        "\nJOB DESCRIPTION END"
    )
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        response_mime_type="application/json",
        response_json_schema=GEMINI_RESPONSE_SCHEMA,
        temperature=0.0,
    )

    configured_fallbacks = [
        item.strip()
        for item in os.getenv("GEMINI_FALLBACK_MODELS", "").split(",")
        if item.strip()
    ]
    candidates = []
    for candidate in [model, *configured_fallbacks, *DEFAULT_FALLBACK_MODELS]:
        normalized = candidate.strip()
        if normalized.startswith("models/"):
            normalized = normalized.removeprefix("models/")
        if normalized and normalized not in candidates:
            candidates.append(normalized)

    last_error = None
    attempted_models = []

    for candidate_model in candidates:
        attempted_models.append(candidate_model)
        for attempt in range(MAX_ATTEMPTS_PER_MODEL):
            try:
                response = client.models.generate_content(
                    model=candidate_model,
                    contents=user_prompt,
                    config=config,
                )
                data = json.loads(sanitize_json(response.text))
                return MatchResult.model_validate(data)

            except Exception as exc:
                last_error = exc
                msg = str(exc).lower()

                rate_limited = "429" in msg or ("rate" in msg and "limit" in msg)
                timed_out = "timeout" in msg or "timed out" in msg
                service_unavailable = (
                    "503" in msg
                    or "service unavailable" in msg
                    or "temporarily unavailable" in msg
                    or "high demand" in msg
                )

                if isinstance(exc, (json.JSONDecodeError, ValueError)):
                    if attempt < MAX_ATTEMPTS_PER_MODEL - 1:
                        time.sleep(0.25)
                        continue
                    return MatchResult(
                        status="evaluation_unavailable",
                        match_score=0,
                        top_strengths=[],
                        missing_skills=[],
                        summary="The model response failed validation.\nNo score was produced.",
                    )

                if rate_limited:
                    if attempt < MAX_ATTEMPTS_PER_MODEL - 1:
                        time.sleep((2 ** attempt) + random.uniform(0, 0.5))
                        continue
                    return MatchResult(
                        status="rate_limited",
                        match_score=0,
                        top_strengths=[],
                        missing_skills=[],
                        summary="The API rate limit was reached.\nNo score was produced after bounded retries.",
                    )

                if timed_out:
                    if attempt < MAX_ATTEMPTS_PER_MODEL - 1:
                        time.sleep((2 ** attempt) + random.uniform(0, 0.5))
                        continue
                    return MatchResult(
                        status="timeout",
                        match_score=0,
                        top_strengths=[],
                        missing_skills=[],
                        summary="The model request timed out.\nNo score was produced after bounded retries.",
                    )

                if service_unavailable:
                    if attempt < MAX_ATTEMPTS_PER_MODEL - 1:
                        time.sleep((2 ** attempt) + random.uniform(0, 0.5))
                        continue
                    break

                # A 404 means this particular model is unavailable to the API key.
                # Try the next configured model instead of treating it as a global failure.
                if "404" in msg or "not_found" in msg or "not found" in msg:
                    break

                break

    attempted = ", ".join(attempted_models)
    raise RuntimeError(
        f"Evaluation failed after trying models: {attempted}. Last provider error: {last_error}"
    )

# AIVI Deliverable 03 — Gemini Resume–JD Matcher

Standalone Gemini API pipeline required by the AIVI AI Engineering Challenge.

## Requirements implemented

- Raw resume text + job description input
- Gemini API integration
- Strict JSON output
- `match_score` constrained to 0–100
- `top_strengths`
- `missing_skills`
- exactly two-line summary
- JSON sanitization for fenced/model-wrapped output
- Pydantic validation
- bounded handling for HTTP 429 and timeouts
- prompt-injection-safe document handling
- deterministic invalid-input handling
- regression tests

## Run

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/macOS
```

Put your Gemini API key in `.env` as `GEMINI_API_KEY=...`.

```bash
python main.py --resume-file samples/resume.txt --jd-file samples/job_description.txt
```

The program writes one JSON object to stdout and exits non-zero on unrecoverable failures.

## Security notes

Resume and JD text are untrusted data. Embedded instructions are not treated as higher-priority instructions. Failed model/API calls never produce a guessed score.

## Challenge mapping

This implementation is Deliverable 03 of the AIVI AI Engineering Challenge and operationalizes the production controls defined in Deliverable 02.
# AIVI Deliverable 03 — Gemini Resume–JD Matcher

Standalone Gemini API implementation for the AIVI AI Engineering Challenge.

## What is included

- Resume text + Job Description input
- Gemini API integration
- Strict JSON validation with Pydantic
- JSON sanitization
- Prompt-injection protection
- 0–100 match score
- Top strengths
- Missing skills
- Exactly two-line summary
- Error handling for invalid input, rate limits, timeouts and malformed JSON
- Automated tests

## Easiest way to run on Windows

1. Clone/download this repository.
2. Open the repository folder.
3. Double-click **setup_windows.bat**.
4. When it asks for the Gemini API key, paste your key and press Enter.
5. The script creates a local `.env`, installs dependencies and runs the live Gemini demo.

**Important:** The API key is stored only in the local `.env` file. `.env` is listed in `.gitignore`, so it must not be committed to GitHub.

## Manual run

Create a local file named `.env`:

```env
GEMINI_API_KEY=YOUR_ACTUAL_GEMINI_API_KEY
GEMINI_MODEL=gemini-2.5-flash
```

Then run:

```bash
python -m pip install -r requirements.txt
python main.py --resume-file samples/resume.txt --jd-file samples/job_description.txt
```

## Expected output

The program prints one JSON object containing:

```json
{
  "status": "success",
  "match_score": 0,
  "top_strengths": [],
  "missing_skills": [],
  "summary": "Two-line evidence-based summary."
}
```

The actual score and lists are generated from the supplied resume and job description.

## Security

Resume and Job Description text are treated as untrusted data. Instructions embedded inside them cannot override the system prompt. Failed API/model calls never produce a guessed score.

Never commit an API key, token or `.env` file.

## Challenge mapping

This repository implements Deliverable 03 and applies the production controls designed in Deliverable 02.

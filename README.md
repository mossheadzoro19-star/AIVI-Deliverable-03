# AIVI Deliverable 03 — Gemini Resume–JD Matcher

Standalone Gemini API implementation for the AIVI AI Engineering Challenge.

## What is included

- Resume text + Job Description input
- Gemini API integration
- Gemini-compatible structured JSON response schema
- Strict application-level JSON validation with Pydantic
- JSON sanitization
- Prompt-injection protection
- 0–100 match score
- Top strengths
- Missing skills
- Exactly two-line summary
- Bounded handling for invalid input, rate limits, timeouts and malformed JSON
- Automated tests
- GitHub Codespaces development environment

## Run in GitHub Codespaces

This repository includes a `.devcontainer/devcontainer.json` configuration for Python 3.12.

After opening the repository in Codespaces:

    pip install -r requirements.txt

Create a local `.env` file inside the Codespace:

    GEMINI_API_KEY=YOUR_ACTUAL_GEMINI_API_KEY
    GEMINI_MODEL=gemini-2.5-flash

The `.env` file is ignored by Git and must never be committed.

Verify the key is loaded without printing the secret:

    python -c "from dotenv import load_dotenv; import os; load_dotenv('.env'); k=os.getenv('GEMINI_API_KEY'); print('API key loaded:', bool(k))"

Run the live demo:

    python main.py --resume-file samples/resume.txt --jd-file samples/job_description.txt

## Direct Gemini API connectivity test

If the application reports an authentication problem, test the API directly with the `x-goog-api-key` header. A successful HTTP 200 response confirms API connectivity independently of the application code.

## Windows alternative

For local Windows execution, `setup_windows.bat` can create the local `.env`, install dependencies and run the demo.

## Expected output

The program prints one JSON object containing `status`, `match_score`, `top_strengths`, `missing_skills`, and a two-line `summary`. The actual score and lists are generated from the supplied resume and job description.

## Security

Resume and Job Description text are treated as untrusted data. Instructions embedded inside them cannot override the system prompt.
The Gemini generation schema is intentionally kept separate from the Pydantic application schema because Gemini's response-schema interface does not accept every JSON Schema keyword emitted by Pydantic.
Failed API/model calls never produce a guessed score.
Never commit an API key, token or `.env` file.

## Challenge mapping

This repository implements Deliverable 03 and applies the production controls designed in Deliverable 02:
- evidence-first resume/JD matching
- prompt-injection resistance
- strict structured output
- safe failure states
- bounded retries
- post-generation Pydantic validation


## Streamlit UI

Run `streamlit run app.py` to launch the browser demo. It supports pasted resume/JD text and `.txt`, `.md`, or text-based `.pdf` uploads. Scanned/image-only PDFs are rejected with a clear OCR-required message rather than being treated as usable resume evidence.

## Deploy as a persistent web app

The recommended public deployment is Streamlit Community Cloud. It deploys the GitHub repository directly and provides a `streamlit.app` URL. The app can sleep after 12 hours without traffic and wakes when visited; this is platform hibernation, not a requirement to restart the app manually. 

1. Open the Streamlit Community Cloud workspace at https://share.streamlit.io/ and sign in with GitHub.
2. Create an app and select repository `mossheadzoro19-star/AIVI-Deliverable-03`, branch `main`, and entrypoint `app.py`.
3. In the deployment Advanced settings / app Secrets, add:

       GEMINI_API_KEY = "YOUR_API_KEY"
       GEMINI_MODEL = "gemini-3.8-flash"
       GEMINI_FALLBACK_MODELS = "gemini-3.7-flash,gemini-3.5-flash"

4. Never commit the API key or a `.streamlit/secrets.toml` file. Secrets are read securely from Streamlit Cloud and fall back to local environment variables for Codespaces.
5. Keep the deployment Python version aligned with the repository Codespace version (Python 3.12).

After deployment, GitHub commits automatically trigger app updates. If dependency changes are made, Community Cloud rebuilds the environment from `requirements.txt`.

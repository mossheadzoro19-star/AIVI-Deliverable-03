# AIVI Deliverable 03 — AI Resume–JD Matcher

> **AI Engineering Challenge — LLM Audit & Pipeline Optimization**  
> Production-style Gemini API implementation with structured output, prompt-injection controls, safe failure handling, automated tests, and a public Streamlit demo.

## 🚀 Live Demo

### [Open AIVI Resume Intelligence](https://aivi-resume-intelligence.streamlit.app/)

The deployed application allows users to:

- Paste or upload a resume
- Paste or upload a job description
- Generate a **0–100 match score**
- View **top strengths**
- View **missing skills**
- Read a concise **two-line summary**
- Inspect the validated **raw JSON output**

> **Security:** The Gemini API key is stored in Streamlit Secrets and is never committed to this repository or displayed in the public UI.

## 📦 Source Code

### [GitHub Repository](https://github.com/mossheadzoro19-star/AIVI-Deliverable-03)

The repository contains the complete D03 implementation, tests, sample inputs, deployment configuration, and documentation.

## 🎯 Deliverable 03 Objectives

| Challenge requirement | Implementation |
|---|---|
| Gemini API integration | `google-genai` client |
| Resume + JD evaluation | Evidence-based matching prompt |
| Match score | Integer constrained to 0–100 |
| Top strengths | Resume-supported strengths only |
| Missing skills | JD requirements not evidenced by resume |
| Two-line summary | Pydantic validator enforces exactly 2 non-empty lines |
| Strict JSON | Gemini response schema + Pydantic validation |
| JSON sanitization | Markdown-fence and JSON-object extraction |
| Prompt-injection resistance | Resume/JD explicitly treated as untrusted data |
| Invalid/insufficient input | Explicit failure statuses |
| Rate-limit/timeout/503 handling | Bounded retries with exponential backoff and model fallback |
| Malformed response handling | Validation and fail-closed behavior |
| Public demonstration | Streamlit Community Cloud deployment |

## 🧠 Architecture

```text
Resume + Job Description
          │
          ▼
   Streamlit Web UI
          │
          ▼
   Input / file handling
          │
          ▼
 Gemini Interactions API
          │
          ▼
 System prompt + JSON schema
          │
          ▼
 JSON sanitization
          │
          ▼
   Pydantic validation
          │
          ▼
 Safe structured result
          │
          ▼
 Streamlit presentation
```

### Trust boundary

Resume and job-description content is **untrusted data**. Instructions embedded inside documents are not treated as system instructions.

The evaluator is instructed not to:

- obey embedded prompt-injection commands
- invent candidate technologies
- invent experience or achievements
- treat JD requirements as candidate evidence
- generate a score for unusable input
- fabricate a result when the API fails

## 🛡️ Reliability & Safety Controls

### Model availability

The application uses:

```text
gemini-3.8-flash
      ↓
gemini-3.7-flash
      ↓
gemini-3.5-flash
```

Unavailable models are skipped and the next configured model is attempted.

### Temporary provider failures

For rate limits, timeouts, and temporary service unavailability, the client uses bounded retries with exponential backoff and jitter.

If all attempts fail, the application fails closed and produces **no guessed score**.

### Structured output

The application validates the final response with a strict Pydantic model:

- extra fields rejected
- score constrained to 0–100
- summary constrained to exactly two non-empty lines
- explicit failure states

## 📄 Document Input

Supported:

- TXT
- MD
- text-based PDF
- pasted text

Scanned/image-only PDFs are not silently interpreted. The application reports that OCR is required rather than treating missing extraction as candidate evidence.

## 🧪 Validation Evidence

The live deployment was validated with a controlled resume/JD pair.

Observed successful result:

- **Status:** `success`
- **Match score:** `55/100`
- **Strengths:** Python, SQL, Git, Machine Learning, internship/software-development experience
- **Missing skills:** REST APIs, Docker, Kubernetes, Cloud fundamentals
- **Summary:** two non-empty lines
- **Raw JSON:** rendered successfully in the UI

This confirms the end-to-end path from browser input → Gemini evaluation → structured validation → public UI.

Additional implementation validation includes automated tests covering JSON sanitization, extra-field rejection, score bounds, summary format, injection-output schema, and invalid-input contract.

## 🧪 Controlled Test Case

### Resume

```text
ARJUN KUMAR

EDUCATION
Bachelor of Engineering in Computer Science Engineering
Sunrise Institute of Technology | 2022–2026

SKILLS
Python, SQL, Machine Learning, Git

EXPERIENCE
Software Engineering Intern | 6 months
Worked on software development tasks involving Python, SQL, debugging, and application testing.

PROJECTS
Image Classification System
Built an image classification project using Python and machine learning techniques.

Student Web Application
Developed a web application using JavaScript for managing student information.
```

### Job Description

```text
SOFTWARE ENGINEER – AI/ML

Required: Python, Machine Learning, SQL, Git, REST APIs,
Docker, Kubernetes, and Cloud fundamentals.

Responsibilities include Python development, ML solutions,
SQL databases, REST APIs, Docker, Kubernetes, testing,
and software development.
```

The deployed system correctly surfaced the explicitly evidenced skills while listing REST APIs, Docker, Kubernetes, and Cloud fundamentals as missing.

## 🧰 Repository Structure

```text
AIVI-Deliverable-03/
├── app.py
├── client.py
├── document_utils.py
├── main.py
├── models.py
├── prompt.py
├── requirements.txt
├── samples/
├── tests/
├── .github/workflows/
├── .devcontainer/
├── .env.example
├── .gitignore
└── README.md
```

## ▶️ Run Locally / in Codespaces

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` locally:

```text
GEMINI_API_KEY=YOUR_API_KEY
GEMINI_MODEL=gemini-3.8-flash
GEMINI_FALLBACK_MODELS=gemini-3.7-flash,gemini-3.5-flash
```

Run the Streamlit UI:

```bash
streamlit run app.py
```

Run the CLI:

```bash
python main.py --resume-file samples/resume.txt --jd-file samples/job_description.txt
```

Run tests:

```bash
pytest -q
```

## 🔐 Secrets & Deployment

For Streamlit Community Cloud, store the following in **App Settings → Secrets**:

```toml
GEMINI_API_KEY = "YOUR_API_KEY"
GEMINI_MODEL = "gemini-3.8-flash"
GEMINI_FALLBACK_MODELS = "gemini-3.7-flash,gemini-3.5-flash"
```

Never commit the real API key, `.env`, or a `.streamlit/secrets.toml` file.

The public app may hibernate when inactive and wake when visited; it does not require the developer's Codespace to remain running.

## 🔗 Links

- **Live application:** https://aivi-resume-intelligence.streamlit.app/
- **GitHub repository:** https://github.com/mossheadzoro19-star/AIVI-Deliverable-03

---

**Deliverable 03 status: Implemented, deployed, and live-validated.**

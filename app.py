import json
import os

import streamlit as st
from dotenv import load_dotenv

from client import DEFAULT_MODEL, evaluate
from document_utils import extract_document_text

load_dotenv()

st.set_page_config(
    page_title="AIVI Resume Intelligence",
    page_icon="🤖",
    layout="wide",
)

st.title("AIVI Resume Intelligence")
st.caption("Gemini-powered resume ↔ job description matching with structured output and safe failure handling.")

with st.sidebar:
    st.subheader("Configuration")
    configured_model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)
    st.write(f"Model: `{configured_model}`")
    st.write("API key: " + ("configured" if os.getenv("GEMINI_API_KEY") else "not configured"))
    st.info("Resume and job-description content are treated as untrusted data by the evaluation prompt.")

left, right = st.columns(2)

with left:
    st.subheader("Resume")
    resume_file = st.file_uploader(
        "Upload resume",
        type=["txt", "md", "pdf"],
        help="PDF extraction supports text-based PDFs. Scanned/image-only PDFs require OCR.",
    )
    resume_text = st.text_area(
        "Or paste resume text",
        height=300,
        placeholder="Paste the candidate resume here...",
    )

with right:
    st.subheader("Job Description")
    jd_file = st.file_uploader(
        "Upload job description",
        type=["txt", "md", "pdf"],
        key="jd_file",
        help="Upload a text or text-based PDF job description.",
    )
    jd_text = st.text_area(
        "Or paste job description",
        height=300,
        placeholder="Paste the job description here...",
    )

def resolve_input(uploaded_file, pasted_text: str, label: str) -> str:
    if uploaded_file is not None:
        return extract_document_text(uploaded_file.name, uploaded_file.getvalue())
    if pasted_text.strip():
        return pasted_text.strip()
    raise ValueError(f"Please provide a {label}.")

st.divider()

if st.button("Analyze Resume", type="primary", use_container_width=True):
    try:
        load_dotenv(override=True)
        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("GEMINI_MODEL", DEFAULT_MODEL)

        if not api_key:
            st.error("GEMINI_API_KEY is not configured. Add it to .env locally or Streamlit secrets when deployed.")
            st.stop()

        with st.spinner("Evaluating resume against the job description..."):
            resume = resolve_input(resume_file, resume_text, "resume")
            jd = resolve_input(jd_file, jd_text, "job description")
            result = evaluate(resume, jd, api_key, model)

        if result.status == "success":
            st.success("Evaluation completed successfully.")

            score_col, status_col = st.columns(2)
            score_col.metric("Match Score", f"{result.match_score}/100")
            status_col.metric("Status", result.status)

            strengths_col, missing_col = st.columns(2)

            with strengths_col:
                st.subheader("Top Strengths")
                if result.top_strengths:
                    for item in result.top_strengths:
                        st.markdown(f"- {item}")
                else:
                    st.write("No strengths returned.")

            with missing_col:
                st.subheader("Missing Skills")
                if result.missing_skills:
                    for item in result.missing_skills:
                        st.markdown(f"- {item}")
                else:
                    st.write("No missing skills returned.")

            st.subheader("Summary")
            for line in result.summary.splitlines():
                st.write(line)

            with st.expander("Raw JSON"):
                st.code(
                    json.dumps(result.model_dump(), indent=2, ensure_ascii=False),
                    language="json",
                )
        else:
            st.warning(result.summary)
            with st.expander("Structured failure result"):
                st.code(
                    json.dumps(result.model_dump(), indent=2, ensure_ascii=False),
                    language="json",
                )

    except ValueError as exc:
        st.error(str(exc))
    except Exception:
        st.error("The evaluation could not be completed. Check the terminal logs for the technical error.")

import argparse
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from client import evaluate


def read_text(path: str) -> str:
    value = Path(path).read_text(encoding="utf-8").strip()
    if not value:
        raise ValueError(f"Input file is empty: {path}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="AIVI Gemini Resume-JD Matcher")
    parser.add_argument("--resume-file", required=True)
    parser.add_argument("--jd-file", required=True)
    args = parser.parse_args()

    try:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set")

        result = evaluate(read_text(args.resume_file), read_text(args.jd_file), api_key, model)
        print(json.dumps(result.model_dump(), indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(json.dumps({
            "status": "evaluation_unavailable",
            "match_score": 0,
            "top_strengths": [],
            "missing_skills": [],
            "summary": f"Evaluation failed safely.\n{type(exc).__name__}: {exc}",
        }, indent=2, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())

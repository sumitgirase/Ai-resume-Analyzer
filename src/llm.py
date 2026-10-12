import os
import re
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from src.models import Analysis

load_dotenv()

DEFAULT_MODEL = "google/gemini-2.5-flash"
MAX_CHARS = 12000  # truncate very long inputs

SYSTEM_PROMPT = """You are an expert technical recruiter. Compare a candidate's \
resume against a job description.

Return ONLY valid JSON, with no markdown and no extra text, in exactly this shape:
{
  "match_score": <integer 0-100>,
  "summary": "<2-3 sentence overall verdict>",
  "matching_skills": ["<skill found in both>"],
  "missing_skills": ["<skill the job wants but the resume lacks>"],
  "strengths": ["<specific strength relevant to this job>"],
  "suggestions": ["<concrete, actionable resume improvement>"]
}

Scoring guide:
- 90-100: near-perfect match
- 70-89: strong match with minor gaps
- 50-69: partial match, notable gaps
- below 50: weak match

For matching_skills and missing_skills, list only concrete technical skills, tools, and technologies (e.g. Python, SQL, Docker), not soft skills.

Base everything only on the text provided. Do not invent experience."""


def get_client() -> OpenAI:
    key = os.getenv("OPENROUTER_API_KEY")
    if not key:
        try:  # fallback for Streamlit Cloud secrets
            import streamlit as st
            key = st.secrets["OPENROUTER_API_KEY"]
        except Exception:
            pass
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY not found. Check your .env file.")
    return OpenAI(base_url="https://openrouter.ai/api/v1", api_key=key)


def _extract_json(text: str) -> str:
    """Strip markdown fences and keep only the outermost JSON object."""
    text = re.sub(r"```(?:json)?", "", text).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model reply.")
    return text[start : end + 1]


def analyze(resume_text: str, job_description: str,
            model: str = DEFAULT_MODEL, retries: int = 2) -> Analysis:
    client = get_client()
    user_message = (
        f"### RESUME ###\n{resume_text[:MAX_CHARS]}\n\n"
        f"### JOB DESCRIPTION ###\n{job_description[:MAX_CHARS]}"
    )

    last_error = None
    for _ in range(retries):
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
            max_tokens=1500,
        )
        reply = response.choices[0].message.content or ""
        try:
            return Analysis.model_validate_json(_extract_json(reply))
        except (ValueError, ValidationError) as e:
            last_error = e  # try again

    raise ValueError(f"Model returned invalid output after {retries} tries: {last_error}")


if __name__ == "__main__":
    from src.parser import extract_text

    with open("test_resume.pdf", "rb") as f:
        resume = extract_text(f)

    jd = """We are hiring a Python developer with experience in SQL, REST APIs,
    Docker, and cloud deployment. Knowledge of machine learning is a plus."""

    result = analyze(resume, jd)
    print(result.model_dump_json(indent=2))
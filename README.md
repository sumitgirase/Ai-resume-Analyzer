# ResumeIQ: AI Resume Analyzer & Job Matcher 📄

🔗 **Live Demo:** [Try it here](https://ai-resume-analyzer-qj6xn6upbd5aq39u7rfrst.streamlit.app/)
*(The free host sleeps when idle, so the first load may take a few seconds.)*

Upload your resume and paste a job description to get a match score, matching and missing skills, and specific suggestions for improving your resume.

![Results](screenshots/results.png)

## Features

- 📑 PDF resume parsing with clear errors for scanned or empty files
- 🤖 LLM analysis through OpenRouter, with a selectable model
- 📊 Hybrid score that combines AI judgment with a repeatable keyword and similarity score
- ✅ Matching and missing skills, strengths, and actionable suggestions
- ⬇️ Downloadable report
- 🔒 Resumes are processed in memory and never stored

## How scoring works

| Score | How it is calculated |
|---|---|
| **AI score** | The LLM compares the resume and job description and returns a 0-100 score as structured JSON |
| **Keyword score** | Percentage of skills requested in the job description (from a curated skill list) that appear in the resume |
| **Similarity score** | TF-IDF cosine similarity between the resume and job description, scaled to 0-100 |
| **Deterministic score** | 70% keyword score + 30% similarity score |
| **Final score** | 60% AI score + 40% deterministic score |

LLM scores can vary between runs, so blending in a deterministic score makes the result steadier and easier to explain.

## Architecture

```
app.py            Streamlit UI
src/
├── parser.py     PDF → clean text (pypdf)
├── models.py     Pydantic schema for the AI response
├── llm.py        OpenRouter call, prompt, JSON validation + retry
└── scoring.py    TF-IDF similarity, keyword overlap, blended score
```

## Tech stack

Python · Streamlit · OpenRouter (OpenAI-compatible API) · Pydantic · scikit-learn · pypdf

## Challenges solved

- **Unreliable LLM output:** forced a strict JSON schema, validated it with Pydantic, and added JSON cleanup and retries.
- **Inconsistent scores:** added a deterministic TF-IDF and keyword score and blended it with the AI score.
- **API credit errors:** capped `max_tokens` so requests stay within the account balance.
- **Messy PDFs:** cleaned extracted text and return a clear message for image-only PDFs.

## Run locally

```bash
git clone https://github.com/sumitgirase/Ai-resume-Analyzer.git
cd Ai-resume-Analyzer
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file with your key from [OpenRouter](https://openrouter.ai/keys):

```
OPENROUTER_API_KEY=your_key_here
```

Then run:

```bash
streamlit run app.py
```

## Roadmap

- DOCX resume support
- Compare one resume against several jobs
- Rewrite bullet points to match a job description

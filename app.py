import streamlit as st

from src.parser import extract_text
from src.llm import analyze
from src.scoring import blended_score, deterministic_score, keyword_overlap

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="wide")

MODELS = [
    "google/gemini-2.5-flash",
    "openai/gpt-4o-mini",
    "anthropic/claude-3.5-haiku",
]

with st.sidebar:
    st.header("Settings")
    model = st.selectbox("Model", MODELS)
    st.caption(
        "🔒 Your resume is processed in memory and is not stored by this app. "
        "Text is sent to the selected model through OpenRouter for analysis."
    )

st.title("📄 AI Resume Analyzer & Job Matcher")
st.write("Upload your resume and paste a job description to see how well they match.")

col1, col2 = st.columns(2)
with col1:
    uploaded = st.file_uploader("Upload resume (PDF)", type="pdf")
with col2:
    job_description = st.text_area("Paste the job description", height=220)

if st.button("Analyze", type="primary"):
    if not uploaded:
        st.error("Please upload a PDF resume.")
    elif len(job_description.strip()) < 50:
        st.error("The job description is too short. Please paste the full text.")
    else:
        try:
            with st.spinner("Reading your resume..."):
                resume_text = extract_text(uploaded)
            with st.spinner("Analyzing with AI..."):
                result = analyze(resume_text, job_description, model=model)
        except ValueError as e:
            st.error(str(e))
        except Exception as e:
            st.error(f"Something went wrong: {e}")
        else:
            final = blended_score(result.match_score, resume_text, job_description)
            det = deterministic_score(resume_text, job_description)

            st.subheader("Results")
            m1, m2, m3 = st.columns(3)
            m1.metric("Final match score", f"{final}/100")
            m2.metric("AI score", f"{result.match_score}/100")
            m3.metric("Keyword + similarity score", f"{det}/100")
            st.progress(final / 100)
            st.write(result.summary)

            left, right = st.columns(2)
            with left:
                st.markdown("#### ✅ Matching skills")
                for s in result.matching_skills:
                    st.success(s)
            with right:
                st.markdown("#### ❌ Missing skills")
                for s in result.missing_skills:
                    st.error(s)

            with st.expander("Strengths", expanded=True):
                for s in result.strengths:
                    st.write(f"- {s}")
            with st.expander("Suggestions to improve your resume", expanded=True):
                for s in result.suggestions:
                    st.write(f"- {s}")

            report = (
                f"# Resume Analysis\n\nFinal score: {final}/100\n\n"
                f"{result.summary}\n\n"
                f"## Matching skills\n" + "\n".join(f"- {s}" for s in result.matching_skills) +
                "\n\n## Missing skills\n" + "\n".join(f"- {s}" for s in result.missing_skills) +
                "\n\n## Suggestions\n" + "\n".join(f"- {s}" for s in result.suggestions)
            )
            st.download_button("Download report", report, file_name="analysis.md")
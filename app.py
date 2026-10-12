import html
import streamlit as st

from src.parser import extract_text
from src.llm import analyze
from src.scoring import blended_score, deterministic_score

st.set_page_config(page_title="ResumeIQ", page_icon="📄", layout="wide")

MODELS = [
    "google/gemini-2.5-flash",
    "openai/gpt-4o-mini",
    "anthropic/claude-3.5-haiku",
]

CSS = """
<style>
#MainMenu, footer {visibility: hidden;}
header {background: transparent;}
.block-container {padding-top: 2rem; max-width: 1100px;}

.hero {text-align: center; padding: 2.8rem 1rem 2.4rem; border-radius: 22px;
  background: linear-gradient(135deg, #6C5CE7 0%, #00B8D9 100%); margin-bottom: 1.5rem;}
.hero h1 {color: #fff; font-size: 2.8rem; font-weight: 800; margin: 0 0 .5rem;}
.hero p {color: rgba(255,255,255,.92); font-size: 1.1rem; margin: 0;}

.steps {display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap;}
.step {flex: 1; min-width: 200px; background: #1A1D29; border: 1px solid #2A2E3F;
  border-radius: 16px; padding: 1rem 1.2rem;}
.step b {color: #8E82F5;}
.step span {display: block; color: #9AA0B4; font-size: .9rem; margin-top: .25rem;}

.card {background: #1A1D29; border: 1px solid #2A2E3F; border-radius: 16px;
  padding: 1.25rem 1.5rem; margin-bottom: 1rem;}
.card h4 {margin: 0 0 .8rem; font-size: 1.05rem;}
.card ul {margin: 0; padding-left: 1.2rem;}
.card li {margin-bottom: .45rem; color: #D5D8E3;}

.chip {display: inline-block; padding: .3rem .85rem; margin: .2rem .3rem .2rem 0;
  border-radius: 999px; font-size: .85rem; font-weight: 500;}
.chip.good {background: rgba(46,204,113,.15); color: #2ECC71; border: 1px solid rgba(46,204,113,.4);}
.chip.bad {background: rgba(255,107,107,.15); color: #FF6B6B; border: 1px solid rgba(255,107,107,.4);}

.ring {width: 160px; height: 160px; border-radius: 50%; margin: 0 auto;
  display: grid; place-items: center;
  background: conic-gradient(var(--c) calc(var(--p) * 1%), #2A2E3F 0);}
.ring-in {width: 128px; height: 128px; border-radius: 50%; background: #1A1D29;
  display: flex; flex-direction: column; align-items: center; justify-content: center;}
.ring-in span {font-size: 2.4rem; font-weight: 800; line-height: 1;}
.ring-in small {color: #9AA0B4;}
.ring-label {text-align: center; margin-top: .8rem; color: #9AA0B4; font-size: .9rem;}

.mini {display: flex; gap: 1rem; margin-top: 1rem;}
.mini div {flex: 1; background: #12141D; border-radius: 12px; padding: .7rem 1rem;}
.mini b {font-size: 1.4rem; display: block;}
.mini small {color: #9AA0B4;}

.stButton > button {width: 100%; border: 0; border-radius: 12px; padding: .7rem 2rem;
  font-weight: 700; font-size: 1.05rem; color: #fff;
  background: linear-gradient(135deg, #6C5CE7, #00B8D9);}
.stButton > button:hover {filter: brightness(1.12); color: #fff;}
.stDownloadButton > button {border-radius: 12px; font-weight: 600;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def chips(items, kind):
    if not items:
        return "<span style='color:#9AA0B4'>None found</span>"
    return "".join(f"<span class='chip {kind}'>{html.escape(s)}</span>" for s in items)


def bullets(items):
    if not items:
        return "<span style='color:#9AA0B4'>Nothing to show</span>"
    return "<ul>" + "".join(f"<li>{html.escape(s)}</li>" for s in items) + "</ul>"


def score_color(score):
    if score >= 70:
        return "#2ECC71"
    if score >= 50:
        return "#F5A623"
    return "#FF6B6B"


with st.sidebar:
    st.header("⚙️ Settings")
    model = st.selectbox("AI model", MODELS)
    st.caption(
        "🔒 Your resume is processed in memory and is not stored by this app. "
        "The text is sent to the selected model through OpenRouter for analysis."
    )

st.markdown(
    "<div class='hero'><h1>📄 ResumeIQ</h1>"
    "<p>See how well your resume fits a job, with AI insights you can act on.</p></div>",
    unsafe_allow_html=True,
)

st.markdown(
    "<div class='steps'>"
    "<div class='step'><b>1. Upload</b><span>Add your resume as a PDF</span></div>"
    "<div class='step'><b>2. Paste</b><span>Drop in the job description</span></div>"
    "<div class='step'><b>3. Improve</b><span>Get a score, gaps and tips</span></div>"
    "</div>",
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2, gap="large")
with col1:
    uploaded = st.file_uploader("Upload resume (PDF)", type="pdf")
with col2:
    job_description = st.text_area("Paste the job description", height=180)

if st.button("🚀 Analyze my resume"):
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

            st.markdown("## Results")
            left, right = st.columns([1, 2], gap="large")
            with left:
                st.markdown(
                    f"<div class='card'><div class='ring' style='--p:{final};--c:{score_color(final)}'>"
                    f"<div class='ring-in'><span>{final}</span><small>/ 100</small></div></div>"
                    f"<div class='ring-label'>Final match score</div></div>",
                    unsafe_allow_html=True,
                )
            with right:
                st.markdown(
                    f"<div class='card'><h4>Overall verdict</h4>"
                    f"<div style='color:#D5D8E3'>{html.escape(result.summary)}</div>"
                    f"<div class='mini'>"
                    f"<div><b>{result.match_score}</b><small>AI score</small></div>"
                    f"<div><b>{det}</b><small>Keyword + similarity score</small></div>"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )

            c1, c2 = st.columns(2, gap="large")
            with c1:
                st.markdown(
                    f"<div class='card'><h4>✅ Matching skills</h4>{chips(result.matching_skills, 'good')}</div>",
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(
                    f"<div class='card'><h4>❌ Missing skills</h4>{chips(result.missing_skills, 'bad')}</div>",
                    unsafe_allow_html=True,
                )

            c3, c4 = st.columns(2, gap="large")
            with c3:
                st.markdown(
                    f"<div class='card'><h4>💪 Strengths</h4>{bullets(result.strengths)}</div>",
                    unsafe_allow_html=True,
                )
            with c4:
                st.markdown(
                    f"<div class='card'><h4>🛠️ Suggestions</h4>{bullets(result.suggestions)}</div>",
                    unsafe_allow_html=True,
                )

            report = (
                f"# Resume Analysis\n\nFinal score: {final}/100\n\n"
                f"{result.summary}\n\n"
                "## Matching skills\n" + "\n".join(f"- {s}" for s in result.matching_skills) +
                "\n\n## Missing skills\n" + "\n".join(f"- {s}" for s in result.missing_skills) +
                "\n\n## Suggestions\n" + "\n".join(f"- {s}" for s in result.suggestions)
            )
            st.download_button("⬇️ Download report", report, file_name="analysis.md")
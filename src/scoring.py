import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Starter skill list. Add more over time.
SKILLS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "sql", "mysql", "postgresql", "mongodb", "redis",
    "html", "css", "react", "node.js", "django", "flask", "fastapi", "streamlit",
    "rest api", "rest apis", "graphql", "docker", "kubernetes", "git", "linux",
    "aws", "azure", "gcp", "ci/cd", "jenkins",
    "machine learning", "deep learning", "nlp", "pandas", "numpy",
    "scikit-learn", "tensorflow", "pytorch", "llm", "langchain",
    "data structures", "algorithms", "agile", "scrum",
]


def _contains(text: str, skill: str) -> bool:
    """Whole-word match that also handles names like c++, c#, node.js."""
    pattern = r"(?<![a-z0-9+#])" + re.escape(skill) + r"(?![a-z0-9+#])"
    return re.search(pattern, text.lower()) is not None


def keyword_overlap(resume: str, job_description: str):
    """Return (score 0-100 or None, matched skills, missing skills)."""
    required = [s for s in SKILLS if _contains(job_description, s)]
    if not required:
        return None, [], []
    matched = [s for s in required if _contains(resume, s)]
    missing = [s for s in required if s not in matched]
    return round(100 * len(matched) / len(required)), matched, missing


def tfidf_similarity(resume: str, job_description: str) -> int:
    """Cosine similarity of TF-IDF vectors, scaled to 0-100."""
    vec = TfidfVectorizer(stop_words="english")
    matrix = vec.fit_transform([resume, job_description])
    cos = cosine_similarity(matrix[0], matrix[1])[0][0]
    # Raw values for resume vs JD are usually 0.1-0.4, so stretch them.
    return min(100, round(cos * 250))


def deterministic_score(resume: str, job_description: str) -> int:
    kw_score, _, _ = keyword_overlap(resume, job_description)
    tf_score = tfidf_similarity(resume, job_description)
    if kw_score is None:  # job description had no known skills
        return tf_score
    return round(0.7 * kw_score + 0.3 * tf_score)


def blended_score(llm_score: int, resume: str, job_description: str) -> int:
    """60% LLM judgment + 40% deterministic score."""
    return round(0.6 * llm_score + 0.4 * deterministic_score(resume, job_description))


if __name__ == "__main__":
    resume = "Python developer with SQL, Flask and Git experience. Built ML projects."
    jd = "Looking for a Python developer with SQL, Docker, REST APIs and Git."

    print("Keyword overlap:", keyword_overlap(resume, jd))
    print("TF-IDF score:", tfidf_similarity(resume, jd))
    print("Deterministic score:", deterministic_score(resume, jd))
    print("Blended (LLM=55):", blended_score(55, resume, jd))
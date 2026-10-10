import re
from pypdf import PdfReader


def extract_text(file) -> str:
    """Extract and clean text from an uploaded PDF file."""
    try:
        reader = PdfReader(file)
    except Exception as e:
        raise ValueError(f"Could not read the PDF: {e}")

    pages_text = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)

    full_text = "\n".join(pages_text)

    # Clean up: collapse repeated spaces/tabs and remove extra blank lines
    full_text = re.sub(r"[ \t]+", " ", full_text)
    full_text = re.sub(r"\n\s*\n+", "\n", full_text)
    full_text = full_text.strip()

    if not full_text:
        raise ValueError(
            "No text found. Please upload a text-based PDF, not a scanned image."
        )

    return full_text


if __name__ == "__main__":
    # Quick manual test: put a PDF in the project folder and change the name
    with open("TCS_resume.pdf", "rb") as f:
        print(extract_text(f)[:500])

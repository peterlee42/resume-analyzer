"""
Tool: extract_text_from_pdf
Uses pdfplumber for accurate text extraction with layout preservation.
"""

import pdfplumber


def extract_text_from_pdf(file_path: str) -> dict:
    """Extract raw text from a PDF, page by page."""
    pages = []
    full_text = ""

    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            pages.append({"page": i + 1, "text": text})
            full_text += text + "\n"

    return {
        "file": file_path,
        "total_pages": len(pages),
        "full_text": full_text.strip(),
        "pages": pages
    }

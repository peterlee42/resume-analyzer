"""Unit tests for resume analyzer tools."""

import asyncio
import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from tools.extract import extract_text_from_pdf


class _FakePdf:
    def __init__(self, pages):
        self.pages = pages

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _FakePage:
    def __init__(self, text):
        self._text = text

    def extract_text(self):
        return self._text


def test_extract_returns_text_and_pages():
    fake_pdf = _FakePdf([_FakePage("Hello"), _FakePage("World")])

    with patch("tools.extract.pdfplumber.open", return_value=fake_pdf):
        result = extract_text_from_pdf("resume.pdf")

    assert result["file"] == "resume.pdf"
    assert result["total_pages"] == 2
    assert result["full_text"] == "Hello\nWorld"
    assert result["pages"] == [
        {"page": 1, "text": "Hello"},
        {"page": 2, "text": "World"},
    ]


def test_extract_missing_file_raises_error():
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf("nonexistent.pdf")


def test_analyze_resume_structure():
    from tools.analyze import analyze_resume

    payload = {
        "name": "Peter Lee",
        "email": "pjoon.lee@mail.utoronto.ca",
        "phone": "647-986-8325",
        "linkedin": "ca.linkedin.com/in/petersjlee42",
        "github": "github.com/peterlee42",
        "education": [],
        "experience": [],
        "projects": [],
        "skills": {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "tools": [],
        },
    }
    mock_message = SimpleNamespace(
        content=[SimpleNamespace(type="text", text=json.dumps(payload))]
    )

    with patch(
        "tools.analyze.extract_text_from_pdf", return_value={"full_text": "resume text"}
    ):
        with patch(
            "tools.analyze.client.messages.create", return_value=mock_message
        ) as create_mock:
            result = asyncio.run(analyze_resume("fake_path.pdf"))

    create_mock.assert_called_once()
    assert result == payload


def test_score_resume_structure():
    from tools.score import score_resume_against_jd

    payload = {
        "score": 82,
        "matched_keywords": ["Python", "PostgreSQL", "Docker"],
        "missing_keywords": ["Azure"],
        "strengths": ["Strong Python skills"],
        "gaps": ["No Azure experience"],
        "summary": "Strong fit for the role.",
        "recommendation": "good fit",
    }
    mock_message = SimpleNamespace(
        content=[SimpleNamespace(type="text", text=json.dumps(payload))]
    )

    with patch(
        "tools.score.extract_text_from_pdf", return_value={"full_text": "resume text"}
    ):
        with patch("tools.score.client.messages.create", return_value=mock_message):
            result = asyncio.run(
                score_resume_against_jd(
                    "fake_path.pdf", "We need Python and Docker skills."
                )
            )

    assert 0 <= result["score"] <= 100
    assert result["matched_keywords"] == payload["matched_keywords"]
    assert result["missing_keywords"] == payload["missing_keywords"]
    assert result["recommendation"] in {
        "strong fit",
        "good fit",
        "partial fit",
        "weak fit",
    }


def test_summarize_document_structure_and_focus():
    from tools.summarize import summarize_document

    payload = {
        "title": "Peter Lee Resume",
        "document_type": "resume",
        "key_points": ["Computer Science student at UofT", "4.0 GPA"],
        "entities": {
            "people": [],
            "organizations": ["UofT"],
            "dates": [],
            "technologies": ["Python"],
        },
        "summary": "A strong CS resume.",
        "total_pages": 1,
    }
    mock_message = SimpleNamespace(
        content=[SimpleNamespace(type="text", text=json.dumps(payload))]
    )

    with patch(
        "tools.summarize.extract_text_from_pdf",
        return_value={"full_text": "sample text", "total_pages": 1},
    ):
        with patch(
            "tools.summarize.client.messages.create", return_value=mock_message
        ) as create_mock:
            result = asyncio.run(
                summarize_document("fake_path.pdf", focus="technical skills")
            )

    called_prompt = create_mock.call_args.kwargs["messages"][0]["content"]
    assert "Focus especially on: technical skills." in called_prompt
    assert result["summary"] == payload["summary"]
    assert isinstance(result["key_points"], list)


def test_tools_strip_markdown_json_fences():
    from tools.analyze import analyze_resume

    fenced = '```json\n{"name": "Peter Lee", "education": [], "experience": [], "projects": [], "skills": {"languages": [], "frameworks": [], "databases": [], "tools": []}}\n```'
    mock_message = SimpleNamespace(content=[SimpleNamespace(type="text", text=fenced)])

    with patch(
        "tools.analyze.extract_text_from_pdf", return_value={"full_text": "resume text"}
    ):
        with patch("tools.analyze.client.messages.create", return_value=mock_message):
            result = asyncio.run(analyze_resume("fake_path.pdf"))

    assert result["name"] == "Peter Lee"

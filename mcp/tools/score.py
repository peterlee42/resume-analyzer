"""
Tool: score_resume_against_jd
Scores a resume 0-100 against a job description, returning matched/missing keywords and a fit summary.
"""

import json

from anthropic import Anthropic

from tools.extract import extract_text_from_pdf

client = Anthropic()


async def score_resume_against_jd(file_path: str, job_description: str) -> dict:
    """Score a resume against a job description using Claude."""
    extracted = extract_text_from_pdf(file_path)
    resume_text = extracted["full_text"]

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""You are a technical recruiter. Score this resume against the job description.

                Return ONLY a JSON object:
                {{
                "score": <integer 0-100>,
                "matched_keywords": ["keyword1", "keyword2", ...],
                "missing_keywords": ["keyword1", "keyword2", ...],
                "strengths": ["...", "..."],
                "gaps": ["...", "..."],
                "summary": "<2-3 sentence fit summary>",
                "recommendation": "strong fit" | "good fit" | "partial fit" | "weak fit"
                }}

                JOB DESCRIPTION:
                {job_description}

                RESUME:
                {resume_text}

                Return ONLY the JSON.""",
            }
        ],
    )

    raw = next(block.text for block in message.content if block.type == "text").strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

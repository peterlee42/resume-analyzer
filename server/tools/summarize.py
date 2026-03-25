"""
Tool: summarize_document
Produces a structured summary of any PDF document with an optional focus area.
"""

import json

import anthropic

from tools.extract import extract_text_from_pdf

client = anthropic.Anthropic()


async def summarize_document(file_path: str, focus: str = "") -> dict:
    """Summarize any PDF document using Claude."""
    extracted = extract_text_from_pdf(file_path)
    text = extracted["full_text"]

    focus_instruction = f"Focus especially on: {focus}." if focus else ""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": f"""Summarize this document. {focus_instruction}

                Return ONLY a JSON object:
                {{
                "title": "<inferred document title>",
                "document_type": "<e.g. resume, report, contract, paper>",
                "key_points": ["...", "...", "..."],
                "entities": {{
                    "people": [],
                    "organizations": [],
                    "dates": [],
                    "technologies": []
                }},
                "summary": "<3-5 sentence summary>",
                "total_pages": {extracted["total_pages"]}
                }}

                DOCUMENT:
                {text}

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

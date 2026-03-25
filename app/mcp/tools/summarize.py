"""
Tool: summarize_document
Produces a structured summary of any PDF document with an optional focus area.
"""

import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv

try:
    from app.mcp.tools.extract import extract_text_from_pdf
except ModuleNotFoundError:
    # Supports running tests and local scripts from app/mcp.
    from tools.extract import extract_text_from_pdf

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError(
        "ANTHROPIC_API_KEY environment variable is not set. "
        "Please create a .env file with ANTHROPIC_API_KEY=your-api-key"
    )
client = Anthropic(api_key=api_key)


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

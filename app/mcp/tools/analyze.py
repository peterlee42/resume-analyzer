"""
Tool: analyze_resume
Sends extracted resume text to Claude and returns structured JSON.
"""

import json
import os

from anthropic import Anthropic
from dotenv import load_dotenv

from app.mcp.tools.extract import extract_text_from_pdf

load_dotenv()
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError(
        "ANTHROPIC_API_KEY environment variable is not set. "
        "Please create a .env file with ANTHROPIC_API_KEY=your-api-key"
    )
client = Anthropic(api_key=api_key)


async def analyze_resume(file_path: str) -> dict:
    """Parse a resume PDF into structured JSON using Claude."""
    extracted = extract_text_from_pdf(file_path)
    resume_text = extracted["full_text"]

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": f"""Parse this resume and return ONLY a JSON object with these fields:
                {{
                  "name": "",
                  "email": "",
                  "phone": "",
                  "linkedin": "",
                  "github": "",
                  "education": [
                    {{"institution": "", "degree": "", "gpa": "", "dates": "", "coursework": []}}
                  ],
                  "experience": [
                    {{"company": "", "role": "", "dates": "", "location": "", "bullets": []}}
                  ],
                  "projects": [
                    {{"name": "", "technologies": [], "bullets": []}}
                  ],
                  "skills": {{
                    "languages": [],
                    "frameworks": [],
                    "databases": [],
                    "tools": []
                  }}
                }}

                Resume:
                {resume_text}

                Return ONLY the JSON. No explanation, no markdown.""",
            }
        ],
    )

    raw = next(block.text for block in message.content if block.type == "text").strip()

    # Strip markdown fences if present
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())

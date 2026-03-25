"""
Resume & Document Analyzer MCP Server
Exposes tools for parsing, analyzing, and scoring resumes against job descriptions.
"""

import asyncio
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

try:
    from app.mcp.tools.analyze import analyze_resume
    from app.mcp.tools.extract import extract_text_from_pdf
    from app.mcp.tools.score import score_resume_against_jd
    from app.mcp.tools.summarize import summarize_document
except ModuleNotFoundError:
    # Supports running this file directly from the app/mcp directory.
    from tools.analyze import analyze_resume
    from tools.extract import extract_text_from_pdf
    from tools.score import score_resume_against_jd
    from tools.summarize import summarize_document

app = Server("resume-analyzer")


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="extract_pdf_text",
            description="Extract raw text from a PDF file (resume or document).",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the PDF file",
                    }
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="analyze_resume",
            description="Parse a resume and return structured JSON: name, contact, education, experience, skills, projects.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the PDF resume",
                    }
                },
                "required": ["file_path"],
            },
        ),
        Tool(
            name="score_resume",
            description="Score a resume (0-100) against a job description and return matched/missing keywords and fit summary.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the PDF resume",
                    },
                    "job_description": {
                        "type": "string",
                        "description": "Full text of the job description",
                    },
                },
                "required": ["file_path", "job_description"],
            },
        ),
        Tool(
            name="summarize_document",
            description="Produce a concise structured summary of any PDF document (not just resumes).",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the PDF file",
                    },
                    "focus": {
                        "type": "string",
                        "description": "Optional focus area, e.g. 'technical skills' or 'key dates'",
                    },
                },
                "required": ["file_path"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "extract_pdf_text":
            result = extract_text_from_pdf(arguments["file_path"])

        elif name == "analyze_resume":
            result = await analyze_resume(arguments["file_path"])

        elif name == "score_resume":
            result = await score_resume_against_jd(
                arguments["file_path"], arguments["job_description"]
            )

        elif name == "summarize_document":
            result = await summarize_document(
                arguments["file_path"], arguments.get("focus", "")
            )

        else:
            result = {"error": f"Unknown tool: {name}"}

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except Exception as e:
        return [TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())

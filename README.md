# 📄 Resume & Document Analyzer

An AI-powered resume parsing and job fit scoring platform. Upload a PDF resume, paste a job description, and get back a structured analysis — parsed candidate data, a 0–100 fit score, matched and missing keywords, and a plain-English recommendation.

Built with **MCP** · **FastAPI** · **Next.js** · **PostgreSQL** · **Docker**

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js UI    │────▶│    FastAPI      │────▶│   MCP Server    │
│  (file upload,  │     │  (HTTP bridge,  │     │  (tools: parse, │
│   results view) │     │   file storage) │     │  score, summarize)│
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │
                         ┌──────▼──────┐
                         │  PostgreSQL │
                         │  (results)  │
                         └─────────────┘
```

- **MCP Server** — core AI tooling, plugs into Claude Desktop or any MCP-compatible client
- **FastAPI** — HTTP bridge between the UI and MCP tools, handles PDF uploads and persists results
- **Next.js** — frontend with PDF drag-and-drop, resume viewer, and score dashboard
- **PostgreSQL** — stores uploaded resumes, analysis results, and job descriptions
- **Docker Compose** — one command to run the full stack

---

## Features

- **Parse any resume** into structured JSON — contact info, education, experience, projects, and skills
- **Score a candidate** against a job description with a 0–100 fit score, matched/missing keywords, strengths, gaps, and a recommendation
- **Summarize any PDF** with an optional focus area (e.g. "technical skills", "key dates")
- **Persistent results** — all analyses saved to PostgreSQL, retrievable by session
- **MCP-compatible** — tools also available directly via Claude Desktop

---

## MCP Tools

| Tool                 | Input                      | Output                                                                 |
| -------------------- | -------------------------- | ---------------------------------------------------------------------- |
| `extract_pdf_text`   | PDF path                   | Raw text, page-by-page                                                 |
| `analyze_resume`     | PDF path                   | Structured JSON (name, education, experience, skills, projects)        |
| `score_resume`       | PDF path + job description | Score 0–100, matched/missing keywords, strengths, gaps, recommendation |
| `summarize_document` | PDF path + optional focus  | Key points, entities, summary                                          |

### Example: `score_resume` output

```json
{
  "score": 82,
  "matched_keywords": ["Python", "PostgreSQL", "Docker", "REST APIs"],
  "missing_keywords": ["Azure", "MCP servers"],
  "strengths": [
    "Strong Python and backend experience",
    "Proven PostgreSQL usage in production"
  ],
  "gaps": ["No Azure experience listed", "MCP not mentioned"],
  "summary": "Strong technical fit with relevant backend and AI experience. Minor gaps in cloud platform preference and MCP familiarity.",
  "recommendation": "good fit"
}
```

---

## Getting Started

### Prerequisites

- [Docker](https://www.docker.com/) and Docker Compose
- An [Anthropic API key](https://console.anthropic.com)

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/resume-analyzer.git
cd resume-analyzer
```

### 2. Set environment variables

```bash
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
```

### 3. Run the full stack

```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- FastAPI docs: http://localhost:8000/docs
- MCP server: running on stdio (see Claude Desktop setup below)

---

## Claude Desktop Integration

To use the MCP tools directly in Claude Desktop, add the following to your config:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "resume-analyzer": {
      "command": "python",
      "args": ["/absolute/path/to/resume-analyzer/app/mcp/server.py"],
      "env": {
        "ANTHROPIC_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

Restart Claude Desktop and the tools will appear automatically.

---

## Running Tests

```bash
pip install pytest pytest-asyncio
pytest app/mcp/tests -v
```

Tests use mocked Claude API responses — no API key required.

---

## Project Structure

```text
resume-analyzer/
├── docker-compose.yml
├── Dockerfile.api
├── main.py                         # root FastAPI compatibility entrypoint
├── api/
│   └── main.py                     # legacy compatibility import path
└── app/
    ├── api/
    │   ├── main.py                 # FastAPI app implementation
    │   ├── db.py                   # PostgreSQL connection (asyncpg)
    │   └── routes/
    └── mcp/
        ├── server.py               # MCP server entry point
        ├── tools/
        │   ├── extract.py          # PDF text extraction (pdfplumber)
        │   ├── analyze.py          # Resume parser -> structured JSON
        │   ├── score.py            # Resume scorer vs job description
        │   └── summarize.py        # General document summarizer
        └── tests/
            └── test_tools.py       # Unit tests with mocked Anthropic API
```

---

## Tech Stack

| Layer       | Technology                                                                                                               |
| ----------- | ------------------------------------------------------------------------------------------------------------------------ |
| AI tooling  | [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk), [Anthropic Claude API](https://docs.anthropic.com) |
| Backend     | [FastAPI](https://fastapi.tiangolo.com), [asyncpg](https://github.com/MagicStack/asyncpg)                                |
| Frontend    | [Next.js](https://nextjs.org), [Tailwind CSS](https://tailwindcss.com)                                                   |
| Database    | [PostgreSQL](https://www.postgresql.org)                                                                                 |
| PDF parsing | [pdfplumber](https://github.com/jsvine/pdfplumber)                                                                       |
| Infra       | [Docker](https://www.docker.com), Docker Compose                                                                         |
| Testing     | [pytest](https://pytest.org), [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio)                             |

---

## License

MIT

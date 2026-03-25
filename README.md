# 📄 Resume & Document Analyzer — MCP Server

An [MCP (Model Context Protocol)](https://modelcontextprotocol.io) server that exposes AI-powered tools for resume parsing, job fit scoring, and document summarization. Plug it directly into Claude Desktop or any MCP-compatible client and stop reading PDFs manually.

Built with **Python**, **Claude API**, and **pdfplumber**.

---

## Features

- **Parse any resume** into clean structured JSON — contact info, education, experience, projects, and skills
- **Score a candidate** against a job description with a 0–100 fit score, matched keywords, gaps, and a plain-English recommendation
- **Summarize any PDF** document with an optional focus area (e.g. "technical skills", "key dates")
- **Extract raw text** from any PDF for downstream processing

---

## Tools

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

## Setup

### Prerequisites

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com)

### 1. Clone the repo

```bash
git clone https://github.com/yourusername/resume-mcp-server.git
cd resume-mcp-server
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your API key

```bash
export ANTHROPIC_API_KEY=your-api-key-here
```

### 4. Run the server

```bash
python server.py
```

---

## Connect to Claude Desktop

Add this to your Claude Desktop config:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "resume-analyzer": {
      "command": "python",
      "args": ["/absolute/path/to/resume-mcp-server/server.py"],
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
pytest tests/ -v
```

Tests use mocked Claude API responses so no API key is needed to run them.

---

## Project Structure

```
resume-mcp-server/
├── server.py                   # MCP server entry point, tool registry
├── requirements.txt
├── claude_desktop_config.json  # Claude Desktop config template
├── tools/
│   ├── extract.py              # PDF text extraction via pdfplumber
│   ├── analyze.py              # Resume parser → structured JSON
│   ├── score.py                # Resume scorer vs job description
│   └── summarize.py            # General document summarizer
└── tests/
    └── test_tools.py           # Unit tests with mocked Anthropic API
```

---

## Tech Stack

- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk) — server transport and tool registration
- [Anthropic Claude API](https://docs.anthropic.com) — AI parsing and analysis
- [pdfplumber](https://github.com/jsvine/pdfplumber) — PDF text extraction
- [pytest](https://pytest.org) + [pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio) — testing

---

## License

MIT

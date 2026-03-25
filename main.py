"""
Resume Analyzer — FastAPI Backend
Bridges the Next.js frontend with the MCP tool layer.
"""

from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from app.api.db import init_db
from app.api.routes import analyze, results, score, summarize, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Resume Analyzer API",
    description="AI-powered resume parsing, scoring, and document summarization.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api/upload", tags=["Upload"])
app.include_router(analyze.router, prefix="/api/analyze", tags=["Analyze"])
app.include_router(score.router, prefix="/api/score", tags=["Score"])
app.include_router(summarize.router, prefix="/api/summarize", tags=["Summarize"])
app.include_router(results.router, prefix="/api/results", tags=["Results"])


@app.get("/health")
async def health():
    return {"status": "ok"}

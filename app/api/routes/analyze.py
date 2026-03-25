"""
POST /api/analyze
Parses a resume PDF into structured JSON via the MCP analyze tool.
"""

import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.api.db import get_pool
from app.mcp.tools.analyze import analyze_resume

router = APIRouter()


class AnalyzeRequest(BaseModel):
    upload_id: int


@router.post("")
async def analyze(req: AnalyzeRequest):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT file_path FROM uploads WHERE id = $1", req.upload_id)
        if not row:
            raise HTTPException(status_code=404, detail="Upload not found.")

        result = await analyze_resume(row["file_path"])

        analysis = await conn.fetchrow(
            """INSERT INTO analyses (upload_id, type, result)
               VALUES ($1, 'analyze', $2) RETURNING id""",
            req.upload_id, json.dumps(result)
        )

    return {"analysis_id": analysis["id"], "result": result}

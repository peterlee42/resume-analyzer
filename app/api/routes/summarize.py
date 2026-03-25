"""
POST /api/summarize
Summarizes any PDF with an optional focus area.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.api.db import get_pool
from app.mcp.tools.summarize import summarize_document
import json

router = APIRouter()


class SummarizeRequest(BaseModel):
    upload_id: int
    focus: Optional[str] = ""


@router.post("")
async def summarize(req: SummarizeRequest):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT file_path FROM uploads WHERE id = $1", req.upload_id)
        if not row:
            raise HTTPException(status_code=404, detail="Upload not found.")

        result = await summarize_document(row["file_path"], req.focus or "")

        analysis = await conn.fetchrow(
            """INSERT INTO analyses (upload_id, type, input_meta, result)
               VALUES ($1, 'summarize', $2, $3) RETURNING id""",
            req.upload_id,
            json.dumps({"focus": req.focus}),
            json.dumps(result)
        )

    return {"analysis_id": analysis["id"], "result": result}

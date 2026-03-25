"""
POST /api/score
Scores a resume against a job description.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.api.db import get_pool
from app.mcp.tools.score import score_resume_against_jd
import json

router = APIRouter()


class ScoreRequest(BaseModel):
    upload_id: int
    job_description: str


@router.post("")
async def score(req: ScoreRequest):
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT file_path FROM uploads WHERE id = $1", req.upload_id)
        if not row:
            raise HTTPException(status_code=404, detail="Upload not found.")

        result = await score_resume_against_jd(row["file_path"], req.job_description)

        analysis = await conn.fetchrow(
            """INSERT INTO analyses (upload_id, type, input_meta, result)
               VALUES ($1, 'score', $2, $3) RETURNING id""",
            req.upload_id,
            json.dumps({"job_description": req.job_description[:500]}),
            json.dumps(result)
        )

    return {"analysis_id": analysis["id"], "result": result}

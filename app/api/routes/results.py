"""
GET /api/results/{upload_id}
Returns all analyses for a given upload.
"""

from fastapi import APIRouter, HTTPException
from app.api.db import get_pool
import json

router = APIRouter()


@router.get("/{upload_id}")
async def get_results(upload_id: int):
    pool = await get_pool()
    async with pool.acquire() as conn:
        upload = await conn.fetchrow("SELECT * FROM uploads WHERE id = $1", upload_id)
        if not upload:
            raise HTTPException(status_code=404, detail="Upload not found.")

        rows = await conn.fetch(
            "SELECT id, type, input_meta, result, created_at FROM analyses WHERE upload_id = $1 ORDER BY created_at DESC",
            upload_id
        )

    analyses = [
        {
            "analysis_id": r["id"],
            "type": r["type"],
            "input_meta": json.loads(r["input_meta"]) if r["input_meta"] else None,
            "result": json.loads(r["result"]),
            "created_at": r["created_at"].isoformat()
        }
        for r in rows
    ]

    return {
        "upload_id": upload_id,
        "filename": upload["filename"],
        "analyses": analyses
    }

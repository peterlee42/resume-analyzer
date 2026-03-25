"""
POST /api/upload
Accepts a PDF file, saves to disk, records in DB, returns upload_id.
"""

import os
import uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.api.db import get_pool

router = APIRouter()

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/tmp/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    safe_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, safe_name)

    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "INSERT INTO uploads (filename, file_path) VALUES ($1, $2) RETURNING id",
            file.filename, file_path
        )

    return {"upload_id": row["id"], "filename": file.filename}

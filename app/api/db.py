"""
PostgreSQL connection via asyncpg.
Tables are created on startup if they don't exist.
"""

import os
from typing import Optional

import asyncpg

_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(dsn=os.environ["DATABASE_URL"])
    return _pool


async def init_db():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS uploads (
                id          SERIAL PRIMARY KEY,
                filename    TEXT NOT NULL,
                file_path   TEXT NOT NULL,
                created_at  TIMESTAMPTZ DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS analyses (
                id          SERIAL PRIMARY KEY,
                upload_id   INT REFERENCES uploads(id) ON DELETE CASCADE,
                type        TEXT NOT NULL,  -- 'analyze' | 'score' | 'summarize'
                input_meta  JSONB,          -- e.g. job_description, focus
                result      JSONB NOT NULL,
                created_at  TIMESTAMPTZ DEFAULT NOW()
            );
        """)

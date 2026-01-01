"""Database Service - lightweight SQLite-backed async helpers"""

import asyncio
import sqlite3
from typing import Any, List, Dict, Optional
from pathlib import Path


class Database:
    """Simple async-friendly SQLite wrapper using thread executor."""

    def __init__(self, db_path: str = "./database/data.db"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    async def connect(self):
        def _connect():
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            return conn
        self._conn = await asyncio.to_thread(_connect)

    async def disconnect(self):
        if self._conn:
            await asyncio.to_thread(self._conn.close)
            self._conn = None

    async def execute(self, query: str, params: tuple = ()):  # returns cursor-like
        def _exec():
            cur = self._conn.cursor()
            cur.execute(query, params)
            self._conn.commit()
            return cur
        return await asyncio.to_thread(_exec)

    async def fetch_one(self, query: str, params: tuple = ()):  # -> Optional[Dict]
        def _fetch():
            cur = self._conn.cursor()
            cur.execute(query, params)
            row = cur.fetchone()
            return dict(row) if row else None
        return await asyncio.to_thread(_fetch)

    async def fetch_all(self, query: str, params: tuple = ()):  # -> List[Dict]
        def _fetch():
            cur = self._conn.cursor()
            cur.execute(query, params)
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        return await asyncio.to_thread(_fetch)


db = Database()

"""File handling utilities for extracting and splitting text from documents."""

import asyncio
from pathlib import Path
from typing import List


class FileHandler:
    async def extract_text(self, filepath: str) -> str:
        def _read():
            p = Path(filepath)
            if not p.exists():
                return ""
            # Try reading as text; real implementation would handle PDFs, DOCX, etc.
            return p.read_text(encoding='utf-8', errors='ignore')
        return await asyncio.to_thread(_read)

    async def split_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        if not text:
            return []
        chunks = []
        start = 0
        while start < len(text):
            chunks.append(text[start:start + chunk_size])
            start += chunk_size - overlap
        return chunks

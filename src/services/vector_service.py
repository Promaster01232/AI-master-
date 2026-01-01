"""Vector Service for handling vector operations"""

import asyncio
from typing import Dict, List, Optional


class VectorService:
    def __init__(self):
        # index: document_id -> list of chunks (dict with chunk_id, content, embedding, metadata)
        self.index: Dict[str, List[Dict]] = {}

    async def initialize(self):
        return

    async def add_chunk(self, document_id: str, chunk_id: str, content: str, embedding: List[float], metadata: Dict):
        self.index.setdefault(document_id, []).append({
            "chunk_id": chunk_id,
            "content": content,
            "embedding": embedding,
            "metadata": metadata,
        })

    async def delete_document(self, document_id: str):
        if document_id in self.index:
            del self.index[document_id]

    async def search(self, query: str, document_ids: Optional[List[str]] = None, limit: int = 10):
        # This is a stubbed search. In a real implementation you would compute
        # an embedding for the query and perform nearest-neighbor search.
        results = []
        docs = document_ids if document_ids is not None else list(self.index.keys())
        for did in docs:
            for chunk in self.index.get(did, [])[:limit]:
                results.append({
                    "document_id": did,
                    "chunk_id": chunk["chunk_id"],
                    "content": chunk["content"],
                    "score": 1.0,
                    "metadata": chunk.get("metadata", {}),
                })
        return results


# Export singleton for backward compatibility
vector_service = VectorService()

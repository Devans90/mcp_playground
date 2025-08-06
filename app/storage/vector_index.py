# app/storage/vector_index.py
from __future__ import annotations
from typing import List, Dict, Any, Optional
import os
from ..config import AppConfig

class VectorIndex:
    """
    Simple wrapper that prefers Chroma; falls back to a no-op in-memory index.
    """
    def __init__(self, cfg: AppConfig) -> None:
        self.cfg = cfg
        self.backend = None
        self.client = None
        try:
            import chromadb  # type: ignore
            self.backend = "chroma"
            os.makedirs(cfg.vector.chroma_path, exist_ok=True)
            self.client = chromadb.PersistentClient(path=cfg.vector.chroma_path)
            self.collections: Dict[str, Any] = {}
        except Exception:
            self.backend = "memory"
            self.mem: List[Dict[str, Any]] = []

    def _get_collection(self, name: str = "default"):
        if self.backend != "chroma":
            return None
        if name not in self.collections:
            self.collections[name] = self.client.get_or_create_collection(name=name)
        return self.collections[name]

    def index_documents(self, docs: List[str], metadatas: Optional[List[Dict[str, Any]]] = None, namespace: str = "default") -> int:
        if self.backend == "chroma":
            col = self._get_collection(namespace)
            ids = [f"{namespace}-{i}" for i in range(len(docs))]
            col.upsert(ids=ids, documents=docs, metadatas=metadatas)
            return len(docs)
        else:
            for i, d in enumerate(docs):
                self.mem.append({"text": d, "metadata": (metadatas[i] if metadatas else {})})
            return len(docs)

    def query(self, query: str, k: int = 5, namespace: str = "default") -> List[Dict[str, Any]]:
        if self.backend == "chroma":
            col = self._get_collection(namespace)
            res = col.query(query_texts=[query], n_results=k, include=["documents", "metadatas", "distances"])
            out = []
            for i in range(len(res["documents"][0])):
                out.append({
                    "text": res["documents"][0][i],
                    "score": float(res["distances"][0][i]) if res.get("distances") else 0.0,
                    "metadata": res["metadatas"][0][i],
                })
            return out
        else:
            # naive contains-based scoring
            scored = []
            for item in self.mem:
                score = 1.0 if query.lower() in item["text"].lower() else 0.0
                scored.append({"text": item["text"], "score": score, "metadata": item["metadata"]})
            return sorted(scored, key=lambda x: x["score"], reverse=True)[:k]

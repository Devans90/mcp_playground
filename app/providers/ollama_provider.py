from __future__ import annotations
from typing import List, Optional
import time, httpx
from pydantic import BaseModel
from ..config import AppConfig, ModelRoute
from ..types import Message, AssistantResponse

class OllamaProvider:
    """
    Ollama local provider via REST API.
    """
    def __init__(self, cfg: AppConfig) -> None:
        self.cfg = cfg
        self.base = cfg.local.base_url.rstrip("/")

    def complete(self, messages: List[Message], route: ModelRoute) -> AssistantResponse:
        t0 = time.time()
        # Convert chat to a single prompt for simplicity
        prompt = "\n".join(f"{m.role}: {m.content}" for m in messages)
        payload = {"model": route.model, "prompt": prompt, "stream": False}
        with httpx.Client(timeout=30) as cx:
            resp = cx.post(f"{self.base}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
        t1 = time.time()
        return AssistantResponse(
            messages=[Message(role="assistant", content=data.get("response", ""))],
            finish_reason="stop",
            latency_ms=int((t1 - t0) * 1000),
        )

    def embed(self, texts: List[str], model: Optional[str] = None):
        # If using Ollama embeddings model, call /api/embeddings
        model = model or "nomic-embed-text"
        with httpx.Client(timeout=30) as cx:
            out = []
            for t in texts:
                r = cx.post(f"{self.base}/api/embeddings", json={"model": model, "prompt": t})
                r.raise_for_status()
                out.append(r.json()["embedding"])
            return out

    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        return len(text.split())

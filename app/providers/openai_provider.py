from __future__ import annotations
from typing import List, Optional
import time
from pydantic import BaseModel
from openai import OpenAI
from ..config import AppConfig, ModelRoute
from ..types import Message, AssistantResponse

class OpenAIProvider:
    """
    OpenAI provider using the official SDK.
    """
    def __init__(self, cfg: AppConfig) -> None:
        self.cfg = cfg
        self.client = OpenAI(api_key=cfg.openai.api_key.get_secret_value() if cfg.openai.api_key else None,
                             base_url=str(cfg.openai.base_url) if cfg.openai.base_url else None)

    def complete(self, messages: List[Message], route: ModelRoute) -> AssistantResponse:
        t0 = time.time()
        # Simple messages->responses call; tool-calling handled by orchestrator
        resp = self.client.chat.completions.create(
            model=route.model,
            messages=[m.model_dump() for m in messages],
            temperature=route.temperature,
            max_tokens=route.max_tokens,
        )
        t1 = time.time()
        choice = resp.choices[0]
        out = AssistantResponse(
            messages=[Message(role="assistant", content=choice.message.content or "")],
            tool_calls=[],
            finish_reason=choice.finish_reason,
            usage_tokens=(resp.usage.total_tokens if hasattr(resp, "usage") and resp.usage else None),
            latency_ms=int((t1 - t0) * 1000),
        )
        return out

    def embed(self, texts: List[str], model: Optional[str] = None):
        model = model or self.cfg.vector.embedding_model
        resp = self.client.embeddings.create(model=model, input=texts)
        return [e.embedding for e in resp.data]

    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        # Simple proxy; accurate counting would use tiktoken for OpenAI models
        return len(text.split())

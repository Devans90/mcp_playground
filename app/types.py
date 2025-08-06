from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Message(BaseModel):
    """Chat message used by providers and router."""
    role: str
    content: str

class AssistantResponse(BaseModel):
    """Normalized response from any provider."""
    messages: List[Message]
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    finish_reason: Optional[str] = None
    usage_tokens: Optional[int] = None
    latency_ms: Optional[int] = None

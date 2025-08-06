# app/router.py
from __future__ import annotations
from typing import List, Optional, Dict
from pydantic import BaseModel
from .config import AppConfig, ModelRoute, ProviderName
from .types import Message, AssistantResponse  # <-- use shared types
from .providers.openai_provider import OpenAIProvider
from .providers.ollama_provider import OllamaProvider
from .providers.bedrock_provider import BedrockProvider

class LLMProvider:
    def complete(self, messages: List[Message], route: ModelRoute) -> AssistantResponse: ...
    def embed(self, texts: List[str], model: Optional[str] = None): ...
    def count_tokens(self, text: str, model: Optional[str] = None) -> int: ...

class ModelRouter:
    """
    Selects provider per request; supports optional task-based routing.
    """
    def __init__(self, cfg: AppConfig) -> None:
        self.cfg = cfg
        self.providers: Dict[ProviderName, object] = {
            ProviderName.OPENAI: OpenAIProvider(cfg),
            ProviderName.LOCAL: OllamaProvider(cfg),
        }
        if cfg.bedrock.region:
            try:
                self.providers[ProviderName.BEDROCK] = BedrockProvider(cfg)
            except Exception:
                # If Bedrock fails to initialize, we skip it
                print("Bedrock provider initialization failed, skipping.")
            
    def select_route(self, task_hint: Optional[str] = None) -> ModelRoute:
        if task_hint and task_hint in self.cfg.routing_rules.by_task:
            return self.cfg.routing_rules.by_task[task_hint]
        return self.cfg.default_route

    def complete(self, messages: List[Message], route: Optional[ModelRoute] = None) -> AssistantResponse:
        route = route or self.select_route()
        provider = self.providers[route.provider]
        return provider.complete(messages, route)

    def embed(self, texts: List[str], model: Optional[str] = None):
        route = self.select_route("embed")
        provider = self.providers[route.provider]
        return provider.embed(texts, model or self.cfg.vector.embedding_model)

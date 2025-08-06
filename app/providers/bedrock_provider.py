from __future__ import annotations
from typing import List, Optional
import time
import boto3
from ..config import AppConfig, ModelRoute
from ..types import Message, AssistantResponse

class BedrockProvider:
    """
    Placeholder for Bedrock provider.
    NOTE: Final model invocation varies by model family (Claude, Llama, etc.).
    I will wire specific calls after you confirm the exact model(s).
    """
    def __init__(self, cfg: AppConfig) -> None:
        self.cfg = cfg
        session = boto3.Session(profile_name=cfg.bedrock.profile) if cfg.bedrock.profile else boto3.Session()
        self.client = session.client("bedrock-runtime", region_name=cfg.bedrock.region)

    def complete(self, messages: List[Message], route: ModelRoute) -> AssistantResponse:
        # TODO: implement once target Bedrock model is chosen
        return AssistantResponse(messages=[], tool_calls=[], finish_reason="not_implemented")

    def embed(self, texts: List[str], model: Optional[str] = None):
        # TODO: implement if needed for chosen model
        return []

    def count_tokens(self, text: str, model: Optional[str] = None) -> int:
        return len(text.split())

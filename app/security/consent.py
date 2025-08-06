# app/security/consent.py
from __future__ import annotations
from typing import Dict, Any
from ..config import AppConfig

COSTY_TOOLS = {
    "tool_web_search",
    "tool_summarize",
    "tool_rag_index_texts",
    "tool_calendar_add",   # network; may not have direct cost but guarded
    "tool_email_send",
    "tool_slack_post",
    "tool_teams_post",
}

class ConsentPolicy:
    """
    Consent policy for tool execution.
    """
    def __init__(self, cfg: AppConfig) -> None:
        self.cfg = cfg
        self._grants = set()

    def needs_consent(self, tool_name: str, args: Dict[str, Any]) -> bool:
        if tool_name in self._grants:
            return False
        if self.cfg.permissions.always_allow_reads:
            if tool_name in {"tool_file_read", "tool_notes_list", "tool_tasks_list", "tool_calendar_list"}:
                return False
        if self.cfg.permissions.require_consent_for_costs and tool_name in COSTY_TOOLS:
            return True
        return False

    def grant(self, tool_name: str) -> None:
        self._grants.add(tool_name)

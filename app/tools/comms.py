from __future__ import annotations
from typing import List, Optional
import httpx
from ..config import AppConfig

def tool_email_send(cfg: AppConfig, to: List[str], subject: str, body: str,
                    cc: Optional[List[str]] = None, bcc: Optional[List[str]] = None) -> str:
    # Optional simple SMTP implementation can be added later; disabled by default
    raise RuntimeError("Email not configured.")

def tool_slack_post(cfg: AppConfig, message: str, channel: Optional[str] = None) -> str:
    if not cfg.slack.webhook_url:
        raise RuntimeError("Slack webhook not configured.")
    with httpx.Client(timeout=15) as cx:
        r = cx.post(cfg.slack.webhook_url.get_secret_value(), json={"text": message})
        r.raise_for_status()
    return "ok"

def tool_teams_post(cfg: AppConfig, message: str) -> str:
    if not cfg.teams.webhook_url:
        raise RuntimeError("Teams webhook not configured.")
    with httpx.Client(timeout=15) as cx:
        r = cx.post(cfg.teams.webhook_url.get_secret_value(), json={"text": message})
        r.raise_for_status()
    return "ok"
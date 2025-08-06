from __future__ import annotations
from typing import Optional
import pyperclip  # optional; if unavailable, we degrade gracefully
from ..config import AppConfig
from ..security.sandbox import enforce_allowlist

def tool_file_read(cfg: AppConfig, path: str) -> str:
    abs_path = enforce_allowlist(path, cfg)
    with open(abs_path, "r", encoding="utf-8") as f:
        return f.read()

def tool_file_write(cfg: AppConfig, path: str, content: str) -> str:
    abs_path = enforce_allowlist(path, cfg)
    with open(abs_path, "w", encoding="utf-8") as f:
        f.write(content)
    return abs_path

def tool_calculator(expression: str) -> str:
    # Extremely conservative evaluator
    import math
    allowed = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
    allowed["__builtins__"] = {}
    return str(eval(expression, allowed, {}))

def tool_clipboard_set(text: str) -> bool:
    try:
        pyperclip.copy(text)
        return True
    except Exception:
        return False

def tool_notify(title: str, body: str) -> bool:
    # Server-only: no-op, returns False to indicate not supported
    return False

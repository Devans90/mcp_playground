from __future__ import annotations
import os
from ..config import AppConfig

def enforce_allowlist(path: str, cfg: AppConfig) -> str:
    """
    Ensure path is within sandbox root; return normalized absolute path.
    """
    root = os.path.abspath(cfg.permissions.sandbox_root)
    target = os.path.abspath(path if os.path.isabs(path) else os.path.join(root, path))
    if not target.startswith(root):
        raise PermissionError("Path escapes sandbox root.")
    os.makedirs(os.path.dirname(target), exist_ok=True)
    return target

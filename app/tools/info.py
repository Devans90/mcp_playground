from __future__ import annotations
from typing import List, Dict
import httpx
from ..config import AppConfig

def tool_web_search(cfg: AppConfig, query: str, k: int = 5) -> List[Dict[str, str]]:
    """
    Tavily web search. Requires cfg.search.api_key.
    Returns: [{'title','url','snippet'}]
    """
    if not cfg.search.api_key:
        raise RuntimeError("Tavily API key not configured.")
    with httpx.Client(timeout=30) as cx:
        r = cx.post("https://api.tavily.com/search", json={"api_key": cfg.search.api_key.get_secret_value(), "query": query, "max_results": k})
        r.raise_for_status()
        data = r.json()
        out = []
        for item in data.get("results", [])[:k]:
            out.append({"title": item.get("title",""), "url": item.get("url",""), "snippet": item.get("content","")[:300]})
        return out

def tool_retrieve_url(url: str) -> str:
    """
    Retrieve URL and return plaintext (very basic).
    """
    with httpx.Client(timeout=30) as cx:
        r = cx.get(url)
        r.raise_for_status()
        return r.text

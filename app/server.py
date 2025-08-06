from __future__ import annotations
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse
from .config import AppConfig, load_config
from .router import ModelRouter, Message
from .storage.memory_store import MemoryStore
from .storage.vector_index import VectorIndex
from .security.consent import ConsentPolicy
from .observability.telemetry import setup_tracing
from .dash_ui import build_dash_app

def register_mcp_tools(app: FastAPI, router: ModelRouter, store: MemoryStore, index: VectorIndex, consent: ConsentPolicy):
    """
    Placeholder for MCP registration.
    I will add concrete FastMCP bindings once you confirm FastMCP version + APIs.
    """
    return

def build_fastapi_app(cfg: AppConfig) -> FastAPI:
    app = FastAPI(title="FastMCP Assistant")
    tracer = setup_tracing(cfg.observability.service_name)

    store = MemoryStore(cfg)
    index = VectorIndex(cfg)
    model_router = ModelRouter(cfg)
    consent = ConsentPolicy(cfg)

    register_mcp_tools(app, model_router, store, index, consent)

    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    @app.get("/config")
    def redacted_config():
        # Minimal redaction
        c = cfg.model_dump()
        if c.get("openai", {}).get("api_key"): c["openai"]["api_key"] = "***"
        if c.get("search", {}).get("api_key"): c["search"]["api_key"] = "***"
        if c.get("slack", {}).get("webhook_url"): c["slack"]["webhook_url"] = "***"
        if c.get("teams", {}).get("webhook_url"): c["teams"]["webhook_url"] = "***"
        return c

    # Simple test endpoint to call the model
    @app.post("/chat")
    def chat(body: Dict[str, Any]):
        messages = [Message(**m) for m in body.get("messages", [])]
        resp = model_router.complete(messages)
        return JSONResponse(resp.model_dump())

    # Optional Dash UI
    if cfg.server.enable_dash:
        dash_app = build_dash_app(store)
        from starlette.middleware.wsgi import WSGIMiddleware
        app.mount("/dash", WSGIMiddleware(dash_app.server))
    return app

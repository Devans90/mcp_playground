# main.py
import os
import uvicorn
from app.config import load_config
from app.server import build_fastapi_app 

def main():
    """
    Load config, build FastAPI app, and run the server.
    """
    cfg = load_config(os.getenv("APP_CONFIG", "config.yaml"))
    app = build_fastapi_app(cfg)
    uvicorn.run(app, host=cfg.server.host, port=cfg.server.port, log_level="info")

if __name__ == "__main__":
    main()
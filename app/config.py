from __future__ import annotations
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field, HttpUrl, SecretStr
from pydantic.functional_validators import field_validator
import os
import yaml
from enum import Enum

class VectorBackend(str, Enum):
    """Vector index backend options."""
    SQLITE = "sqlite"
    CHROMA = "chroma"

class ConsentMode(str, Enum):
    """Consent policy modes."""
    REQUIRE = "require"
    AUTO = "auto"

class TransportMode(str, Enum):
    """Server transport modes."""
    STDIO = "stdio"
    HTTP = "http"
    BOTH = "both"

class ProviderName(str, Enum):
    """Model providers used by the router."""
    OPENAI = "openai"
    BEDROCK = "bedrock"
    LOCAL = "local"

class WebSearchProvider(str, Enum):
    """Pluggable web search providers."""
    TAVILY = "tavily"
    SERPAPI = "serpapi"
    BING = "bing"
    CUSTOM = "custom"

class ModelRoute(BaseModel):
    provider: ProviderName
    model: str
    temperature: float = 0.2
    max_tokens: Optional[int] = None
    reasoning: bool = False

class OpenAIConfig(BaseModel):
    api_key: Optional[SecretStr] = None
    base_url: Optional[HttpUrl] = None

class BedrockConfig(BaseModel):
    region: Optional[str] = None
    profile: Optional[str] = None

class OllamaConfig(BaseModel):
    base_url: str = "http://localhost:11434"

class VectorConfig(BaseModel):
    backend: str = VectorBackend.CHROMA
    chroma_path: str = "./data/chroma"
    sqlite_path: str = "./data/embeddings.sqlite3"
    embedding_model: str = "text-embedding-3-small"

class StorageConfig(BaseModel):
    sqlite_path: str = "./data/app.sqlite3"

class PermissionsConfig(BaseModel):
    consent_mode: str = ConsentMode.REQUIRE
    sandbox_root: str = "./sandbox"
    always_allow_reads: bool = True
    require_consent_for_costs: bool = True

class ObservabilityConfig(BaseModel):
    json_logs: bool = True
    opentelemetry_enabled: bool = True
    service_name: str = "fastmcp-assistant"

class ServerConfig(BaseModel):
    transport: str = TransportMode.BOTH
    host: str = "0.0.0.0"
    port: int = 8080
    enable_dash: bool = True

class WebSearchConfig(BaseModel):
    provider: str = WebSearchProvider.TAVILY
    api_key: Optional[SecretStr] = None
    custom_base_url: Optional[HttpUrl] = None

class GoogleCalendarConfig(BaseModel):
    enabled: bool = True
    oauth_client_secret_path: str = "./secrets/google_client_secret.json"
    token_path: str = "./secrets/google_token.json"
    calendar_id: Optional[str] = "primary"

class EmailConfig(BaseModel):
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = 587
    username: Optional[str] = None
    password: Optional[SecretStr] = None
    from_address: Optional[str] = None
    tls: bool = True

class SlackConfig(BaseModel):
    webhook_url: Optional[SecretStr] = None

class TeamsConfig(BaseModel):
    webhook_url: Optional[SecretStr] = None

class LimitsConfig(BaseModel):
    per_request_max_tokens: int = 4000
    per_request_timeout_s: int = 20
    max_tool_calls_per_turn: int = 4

class RoutingRules(BaseModel):
    by_task: Dict[str, ModelRoute] = Field(default_factory=dict)

class AppConfig(BaseModel):
    openai: OpenAIConfig = OpenAIConfig()
    bedrock: BedrockConfig = BedrockConfig()
    local: OllamaConfig = OllamaConfig()
    vector: VectorConfig = VectorConfig()
    storage: StorageConfig = StorageConfig()
    permissions: PermissionsConfig = PermissionsConfig()
    observability: ObservabilityConfig = ObservabilityConfig()
    server: ServerConfig = ServerConfig()
    search: WebSearchConfig = WebSearchConfig()
    google_calendar: GoogleCalendarConfig = GoogleCalendarConfig()
    email: EmailConfig = EmailConfig()
    slack: SlackConfig = SlackConfig()
    teams: TeamsConfig = TeamsConfig()
    limits: LimitsConfig = LimitsConfig()
    default_route: ModelRoute = ModelRoute(provider=ProviderName.OPENAI, model="o4-mini")
    routing_rules: RoutingRules = RoutingRules()

def load_config(path: str = "config.yaml") -> AppConfig:
    """
    Load YAML config and overlay secrets from environment variables (.env).
    Environment variables used if present:
      - OPENAI_API_KEY, TAVILY_API_KEY, AWS_PROFILE, AWS_REGION, OLLAMA_BASE_URL,
        GOOGLE_CLIENT_SECRET_PATH, GOOGLE_TOKEN_PATH, GOOGLE_CALENDAR_ID, etc.
    """
    data: Dict[str, Any] = {}
    if os.path.exists(path):
      with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    cfg = AppConfig(**data)

    # Overlay secrets from env (no hardcoding)
    if os.getenv("OPENAI_API_KEY"):
        cfg.openai.api_key = SecretStr(os.environ["OPENAI_API_KEY"])
    if os.getenv("TAVILY_API_KEY"):
        cfg.search.api_key = SecretStr(os.environ["TAVILY_API_KEY"])
    if os.getenv("AWS_PROFILE"): cfg.bedrock.profile = os.environ["AWS_PROFILE"]
    if os.getenv("AWS_REGION"): cfg.bedrock.region = os.environ["AWS_REGION"]
    if os.getenv("OLLAMA_BASE_URL"): cfg.local.base_url = os.environ["OLLAMA_BASE_URL"]
    if os.getenv("GOOGLE_CLIENT_SECRET_PATH"):
        cfg.google_calendar.oauth_client_secret_path = os.environ["GOOGLE_CLIENT_SECRET_PATH"]
    if os.getenv("GOOGLE_TOKEN_PATH"):
        cfg.google_calendar.token_path = os.environ["GOOGLE_TOKEN_PATH"]
    if os.getenv("GOOGLE_CALENDAR_ID"):
        cfg.google_calendar.calendar_id = os.environ["GOOGLE_CALENDAR_ID"]
    if os.getenv("SLACK_WEBHOOK_URL"):
        cfg.slack.webhook_url = SecretStr(os.environ["SLACK_WEBHOOK_URL"])
    if os.getenv("TEAMS_WEBHOOK_URL"):
        cfg.teams.webhook_url = SecretStr(os.environ["TEAMS_WEBHOOK_URL"])
    if os.getenv("SMTP_HOST"): cfg.email.smtp_host = os.environ["SMTP_HOST"]
    if os.getenv("SMTP_PORT"): cfg.email.smtp_port = int(os.environ["SMTP_PORT"])
    if os.getenv("SMTP_USERNAME"): cfg.email.username = os.environ["SMTP_USERNAME"]
    if os.getenv("SMTP_PASSWORD"): cfg.email.password = SecretStr(os.environ["SMTP_PASSWORD"])
    if os.getenv("SMTP_FROM_ADDRESS"): cfg.email.from_address = os.environ["SMTP_FROM_ADDRESS"]

    return cfg

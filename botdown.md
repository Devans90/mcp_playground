# FASTMCP PERSONAL ASSISTANT — LLM-ORIENTED SPEC (HIGH LEVEL)

## PURPOSE
- Provide a **tool-using personal assistant** via an MCP-compatible server.
- Route among **OpenAI**, **AWS Bedrock**, and **local (Ollama)** models.
- Expose a stable set of **tools** (web search, notes, tasks, calendar, files, RAG, comms).
- Enforce **consent** for cost-incurring and action-taking tools.
- Serve over **FastAPI** with optional **Dash UI**; MCP registration layer planned.

---

## GLOBAL CONTRACTS

### Message schema
```json
{
  "role": "system | user | assistant | tool",
  "content": "string"
}
Tool call envelope (internal)

{
  "name": "tool_name",
  "args": { "k": "v", "...": "..." }
}
AssistantResponse (internal)

{
  "messages": [ { "role": "...", "content": "..." } ],
  "tool_calls": [ { "name": "...", "args": { } } ],
  "finish_reason": "stop | length | tool_budget | error | not_implemented",
  "usage_tokens": 123,
  "latency_ms": 42
}
MODEL ROUTING
Providers
openai → default route: o4-mini (configurable)

bedrock → placeholder until target model chosen

local (Ollama) → base_url from config

Route object

{
  "provider": "openai | bedrock | local",
  "model": "string",
  "temperature": 0.2,
  "max_tokens": null,
  "reasoning": false
}
Selection policy
If a task_hint matches routing_rules.by_task[hint], use that route.

Else use default_route.

Embeddings use vector.embedding_model unless overridden.

CONSENT & COST POLICY
Reads are always allowed when permissions.always_allow_reads = true.

Cost-incurring / action tools require consent when permissions.require_consent_for_costs = true.

Autonomy: must ask before actions; toggleable in config for future.

Granted consent may be cached per-session/tool.

Costy tools (default):

tool_web_search, tool_summarize, tool_rag_index_texts,

tool_calendar_add, tool_email_send, tool_slack_post, tool_teams_post.

LIMITS

{
  "limits": {
    "per_request_max_tokens": 4000,
    "per_request_timeout_s": 20,
    "max_tool_calls_per_turn": 4
  }
}
Enforce hard stop if any limit is hit; set finish_reason = "tool_budget" or "length" accordingly.

CONFIGURATION (YAML + .env overlay)
AppConfig (keys)
yaml
Copy
Edit
server:
  transport: both | http | stdio
  host: 0.0.0.0
  port: 8080
  enable_dash: true
permissions:
  consent_mode: require | auto
  sandbox_root: ./sandbox
  always_allow_reads: true
  require_consent_for_costs: true
openai:
  api_key: env(OPENAI_API_KEY)
  base_url: null
bedrock:
  region: env(AWS_REGION)
  profile: env(AWS_PROFILE)
local:
  base_url: env(OLLAMA_BASE_URL)
vector:
  backend: chroma | sqlite
  chroma_path: ./data/chroma
  sqlite_path: ./data/embeddings.sqlite3
  embedding_model: text-embedding-3-small
storage:
  sqlite_path: ./data/app.sqlite3
observability:
  json_logs: true
  opentelemetry_enabled: true
  service_name: fastmcp-assistant
search:
  provider: tavily
  api_key: env(TAVILY_API_KEY)
  custom_base_url: null
google_calendar:
  enabled: true
  oauth_client_secret_path: ./secrets/google_client_secret.json
  token_path: ./secrets/google_token.json
  calendar_id: primary
email:
  smtp_host: null
  smtp_port: 587
  username: null
  password: null
  from_address: null
  tls: true
slack:
  webhook_url: null
teams:
  webhook_url: null
limits: { ... }            # see LIMITS
default_route: { ... }     # see MODEL ROUTING
routing_rules:
  by_task:
    summarize: { provider: openai, model: o4-mini }
Secrets come from .env and override YAML.

STORAGE & INDEXING
Structured: SQLite at storage.sqlite_path for notes/tasks/events.

Vector: Chroma persistent client at vector.chroma_path (default); memory fallback.

Namespaces/partitions: collections named default, work, personal (extensible).

TOOL SURFACE (MCP-intent)
Return types are summarized; actual JSON objects follow Pydantic schemas in code.
consent: required or not_required (given current policy).
side_effects: "none" | "network" | "writes".

Information & RAG
tool_web_search(query: str, k: int=5) → [{"title","url","snippet"}]

provider: Tavily

consent: required (cost)

side_effects: network

tool_retrieve_url(url: str) → text

consent: not_required

side_effects: network

tool_summarize(text: str, route?: ModelRoute) → summary_text

consent: required (model usage)

side_effects: network (unless local route)

tool_rag_index_texts(texts: [str], metadatas?: [obj]) → int count

consent: required (model/vector cost if embeddings are remote; allowed by policy)

side_effects: writes (vector store)

tool_rag_search(query: str, k: int=5) → [{"text","score","metadata"}]

consent: not_required

side_effects: none

Personal data (local)
tool_notes_create(title: str, body: str, tags?: [str]) → Note

consent: not_required

side_effects: writes (SQLite)

tool_notes_list(query?: str, tag?: str) → [Note]

consent: not_required

side_effects: none

tool_tasks_create(title: str, due_iso?: str) → TaskItem

consent: not_required

side_effects: writes (SQLite)

tool_tasks_list(status?: "todo"|"done") → [TaskItem]

consent: not_required

side_effects: none

Calendar (Google)
tool_calendar_add(title: str, start_iso: str, end_iso: str, attendees?: [str], location?: str) → CalendarEvent

consent: required

side_effects: network (Google Calendar write)

tool_calendar_list(start_iso?: str, end_iso?: str) → [CalendarEvent]

consent: not_required (read)

side_effects: network

System & files
tool_file_read(path: str) → text

sandboxed under permissions.sandbox_root

consent: not_required

side_effects: none

tool_file_write(path: str, content: str) → abs_path

sandboxed

consent: not_required (no cost; still a write)

side_effects: writes (disk)

tool_calculator(expression: str) → string result

consent: not_required

side_effects: none

Communications (disabled by default; require secrets)
tool_email_send(to: [str], subject: str, body: str, cc?: [str], bcc?: [str]) → "ok" | error

consent: required

side_effects: network

tool_slack_post(message: str, channel?: str) → "ok"

consent: required

side_effects: network

tool_teams_post(message: str) → "ok"

consent: required

side_effects: network

UX niceties (server-only)
tool_clipboard_set(text: str) → bool (may no-op on server)

consent: not_required

side_effects: local OS (if supported)

tool_notify(title: str, body: str) → bool (server-only no-op)

consent: not_required

side_effects: none

ORCHESTRATION LOOP (ABRIDGED PSEUDOCODE)
css
Copy
Edit
on run_assistant(user_message, session_id):
  sys_prompt := describe tools, consent, limits
  messages := [sys, user]
  route := router.select_route(task_hint=None)

  for step in 1..limits.max_tool_calls_per_turn:
    resp := router.complete(messages, route)
    append(resp.assistant_message)
    if resp.tool_calls is empty: break

    for call in resp.tool_calls:
      if consent.needs_consent(call.name, call.args):
        ask_user_for_consent(call)         # produce assistant question
        return partial_response            # wait for user approval
      result := dispatch_tool(call)        # sandbox + policy checks
      messages.append({role:"tool", content: serialize(result)})

  finalize with finish_reason; enforce token/timeout budgets
HTTP SURFACE (FastAPI)
GET /healthz → { "ok": true }

GET /config → redacted config JSON (secrets masked)

POST /chat → body: { "messages": [Message, ...] } → AssistantResponse

GET /dash → optional Dash UI (read-only listing for notes/tasks; can be extended)

MCP registration endpoint(s) are planned; exact bindings depend on FastMCP version.

OBSERVABILITY
JSON logs (structured).

OpenTelemetry spans around provider calls and tool executions.

Minimal metrics: tokens, latency, tool-call counts, consent prompts issued.

SAFETY
File operations sandboxed to permissions.sandbox_root.

PII redaction pass before logging outbound text.

Calendar/email/slack/teams disabled until secrets exist.

Bedrock adapter is a stub until a specific model is selected.

LLM EXECUTION GUIDELINES
Never assume missing details. If arguments for a tool are incomplete, ask the user.

Respect consent policy. For any tool in the “costy” set, request consent before executing.

Prefer local reads over network when possible (e.g., use notes/tasks/events first).

Cite sources by returning the url fields from tool_web_search results in your response content.

Keep iterations bounded. Do not exceed limits.max_tool_calls_per_turn without explicit user approval.

Calendar writes must confirm: title, start_iso, end_iso, and attendees; echo back a summary before execution.

Vector indexing: only index with explicit user request or after consent.

Routing: use routing_rules.by_task if your intent matches a known hint; otherwise default route.

Timeout awareness: if operations risk exceeding per_request_timeout_s, propose a smaller batch or ask to proceed.

Server environment: avoid UI/OS assumptions; tool_notify is a no-op, tool_clipboard_set may return false.

EXAMPLES (MACHINE-STYLE)
Example A — Summarize a URL with citations
tool_retrieve_url({ url }) → plaintext

Request consent for tool_summarize (cost) → if approved:

tool_summarize({ text }) → summary

Optionally tool_web_search({ query: site:title }) for corroboration (consent) → add citations

Example B — Create calendar event
Ask user for: title, start_iso, end_iso, attendees?, location?

Confirm summary and request consent

tool_calendar_add({...}) → CalendarEvent

Reflect created event details back to user

Example C — Personal note and RAG
tool_notes_create({ title, body, tags })

(Optional) tool_rag_index_texts({ texts: [body], metadatas: [{title, tags}] }) with consent

Later: tool_rag_search({ query }) → passages

STATE & ERROR POLICY
Partial failures: return assistant message with error summary and next action suggestion.

Missing secrets: tools return clear errors: "not configured"; assistant should ask user to add secret.

Unsupported: bedrock operations return finish_reason="not_implemented" until configured.

MCP (INTENT)
Tools listed above will be registered under the same names for MCP.

Resources/Prompts: optional presets (e.g., “summarize”, “plan-day”) may be added later.

Transport: stdio and/or HTTP per config.

DEFAULT ROUTING HINTS
summarize → OpenAI o4-mini

embed → vector.embedding_model (OpenAI by default)

Fallback: default_route

COMPLETION STYLE
Default tone: concise, explicit steps; ask clarifying questions when required arguments are missing.

Include action previews before consent-requiring calls.

makefile
Copy
Edit

::contentReference[oaicite:0]{index=0}
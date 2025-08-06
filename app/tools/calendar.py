from __future__ import annotations
from typing import Optional, List
from datetime import datetime
import uuid
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from ..config import AppConfig
from ..storage.memory_store import CalendarEvent

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def _get_gcal_service(cfg: AppConfig):
    if not cfg.google_calendar.enabled:
        raise RuntimeError("Google Calendar is disabled.")
    creds = None
    if cfg.google_calendar.token_path and isinstance(cfg.google_calendar.token_path, str):
        try:
            creds = Credentials.from_authorized_user_file(cfg.google_calendar.token_path, SCOPES)
        except Exception:
            creds = None
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(cfg.google_calendar.oauth_client_secret_path, SCOPES)
        creds = flow.run_local_server(port=0)
        with open(cfg.google_calendar.token_path, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    return build("calendar", "v3", credentials=creds)

def tool_calendar_add(cfg: AppConfig, title: str, start_iso: str, end_iso: str,
                      attendees: Optional[List[str]] = None, location: Optional[str] = None) -> CalendarEvent:
    service = _get_gcal_service(cfg)
    event = {
        "summary": title,
        "start": {"dateTime": start_iso},
        "end": {"dateTime": end_iso},
    }
    if attendees:
        event["attendees"] = [{"email": a} for a in attendees]
    if location:
        event["location"] = location
    created = service.events().insert(calendarId=cfg.google_calendar.calendar_id or "primary", body=event).execute()
    return CalendarEvent(
        id=created.get("id", str(uuid.uuid4())),
        title=title,
        start_ts=datetime.fromisoformat(start_iso).timestamp(),
        end_ts=datetime.fromisoformat(end_iso).timestamp(),
        attendees=attendees or [],
        location=location,
    )

def tool_calendar_list(cfg: AppConfig, start_iso: Optional[str] = None, end_iso: Optional[str] = None) -> List[CalendarEvent]:
    service = _get_gcal_service(cfg)
    time_min = start_iso
    time_max = end_iso
    events_result = service.events().list(calendarId=cfg.google_calendar.calendar_id or "primary",
                                          timeMin=time_min, timeMax=time_max, singleEvents=True,
                                          orderBy="startTime").execute()
    items = events_result.get("items", [])
    out: List[CalendarEvent] = []
    for e in items:
        start = e["start"].get("dateTime") or e["start"].get("date")
        end = e["end"].get("dateTime") or e["end"].get("date")
        out.append(CalendarEvent(
            id=e.get("id",""),
            title=e.get("summary",""),
            start_ts=datetime.fromisoformat(start).timestamp(),
            end_ts=datetime.fromisoformat(end).timestamp(),
            attendees=[a["email"] for a in e.get("attendees", [])],
            location=e.get("location"),
        ))
    return out
from __future__ import annotations
from typing import List, Optional
import sqlite3
import time
import os
from pydantic import BaseModel
from ..config import AppConfig

class Note(BaseModel):
    id: str
    title: str
    body: str
    tags: List[str]
    created_ts: float
    updated_ts: float

class TaskItem(BaseModel):
    id: str
    title: str
    due_ts: Optional[float] = None
    status: str = "todo"

class CalendarEvent(BaseModel):
    id: str
    title: str
    start_ts: float
    end_ts: float
    attendees: List[str]
    location: Optional[str] = None

class MemoryStore:
    """
    SQLite store for notes/tasks/events. Keeps schema minimal.
    """
    def __init__(self, cfg: AppConfig) -> None:
        self.path = cfg.storage.sqlite_path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self._init_schema()

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS notes (
            id TEXT PRIMARY KEY, title TEXT, body TEXT, tags TEXT,
            created_ts REAL, updated_ts REAL
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY, title TEXT, due_ts REAL, status TEXT
        )""")
        cur.execute("""CREATE TABLE IF NOT EXISTS events (
            id TEXT PRIMARY KEY, title TEXT, start_ts REAL, end_ts REAL,
            attendees TEXT, location TEXT
        )""")
        self.conn.commit()

    def save_note(self, note: Note) -> Note:
        cur = self.conn.cursor()
        cur.execute("REPLACE INTO notes(id,title,body,tags,created_ts,updated_ts) VALUES (?,?,?,?,?,?)",
            (note.id, note.title, note.body, ",".join(note.tags), note.created_ts, note.updated_ts))
        self.conn.commit()
        return note

    def list_notes(self, query: Optional[str] = None, tags: Optional[List[str]] = None) -> List[Note]:
        cur = self.conn.cursor()
        if query:
            cur.execute("SELECT id,title,body,tags,created_ts,updated_ts FROM notes WHERE title LIKE ? OR body LIKE ? ORDER BY updated_ts DESC",
                        (f"%{query}%", f"%{query}%"))
        else:
            cur.execute("SELECT id,title,body,tags,created_ts,updated_ts FROM notes ORDER BY updated_ts DESC")
        rows = cur.fetchall()
        out = []
        for r in rows:
            tag_list = [t for t in (r[3] or "").split(",") if t]
            if tags and not set(tags).issubset(set(tag_list)):
                continue
            out.append(Note(id=r[0], title=r[1], body=r[2], tags=tag_list, created_ts=r[4], updated_ts=r[5]))
        return out

    def save_task(self, task: TaskItem) -> TaskItem:
        cur = self.conn.cursor()
        cur.execute("REPLACE INTO tasks(id,title,due_ts,status) VALUES (?,?,?,?)",
                    (task.id, task.title, task.due_ts, task.status))
        self.conn.commit()
        return task

    def list_tasks(self, status: Optional[str] = None) -> List[TaskItem]:
        cur = self.conn.cursor()
        if status:
            cur.execute("SELECT id,title,due_ts,status FROM tasks WHERE status=? ORDER BY due_ts NULLS LAST", (status,))
        else:
            cur.execute("SELECT id,title,due_ts,status FROM tasks ORDER BY due_ts NULLS LAST")
        rows = cur.fetchall()
        return [TaskItem(id=r[0], title=r[1], due_ts=r[2], status=r[3]) for r in rows]

    def save_event(self, event: CalendarEvent) -> CalendarEvent:
        cur = self.conn.cursor()
        cur.execute("REPLACE INTO events(id,title,start_ts,end_ts,attendees,location) VALUES (?,?,?,?,?,?)",
                    (event.id, event.title, event.start_ts, event.end_ts, ",".join(event.attendees), event.location))
        self.conn.commit()
        return event

    def list_events(self, start_ts: Optional[float] = None, end_ts: Optional[float] = None) -> List[CalendarEvent]:
        cur = self.conn.cursor()
        q = "SELECT id,title,start_ts,end_ts,attendees,location FROM events"
        params = []
        if start_ts is not None and end_ts is not None:
            q += " WHERE start_ts>=? AND end_ts<=?"
            params = [start_ts, end_ts]
        q += " ORDER BY start_ts ASC"
        cur.execute(q, params)
        rows = cur.fetchall()
        return [CalendarEvent(id=r[0], title=r[1], start_ts=r[2], end_ts=r[3],
                              attendees=[a for a in (r[4] or "").split(",") if a],
                              location=r[5]) for r in rows]

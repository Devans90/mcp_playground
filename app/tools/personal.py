from __future__ import annotations
from typing import Optional, List, Dict, Any
import time
import uuid
from ..storage.memory_store import MemoryStore, Note, TaskItem
from ..storage.vector_index import VectorIndex

def tool_summarize(summary_text: str, summarize_fn) -> str:
    """
    Summarize text using a passed-in callable summarize_fn(messages)->str.
    Keeps this decoupled from providers.
    """
    return summarize_fn(summary_text)

def tool_rag_index_texts(index: VectorIndex, texts: List[str], metadatas: Optional[List[Dict[str, Any]]] = None) -> int:
    return index.index_documents(texts, metadatas)

def tool_rag_search(index: VectorIndex, query: str, k: int = 5) -> List[Dict[str, Any]]:
    return index.query(query, k)

def tool_notes_create(store: MemoryStore, title: str, body: str, tags: Optional[List[str]] = None) -> Note:
    now = time.time()
    n = Note(id=str(uuid.uuid4()), title=title, body=body, tags=tags or [], created_ts=now, updated_ts=now)
    return store.save_note(n)

def tool_notes_list(store: MemoryStore, query: Optional[str] = None, tag: Optional[str] = None) -> List[Note]:
    tags = [tag] if tag else None
    return store.list_notes(query=query, tags=tags)

def tool_tasks_create(store: MemoryStore, title: str, due_iso: Optional[str] = None) -> TaskItem:
    due_ts = None
    if due_iso:
        from datetime import datetime
        due_ts = datetime.fromisoformat(due_iso).timestamp()
    t = TaskItem(id=str(uuid.uuid4()), title=title, due_ts=due_ts, status="todo")
    return store.save_task(t)

def tool_tasks_list(store: MemoryStore, status: Optional[str] = None) -> List[TaskItem]:
    return store.list_tasks(status=status)

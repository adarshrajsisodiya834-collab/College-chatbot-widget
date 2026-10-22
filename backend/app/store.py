import json
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .config import DATA_DIR, WIDGET_CONFIGS

_lock = threading.Lock()
SESSIONS = {}
FEEDBACK = []

def now():
    return datetime.now(timezone.utc).isoformat()

def knowledge_path(widget_id):
    return DATA_DIR / f"{widget_id}.json"

def load_items(widget_id):
    path = knowledge_path(widget_id)
    if not path.exists():
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []

def save_items(widget_id, items):
    knowledge_path(widget_id).write_text(
        json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8"
    )

def add_item(item):
    with _lock:
        items = load_items(item["widget_id"])
        item = {
            "id": str(uuid.uuid4()),
            "created_at": now(),
            "updated_at": now(),
            **item
        }
        items.append(item)
        save_items(item["widget_id"], items)
        return item

def create_session(widget_id):
    session_id = "sess_" + uuid.uuid4().hex[:12]
    SESSIONS[session_id] = []
    return session_id

def get_session(session_id):
    return SESSIONS.setdefault(session_id, [])

def add_message(session_id, role, content):
    get_session(session_id).append({"role": role, "content": content, "at": now()})

def add_feedback(data):
    FEEDBACK.append({"id": str(uuid.uuid4()), "created_at": now(), **data})

def get_config(widget_id):
    return WIDGET_CONFIGS.get(widget_id)

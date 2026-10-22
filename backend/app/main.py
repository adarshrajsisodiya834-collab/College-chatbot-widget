import sys
import time
from collections import defaultdict, deque
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse

if __package__ in (None, ""):
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from backend.app.config import ALLOWED_ORIGINS, BASE_DIR
    from backend.app.models import ChatRequest, ChatResponse, FeedbackRequest, KnowledgeItem
    from backend.app.store import add_feedback, add_item, create_session, get_config, get_session, add_message, load_items
    from backend.app.rag import retrieve, scripted_answer
else:
    from .config import ALLOWED_ORIGINS, BASE_DIR
    from .models import ChatRequest, ChatResponse, FeedbackRequest, KnowledgeItem
    from .store import add_feedback, add_item, create_session, get_config, get_session, add_message, load_items
    from .rag import retrieve, scripted_answer

app = FastAPI(title="College Chatbot API", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

RATE_WINDOW = 60
RATE_LIMIT = 30
requests_by_ip = defaultdict(deque)

@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if request.url.path.startswith("/api/v1/chat"):
        ip = request.client.host if request.client else "unknown"
        now = time.time()
        q = requests_by_ip[ip]
        while q and q[0] < now - RATE_WINDOW:
            q.popleft()
        if len(q) >= RATE_LIMIT:
            return JSONResponse(status_code=429, content={"detail": "Too many requests. Please try again later."})
        q.append(now)
    return await call_next(request)

@app.get("/api/v1/health")
def health():
    return {"status": "ok", "engine": "scripted"}

@app.get("/api/v1/widget/{widget_id}/config")
def widget_config(widget_id: str):
    config = get_config(widget_id)
    if not config:
        raise HTTPException(404, "This chatbot is currently unavailable.")
    return config

@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    config = get_config(payload.widget_id)
    if not config:
        raise HTTPException(404, "This chatbot is currently unavailable.")

    session_id = payload.session_id or create_session(payload.widget_id)
    history = get_session(session_id)
    add_message(session_id, "user", payload.message)

    results = retrieve(payload.widget_id, payload.message)
    answer = scripted_answer(payload.message, results, history)

    sources = []
    if config.get("show_sources", True):
        for r in results[:1]:
            sources.append({
                "title": r["title"],
                "type": r["type"],
                "page": r.get("page"),
                "url": r.get("url"),
                "snippet": r["text"][:180].strip()
            })

    add_message(session_id, "assistant", answer)
    return {"answer": answer, "sources": sources, "session_id": session_id}

@app.post("/api/v1/feedback")
def feedback(payload: FeedbackRequest):
    if payload.feedback not in {"up", "down"}:
        raise HTTPException(400, "Feedback must be 'up' or 'down'.")
    if not get_config(payload.widget_id):
        raise HTTPException(404, "Unknown chatbot.")
    add_feedback(payload.model_dump())
    return {"status": "received"}

@app.post("/api/v1/knowledge")
def add_knowledge(payload: KnowledgeItem):
    if not get_config(payload.widget_id):
        raise HTTPException(404, "Unknown chatbot.")
    return add_item(payload.model_dump())

@app.get("/api/v1/knowledge/{widget_id}")
def list_knowledge(widget_id: str):
    if not get_config(widget_id):
        raise HTTPException(404, "Unknown chatbot.")
    return load_items(widget_id)

@app.get("/widget.js")
def widget_js():
    return FileResponse(BASE_DIR / "widget" / "widget.js", media_type="application/javascript")


@app.get("/icon.png")
def icon_png():
    return FileResponse(BASE_DIR / "backend" / "icon.png", media_type="image/png")

@app.get("/")
def root():
    return FileResponse(BASE_DIR / "demo" / "index.html", media_type="text/html")

from typing import Optional
from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    widget_id: str
    session_id: Optional[str] = None
    message: str = Field(min_length=1, max_length=4000)

class ChatResponse(BaseModel):
    answer: str
    sources: list[dict] = []
    session_id: str

class FeedbackRequest(BaseModel):
    widget_id: str
    session_id: str
    message_id: Optional[str] = None
    feedback: str
    category: Optional[str] = None

class KnowledgeItem(BaseModel):
    widget_id: str
    title: str
    content: str
    type: str = "text"
    source_url: Optional[str] = None
    page: Optional[int] = None

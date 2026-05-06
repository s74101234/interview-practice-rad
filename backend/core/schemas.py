from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    message: str


class ChatMessage(BaseModel):
    role: str
    content: str
    tool: Optional[str] = None


class ChatResponse(BaseModel):
    message: ChatMessage


class UploadResponse(BaseModel):
    job_id: str
    filename: str


class SearchResult(BaseModel):
    text: str
    source: str
    page: str
    score: float

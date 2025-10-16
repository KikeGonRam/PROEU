from typing import Optional
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str
    resolved: bool
    source: Optional[str] = None
    admin_email: Optional[str] = None


class AdaptRequest(BaseModel):
    snippet: str


class AdaptResponse(BaseModel):
    adapted_answer: str


class EscalateRequest(BaseModel):
    original_message: str
    user_email: Optional[str] = None


class EscalateResponse(BaseModel):
    ticket_id: str
    admin_email: Optional[str] = None

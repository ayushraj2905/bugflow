from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.chat_assistant_service import ChatAssistantService

router = APIRouter(prefix="/api/v1/chat", tags=["AI Chatbot & Project Assistant"])

class ChatMessageRequest(BaseModel):
    message: str

class ChatMessageResponse(BaseModel):
    reply: str
    suggestions: List[str] = []

@router.post("/", response_model=ChatMessageResponse)
@router.post("", response_model=ChatMessageResponse)
def send_chat_message(req: ChatMessageRequest, db: Session = Depends(get_db)):
    if not req.message or not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    res = ChatAssistantService.get_response(req.message, db)
    return res

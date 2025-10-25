from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid
from app.orchestrator import ChatOrchestrator
from app.groq_client import GroqAgent
from app.firebase_db import FirebaseDatabase

router = APIRouter()

# Initialize components
db_client = FirebaseDatabase()
agent_client = GroqAgent()
orchestrator = ChatOrchestrator(db_client=db_client, agent_client=agent_client)

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@router.post("/", response_model=ChatResponse)
async def chat_with_ai(chat_message: ChatMessage):
    """
    AI asistanıyla sohbet et.
    """
    try:
        # Session ID oluştur veya kullan
        session_id = chat_message.session_id or f"session_{uuid.uuid4().hex[:8]}"
        
        # Orchestrator ile mesajı işle
        ai_response = orchestrator.handle_message(session_id, chat_message.message)
        
        return ChatResponse(
            response=ai_response,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat hatası: {str(e)}")

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Belirli bir session'ın chat geçmişini getir.
    """
    try:
        messages = db_client.get_chat_history(session_id)
        return {"session_id": session_id, "messages": messages}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat geçmişi getirme hatası: {str(e)}")

@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Belirli bir session'ın chat geçmişini temizle.
    """
    try:
        # Firebase'de chat history'yi temizle
        db_client.db.collection('chat_history').document(session_id).delete()
        return {"message": f"Chat geçmişi temizlendi: {session_id}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat geçmişi temizleme hatası: {str(e)}")

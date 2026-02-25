from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional
from backend.app.schemas.qa import ChatRequest, ChatResponse, AdaptScriptRequest, AdaptScriptResponse
from backend.app.schemas.session import StartSessionRequest, SessionResponse, PreviewStatusResponse
from backend.app.services.qa.service import QAService
from backend.app.services.session.manager import SessionManager
from backend.app.services.student.state_manager import StudentStateManager

router = APIRouter()

# Dependency for QAService (Singleton or Per-Request)
def get_qa_service():
    return QAService()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    qa_service: QAService = Depends(get_qa_service)
):
    """
    Core Chat Interface for QA and Teacher Interaction.
    
    Logic:
    1. Check Session Validity.
    2. Route Intent (QA vs Feedback vs Control).
    3. Execute Logic (RAG Retrieval or Teacher Agent Supplement).
    4. Update Student State (Confusion Count).
    """
    try:
        # Validate Session
        if not request.session_id:
            # For demo, auto-create a session if missing or handle as stateless
            request.session_id = "demo_session"
            
        # Call QA Service
        response = await qa_service.answer_question(request, user_id="student_001") # Mock user_id for demo
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/script/adapt", response_model=AdaptScriptResponse)
async def adapt_script(
    request: AdaptScriptRequest,
    qa_service: QAService = Depends(get_qa_service)
):
    """
    Adapt a lecture script segment based on student profile.
    Used for "Style Transfer" demo after student interaction.
    """
    try:
        response = await qa_service.adapt_script(request, user_id="student_001")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/start", response_model=SessionResponse)
async def start_session(
    request: StartSessionRequest,
    user_id: str = "student_001" # In real app, get from Auth token
):
    """
    Initialize a new learning session.
    """
    try:
        return SessionManager.create_session(request, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}/preview", response_model=Optional[PreviewStatusResponse])
async def get_preview_status(session_id: str):
    """
    Get the status of a video preview generation task.
    """
    status = SessionManager.get_preview_status(session_id)
    if not status:
        raise HTTPException(status_code=404, detail="Session or Task not found")
    return status

@router.post("/session/feedback/reset")
async def reset_confusion(session_id: str):
    """
    Manually reset confusion count (e.g., when student says "I get it now").
    """
    StudentStateManager.reset_confusion(session_id)
    return {"status": "success", "message": "Confusion count reset."}

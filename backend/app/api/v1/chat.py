from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from typing import Optional
import json
from backend.app.schemas.qa import ChatRequest, ChatResponse, AdaptScriptRequest, AdaptScriptResponse
from backend.app.schemas.session import StartSessionRequest, SessionResponse, PreviewStatusResponse
from backend.app.services.qa.service import QAService
from backend.app.services.session.manager import SessionManager
from backend.app.services.student.state_manager import StudentStateManager

router = APIRouter()

# Dependency for QAService (Singleton or Per-Request)
def get_qa_service():
    return QAService()

async def mock_edge_filter(query: str) -> tuple[bool, str]:
    """
    [Mock] Edge Computing Layer:
    Simulate intent classification and sensitive content filtering at the Edge (e.g., Cloudflare Worker).
    Returns (is_allowed, reason).
    """
    # Simulate low-latency check
    if any(keyword in query.lower() for keyword in ["sql injection", "rm -rf", "<script>"]):
        return False, "Edge Security: Malicious content detected."
    return True, "Passed"

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    qa_service: QAService = Depends(get_qa_service)
):
    """
    WebSocket Endpoint for Real-time Chat.
    Supports streaming response, typewriter effect, and multimedia push.
    """
    await websocket.accept()
    try:
        while True:
            # 1. Receive JSON Message
            data = await websocket.receive_text()
            try:
                message_data = json.loads(data)
                # Expecting format: {"query": "...", "session_id": "...", "current_path": "..."}
                
                # [Mock] Edge Computing Filter
                is_allowed, reason = await mock_edge_filter(message_data.get("query", ""))
                if not is_allowed:
                     await websocket.send_json({"type": "error", "content": reason})
                     continue

                request = ChatRequest(**message_data)
            except Exception as e:
                await websocket.send_json({"type": "error", "content": "Invalid JSON format or schema."})
                continue
                
            # 2. Process & Stream Response
            try:
                # Use a mocked user_id for demo
                user_id = "student_001" 
                
                # Call streaming service
                async for chunk in qa_service.stream_answer_question(request, user_id=user_id):
                    # chunk is already a JSON string from service
                    await websocket.send_text(chunk)
                    
            except Exception as e:
                await websocket.send_json({"type": "error", "content": str(e)})
                
    except WebSocketDisconnect:
        print("Client disconnected")

@router.get("/sse")
async def sse_endpoint(
    query: str,
    session_id: Optional[str] = None,
    current_path: Optional[str] = None,
    qa_service: QAService = Depends(get_qa_service)
):
    """
    Server-Sent Events Endpoint for Real-time Chat.
    """
    # [Mock] Edge Computing Filter
    is_allowed, reason = await mock_edge_filter(query)
    if not is_allowed:
         # For SSE, we can yield an error event and close
         async def block_generator():
             yield f"data: {json.dumps({'type': 'error', 'content': reason})}\n\n"
         return StreamingResponse(block_generator(), media_type="text/event-stream")

    request = ChatRequest(query=query, session_id=session_id, current_path=current_path)
    
    async def event_generator():
        try:
            async for chunk in qa_service.stream_answer_question(request, user_id="student_001"):
                # SSE format: data: <payload>\n\n
                yield f"data: {chunk}\n\n"
        except Exception as e:
            error_data = json.dumps({"type": "error", "content": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

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

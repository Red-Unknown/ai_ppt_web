from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Body
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
import json
from backend.app.schemas.qa import (
    ChatRequest, ChatResponse, AdaptScriptRequest, AdaptScriptResponse,
    ChatSessionResponse, ChatMessage, TruncateRequest
)
from backend.app.schemas.session import StartSessionRequest, SessionResponse, PreviewStatusResponse
from backend.app.services.qa.service import QAService
from backend.app.services.session.manager import SessionManager
from backend.app.services.student.state_manager import StudentStateManager
from backend.app.utils.cache import local_cache

router = APIRouter()

# --- REST API for Chat Sessions ---

@router.get("/sessions", response_model=list[ChatSessionResponse])
async def get_sessions():
    """Get all chat sessions for the current user."""
    # Mock user_id
    user_id = "student_001"
    return SessionManager.get_user_sessions(user_id)

@router.post("/sessions")
async def create_session():
    """Create a new chat session."""
    user_id = "student_001"
    session_id = SessionManager.create_chat_session(user_id)
    return {"session_id": session_id}

@router.get("/history/{session_id}", response_model=list[ChatMessage])
async def get_history(session_id: str):
    """Get chat history for a specific session."""
    return SessionManager.get_chat_history(session_id)

@router.post("/history/{session_id}/truncate")
async def truncate_history(session_id: str, request: TruncateRequest):
    """Truncate chat history from a specific index."""
    success = SessionManager.truncate_history(session_id, request.index)
    if not success:
        raise HTTPException(status_code=400, detail="Invalid index or session")
    return {"status": "success"}

# --- Learning Session API ---

@router.post("/session/start", response_model=SessionResponse)
async def start_learning_session(request: StartSessionRequest):
    """
    Start a new Learning or Preview session.
    """
    user_id = "student_001"
    return SessionManager.create_session(request, user_id)

@router.get("/session/{session_id}/preview", response_model=PreviewStatusResponse)
async def get_session_preview(session_id: str):
    """
    Get the status of a video preview generation task.
    """
    status = SessionManager.get_preview_status(session_id)
    if not status:
        # Return a default status or 404
        # Since the frontend polls this, 404 might break the poller if not handled gracefully.
        # But SessionManager.get_preview_status returns None if not found.
        raise HTTPException(status_code=404, detail="Preview task not found")
    return status

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
                
                # Save User Message
                if request.session_id:
                    SessionManager.add_message(request.session_id, "user", request.query)

                full_response_content = ""
                response_sources = []

                # Call streaming service
                async for chunk in qa_service.stream_answer_question(request, user_id=user_id):
                    # chunk is already a JSON string from service
                    await websocket.send_text(chunk)
                    
                    # Accumulate for history
                    try:
                        chunk_data = json.loads(chunk)
                        if chunk_data.get("type") == "token":
                            full_response_content += chunk_data.get("content", "")
                        elif chunk_data.get("type") == "sources":
                            response_sources = chunk_data.get("data", [])
                    except:
                        pass
                
                # Save Assistant Message
                if request.session_id and full_response_content:
                    SessionManager.add_message(request.session_id, "assistant", full_response_content, sources=response_sources)

            except Exception as e:
                await websocket.send_json({"type": "error", "content": str(e)})
                
    except WebSocketDisconnect:
        print("Client disconnected")

@router.get("/sse")
async def sse_endpoint(
    query: str,
    session_id: Optional[str] = None,
    current_path: Optional[str] = None,
    model: Optional[str] = "deepseek",
    prompt_style: Optional[str] = "default",
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

    request = ChatRequest(
        query=query, 
        session_id=session_id, 
        current_path=current_path,
        model=model,
        prompt_style=prompt_style
    )
    
    async def event_generator():
        try:
            async for chunk in qa_service.stream_answer_question(request, user_id="student_001"):
                # SSE format: data: <payload>\n\n
                yield f"data: {chunk}\n\n"
        except Exception as e:
            error_data = json.dumps({"type": "error", "content": str(e)})
            yield f"data: {error_data}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@router.get("/metrics")
async def get_metrics():
    """
    Get Cache Hit Rate and Performance Metrics.
    """
    return JSONResponse(content=local_cache.get_metrics())

@router.post("/config/reload")
async def reload_config(qa_service: QAService = Depends(get_qa_service)):
    """
    Hot Reload QAService Configuration.
    """
    try:
        qa_service.reload_config()
        return {"status": "success", "message": "Configuration reloaded."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

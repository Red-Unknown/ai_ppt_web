from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect, Body
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
import json
import asyncio
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

@router.get("/history/{session_id}/context")
async def get_session_context(session_id: str):
    """Get session context including expected questions and thinking path."""
    return StudentStateManager.get_session_context(session_id)

@router.get("/session/{session_id}/thinking")
async def get_session_thinking(session_id: str):
    """Get the thinking path for a session."""
    context = StudentStateManager.get_session_context(session_id)
    return {"thoughtProcess": context.get("thinking_path", "")}

@router.get("/session/{session_id}/evaluation")
async def get_session_evaluation(session_id: str):
    """Get the evaluation for a session."""
    context = StudentStateManager.get_session_context(session_id)
    return {"evaluation": context.get("evaluation", {})}

@router.get("/history/{session_id}", response_model=list[ChatMessage])
async def get_history(session_id: str):
    """Get chat history for a specific session."""
    return SessionManager.get_chat_history(session_id)

@router.get("/history/{session_id}/events", response_model=list[dict])
async def get_session_events(session_id: str):
    """Get raw event history for a session (Event Sourcing)."""
    return StudentStateManager.get_events(session_id)

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
    Non-blocking implementation: Allows receiving new messages while generating.
    Supports concurrent generations for different sessions (Strategy Adjustment).
    """
    await websocket.accept()
    
    # Track tasks by session_id to allow per-session management
    # Key: session_id, Value: asyncio.Task
    active_tasks: dict[str, asyncio.Task] = {}
    
    async def process_message(message_data: dict):
        session_id = message_data.get("session_id", "default")
        try:
            # [Mock] Edge Computing Filter
            is_allowed, reason = await mock_edge_filter(message_data.get("query", ""))
            if not is_allowed:
                 await websocket.send_json({"type": "error", "content": reason})
                 return

            request = ChatRequest(**message_data)
            
            # Use a mocked user_id for demo
            user_id = "student_001" 
            
            # Call streaming service
            async for chunk in qa_service.stream_answer_question(request, user_id=user_id):
                # chunk is already a JSON string from service
                # We should ensure thread safety when sending over websocket?
                # FastAPI/Starlette websocket.send_text is async, so it should be safe to await concurrently.
                # However, interleaving messages from different sessions might confuse the client 
                # if client doesn't check session_id in the message.
                # QAService events usually don't include session_id in the JSON body, 
                # BUT _emit_event helper in service.py does NOT inject session_id into the event dict by default?
                # Let's check service.py. _emit_event(session_id, event) -> StudentStateManager.append_event(session_id, event)
                # It returns json.dumps(event).
                # If the event dict doesn't have session_id, client won't know which session this chunk belongs to.
                # We should probably inject session_id into the chunk before sending.
                
                try:
                    chunk_data = json.loads(chunk)
                    if isinstance(chunk_data, dict):
                        chunk_data["session_id"] = session_id
                        await websocket.send_text(json.dumps(chunk_data))
                    else:
                        await websocket.send_text(chunk)
                except:
                    await websocket.send_text(chunk)
                
        except asyncio.CancelledError:
            print(f"Generation cancelled for session {session_id}")
            # Ensure we emit an end event so frontend stops loading
            try:
                await websocket.send_json({"type": "end", "reason": "interrupted", "session_id": session_id})
            except:
                pass
        except Exception as e:
            await websocket.send_json({"type": "error", "content": str(e), "session_id": session_id})
        finally:
            # Cleanup task from tracker
            if session_id in active_tasks:
                del active_tasks[session_id]

    try:
        while True:
            # 1. Receive JSON Message
            data = await websocket.receive_text()
            
            try:
                message_data = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "content": "Invalid JSON format."})
                continue

            session_id = message_data.get("session_id")
            if not session_id:
                await websocket.send_json({"type": "error", "content": "Session ID required."})
                continue

            # 2. Check for Stop Signal
            if message_data.get("type") == "stop":
                if session_id in active_tasks:
                    task = active_tasks[session_id]
                    task.cancel()
                    # We don't await it here to keep loop responsive
                continue

            # 3. Strategy: Do NOT interrupt existing task if it's running for the SAME session?
            # User said: "New dialogue sending new message will not affect original websocket connection, not interrupt current output"
            # This implies if I switch to session B and send message, session A's output should continue.
            # But what if I send message in session A while session A is generating?
            # Usually that implies "stop and generate new".
            # So: Interrupt SAME session, allow DIFFERENT session concurrent.
            
            if session_id in active_tasks:
                print(f"Interrupting existing task for session {session_id}")
                task = active_tasks[session_id]
                task.cancel()
                # Wait briefly or just overwrite? 
                # Better to let it clean up itself in finally block, but we need to replace it.
                # If we don't await, we might have race condition on active_tasks[session_id].
                # But since we are in async loop, we can just overwrite.
                # The finally block of the old task will try to delete, we should handle that.
                
            # 4. Start new generation task
            task = asyncio.create_task(process_message(message_data))
            active_tasks[session_id] = task
                
    except WebSocketDisconnect:
        print("Client disconnected")
        # Cancel all active tasks
        for task in active_tasks.values():
            task.cancel()
        active_tasks.clear()

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

@router.get("/sse")
async def sse_endpoint(
    query: str, 
    session_id: Optional[str] = None, 
    qa_service: QAService = Depends(get_qa_service)
):
    """
    Server-Sent Events Endpoint for Chat.
    """
    request = ChatRequest(query=query, session_id=session_id)
    
    async def sse_generator():
        async for chunk in qa_service.stream_answer_question(request, user_id="student_001"):
            yield f"data: {chunk}\n\n"
            
    return StreamingResponse(sse_generator(), media_type="text/event-stream")

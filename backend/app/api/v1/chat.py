from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
import json
from backend.app.schemas.qa import ChatRequest, ChatResponse, AdaptScriptRequest, AdaptScriptResponse
from backend.app.schemas.session import StartSessionRequest, SessionResponse, PreviewStatusResponse
from backend.app.services.qa.service import QAService
from backend.app.services.session.manager import SessionManager
from backend.app.services.student.state_manager import StudentStateManager
from backend.app.utils.cache import local_cache

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

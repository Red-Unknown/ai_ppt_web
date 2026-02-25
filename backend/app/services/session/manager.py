import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
from backend.app.schemas.session import (
    SessionStatus, SessionMode, StartSessionRequest, 
    SessionResponse, PreviewStatusResponse
)

# In-memory storage for demonstration (Replace with Redis/DB)
_SESSIONS: Dict[str, Dict] = {}
_TASKS: Dict[str, Dict] = {}

class SessionManager:
    """
    Manages user sessions for learning and preview generation.
    """
    
    @staticmethod
    def create_session(request: StartSessionRequest, user_id: str) -> SessionResponse:
        session_id = f"sess_{uuid.uuid4().hex[:8]}"
        
        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "course_id": request.course_id,
            "mode": request.mode,
            "status": SessionStatus.ACTIVE,
            "created_at": datetime.now(),
            "current_node": request.target_node_id,
            "history": []
        }
        
        _SESSIONS[session_id] = session_data
        
        response = SessionResponse(
            session_id=session_id,
            status=SessionStatus.ACTIVE
        )

        if request.mode == SessionMode.PREVIEW:
            # Trigger async task for preview generation
            task_id = f"task_gen_{uuid.uuid4().hex[:8]}"
            _TASKS[task_id] = {
                "status": SessionStatus.PROCESSING,
                "progress": 0,
                "session_id": session_id,
                "started_at": datetime.now()
            }
            response.task_id = task_id
            response.message = "Video preview generation task submitted."
            response.status = SessionStatus.PROCESSING
        else:
            response.message = "Learning session started."
            response.start_node = {"node_id": request.target_node_id, "title": "Introduction"}

        return response

    @staticmethod
    def get_preview_status(session_id: str) -> Optional[PreviewStatusResponse]:
        # Find task associated with session (In real app, query by session_id)
        task = next((t for t in _TASKS.values() if t["session_id"] == session_id), None)
        
        if not task:
            return None
            
        # Simulate progress update
        elapsed = (datetime.now() - task["started_at"]).total_seconds()
        if task["status"] == SessionStatus.PROCESSING:
            task["progress"] = min(100, int(elapsed * 10)) # 10% per second
            if task["progress"] >= 100:
                task["status"] = SessionStatus.COMPLETED
                task["video_url"] = f"https://cdn.example.com/previews/{session_id}.mp4"
                task["expires_at"] = datetime.now() + timedelta(hours=1)
        
        return PreviewStatusResponse(
            status=task["status"],
            progress=task.get("progress"),
            video_url=task.get("video_url"),
            expires_at=task.get("expires_at"),
            cached=False
        )

    @staticmethod
    def get_session(session_id: str) -> Optional[Dict]:
        return _SESSIONS.get(session_id)

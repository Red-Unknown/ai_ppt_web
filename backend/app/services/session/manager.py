import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
from backend.app.schemas.session import (
    SessionStatus, SessionMode, StartSessionRequest, 
    SessionResponse, PreviewStatusResponse
)
from backend.app.schemas.qa import ChatMessage, ChatSessionResponse
from backend.app.services.student.state_manager import StudentStateManager

# In-memory storage for demonstration (Replace with Redis/DB)
_SESSIONS: Dict[str, Dict] = {}
# _CHAT_SESSIONS is now a fallback if StudentStateManager is not used for some reason,
# but we should prefer StudentStateManager for persistence.
_CHAT_SESSIONS: Dict[str, Dict] = {}  
_TASKS: Dict[str, Dict] = {}

class SessionManager:
    """
    Manages user sessions for learning and preview generation.
    Now delegates chat history to StudentStateManager (Redis-backed).
    """
    
    # --- General Chat Methods (New) ---
    
    @staticmethod
    def create_chat_session(user_id: str) -> str:
        # Use StudentStateManager to create session
        return StudentStateManager.create_session(user_id)

    @staticmethod
    def get_user_sessions(user_id: str) -> list[ChatSessionResponse]:
        # Use StudentStateManager to get sessions
        sessions_data = StudentStateManager.get_user_sessions(user_id)
        sessions = []
        for s in sessions_data:
            sessions.append(ChatSessionResponse(
                id=s["id"],
                title=s["title"],
                updated_at=s["updated_at"]
            ))
        return sessions

    @staticmethod
    def get_chat_history(session_id: str) -> list[ChatMessage]:
        # Use StudentStateManager to get history
        # It returns list of dicts, we convert to ChatMessage
        history_data = StudentStateManager.get_history(session_id, limit=100)
        return [ChatMessage(**msg) for msg in history_data]

    @staticmethod
    def add_message(session_id: str, role: str, content: str, sources: list = None):
        # Delegate to StudentStateManager
        # Note: reasoning/tool_calls are handled by QAService calling StudentStateManager.add_history directly
        # This method might be used by other components, so we keep it compatible
        StudentStateManager.add_history(session_id, role, content)

    @staticmethod
    def reset_search_quota(session_id: str):
        """Reset search quota for a new turn (Q&A pair)."""
        # We can store this in StudentStateManager too if needed, 
        # or keep using _CHAT_SESSIONS for ephemeral state if it's per-turn
        # For now, let's use the ephemeral dict for quota as it's session-volatile
        session = _CHAT_SESSIONS.get(session_id)
        if not session:
             _CHAT_SESSIONS[session_id] = {"search_used": False}
        else:
            session["search_used"] = False

    @staticmethod
    def try_acquire_search_quota(session_id: str) -> bool:
        """
        Atomic check-and-set for search quota.
        """
        session = _CHAT_SESSIONS.get(session_id)
        if not session:
            _CHAT_SESSIONS[session_id] = {"search_used": False}
            session = _CHAT_SESSIONS[session_id]
            
        if session.get("search_used", False):
            return False
            
        session["search_used"] = True
        return True

    @staticmethod
    def is_search_used(session_id: str) -> bool:
        """Check if web search has been used in this session."""
        session = _CHAT_SESSIONS.get(session_id)
        return session.get("search_used", False) if session else False
    
    @staticmethod
    def calculate_fingerprint(query: str) -> str:
        """Calculate MD5 fingerprint for query normalization."""
        import hashlib
        normalized = query.lower().strip()
        return hashlib.md5(normalized.encode('utf-8')).hexdigest()

    @staticmethod
    def get_cached_docs(session_id: str, query: str) -> Optional[list]:
        """Retrieve cached documents for a query fingerprint."""
        session = _CHAT_SESSIONS.get(session_id)
        if not session:
            return None
        
        fingerprint = SessionManager.calculate_fingerprint(query)
        return session.get("cache", {}).get(fingerprint)

    @staticmethod
    def cache_docs(session_id: str, query: str, docs: list):
        """Cache documents for a query."""
        session = _CHAT_SESSIONS.get(session_id)
        if not session:
            _CHAT_SESSIONS[session_id] = {}
            session = _CHAT_SESSIONS[session_id]
            
        fingerprint = SessionManager.calculate_fingerprint(query)
        if "cache" not in session:
            session["cache"] = {}
        session["cache"][fingerprint] = docs

    @staticmethod
    def truncate_history(session_id: str, index: int) -> bool:
        StudentStateManager.truncate_history(session_id, index)
        return True

    # --- Learning Session Methods (Existing) ---
    
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

import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional
from backend.app.schemas.session import (
    SessionStatus, SessionMode, StartSessionRequest, 
    SessionResponse, PreviewStatusResponse
)
from backend.app.schemas.qa import ChatMessage, ChatSessionResponse

# In-memory storage for demonstration (Replace with Redis/DB)
_SESSIONS: Dict[str, Dict] = {}
_CHAT_SESSIONS: Dict[str, Dict] = {}  # Dedicated for general chat: {session_id: {user_id, title, history: [], updated_at}}
_TASKS: Dict[str, Dict] = {}

class SessionManager:
    """
    Manages user sessions for learning and preview generation.
    """
    
    # --- General Chat Methods (New) ---
    
    @staticmethod
    def create_chat_session(user_id: str) -> str:
        session_id = f"chat_{uuid.uuid4().hex[:8]}"
        now = datetime.now().isoformat()
        
        _CHAT_SESSIONS[session_id] = {
            "id": session_id,
            "user_id": user_id,
            "title": "New Chat",
            "updated_at": now,
            "history": [],
            "cache": {},          # Single Chat Cache: {fingerprint: docs}
            "search_used": False  # Web Search Limit Flag
        }
        return session_id

    @staticmethod
    def get_user_sessions(user_id: str) -> list[ChatSessionResponse]:
        sessions = []
        # Sort by updated_at desc
        user_sessions = [s for s in _CHAT_SESSIONS.values() if s["user_id"] == user_id]
        user_sessions.sort(key=lambda x: x["updated_at"], reverse=True)
        
        for s in user_sessions:
            sessions.append(ChatSessionResponse(
                id=s["id"],
                title=s["title"],
                updated_at=s["updated_at"]
            ))
        return sessions

    @staticmethod
    def get_chat_history(session_id: str) -> list[ChatMessage]:
        session = _CHAT_SESSIONS.get(session_id)
        if not session:
            return []
        return [ChatMessage(**msg) for msg in session["history"]]

    @staticmethod
    def add_message(session_id: str, role: str, content: str, sources: list = None):
        session = _CHAT_SESSIONS.get(session_id)
        if not session:
            # Auto-create for simplicity if missing (e.g. dev restart)
            # In prod, this should fail or rely on persistent storage
            now = datetime.now().isoformat()
            _CHAT_SESSIONS[session_id] = {
                "id": session_id,
                "user_id": "student_001", # Fallback user
                "title": "Restored Chat",
                "updated_at": now,
                "history": []
            }
            session = _CHAT_SESSIONS[session_id]
            
        msg = {
            "role": role,
            "content": content,
            "sources": sources or [],
            "timestamp": datetime.now().isoformat()
        }
        session["history"].append(msg)
        session["updated_at"] = msg["timestamp"]
        
        # Update title if it's the first user message
        if role == "user" and len(session["history"]) <= 2:
            # Simple heuristic: first 20 chars
            session["title"] = content[:30] + "..." if len(content) > 30 else content

    @staticmethod
    def reset_search_quota(session_id: str):
        """Reset search quota for a new turn (Q&A pair)."""
        session = _CHAT_SESSIONS.get(session_id)
        if session:
            session["search_used"] = False

    @staticmethod
    def try_acquire_search_quota(session_id: str) -> bool:
        session = _CHAT_SESSIONS.get(session_id)
        if not session:
            return False
        # If 'search_used' key is missing, default to False (unused)
        if session.get("search_used", False):
            return False
        session["search_used"] = True
        return True

    @staticmethod
    def is_search_used(session_id: str) -> bool:
        session = _CHAT_SESSIONS.get(session_id)
        if not session:
            return False
        return session.get("search_used", False)
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
        if session:
            fingerprint = SessionManager.calculate_fingerprint(query)
            if "cache" not in session:
                session["cache"] = {}
            session["cache"][fingerprint] = docs

    @staticmethod
    def try_acquire_search_quota(session_id: str) -> bool:
        """
        Atomic check-and-set for search quota.
        Returns True if quota was acquired (search allowed), False otherwise.
        """
        # In a real Redis/DB scenario, this should be a Lua script or transaction.
        # Here we use a simple lock-like approach for the in-memory dict.
        # Since standard dict operations in Python (CPython) are atomic for single items,
        # we can check and set. But for strict correctness in multi-threaded envs, 
        # we might need a lock. However, FastAPI is async, running in single thread loop 
        # unless using threads.
        
        session = _CHAT_SESSIONS.get(session_id)
        if not session:
            return False
            
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
    def mark_search_used(session_id: str):
        """Mark web search as used for this session."""
        session = _CHAT_SESSIONS.get(session_id)
        if session:
            session["search_used"] = True

    @staticmethod
    def truncate_history(session_id: str, index: int) -> bool:
        session = _CHAT_SESSIONS.get(session_id)
        if not session or index < 0:
            return False
            
        if index < len(session["history"]):
            session["history"] = session["history"][:index]
            session["updated_at"] = datetime.now().isoformat()
            return True
        return False

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

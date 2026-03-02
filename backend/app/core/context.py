
import contextvars
from typing import Optional, Dict, Any, Generator
from contextlib import contextmanager
import uuid

# --- Context Variables Definition ---
# Using separate ContextVars for better isolation and performance than a single dict
session_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("session_id", default=None)
user_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("user_id", default=None)
request_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("request_id", default=None)
trace_id_ctx: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("trace_id", default=None)

# --- Context Management Utilities ---

class AppContext:
    """
    Utility class to manage application context lifecycle.
    """
    
    @staticmethod
    def get_session_id() -> Optional[str]:
        return session_id_ctx.get()

    @staticmethod
    def get_user_id() -> Optional[str]:
        return user_id_ctx.get()

    @staticmethod
    def get_request_id() -> Optional[str]:
        return request_id_ctx.get()

    @staticmethod
    def get_trace_id() -> Optional[str]:
        return trace_id_ctx.get()

    @staticmethod
    @contextmanager
    def scope(session_id: str = None, user_id: str = None, request_id: str = None, trace_id: str = None):
        """
        Context manager to set context variables for a block of code and reset them afterwards.
        Ensures thread-safety and proper cleanup.
        """
        tokens = {}
        
        # Set new values if provided
        if session_id:
            tokens['session_id'] = session_id_ctx.set(session_id)
        if user_id:
            tokens['user_id'] = user_id_ctx.set(user_id)
        
        # Auto-generate request_id if not provided
        if not request_id:
            request_id = f"req_{uuid.uuid4().hex[:8]}"
        tokens['request_id'] = request_id_ctx.set(request_id)
            
        if trace_id:
            tokens['trace_id'] = trace_id_ctx.set(trace_id)
            
        try:
            yield
        finally:
            # Reset all tokens
            if 'trace_id' in tokens:
                trace_id_ctx.reset(tokens['trace_id'])
            if 'request_id' in tokens:
                request_id_ctx.reset(tokens['request_id'])
            if 'user_id' in tokens:
                user_id_ctx.reset(tokens['user_id'])
            if 'session_id' in tokens:
                session_id_ctx.reset(tokens['session_id'])

    @staticmethod
    def snapshot() -> Dict[str, Any]:
        """
        Get a snapshot of the current context state. Useful for logging or debugging.
        """
        return {
            "session_id": session_id_ctx.get(),
            "user_id": user_id_ctx.get(),
            "request_id": request_id_ctx.get(),
            "trace_id": trace_id_ctx.get()
        }

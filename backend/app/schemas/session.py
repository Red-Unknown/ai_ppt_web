from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

class SessionMode(str, Enum):
    LEARNING = "learning"
    PREVIEW = "preview"

class SessionStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    PROCESSING = "processing" # For async tasks like preview generation

class StartSessionRequest(BaseModel):
    course_id: str
    mode: SessionMode
    target_node_id: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    status: SessionStatus
    message: Optional[str] = None
    task_id: Optional[str] = None # For async tasks
    start_node: Optional[Dict[str, Any]] = None

class PreviewStatusResponse(BaseModel):
    status: SessionStatus
    progress: Optional[int] = Field(None, ge=0, le=100)
    eta_seconds: Optional[int] = None
    video_url: Optional[str] = None
    cached: bool = False
    expires_at: Optional[datetime] = None

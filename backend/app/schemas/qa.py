from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field

class Intent(str, Enum):
    QA = "qa"
    FEEDBACK = "feedback"
    CONTROL = "control"
    UNKNOWN = "unknown"

class ChatRequest(BaseModel):
    query: str = Field(..., description="The user's question")
    current_path: Optional[str] = Field(None, description="Current learning path, e.g., /chapter1/section2")
    top_k: int = Field(3, description="Number of results to retrieve")
    session_id: Optional[str] = Field(None, description="Session ID for conversation history")
    model: Optional[str] = Field("deepseek", description="Model to use: deepseek, gpt-4o")
    prompt_style: Optional[str] = Field("default", description="Prompt style: default, creative, socratic")

class SourceNode(BaseModel):
    node_id: str
    content: str
    path: str
    relevance_score: float
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    answer: str
    source_nodes: List[SourceNode] = []
    session_id: Optional[str] = None
    action: Optional[str] = Field(None, description="Action for the client: RESUME, SUPPLEMENT, FALLBACK_VIDEO")
    action_data: Optional[Dict[str, Any]] = Field(None, description="Data for the action, e.g., video_url")

class AdaptScriptRequest(BaseModel):
    original_script: str = Field(..., description="The original script text")
    session_id: str = Field(..., description="The session ID to get student profile context")
    target_style: Optional[str] = Field(None, description="Optional target style override")

class AdaptScriptResponse(BaseModel):
    adapted_script: str
    style_applied: str
    processing_time: float

class ChatMessage(BaseModel):
    role: str
    content: str
    sources: Optional[List[Dict[str, Any]]] = None
    reasoning_content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    timestamp: Optional[str] = None

class ChatSessionResponse(BaseModel):
    id: str
    title: str
    updated_at: str

class TruncateRequest(BaseModel):
    index: int

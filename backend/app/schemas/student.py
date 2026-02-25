from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime

class InteractionMode(str, Enum):
    STANDARD = "standard"
    PERSONALIZED = "personalized"

class LearningStyle(str, Enum):
    VISUAL = "visual"
    AUDITORY = "auditory"
    TEXTUAL = "textual"
    KINESTHETIC = "kinesthetic"

class StudentProfile(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the student")
    name: Optional[str] = None
    weaknesses: List[str] = Field(default_factory=list, description="List of topics the student struggles with")
    strengths: List[str] = Field(default_factory=list, description="List of topics the student is good at")
    learning_style: LearningStyle = Field(default=LearningStyle.VISUAL, description="Preferred learning style")
    interaction_mode: InteractionMode = Field(default=InteractionMode.STANDARD, description="Current interaction mode preference")

class StudentState(BaseModel):
    session_id: str = Field(..., description="Current active session ID")
    current_topic: Optional[str] = Field(None, description="Topic currently being studied")
    confusion_count: int = Field(default=0, description="Number of times student expressed confusion on current topic")
    last_interaction_time: datetime = Field(default_factory=datetime.now, description="Timestamp of last interaction")
    
class CreateProfileRequest(BaseModel):
    weaknesses: Optional[List[str]] = None
    learning_style: Optional[LearningStyle] = None
    interaction_mode: Optional[InteractionMode] = None

class UpdateProfileRequest(BaseModel):
    weaknesses: Optional[List[str]] = None
    learning_style: Optional[LearningStyle] = None
    interaction_mode: Optional[InteractionMode] = None

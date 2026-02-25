import json
from typing import Optional, Dict
from datetime import datetime
from backend.app.schemas.student import StudentProfile, StudentState, InteractionMode, LearningStyle

# Mock Redis Client for development
class MockRedis:
    def __init__(self):
        self.data: Dict[str, str] = {}

    def get(self, key: str) -> Optional[str]:
        return self.data.get(key)

    def set(self, key: str, value: str, ex: Optional[int] = None):
        self.data[key] = value

    def delete(self, key: str):
        if key in self.data:
            del self.data[key]

# Singleton instance
redis_client = MockRedis()

class StudentStateManager:
    """
    Manages student profiles and session states using Redis (Mocked).
    """
    
    PROFILE_PREFIX = "student:profile:"
    STATE_PREFIX = "student:state:"

    @staticmethod
    def _get_profile_key(user_id: str) -> str:
        return f"{StudentStateManager.PROFILE_PREFIX}{user_id}"

    @staticmethod
    def _get_state_key(session_id: str) -> str:
        return f"{StudentStateManager.STATE_PREFIX}{session_id}"

    @classmethod
    def get_profile(cls, user_id: str) -> Optional[StudentProfile]:
        data = redis_client.get(cls._get_profile_key(user_id))
        if data:
            return StudentProfile.parse_raw(data)
        return None

    @classmethod
    def create_or_update_profile(cls, user_id: str, profile_data: Dict) -> StudentProfile:
        key = cls._get_profile_key(user_id)
        existing_data = redis_client.get(key)
        
        if existing_data:
            current_profile = StudentProfile.parse_raw(existing_data)
            updated_data = current_profile.dict()
            updated_data.update({k: v for k, v in profile_data.items() if v is not None})
            new_profile = StudentProfile(**updated_data)
        else:
            # Create default if not exists
            new_profile = StudentProfile(
                user_id=user_id,
                weaknesses=profile_data.get("weaknesses", []),
                learning_style=profile_data.get("learning_style", LearningStyle.VISUAL),
                interaction_mode=profile_data.get("interaction_mode", InteractionMode.STANDARD)
            )
            
        redis_client.set(key, new_profile.json())
        return new_profile

    @classmethod
    def get_state(cls, session_id: str) -> Optional[StudentState]:
        data = redis_client.get(cls._get_state_key(session_id))
        if data:
            return StudentState.parse_raw(data)
        return None

    @classmethod
    def init_state(cls, session_id: str, topic: str) -> StudentState:
        state = StudentState(
            session_id=session_id,
            current_topic=topic,
            confusion_count=0,
            last_interaction_time=datetime.now()
        )
        redis_client.set(cls._get_state_key(session_id), state.json())
        return state

    @classmethod
    def increment_confusion(cls, session_id: str) -> int:
        state = cls.get_state(session_id)
        if state:
            state.confusion_count += 1
            state.last_interaction_time = datetime.now()
            redis_client.set(cls._get_state_key(session_id), state.json())
            return state.confusion_count
        return 0

    @classmethod
    def reset_confusion(cls, session_id: str):
        state = cls.get_state(session_id)
        if state:
            state.confusion_count = 0
            state.last_interaction_time = datetime.now()
            redis_client.set(cls._get_state_key(session_id), state.json())

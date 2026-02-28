import json
import uuid
from typing import Optional, Dict, List
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
    HISTORY_PREFIX = "student:history:"
    SESSIONS_PREFIX = "student:sessions:"

    @staticmethod
    def _get_profile_key(user_id: str) -> str:
        return f"{StudentStateManager.PROFILE_PREFIX}{user_id}"

    @staticmethod
    def _get_state_key(session_id: str) -> str:
        return f"{StudentStateManager.STATE_PREFIX}{session_id}"

    @staticmethod
    def _get_history_key(session_id: str) -> str:
        return f"{StudentStateManager.HISTORY_PREFIX}{session_id}"

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

    @classmethod
    def add_history(cls, session_id: str, role: str, content: str):
        """Add a message to the session history."""
        key = cls._get_history_key(session_id)
        data = redis_client.get(key)
        history = json.loads(data) if data else []
        
        history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Limit history size to last 50 messages to prevent bloat
        if len(history) > 50:
            history = history[-50:]
            
        redis_client.set(key, json.dumps(history))

    @classmethod
    def get_history(cls, session_id: str, limit: int = 10) -> List[Dict]:
        """Get recent chat history."""
        key = cls._get_history_key(session_id)
        data = redis_client.get(key)
        if not data:
            return []
            
        history = json.loads(data)
        return history[-limit:]

    @classmethod
    def truncate_history(cls, session_id: str, index: int):
        """Truncate history, keeping messages up to index (exclusive)."""
        key = cls._get_history_key(session_id)
        data = redis_client.get(key)
        if not data:
            return
        history = json.loads(data)
        if 0 <= index <= len(history):
            history = history[:index]
            redis_client.set(key, json.dumps(history))

    @staticmethod
    def _get_sessions_key(user_id: str) -> str:
        return f"{StudentStateManager.SESSIONS_PREFIX}{user_id}"

    @classmethod
    def create_session(cls, user_id: str, title: str = "New Chat") -> str:
        session_id = str(uuid.uuid4())
        # Init state
        cls.init_state(session_id, "General")
        
        # Add to user sessions
        key = cls._get_sessions_key(user_id)
        data = redis_client.get(key)
        sessions = json.loads(data) if data else []
        sessions.insert(0, {
            "id": session_id,
            "title": title,
            "timestamp": datetime.now().isoformat()
        })
        redis_client.set(key, json.dumps(sessions))
        return session_id

    @classmethod
    def get_user_sessions(cls, user_id: str) -> List[Dict]:
        key = cls._get_sessions_key(user_id)
        data = redis_client.get(key)
        return json.loads(data) if data else []

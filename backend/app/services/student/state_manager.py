import json
import uuid
import logging
import redis
from typing import Optional, Dict, List
from datetime import datetime
from backend.app.schemas.student import StudentProfile, StudentState, InteractionMode, LearningStyle

logger = logging.getLogger(__name__)

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

    def ping(self):
        return True

# Initialize Redis with Fallback
try:
    # Attempt to connect to local Redis with short timeout
    # In production, host/port should come from settings
    real_redis = redis.Redis(host='localhost', port=6379, db=0, socket_connect_timeout=1, decode_responses=True)
    real_redis.ping()
    redis_client = real_redis
    logger.info("Connected to Real Redis.")
except Exception as e:
    logger.warning(f"Redis connection failed: {e}. Using MockRedis (In-Memory Fallback).")
    redis_client = MockRedis()

# Wrapper for robust Redis operations
class SafeRedis:
    def __init__(self, client):
        self.client = client

    def get(self, key: str) -> Optional[str]:
        try:
            return self.client.get(key)
        except Exception as e:
            logger.error(f"Redis GET failed: {e}")
            return None

    def set(self, key: str, value: str, ex: Optional[int] = None):
        try:
            self.client.set(key, value, ex)
        except Exception as e:
            logger.error(f"Redis SET failed: {e}")

    def delete(self, key: str):
        try:
            self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis DELETE failed: {e}")

# Replace global client with safe wrapper
redis_client = SafeRedis(redis_client)

class StudentStateManager:
    """
    Manages student profiles and session states using Redis (with in-memory fallback).
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
            return StudentProfile.model_validate_json(data)
        return None

    @classmethod
    def create_or_update_profile(cls, user_id: str, profile_data: Dict) -> StudentProfile:
        key = cls._get_profile_key(user_id)
        existing_data = redis_client.get(key)
        
        if existing_data:
            current_profile = StudentProfile.model_validate_json(existing_data)
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
            
        redis_client.set(key, new_profile.model_dump_json())
        return new_profile

    @classmethod
    def get_state(cls, session_id: str) -> Optional[StudentState]:
        data = redis_client.get(cls._get_state_key(session_id))
        if data:
            return StudentState.model_validate_json(data)
        return None

    @classmethod
    def init_state(cls, session_id: str, topic: str) -> StudentState:
        state = StudentState(
            session_id=session_id,
            current_topic=topic,
            confusion_count=0,
            last_interaction_time=datetime.now(),
            last_qa_query=None
        )
        redis_client.set(cls._get_state_key(session_id), state.model_dump_json())
        return state

    @classmethod
    def update_last_query(cls, session_id: str, query: str):
        state = cls.get_state(session_id)
        if state:
            state.last_qa_query = query
            state.last_interaction_time = datetime.now()
            redis_client.set(cls._get_state_key(session_id), state.model_dump_json())

    @classmethod
    def increment_confusion(cls, session_id: str) -> int:
        state = cls.get_state(session_id)
        if state:
            state.confusion_count += 1
            state.last_interaction_time = datetime.now()
            redis_client.set(cls._get_state_key(session_id), state.model_dump_json())
            return state.confusion_count
        return 0

    @classmethod
    def reset_confusion(cls, session_id: str):
        state = cls.get_state(session_id)
        if state:
            state.confusion_count = 0
            state.last_interaction_time = datetime.now()
            redis_client.set(cls._get_state_key(session_id), state.model_dump_json())

    @classmethod
    def add_history(cls, session_id: str, role: str, content: str):
        """Add a message to the session history."""
        key = cls._get_history_key(session_id)
        data = redis_client.get(key)
        try:
            history = json.loads(data) if data else []
        except json.JSONDecodeError:
            logger.error(f"Corrupted history data for session {session_id}. Resetting.")
            history = []
        
        history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # Limit history size to last 100 messages to prevent bloat
        if len(history) > 100:
            history = history[-100:]
            
        redis_client.set(key, json.dumps(history))

    @classmethod
    def get_history(cls, session_id: str, limit: int = 10) -> List[Dict]:
        """Get recent chat history."""
        key = cls._get_history_key(session_id)
        data = redis_client.get(key)
        if not data:
            return []
            
        try:
            history = json.loads(data)
        except json.JSONDecodeError:
            logger.error(f"Corrupted history data for session {session_id}. Returning empty.")
            return []
            
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

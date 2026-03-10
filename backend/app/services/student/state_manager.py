import json
import uuid
import logging
import redis
from typing import Optional, Dict, List, Any
from datetime import datetime
from backend.app.schemas.student import StudentProfile, StudentState, InteractionMode, LearningStyle

logger = logging.getLogger(__name__)

# Mock Redis Client for development
class MockRedis:
    def __init__(self):
        self.data: Dict[str, Any] = {}

    def get(self, key: str) -> Optional[str]:
        val = self.data.get(key)
        if isinstance(val, list):
            return None # Mock limitation: get() shouldn't return list for string keys
        return val

    def set(self, key: str, value: str, ex: Optional[int] = None):
        self.data[key] = value

    def delete(self, key: str):
        if key in self.data:
            del self.data[key]

    def rpush(self, key: str, value: str) -> int:
        if key not in self.data:
            self.data[key] = []
        if not isinstance(self.data[key], list):
            self.data[key] = []
        self.data[key].append(value)
        return len(self.data[key])

    def lrange(self, key: str, start: int, end: int) -> List[str]:
        if key not in self.data:
            return []
        val = self.data[key]
        if not isinstance(val, list):
            return []
        if end == -1:
            return val[start:]
        return val[start : end + 1]

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

    def rpush(self, key: str, value: str) -> Optional[int]:
        try:
            return self.client.rpush(key, value)
        except Exception as e:
            logger.error(f"Redis RPUSH failed: {e}")
            return None

    def lrange(self, key: str, start: int, end: int) -> List[str]:
        try:
            return self.client.lrange(key, start, end)
        except Exception as e:
            logger.error(f"Redis LRANGE failed: {e}")
            return []

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
    EVENTS_PREFIX = "student:events:"
    MASTERY_PREFIX = "student:mastery:"

    @staticmethod
    def _get_mastery_key(user_id: str, topic: str) -> str:
        return f"{StudentStateManager.MASTERY_PREFIX}{user_id}:{topic}"

    @classmethod
    def update_mastery(cls, user_id: str, topic: str, is_correct: bool):
        """
        Update knowledge mastery using simplified Bayesian Knowledge Tracing (BKT).
        P(L) = P(L|Correct) if correct else P(L|Incorrect)
        """
        key = cls._get_mastery_key(user_id, topic)
        current_prob = float(redis_client.get(key) or 0.5)
        
        # BKT Parameters (Simplified)
        P_G = 0.3  # Guess
        P_S = 0.1  # Slip
        P_T = 0.1  # Transit
        
        if is_correct:
            # P(L|Correct) = (P(L) * (1 - P_S)) / (P(L) * (1 - P_S) + (1 - P(L)) * P_G)
            num = current_prob * (1 - P_S)
            den = num + (1 - current_prob) * P_G
        else:
            # P(L|Incorrect) = (P(L) * P_S) / (P(L) * P_S + (1 - P(L)) * (1 - P_G))
            num = current_prob * P_S
            den = num + (1 - current_prob) * (1 - P_G)
            
        posterior = num / den
        # Update with Transit: P(L)_new = P(L)_posterior + (1 - P(L)_posterior) * P_T
        new_prob = posterior + (1 - posterior) * P_T
        
        redis_client.set(key, str(min(0.99, max(0.01, new_prob))))
        return new_prob

    @classmethod
    def get_mastery(cls, user_id: str, topic: str) -> float:
        """Get current mastery probability for a topic."""
        key = cls._get_mastery_key(user_id, topic)
        return float(redis_client.get(key) or 0.5)

    @staticmethod
    def _get_profile_key(user_id: str) -> str:
        return f"{StudentStateManager.PROFILE_PREFIX}{user_id}"

    @staticmethod
    def _get_state_key(session_id: str) -> str:
        return f"{StudentStateManager.STATE_PREFIX}{session_id}"

    @staticmethod
    def _get_history_key(session_id: str) -> str:
        return f"{StudentStateManager.HISTORY_PREFIX}{session_id}"

    @staticmethod
    def _get_events_key(session_id: str) -> str:
        return f"{StudentStateManager.EVENTS_PREFIX}{session_id}"

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
    def add_history(cls, session_id: str, role: str, content: str, reasoning: str = None, tool_calls: list = None):
        """Add a message to the session history."""
        key = cls._get_history_key(session_id)
        data = redis_client.get(key)
        try:
            history = json.loads(data) if data else []
        except json.JSONDecodeError:
            logger.error(f"Corrupted history data for session {session_id}. Resetting.")
            history = []
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        if reasoning:
            message["reasoning_content"] = reasoning
            
        if tool_calls:
            message["tool_calls"] = tool_calls
            
        history.append(message)
        
        # Limit history size to last 100 messages to prevent bloat
        if len(history) > 100:
            history = history[-100:]
            
        redis_client.set(key, json.dumps(history))

    @classmethod
    def append_event(cls, session_id: str, event: Dict[str, Any]):
        """Append an event to the session event log (Event Sourcing)."""
        if not session_id:
            return
        key = cls._get_events_key(session_id)
        # Add timestamp if missing
        if "timestamp" not in event:
            event["timestamp"] = datetime.now().isoformat()
        redis_client.rpush(key, json.dumps(event))

    @classmethod
    def get_events(cls, session_id: str) -> List[Dict[str, Any]]:
        """Get full event history for a session."""
        if not session_id:
            return []
        key = cls._get_events_key(session_id)
        events_json = redis_client.lrange(key, 0, -1)
        events = []
        if events_json:
            for e_str in events_json:
                try:
                    events.append(json.loads(e_str))
                except (json.JSONDecodeError, TypeError):
                    continue
        return events

    @classmethod
    def get_history(cls, session_id: str, limit: int = 100) -> List[Dict]:
        """Get recent chat history."""
        # Use cls._get_history_key(session_id) to get the correct key
        key = cls._get_history_key(session_id)
        
        try:
            # Check if redis_client is wrapped or direct
            if hasattr(redis_client, 'get'):
                data = redis_client.get(key)
            else:
                # Fallback for mock/raw client difference
                data = None
                
            if not data:
                return []
                
            history = json.loads(data)
            return history[-limit:]
            
        except Exception as e:
            logger.error(f"Error retrieving history for session {session_id}: {e}")
            return []

    @classmethod
    def save_session_context(cls, session_id: str, expect_questions: list = None, thinking_path: str = None, evaluation: dict = None):
        """Save session context like expected questions, thinking path, and evaluation."""
        key = f"session_context:{session_id}"
        context = {}
        
        try:
            existing = redis_client.get(key)
            if existing:
                context = json.loads(existing)
        except:
            pass
            
        if expect_questions is not None:
            context["expect_questions"] = expect_questions
            
        if thinking_path is not None:
            context["thinking_path"] = thinking_path
            
        if evaluation is not None:
            context["evaluation"] = evaluation
            
        context["updated_at"] = datetime.now().isoformat()
        
        try:
            redis_client.set(key, json.dumps(context))
        except Exception as e:
            logger.error(f"Failed to save session context: {e}")

    @classmethod
    def get_session_context(cls, session_id: str) -> Dict:
        """Get session context."""
        key = f"session_context:{session_id}"
        try:
            data = redis_client.get(key)
            return json.loads(data) if data else {}
        except Exception as e:
            logger.error(f"Failed to get session context: {e}")
            return {}

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


import os
import sys
# Add project root to path to allow imports like 'from backend.app...'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import pytest
from unittest.mock import MagicMock, patch, AsyncMock

# Set dummy API key before imports to avoid validation errors
os.environ["OPENAI_API_KEY"] = "sk-dummy-key-for-testing"

# Mock the Redis client to avoid needing a running Redis instance
with patch('redis.Redis') as mock_redis:
    # Mock the response for state_manager
    mock_redis_instance = mock_redis.return_value
    mock_redis_instance.get.return_value = None
    mock_redis_instance.incr.return_value = 1
    
    from backend.app.services.qa.router import DialogueRouter, Intent
    from backend.app.services.teacher.agent import TeacherAgent
    from backend.app.schemas.student import StudentProfile, StudentState, InteractionMode, LearningStyle

@pytest.fixture
def mock_llm():
    with patch('backend.app.services.qa.router.ChatOpenAI') as mock_chat:
        yield mock_chat

@pytest.fixture
def mock_teacher_llm():
    with patch('backend.app.services.teacher.agent.ChatOpenAI') as mock_chat:
        yield mock_chat

@pytest.mark.asyncio
async def test_router_classification_mock(mock_llm):
    # Setup mock router
    router = DialogueRouter()
    
    # Mock the LLM response for the chain in router
    # Since router uses self.chain = prompt | llm | parser, we need to mock the chain or the method
    # But looking at router.py (from context), it likely constructs chain in __init__ or method.
    # Assuming we can mock the private method _route_llm for easier testing of the public route method
    # or just mock the chain if it's an attribute.
    
    # Let's mock _route_llm directly to avoid chain complexity
    router._route_llm = MagicMock(return_value=Intent.QA)
    
    # Test classification
    intent = router.route("What is the core concept of this course?")
    assert intent == Intent.QA
    
    # Change mock for feedback
    router._route_llm.return_value = Intent.FEEDBACK
    intent = router.route("I am confused about this part.")
    assert intent == Intent.FEEDBACK

@pytest.mark.asyncio
async def test_teacher_agent_supplement_mock(mock_teacher_llm):
    # Setup mock teacher agent
    agent = TeacherAgent()

    # Mock _generate_supplement to return a string directly
    # This bypasses the chain execution issues
    agent._generate_supplement = AsyncMock(return_value="Here is a simple analogy: think of it like a water pipe...")

    # Test handling feedback with confusion
    profile = StudentProfile(
        user_id="test_user", 
        name="Test User", 
        weaknesses=["physics"], 
        learning_style=LearningStyle.VISUAL
    )
    state = StudentState(
        session_id="test_session", 
        current_topic="physics_intro", 
        confusion_count=1
    )

    context_content = "Physics is the study of matter..." 

    result = await agent.handle_feedback("I am confused", state, profile, context_content)

    assert result["action"] == "SUPPLEMENT"
    assert "analogy" in result["content"] or "water pipe" in result["content"]

    # Test fallback
    state_fallback = StudentState(
        session_id="test_session", 
        current_topic="physics_intro", 
        confusion_count=2
    )
    result = await agent.handle_feedback("I am still confused", state_fallback, profile, context_content)
    assert result["action"] == "FALLBACK_VIDEO"

if __name__ == "__main__":
    # Allow running directly with python
    import sys
    import asyncio
    
    # minimal manual run
    print("Running manual mock test...")
    
    async def main():
        # Mock classes manually for simple run
        class MockRouter:
            def route(self, query):
                return Intent.QA
        
        router = MockRouter()
        res = router.route("test")
        print(f"Router classification result: {res}")
        
        # Simple agent test
        agent = TeacherAgent()
        agent._generate_supplement = AsyncMock(return_value="Analogy content")
        
        profile = StudentProfile(user_id="u1", user_name="Test")
        state = StudentState(session_id="s1", current_topic="topic")
        
        # We skip the full handle_feedback logic in this simple manual check 
        # because we can't easily mock everything in __main__ without pytest fixtures
        # but the pytest execution above is what matters.
        print("Manual check: Imports and basic instantiation worked.")

    # asyncio.run(main()) 
    print("Run 'pytest backend/tests/debug_xzh/test_mock_pipeline.py' to execute tests.")

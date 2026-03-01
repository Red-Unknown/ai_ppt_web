import asyncio
import json
import sys
import os
from unittest.mock import MagicMock, AsyncMock, patch

# Ensure backend module is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock config before importing service
with patch('backend.app.core.config.settings') as mock_settings:
    mock_settings.DEEPSEEK_API_KEY = "mock_key"
    mock_settings.DEEPSEEK_MODEL = "mock_model"
    mock_settings.DEEPSEEK_BASE_URL = "http://mock"
    mock_settings.OPENAI_API_KEY = ""
    mock_settings.DEEPSEEK_PROMPTS_PATH = "mock_path.json"
    
    from backend.app.services.qa.service import QAService
    from backend.app.schemas.qa import ChatRequest

async def run_verification():
    print("Starting QAService Stream Verification...")
    
    # Patch dependencies to avoid real initialization
    with patch('backend.app.services.qa.service.TreeStructureRetriever'), \
         patch('backend.app.services.qa.service.DialogueRouter') as MockRouter, \
         patch('backend.app.services.qa.service.QAAnalyzer') as MockAnalyzer, \
         patch('backend.app.services.qa.service.TeacherAgent'), \
         patch('backend.app.services.qa.service.StudentStateManager'), \
         patch('backend.app.services.qa.service.ChatOpenAI'), \
         patch('backend.app.services.qa.service.prompt_loader') as MockPromptLoader:
        
        # Setup Prompt Loader Mock
        MockPromptLoader.get_prompt.return_value = "Mock Prompt Template"

        # Setup Router and Analyzer
        mock_router_instance = MockRouter.return_value
        mock_router_instance.route.return_value = "QA" # Force QA intent
        
        mock_analyzer_instance = MockAnalyzer.return_value
        mock_analyzer_instance.analyze = AsyncMock(return_value="CALCULATION") # Force Calculation type
        
        # Initialize Service
        service = QAService()
        
        # Inject Mock Skill Manager with a Mock Skill
        service.skill_manager = MagicMock()
        mock_skill = AsyncMock()
        mock_skill.name = "math_solver"
        mock_skill.description = "Mock Math Solver"
        # Setup execute to return a dict directly (AsyncMock handles the async part)
        mock_skill.execute.return_value = {
            "status": "success",
            "content": "Result is 2",
            "details": {"code": "print(1+1)"}
        }
        
        # Setup get_skill to return our mock skill
        service.skill_manager.get_skill.return_value = mock_skill
        
        # Setup execute_skill to act as a proper async method returning the dict
        # We can just use AsyncMock with return_value for simplicity since we don't need dynamic return based on args here
        service.skill_manager.execute_skill = AsyncMock(return_value={
            "status": "success",
            "content": "Result is 2",
            "details": {"code": "print(1+1)"}
        })
        
        # Create Request
        request = ChatRequest(query="Calculate 1+1", session_id="test_session")
        
        # Run Stream
        print("\nStreaming Response:")
        events = []
        try:
            async for chunk in service.stream_answer_question(request):
                data = json.loads(chunk)
                events.append(data)
                # Print concise summary
                msg_type = data.get('type')
                content = data.get('content') or data.get('skill')
                print(f"Received: {msg_type} - {content}")
        except Exception as e:
            print(f"Stream Error: {e}")
            import traceback
            traceback.print_exc()
            
        # Verify Events
        skill_start = next((e for e in events if e.get('type') == 'skill_start'), None)
        skill_end = next((e for e in events if e.get('type') == 'skill_end'), None)
        
        if skill_start and skill_end:
            print("\nSUCCESS: Skill events received correctly.")
            print(f"Skill Start: {skill_start}")
            print(f"Skill End: {skill_end}")
            
            # Verify details in skill_end
            if skill_end.get("details", {}).get("code") == "print(1+1)":
                 print("SUCCESS: Code details present.")
            else:
                 print("FAILURE: Code details missing or incorrect.")
                 sys.exit(1)
                 
        else:
            print("\nFAILURE: Missing skill events.")
            sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_verification())

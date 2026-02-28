import asyncio
import time
import sys
import statistics
from pathlib import Path
from unittest.mock import MagicMock, AsyncMock, patch

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

# Mock LangChain components BEFORE importing service to avoid initialization issues if env vars are missing
with patch('langchain_openai.ChatOpenAI') as MockChatOpenAI:
    from backend.app.services.qa.service import QAService
    from backend.app.schemas.qa import ChatRequest

# Define a mock stream that yields chunks
async def mock_astream(*args, **kwargs):
    response = "This is a benchmark response. " * 5
    chunk_size = 5
    for i in range(0, len(response), chunk_size):
        yield response[i:i+chunk_size]
        await asyncio.sleep(0.01) # Fast generation

class MockRunnable:
    def __or__(self, other):
        return MockRunnable()
    
    async def astream(self, input):
        async for chunk in mock_astream():
            yield chunk

async def run_benchmark():
    print("--- QA Service Benchmark (Mocked LLM) ---")
    
    # Patch QAService dependencies
    with patch('backend.app.services.qa.service.ChatOpenAI'), \
         patch('backend.app.services.qa.service.TreeStructureRetriever') as MockRetriever, \
         patch('backend.app.services.qa.service.StudentStateManager') as MockStateManager, \
         patch('backend.app.services.qa.service.QAService.get_prompt_template') as MockGetPrompt:
        
        # Setup Service
        service = QAService()
        
        # Make the chain construction work: prompt | llm | parser
        # We make get_prompt_template return a Mock that when piped returns a MockRunnable
        
        mock_chain = MockRunnable()
        
        # Mock Prompt Template
        mock_prompt = MagicMock()
        mock_prompt.__or__ = MagicMock(return_value=mock_chain) 
        # So prompt | llm -> mock_chain
        
        MockGetPrompt.return_value = mock_prompt
        
        # We also need mock_chain | parser -> mock_chain
        # MockRunnable needs to handle __or__
        
        # Ensure llm_clients are mocks that don't break the pipe
        service.llm_clients = {"qa": MagicMock(), "summary": MagicMock(), "translation": MagicMock()}
        
        # Mock Retriever
        service.retriever.invoke = MagicMock(return_value=[
            MagicMock(page_content="Mock Context", metadata={"score": 0.9})
        ])
        
        # Mock State Manager
        MockStateManager.get_history.return_value = []
        
        latencies = []
        ttfts = []
        
        async def worker(i):
            req = ChatRequest(query=f"Q{i}", session_id=f"s{i}")
            start = time.time()
            first = None
            
            try:
                async for chunk in service.stream_answer_question(req):
                    if first is None:
                        first = time.time()
            except Exception as e:
                print(f"Error: {e}")
                return None, None
                
            end = time.time()
            return (first - start)*1000, (end - start)*1000

        # Run 50 requests
        tasks = [worker(i) for i in range(50)]
        results = await asyncio.gather(*tasks)
        
        valid_results = [r for r in results if r[0] is not None]
        ttfts = [r[0] for r in valid_results]
        totals = [r[1] for r in valid_results]
        
        print(f"\nRequests: {len(valid_results)}")
        print(f"TTFT (ms): Avg={statistics.mean(ttfts):.2f}, P95={statistics.quantiles(ttfts, n=20)[18]:.2f}")
        print(f"Total (ms): Avg={statistics.mean(totals):.2f}, P95={statistics.quantiles(totals, n=20)[18]:.2f}")

if __name__ == "__main__":
    asyncio.run(run_benchmark())

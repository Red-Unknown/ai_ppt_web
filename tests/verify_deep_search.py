import asyncio
import logging
import sys
import os

# Add project root to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.qa.skills.search_skill import WebSearchSkill

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_scraping():
    skill = WebSearchSkill()
    
    print("--- Test 1: Direct Scraping ---")
    url = "https://www.example.com"
    content = await skill._scrape_content(url)
    print(f"Scraped content from {url}:")
    print(content[:200] + "..." if content else "Failed to scrape")
    
    if "Example Domain" in content:
        print("SUCCESS: Scraped content matches expectation.")
    else:
        print("FAILURE: Content does not match.")

    print("\n--- Test 2: Trigger Scraping via Execute (Mocked Tool) ---")
    # Mock the search tool to return a short snippet with a real URL
    # We need to bypass the "no tool" check by mocking the engine
    skill.engine = "mock_test"
    
    # Create a dummy class to mock ainvoke
    class MockTool:
        async def ainvoke(self, query):
            return [{
                "url": "https://www.example.com",
                "content": "Short snippet." # Very short, should trigger scraping
            }]
            
    skill.search_tool = MockTool()
    # We also need to hack the engine check in execute method
    # The current execute method checks self.engine == "tavily" or "duckduckgo"
    # So we need to set engine to "tavily" to use the ainvoke path
    skill.engine = "tavily" 
    
    result = await skill.execute("test query")
    
    print("Result Content:")
    print(result["content"][:500])
    
    print("\nProcess Steps:")
    for step in result["details"]["process"]:
        print(f"- {step}")
        
    # Verify scraping happened
    if any("Scraped content from" in step for step in result["details"]["process"]):
        print("SUCCESS: Deep scraping triggered.")
    else:
        print("FAILURE: Deep scraping NOT triggered.")

if __name__ == "__main__":
    asyncio.run(test_scraping())

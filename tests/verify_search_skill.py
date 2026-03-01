import asyncio
import os
import sys
import logging

# Ensure backend module is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app.services.qa.skills.search_skill import WebSearchSkill

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_search():
    print("Testing WebSearchSkill...")
    skill = WebSearchSkill()
    
    print(f"Initialized Engine: {skill.engine}")
    
    # Test 1: General Query
    query = "Python latest version"
    print(f"\n--- Query: {query} ---")
    result = await skill.execute(query)
    
    print(f"Status: {result['status']}")
    print(f"Content Summary: {result['content'][:200]}...")
    print(f"Source Count: {len(result['details']['sources'])}")
    if result['details']['sources']:
        first_source = result['details']['sources'][0]
        print(f"First Source: {first_source['title']} ({first_source['link']})")
    
    # Test 2: Noun Explanation (Liberal Arts)
    query_noun = "程朱理学"
    print(f"\n--- Query: {query_noun} (Should optimize) ---")
    result_noun = await skill.execute(query_noun)
    
    # Verify optimization happened (we can't see the internal optimized query easily unless we check logs or inference from results)
    # But we can check if results look encyclopedic
    print(f"Status: {result_noun['status']}")
    print(f"Content Summary: {result_noun['content'][:200]}...")
    print(f"Source Count: {len(result_noun['details']['sources'])}")
    if result_noun['details']['sources']:
         first_source = result_noun['details']['sources'][0]
         print(f"First Source: {first_source['title']} ({first_source['link']})")

if __name__ == "__main__":
    asyncio.run(test_search())

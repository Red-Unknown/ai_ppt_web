import os
import sys
import asyncio
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults

async def verify_deepseek():
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ DEEPSEEK_API_KEY is missing in environment variables.")
        return False
    
    if api_key.startswith("sk-your-key"):
        print("❌ DEEPSEEK_API_KEY appears to be a placeholder ('sk-your-key'). Please set a real key.")
        return False

    print(f"Checking DeepSeek API Key: {api_key[:4]}...{api_key[-4:]}")
    
    try:
        # Use a simple invocation
        llm = ChatOpenAI(
            model="deepseek-chat",
            api_key=api_key,
            base_url="https://api.deepseek.com",
            temperature=0
        )
        response = await llm.ainvoke("Hello, reply with 'OK'.")
        print(f"✅ DeepSeek API Response: {response.content}")
        return True
    except Exception as e:
        print(f"❌ DeepSeek API Verification Failed: {e}")
        return False

async def verify_tavily():
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        print("⚠️ TAVILY_API_KEY is missing. Web Search will degrade to DuckDuckGo or fail.")
        # We allow Tavily to be missing if user accepts DDG, but user asked to verify API KEY.
        # User said: "验证API_KEY是否可用" - implying if set, verify it.
        return True 
    
    if api_key.startswith("tvly-your-key"):
        print("❌ TAVILY_API_KEY appears to be a placeholder ('tvly-your-key').")
        return False

    print(f"Checking Tavily API Key: {api_key[:4]}...")
    try:
        tool = TavilySearchResults(max_results=1)
        # Tavily tool execute might be sync or async depending on version, usually sync in langchain tool
        # But we can try invoking it
        res = tool.invoke("Python version")
        print(f"✅ Tavily Search Result: Found {len(res)} results.")
        return True
    except Exception as e:
        print(f"❌ Tavily API Verification Failed: {e}")
        return False

async def main():
    print("--- Starting API Key Verification ---")
    
    deepseek_ok = await verify_deepseek()
    tavily_ok = await verify_tavily()
    
    if not deepseek_ok:
        print("❌ Critical API Verification Failed. Aborting tests.")
        sys.exit(1)
        
    if not tavily_ok:
        print("⚠️ Tavily Verification Failed, but continuing (Search might fail).")
        
    print("✅ All Critical Keys Verified.")
    sys.exit(0)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

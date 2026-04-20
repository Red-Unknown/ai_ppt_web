"""
真实 Tavily API 联网搜索测试脚本
运行前请确保已设置环境变量：TAVILY_API_KEY

使用方法:
1. 设置环境变量：set TAVILY_API_KEY=your_api_key
2. 运行：python test_tavily_real.py
"""
import asyncio
import os
import sys
import json
import aiohttp
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any


# 缓存
_query_cache = {}
_CACHE_TTL = timedelta(hours=1)


def _get_from_cache(query: str) -> Dict[str, Any] | None:
    """Get cached result for query."""
    cache_key = hashlib.md5(query.encode()).hexdigest()
    if cache_key in _query_cache:
        cached_data, timestamp = _query_cache[cache_key]
        if datetime.now() - timestamp < _CACHE_TTL:
            print(f"  [Cache hit for: {query}]")
            return cached_data
        else:
            del _query_cache[cache_key]
    return None


async def call_tavily_search(api_key: str, query: str) -> Dict[str, Any]:
    """Call Tavily API for web search."""
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "include_answer": True,
        "include_raw_content": False,
        "max_results": 5
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.tavily.com/search",
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Tavily API error: {response.status} - {error_text}")

            return await response.json()


def parse_tavily_response(response: Dict[str, Any], query: str) -> Dict[str, Any]:
    """Parse Tavily API response."""
    answer = response.get("answer", "")
    results = response.get("results", [])
    
    sources = []
    for result in results:
        sources.append({
            "title": result.get("title", "Untitled"),
            "link": result.get("url", ""),
            "snippet": result.get("content", "")
        })

    process_steps = [
        f"Query sent to Tavily API: {query}",
        f"Retrieved {len(results)} search results"
    ]

    return {
        "content": answer,
        "sources": sources,
        "process_steps": process_steps,
        "raw_response": response
    }


async def test_real_tavily_search():
    """使用真实 Tavily API 测试联网搜索"""
    
    # 检查环境变量
    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        print("❌ 错误：未设置 TAVILY_API_KEY 环境变量")
        print("请先设置：set TAVILY_API_KEY=your_api_key")
        return
    
    print(f"✓ 检测到 TAVILY_API_KEY: {api_key[:8]}...")
    print("=" * 70)
    
    # 测试查询 - 时效性问题
    test_queries = [
        "2024 年最新的 AI 技术发展趋势",
        "今天北京的天气怎么样",
    ]
    
    try:
        for query in test_queries:
            print(f"\n🔍 测试查询：{query}")
            print("-" * 70)
            
            # 检查缓存
            cached = _get_from_cache(query)
            if cached:
                print(f"✓ 使用缓存结果")
                result = cached
            else:
                # 调用真实 API
                import time
                start_time = time.time()
                
                tavily_response = await call_tavily_search(api_key, query)
                parsed = parse_tavily_response(tavily_response, query)
                
                latency_ms = int((time.time() - start_time) * 1000)
                
                result = {
                    "status": "success",
                    "content": parsed["content"],
                    "details": {
                        "raw_output": json.dumps(parsed["raw_response"], ensure_ascii=False),
                        "sources": parsed["sources"],
                        "type": "web_search_results",
                        "engine": "tavily",
                        "latency_ms": latency_ms,
                        "status_code": 200,
                        "process": parsed["process_steps"],
                        "cache_hit": False
                    }
                }
                
                # 保存到缓存
                cache_key = hashlib.md5(query.encode()).hexdigest()
                _query_cache[cache_key] = (result, datetime.now())
            
            if result["status"] == "success":
                print(f"✓ 查询成功!")
                print(f"  延迟：{result['details'].get('latency_ms', 'N/A')} ms")
                print(f"  引擎：{result['details'].get('engine', 'N/A')}")
                print(f"  来源数：{len(result['details'].get('sources', []))}")
                print(f"\n📄 内容预览:")
                content = result["content"]
                if content:
                    print(content[:500] + "..." if len(content) > 500 else content)
                else:
                    print("  (内容为空)")
                
                # 显示处理步骤
                process = result['details'].get('process', [])
                if process:
                    print(f"\n📋 处理步骤:")
                    for step in process:
                        print(f"  - {step}")
                
                # 显示来源
                sources = result['details'].get('sources', [])
                if sources:
                    print(f"\n🔗 来源链接:")
                    for i, source in enumerate(sources[:3], 1):
                        print(f"  {i}. {source.get('title', 'Untitled')} - {source.get('link', '')}")
            else:
                print(f"❌ 查询失败：{result.get('content', 'Unknown error')}")
            
            print("=" * 70)
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误：{e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 开始真实 Tavily API 联网搜索测试\n")
    print("注意：此测试会调用真实的 Tavily API，请确保已设置 TAVILY_API_KEY 环境变量\n")
    asyncio.run(test_real_tavily_search())

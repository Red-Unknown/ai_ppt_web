"""
真实Kimi API联网搜索测试脚本
运行前请确保已设置环境变量: KIMI_API_KEY

使用方法:
1. 设置环境变量: set KIMI_API_KEY=your_api_key
2. 运行: python test_kimi_real.py
"""
import asyncio
import os
import sys
import json
import aiohttp
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# 缓存
_query_cache = {}
_CACHE_TTL = timedelta(hours=1)


def _get_from_cache(query: str) -> Optional[Dict[str, Any]]:
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


async def call_kimi_with_search(api_key: str, query: str) -> Dict[str, Any]:
    """
    Call Kimi API with built-in web search tool enabled.
    Uses two-step process: first call triggers search, second call gets results.
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    tools = [{
        "type": "builtin_function",
        "function": {
            "name": "$web_search"
        }
    }]

    # Step 1: Initial call to trigger web search
    payload = {
        "model": "moonshot-v1-32k",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. Use the web search tool to find up-to-date information."
            },
            {
                "role": "user",
                "content": query
            }
        ],
        "tools": tools,
        "stream": False
    }

    async with aiohttp.ClientSession() as session:
        # First call - triggers search
        async with session.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            if response.status != 200:
                error_text = await response.text()
                raise Exception(f"Kimi API error: {response.status} - {error_text}")

            first_response = await response.json()

        # Check if we got a tool call
        choices = first_response.get("choices", [])
        if not choices:
            return first_response

        message = choices[0].get("message", {})
        tool_calls = message.get("tool_calls", [])

        if not tool_calls:
            # No tool call, return as is
            return first_response

        print(f"  [Step 1] Kimi invoked tool call: {tool_calls[0].get('function', {}).get('name')}")

        # Step 2: Call again with tool results to get final answer
        tool_call = tool_calls[0]
        tool_call_id = tool_call.get("id", "")

        # Build messages with tool response
        messages_with_tool = [
            {
                "role": "system",
                "content": "You are a helpful assistant. Use the web search tool to find up-to-date information."
            },
            {
                "role": "user",
                "content": query
            },
            {
                "role": "assistant",
                "content": message.get("content", ""),
                "tool_calls": tool_calls
            },
            {
                "role": "tool",
                "tool_call_id": tool_call_id,
                "content": json.dumps({"status": "success", "search_completed": True})
            }
        ]

        payload2 = {
            "model": "moonshot-v1-32k",
            "messages": messages_with_tool,
            "tools": tools,
            "stream": False
        }

        print(f"  [Step 2] Sending tool response back to Kimi...")
        async with session.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers=headers,
            json=payload2,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response2:
            if response2.status != 200:
                error_text = await response2.text()
                raise Exception(f"Kimi API error (step 2): {response2.status} - {error_text}")

            return await response2.json()


def parse_kimi_response(response: Dict[str, Any], original_query: str) -> Dict[str, Any]:
    """Parse Kimi API response and extract search results."""
    import re
    
    choices = response.get("choices", [])
    if not choices:
        raise Exception("No choices in Kimi API response")

    message = choices[0].get("message", {})
    content = message.get("content", "")
    tool_calls = message.get("tool_calls", [])

    sources = []
    process_steps = ["Query sent to Kimi API with web search enabled"]

    # Extract search results from tool calls if present
    if tool_calls:
        process_steps.append(f"Kimi invoked {len(tool_calls)} tool call(s)")
        for tc in tool_calls:
            if tc.get("function", {}).get("name") == "$web_search":
                try:
                    args = json.loads(tc["function"].get("arguments", "{}"))
                    process_steps.append(f"Web search executed for: {args.get('query', original_query)}")
                except json.JSONDecodeError:
                    pass

    # Try to extract URLs from content as sources
    url_pattern = r'https?://[^\s\]\)>"]+'
    found_urls = re.findall(url_pattern, content)

    for i, url in enumerate(found_urls[:5]):
        sources.append({
            "title": f"Source {i+1}",
            "link": url,
            "snippet": content[:200] + "..." if len(content) > 200 else content
        })

    if not sources and content:
        sources.append({
            "title": "Kimi Search Result",
            "link": "",
            "snippet": content[:500]
        })

    process_steps.append(f"Extracted {len(sources)} sources from response")

    return {
        "content": content,
        "sources": sources,
        "process_steps": process_steps,
        "raw_response": response
    }


async def test_real_kimi_web_search():
    """使用真实Kimi API测试联网搜索"""
    
    # 检查环境变量
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("❌ 错误: 未设置 KIMI_API_KEY 环境变量")
        print("请先设置: set KIMI_API_KEY=your_api_key")
        return
    
    print(f"✓ 检测到 KIMI_API_KEY: {api_key[:8]}...{api_key[-4:]}")
    print("=" * 60)
    
    # 测试查询 - 时效性问题
    test_queries = [
        "2024年最新的AI技术发展趋势",
        "今天北京的天气怎么样",
    ]
    
    try:
        for query in test_queries:
            print(f"\n🔍 测试查询: {query}")
            print("-" * 60)
            
            # 检查缓存
            cached = _get_from_cache(query)
            if cached:
                print(f"✓ 使用缓存结果")
                result = cached
            else:
                # 调用真实API
                import time
                start_time = time.time()
                
                kimi_response = await call_kimi_with_search(api_key, query)
                parsed = parse_kimi_response(kimi_response, query)
                
                latency_ms = int((time.time() - start_time) * 1000)
                
                result = {
                    "status": "success",
                    "content": parsed["content"],
                    "details": {
                        "raw_output": json.dumps(parsed["raw_response"], ensure_ascii=False),
                        "sources": parsed["sources"],
                        "type": "web_search_results",
                        "engine": "kimi",
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
                print(f"  延迟: {result['details'].get('latency_ms', 'N/A')} ms")
                print(f"  引擎: {result['details'].get('engine', 'N/A')}")
                print(f"  来源数: {len(result['details'].get('sources', []))}")
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
            else:
                print(f"❌ 查询失败: {result.get('content', 'Unknown error')}")
            
            print("=" * 60)
            
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 开始真实Kimi API联网搜索测试\n")
    print("注意: 此测试会调用真实的Kimi API，请确保已设置 KIMI_API_KEY 环境变量\n")
    asyncio.run(test_real_kimi_web_search())

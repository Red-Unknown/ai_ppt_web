"""
测试Kimi不同模型的速度对比
"""
import asyncio
import os
import json
import aiohttp
import time


async def call_kimi_with_model(api_key: str, query: str, model: str) -> tuple[dict, float]:
    """
    Call Kimi API with specified model.
    Returns (response, latency_ms)
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    tools = [{
        "type": "builtin_function",
        "function": {"name": "$web_search"}
    }]

    # Step 1: Trigger search
    payload1 = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Use web search to find information."},
            {"role": "user", "content": query}
        ],
        "tools": tools,
        "stream": False
    }

    start_time = time.time()
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers=headers,
            json=payload1,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            first_response = await response.json()

        # Step 2: Get results
        choices = first_response.get("choices", [])
        if choices:
            message = choices[0].get("message", {})
            tool_calls = message.get("tool_calls", [])
            
            if tool_calls:
                tool_call_id = tool_calls[0].get("id", "")
                payload2 = {
                    "model": model,
                    "messages": [
                        {"role": "system", "content": "Use web search to find information."},
                        {"role": "user", "content": query},
                        {"role": "assistant", "content": "", "tool_calls": tool_calls},
                        {"role": "tool", "tool_call_id": tool_call_id, "content": json.dumps({"status": "success"})}
                    ],
                    "tools": tools,
                    "stream": False
                }
                
                async with session.post(
                    "https://api.moonshot.cn/v1/chat/completions",
                    headers=headers,
                    json=payload2,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as response2:
                    result = await response2.json()
    
    latency_ms = (time.time() - start_time) * 1000
    return result, latency_ms


async def test_model_speed():
    """测试不同模型的速度"""
    
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("❌ 未设置 KIMI_API_KEY")
        return
    
    print(f"✓ API Key: {api_key[:8]}...{api_key[-4:]}")
    print("=" * 70)
    
    query = "2024年最新的AI技术发展趋势"
    models = ["moonshot-v1-8k", "moonshot-v1-32k"]
    
    print(f"\n测试查询: {query}\n")
    
    for model in models:
        print(f"\n🚀 测试模型: {model}")
        print("-" * 70)
        
        try:
            result, latency = await call_kimi_with_model(api_key, query, model)
            
            content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            print(f"✓ 总延迟: {latency:.0f} ms")
            print(f"📄 内容长度: {len(content)} 字符")
            print(f"📄 内容预览: {content[:200]}..." if len(content) > 200 else f"📄 内容: {content}")
            
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        print("=" * 70)


if __name__ == "__main__":
    print("🚀 Kimi模型速度对比测试\n")
    asyncio.run(test_model_speed())

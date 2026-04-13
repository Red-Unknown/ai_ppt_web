"""
调试Kimi API响应
"""
import asyncio
import os
import json
import aiohttp


async def debug_kimi_response():
    """调试Kimi API响应"""
    
    api_key = os.environ.get("KIMI_API_KEY")
    if not api_key:
        print("❌ 未设置 KIMI_API_KEY")
        return
    
    print(f"✓ 使用 API Key: {api_key[:8]}...{api_key[-4:]}")
    
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

    payload = {
        "model": "moonshot-v1-32k",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant. You MUST use the web search tool to find the most up-to-date information."
            },
            {
                "role": "user",
                "content": "2024年最新的AI技术发展趋势"
            }
        ],
        "tools": tools,
        "tool_choice": {"type": "builtin_function", "function": {"name": "$web_search"}},
        "stream": False
    }

    print("\n📤 发送请求...")
    print(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://api.moonshot.cn/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as response:
            print(f"\n📥 响应状态: {response.status}")
            
            result = await response.json()
            print(f"\n📄 完整响应:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 解析响应
            if "choices" in result and len(result["choices"]) > 0:
                message = result["choices"][0].get("message", {})
                print(f"\n🔍 Message 内容:")
                print(f"  content: {message.get('content', 'N/A')}")
                print(f"  tool_calls: {message.get('tool_calls', 'N/A')}")
                print(f"  role: {message.get('role', 'N/A')}")


if __name__ == "__main__":
    print("🚀 调试Kimi API响应\n")
    asyncio.run(debug_kimi_response())

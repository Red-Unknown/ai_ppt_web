import requests
import json
import asyncio
import websockets
import base64

BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000"

def test_rest_apis():
    """测试所有 REST API 端点"""
    print("=" * 60)
    print("测试 REST API 端点")
    print("=" * 60)

    # 1. 根路由
    print("\n[1] GET /")
    r = requests.get(f"{BASE_URL}/")
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.json()}")

    # 2. 获取会话列表
    print("\n[2] GET /api/v1/chat/sessions")
    r = requests.get(f"{BASE_URL}/api/v1/chat/sessions")
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.json()}")

    # 3. 创建会话
    print("\n[3] POST /api/v1/chat/sessions")
    r = requests.post(f"{BASE_URL}/api/v1/chat/sessions")
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.json()}")
    session_id = r.json().get("session_id", "test_session_001")

    # 4. 获取会话历史
    print(f"\n[4] GET /api/v1/chat/history/{session_id}")
    r = requests.get(f"{BASE_URL}/api/v1/chat/history/{session_id}")
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.json()}")

    # 5. 获取会话上下文
    print(f"\n[5] GET /api/v1/chat/history/{session_id}/context")
    r = requests.get(f"{BASE_URL}/api/v1/chat/history/{session_id}/context")
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.json()}")

    # 6. 启动学习会话
    print("\n[6] POST /api/v1/chat/session/start")
    payload = {
        "lesson_id": "lesson_001",
        "mode": "learning",
        "current_path": "/chapter1/section1"
    }
    r = requests.post(f"{BASE_URL}/api/v1/chat/session/start", json=payload)
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.json()}")
    learning_session_id = r.json().get("session_id", "learn_001")

    # 7. 获取学习进度
    print(f"\n[7] GET /api/v1/chat/db/learning-progress/{learning_session_id}")
    r = requests.get(f"{BASE_URL}/api/v1/chat/db/learning-progress/{learning_session_id}")
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.json()}")

    # 8. 获取指标
    print("\n[8] GET /api/v1/chat/metrics")
    r = requests.get(f"{BASE_URL}/api/v1/chat/metrics")
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.json()}")

    # 9. SSE 端点测试
    print("\n[9] GET /api/v1/chat/sse (使用 query 参数)")
    r = requests.get(f"{BASE_URL}/api/v1/chat/sse", params={"query": "你好"}, stream=True)
    print(f"状态码: {r.status_code}")
    # 读取部分响应
    content = b""
    for chunk in r.iter_content(chunk_size=1024):
        content += chunk
        if len(content) > 500:
            break
    print(f"响应内容 (前500字节): {content[:500]}")

    print("\n" + "=" * 60)
    print("REST API 测试完成")
    print("=" * 60)

async def test_websocket():
    """测试 WebSocket 端点"""
    print("\n" + "=" * 60)
    print("测试 WebSocket /api/v1/chat/ws")
    print("=" * 60)

    try:
        async with websockets.connect(f"{WS_URL}/api/v1/chat/ws") as ws:
            # 发送消息
            message = {
                "query": "你好",
                "session_id": "ws_test_001",
                "current_path": "/chapter1"
            }
            await ws.send(json.dumps(message))
            print(f"发送消息: {message}")

            # 接收响应
            response_count = 0
            async for msg in ws:
                print(f"收到消息 {response_count + 1}: {msg[:200]}...")
                response_count += 1
                if response_count >= 5:  # 限制接收消息数量
                    break
            print(f"共收到 {response_count} 条消息")
    except Exception as e:
        print(f"WebSocket 测试错误: {e}")

    print("\n" + "=" * 60)
    print("WebSocket 测试完成")
    print("=" * 60)

async def test_tts_websocket():
    """测试 TTS WebSocket 端点"""
    print("\n" + "=" * 60)
    print("测试 TTS WebSocket /api/v1/ws/script")
    print("=" * 60)

    try:
        async with websockets.connect(f"{WS_URL}/api/v1/ws/script") as ws:
            # 发送 TTS 请求
            message = {
                "service": "tts",
                "text": "你好，欢迎学习",
                "voice": "zh-CN-XiaoxiaoNeural"
            }
            await ws.send(json.dumps(message))
            print(f"发送 TTS 请求: {message}")

            # 接收音频数据
            audio_data = b""
            while True:
                msg = await ws.recv()
                if isinstance(msg, bytes):
                    if len(msg) == 0:
                        print("收到结束标志")
                        break
                    audio_data += msg
                    print(f"收到音频数据块: {len(msg)} bytes")
                else:
                    print(f"收到文本消息: {msg}")

            print(f"总音频数据: {len(audio_data)} bytes")
    except Exception as e:
        print(f"TTS WebSocket 测试错误: {e}")

    print("\n" + "=" * 60)
    print("TTS WebSocket 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    # 先测试 REST API
    test_rest_apis()

    # 测试 WebSocket (可选，因为可能需要较长时间)
    # asyncio.run(test_websocket())

    # 测试 TTS WebSocket (可选)
    # asyncio.run(test_tts_websocket())

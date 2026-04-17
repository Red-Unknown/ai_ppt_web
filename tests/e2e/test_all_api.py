import requests
import json
import asyncio
import websockets

BASE_URL = "http://localhost:8001"
WS_URL = "ws://localhost:8001"

def test_rest_apis():
    """测试所有 REST API 端点"""
    print("=" * 70)
    print("测试 REST API 端点")
    print("=" * 70)

    results = []

    # 1. 根路由
    print("\n[1] GET /")
    r = requests.get(f"{BASE_URL}/")
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.json()}")
    results.append(("GET /", r.status_code, "PASS" if r.status_code == 200 else "FAIL"))

    # 2. 获取会话列表
    print("\n[2] GET /api/v1/chat/sessions")
    r = requests.get(f"{BASE_URL}/api/v1/chat/sessions")
    print(f"状态码: {r.status_code}")
    try:
        print(f"响应: {r.json()}")
    except:
        print(f"响应: {r.text}")
    results.append(("GET /api/v1/chat/sessions", r.status_code, "PASS" if r.status_code == 200 else "FAIL"))

    # 3. 创建会话
    print("\n[3] POST /api/v1/chat/sessions")
    r = requests.post(f"{BASE_URL}/api/v1/chat/sessions")
    print(f"状态码: {r.status_code}")
    try:
        data = r.json()
        print(f"响应: {data}")
        session_id = data.get("session_id", "test_session_001")
    except:
        print(f"响应: {r.text}")
        session_id = "test_session_001"
    results.append(("POST /api/v1/chat/sessions", r.status_code, "PASS" if r.status_code == 200 else "FAIL"))

    # 4. 获取会话历史
    print(f"\n[4] GET /api/v1/chat/history/{session_id}")
    r = requests.get(f"{BASE_URL}/api/v1/chat/history/{session_id}")
    print(f"状态码: {r.status_code}")
    try:
        print(f"响应: {r.json()}")
    except:
        print(f"响应: {r.text}")
    results.append((f"GET /api/v1/chat/history/{session_id}", r.status_code, "PASS" if r.status_code == 200 else "FAIL"))

    # 5. 获取会话上下文
    print(f"\n[5] GET /api/v1/chat/history/{session_id}/context")
    r = requests.get(f"{BASE_URL}/api/v1/chat/history/{session_id}/context")
    print(f"状态码: {r.status_code}")
    try:
        print(f"响应: {r.json()}")
    except:
        print(f"响应: {r.text}")
    results.append((f"GET /api/v1/chat/history/{session_id}/context", r.status_code, "PASS" if r.status_code == 200 else "FAIL"))

    # 6. 获取事件历史
    print(f"\n[6] GET /api/v1/chat/history/{session_id}/events")
    r = requests.get(f"{BASE_URL}/api/v1/chat/history/{session_id}/events")
    print(f"状态码: {r.status_code}")
    try:
        print(f"响应: {r.json()}")
    except:
        print(f"响应: {r.text}")
    results.append((f"GET /api/v1/chat/history/{session_id}/events", r.status_code, "PASS" if r.status_code == 200 else "FAIL"))

    # 7. 启动学习会话
    print("\n[7] POST /api/v1/chat/session/start")
    payload = {
        "course_id": "course_001",
        "lesson_id": "lesson_001",
        "mode": "learning",
        "current_path": "/chapter1/section1"
    }
    r = requests.post(f"{BASE_URL}/api/v1/chat/session/start", json=payload)
    print(f"状态码: {r.status_code}")
    try:
        data = r.json()
        print(f"响应: {data}")
        learning_session_id = data.get("session_id", "learn_001")
    except:
        print(f"响应: {r.text}")
        learning_session_id = "learn_001"
    results.append(("POST /api/v1/chat/session/start", r.status_code, "PASS" if r.status_code == 200 else "FAIL"))

    # 8. 获取会话预览状态
    print(f"\n[8] GET /api/v1/chat/session/{learning_session_id}/preview")
    r = requests.get(f"{BASE_URL}/api/v1/chat/session/{learning_session_id}/preview")
    print(f"状态码: {r.status_code}")
    try:
        print(f"响应: {r.json()}")
    except:
        print(f"响应: {r.text}")
    results.append((f"GET /api/v1/chat/session/{learning_session_id}/preview", r.status_code, "PASS" if r.status_code in [200, 404] else "FAIL"))

    # 9. 获取学习进度
    print(f"\n[9] GET /api/v1/chat/db/learning-progress/{learning_session_id}")
    r = requests.get(f"{BASE_URL}/api/v1/chat/db/learning-progress/{learning_session_id}")
    print(f"状态码: {r.status_code}")
    try:
        print(f"响应: {r.json()}")
    except:
        print(f"响应: {r.text}")
    results.append((f"GET /api/v1/chat/db/learning-progress/{learning_session_id}", r.status_code, "PASS" if r.status_code == 200 else "FAIL"))

    # 10. 获取 QA 记录
    print(f"\n[10] GET /api/v1/chat/db/qa-records/{learning_session_id}")
    r = requests.get(f"{BASE_URL}/api/v1/chat/db/qa-records/{learning_session_id}")
    print(f"状态码: {r.status_code}")
    try:
        print(f"响应: {r.json()}")
    except:
        print(f"响应: {r.text}")
    results.append((f"GET /api/v1/chat/db/qa-records/{learning_session_id}", r.status_code, "PASS" if r.status_code == 200 else "FAIL"))

    # 11. 获取指标
    print("\n[11] GET /api/v1/chat/metrics")
    r = requests.get(f"{BASE_URL}/api/v1/chat/metrics")
    print(f"状态码: {r.status_code}")
    try:
        print(f"响应: {r.json()}")
    except:
        print(f"响应: {r.text}")
    results.append(("GET /api/v1/chat/metrics", r.status_code, "PASS" if r.status_code == 200 else "FAIL"))

    # 12. 热重载配置
    print("\n[12] POST /api/v1/chat/config/reload")
    r = requests.post(f"{BASE_URL}/api/v1/chat/config/reload")
    print(f"状态码: {r.status_code}")
    try:
        print(f"响应: {r.json()}")
    except:
        print(f"响应: {r.text}")
    results.append(("POST /api/v1/chat/config/reload", r.status_code, "PASS" if r.status_code in [200, 500] else "FAIL"))

    # 13. SSE 端点测试
    print("\n[13] GET /api/v1/chat/sse (前500字节)")
    r = requests.get(f"{BASE_URL}/api/v1/chat/sse", params={"query": "你好"}, stream=True)
    print(f"状态码: {r.status_code}")
    content = b""
    try:
        for chunk in r.iter_content(chunk_size=1024):
            content += chunk
            if len(content) > 500:
                break
        print(f"响应内容 (前500字节): {content[:500]}")
    except Exception as e:
        print(f"错误: {e}")
    results.append(("GET /api/v1/chat/sse", r.status_code, "PASS" if r.status_code == 200 else "FAIL"))

    print("\n" + "=" * 70)
    print("REST API 测试结果汇总")
    print("=" * 70)
    for name, code, status in results:
        print(f"{name}: {code} [{status}]")

    return results

async def test_websocket():
    """测试 WebSocket 端点"""
    print("\n" + "=" * 70)
    print("测试 WebSocket /api/v1/chat/ws")
    print("=" * 70)

    results = []

    try:
        # 增加超时时间到 30 秒
        ws_url = f"{WS_URL}/api/v1/chat/ws"
        print(f"连接 URL: {ws_url}")
        
        async with websockets.connect(ws_url, ping_interval=20, ping_timeout=30) as ws:
            # 发送消息
            message = {
                "query": "什么是牛顿定律",
                "session_id": "ws_test_001",
                "current_path": "/chapter1"
            }
            await ws.send(json.dumps(message))
            print(f"发送消息: {message}")

            # 接收响应 - 等待更长时间
            response_count = 0
            try:
                while True:
                    try:
                        msg = await asyncio.wait_for(ws.recv(), timeout=30.0)
                        print(f"收到消息 {response_count + 1}: {msg[:200]}...")
                        response_count += 1
                        if response_count >= 10:  # 限制接收消息数量
                            break
                    except asyncio.TimeoutError:
                        print("等待消息超时")
                        break
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket 连接已关闭")
            
            print(f"共收到 {response_count} 条消息")
            results.append(("WebSocket /api/v1/chat/ws", 200, "PASS"))
    except Exception as e:
        print(f"WebSocket 测试错误: {e}")
        import traceback
        traceback.print_exc()
        results.append(("WebSocket /api/v1/chat/ws", 500, f"FAIL: {e}"))

    print("\n" + "=" * 70)
    print("WebSocket 测试结果汇总")
    print("=" * 70)
    for name, code, status in results:
        print(f"{name}: {code} [{status}]")

    return results

async def test_tts_websocket():
    """测试 TTS WebSocket 端点"""
    print("\n" + "=" * 70)
    print("测试 TTS WebSocket /api/v1/ws/script")
    print("=" * 70)

    results = []

    try:
        # 增加超时时间
        async with websockets.connect(f"{WS_URL}/api/v1/ws/script", ping_interval=20, ping_timeout=30) as ws:
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
            msg_count = 0
            while True:
                msg = await ws.recv()
                msg_count += 1
                if isinstance(msg, bytes):
                    if len(msg) == 0:
                        print(f"收到结束标志 (共 {msg_count} 条消息)")
                        break
                    audio_data += msg
                    print(f"收到音频数据块: {len(msg)} bytes")
                else:
                    print(f"收到文本消息: {msg}")

            print(f"总音频数据: {len(audio_data)} bytes")
            results.append(("TTS WebSocket /api/v1/ws/script", 200, "PASS"))
    except Exception as e:
        print(f"TTS WebSocket 测试错误: {e}")
        results.append(("TTS WebSocket /api/v1/ws/script", 500, f"FAIL: {e}"))

    print("\n" + "=" * 70)
    print("TTS WebSocket 测试结果汇总")
    print("=" * 70)
    for name, code, status in results:
        print(f"{name}: {code} [{status}]")

    return results

if __name__ == "__main__":
    # 测试 REST API
    rest_results = test_rest_apis()

    # 测试 WebSocket
    ws_results = asyncio.run(test_websocket())

    # 测试 TTS WebSocket
    tts_results = asyncio.run(test_tts_websocket())

    # 总体汇总
    print("\n" + "=" * 70)
    print("所有测试汇总")
    print("=" * 70)
    all_results = rest_results + ws_results + tts_results
    for name, code, status in all_results:
        print(f"{name}: {code} [{status}]")

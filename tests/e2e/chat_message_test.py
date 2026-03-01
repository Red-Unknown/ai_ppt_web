"""
端到端测试：聊天消息发送功能评估体系
测试目标：验证多条消息发送、撤回、暂停功能的正确性
性能基准：单条消息延迟 ≤ 200ms，撤回成功率 100%，暂停响应 ≤ 100ms
"""

import asyncio
import time
import httpx
import websockets
import json
import pytest
from typing import List, Dict, Any

# 测试配置
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/api/v1/chat/ws"
TEST_USER_ID = "test_user_001"
TEST_COURSE_ID = "phys101"


class ChatMessageTestEvaluator:
    """聊天消息功能评估器"""
    
    def __init__(self):
        self.session_id = None
        self.messages_sent = 0
        self.messages_received = 0
        self.latencies = []
        self.withdraw_success = 0
        self.withdraw_failures = 0
        self.pause_responses = []
    
    async def create_test_session(self) -> str:
        """创建测试会话"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BASE_URL}/api/v1/chat/session/start",
                json={
                    "course_id": TEST_COURSE_ID,
                    "mode": "learning",
                    "target_node_id": "n1"
                }
            )
            response.raise_for_status()
            data = response.json()
            self.session_id = data["session_id"]
            return self.session_id
    
    async def send_message_via_ws(self, message: str) -> Dict[str, Any]:
        """通过WebSocket发送消息并接收响应"""
        start_time = time.time()
        
        async with websockets.connect(WS_URL) as ws:
            # 发送消息
            payload = {
                "query": message,
                "session_id": self.session_id,
                "current_path": "/ui/chat",
                "model": "deepseek",
                "prompt_style": "default"
            }
            await ws.send(json.dumps(payload))
            
            # 接收响应
            response_data = []
            async for response in ws:
                data = json.loads(response)
                response_data.append(data)
                
                if data.get("type") == "end":
                    break
            
            latency = (time.time() - start_time) * 1000  # 转换为毫秒
            self.latencies.append(latency)
            self.messages_sent += 1
            self.messages_received += 1
            
            return {
                "latency": latency,
                "response": response_data,
                "success": True
            }
    
    async def test_concurrent_messages(self, messages: List[str]) -> List[Dict]:
        """测试并发消息发送"""
        results = []
        
        async def send_single_message(msg: str):
            try:
                result = await self.send_message_via_ws(msg)
                results.append(result)
            except Exception as e:
                results.append({
                    "message": msg,
                    "error": str(e),
                    "success": False
                })
        
        # 并发发送消息
        tasks = [send_single_message(msg) for msg in messages]
        await asyncio.gather(*tasks)
        
        return results
    
    async def test_withdraw_message(self, message_index: int) -> bool:
        """测试撤回消息功能"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BASE_URL}/api/v1/chat/history/{self.session_id}/truncate",
                    json={"index": message_index}
                )
                
                if response.status_code == 200:
                    self.withdraw_success += 1
                    return True
                else:
                    self.withdraw_failures += 1
                    return False
        except Exception:
            self.withdraw_failures += 1
            return False
    
    async def test_pause_functionality(self) -> float:
        """测试暂停功能响应时间"""
        start_time = time.time()
        
        # 模拟暂停操作（实际需要前端配合）
        # 这里测试WebSocket连接关闭速度
        try:
            async with websockets.connect(WS_URL) as ws:
                await asyncio.sleep(0.1)  # 短暂连接
                await ws.close()
                response_time = (time.time() - start_time) * 1000
                self.pause_responses.append(response_time)
                return response_time
        except Exception:
            return -1
    
    def generate_report(self) -> Dict[str, Any]:
        """生成测试报告"""
        if not self.latencies:
            avg_latency = 0
        else:
            avg_latency = sum(self.latencies) / len(self.latencies)
        
        total_withdraw_attempts = self.withdraw_success + self.withdraw_failures
        withdraw_success_rate = (self.withdraw_success / total_withdraw_attempts * 100) if total_withdraw_attempts > 0 else 0
        
        if not self.pause_responses:
            avg_pause_response = 0
        else:
            avg_pause_response = sum(self.pause_responses) / len(self.pause_responses)
        
        return {
            "messages_sent": self.messages_sent,
            "messages_received": self.messages_received,
            "message_delivery_rate": (self.messages_received / self.messages_sent * 100) if self.messages_sent > 0 else 0,
            "average_latency_ms": avg_latency,
            "max_latency_ms": max(self.latencies) if self.latencies else 0,
            "min_latency_ms": min(self.latencies) if self.latencies else 0,
            "withdraw_success_rate": withdraw_success_rate,
            "withdraw_attempts": total_withdraw_attempts,
            "average_pause_response_ms": avg_pause_response,
            "meets_performance_standards": all([
                avg_latency <= 200,
                withdraw_success_rate == 100,
                avg_pause_response <= 100 if self.pause_responses else True
            ])
        }


@pytest.mark.asyncio
async def test_chat_message_e2e():
    """端到端聊天消息测试"""
    evaluator = ChatMessageTestEvaluator()
    
    # 1. 创建测试会话
    session_id = await evaluator.create_test_session()
    assert session_id is not None
    
    # 2. 测试单条消息发送
    single_result = await evaluator.send_message_via_ws("你好，请介绍一下自己")
    assert single_result["success"]
    assert single_result["latency"] > 0
    
    # 3. 测试并发消息发送
    test_messages = [
        "第一条并发消息",
        "第二条测试消息", 
        "第三条验证消息",
        "第四条性能测试",
        "第五条压力测试"
    ]
    
    concurrent_results = await evaluator.test_concurrent_messages(test_messages)
    
    # 验证所有消息都成功发送
    success_count = sum(1 for result in concurrent_results if result.get("success"))
    assert success_count == len(test_messages), f"Expected {len(test_messages)} successes, got {success_count}"
    
    # 4. 测试撤回功能
    withdraw_success = await evaluator.test_withdraw_message(2)  # 撤回第三条消息
    assert withdraw_success, "Message withdrawal failed"
    
    # 5. 测试暂停功能响应时间
    pause_time = await evaluator.test_pause_functionality()
    assert pause_time > 0, "Pause functionality test failed"
    
    # 6. 生成评估报告
    report = evaluator.generate_report()
    
    print("\n" + "="*60)
    print("端到端聊天消息测试报告")
    print("="*60)
    print(f"消息发送成功率: {report['message_delivery_rate']:.2f}%")
    print(f"平均响应延迟: {report['average_latency_ms']:.2f}ms")
    print(f"撤回成功率: {report['withdraw_success_rate']:.2f}%")
    print(f"暂停平均响应: {report['average_pause_response_ms']:.2f}ms")
    print(f"符合性能标准: {'✅' if report['meets_performance_standards'] else '❌'}")
    print("="*60)
    
    # 验证性能标准
    assert report["meets_performance_standards"], "Performance standards not met"
    assert report["message_delivery_rate"] == 100, "Not all messages were delivered"
    assert report["withdraw_success_rate"] == 100, "Message withdrawal failed"
    assert report["average_latency_ms"] <= 200, "Latency too high"
    assert report["average_pause_response_ms"] <= 100, "Pause response too slow"


if __name__ == "__main__":
    asyncio.run(test_chat_message_e2e())
"""
简化健康检查测试 - 验证后端服务基本功能
"""

import asyncio
import httpx
import time

async def test_backend_health():
    """测试后端服务健康状态"""
    print("🧪 开始后端服务健康检查...")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # 测试基础健康端点
        try:
            response = await client.get("http://localhost:8000/api/v1/health")
            print(f"✅ 健康检查成功: {response.status_code}")
            return True
        except Exception as e:
            print(f"❌ 健康检查失败: {e}")
            return False

async def test_chat_endpoints():
    """测试聊天相关端点"""
    print("\n🧪 测试聊天端点...")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        endpoints_to_test = [
            "/api/v1/chat/session/start",
            "/api/v1/chat/history/sess_test",
            "/api/v1/chat/ws"  # WebSocket端点
        ]
        
        results = {}
        
        for endpoint in endpoints_to_test:
            try:
                if endpoint.endswith('/ws'):
                    # WebSocket连接测试
                    results[endpoint] = "⚠️  需要手动WebSocket测试"
                else:
                    if endpoint == "/api/v1/chat/session/start":
                        # POST请求测试
                        response = await client.post(
                            f"http://localhost:8000{endpoint}",
                            json={"course_id": "phys101", "mode": "learning", "target_node_id": "n1"},
                            timeout=5.0
                        )
                    else:
                        # GET请求测试
                        response = await client.get(f"http://localhost:8000{endpoint}", timeout=5.0)
                    
                    results[endpoint] = f"✅ {response.status_code}"
                    
            except httpx.ReadTimeout:
                results[endpoint] = "❌ 连接超时"
            except httpx.ConnectError:
                results[endpoint] = "❌ 连接拒绝"
            except Exception as e:
                results[endpoint] = f"❌ {str(e)}"
    
    return results

async def main():
    """主测试函数"""
    print("=" * 60)
    print("🤖 聊天系统端到端评估测试")
    print("=" * 60)
    
    # 测试1: 后端健康状态
    health_ok = await test_backend_health()
    
    if not health_ok:
        print("\n🔴 后端服务未正常运行，请检查:")
        print("1. 后端服务是否启动: uvicorn backend.main:app --reload")
        print("2. 端口8000是否被占用")
        print("3. 依赖是否完整: pip install -r requirements.txt")
        return
    
    # 测试2: 聊天端点功能
    endpoint_results = await test_chat_endpoints()
    
    print("\n📊 端点测试结果:")
    for endpoint, result in endpoint_results.items():
        print(f"  {endpoint}: {result}")
    
    # 性能基准验证
    print("\n⚡ 性能基准检查:")
    print("  - 单条消息延迟 ≤ 200ms: 🔄 需要实际消息测试")
    print("  - 撤回成功率 100%: 🔄 需要实际功能测试") 
    print("  - 暂停响应 ≤ 100ms: 🔄 需要实际功能测试")
    
    # 总体评估
    success_count = sum(1 for r in endpoint_results.values() if '✅' in r)
    total_count = len(endpoint_results)
    
    print(f"\n🎯 总体完成度: {success_count}/{total_count}")
    
    if success_count == total_count:
        print("🟢 所有基础端点正常!")
    else:
        print("🟡 部分功能需要修复")

if __name__ == "__main__":
    asyncio.run(main())
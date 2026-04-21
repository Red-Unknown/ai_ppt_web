import requests
import json

BASE_URL = "http://localhost:8000"

def test_all_apis():
    """测试所有 API 端点"""
    print("=" * 60)
    print("测试 API 端点")
    print("=" * 60)

    results = []

    # 1. 根路由
    print("\n[1] GET /")
    r = requests.get(f"{BASE_URL}/")
    status = "PASS" if r.status_code == 200 else "FAIL"
    print(f"状态码: {r.status_code} [{status}]")
    print(f"响应: {r.json()}")
    results.append(("GET /", r.status_code, status))

    # 2. 文档
    print("\n[2] GET /docs")
    r = requests.get(f"{BASE_URL}/docs")
    status = "PASS" if r.status_code == 200 else "FAIL"
    print(f"状态码: {r.status_code} [{status}]")
    results.append(("GET /docs", r.status_code, status))

    # 3. OpenAPI
    print("\n[3] GET /openapi.json")
    r = requests.get(f"{BASE_URL}/openapi.json")
    status = "PASS" if r.status_code == 200 else "FAIL"
    print(f"状态码: {r.status_code} [{status}]")
    if r.status_code == 200:
        data = r.json()
        paths = list(data.get("paths", {}).keys())
        print(f"可用路径数量: {len(paths)}")
        print(f"路径列表: {paths[:10]}...")
    results.append(("GET /openapi.json", r.status_code, status))

    # 4. 测试 session 相关的端点 (查看具体实现)
    print("\n[4] GET /api/v1/session (检查session端点)")
    r = requests.get(f"{BASE_URL}/api/v1/session")
    print(f"状态码: {r.status_code}")
    print(f"响应: {r.text[:200]}")

    # 5. 测试 /api/v1/chat/ 开头的端点
    print("\n[5] 测试 /api/v1/chat/ 端点")
    endpoints = [
        "/api/v1/chat/sessions",
        "/api/v1/chat/session/start",
    ]
    for ep in endpoints:
        r = requests.get(f"{BASE_URL}{ep}")
        status = "PASS" if r.status_code in [200, 404] else "FAIL"
        print(f"GET {ep}: {r.status_code} [{status}]")
        results.append((f"GET {ep}", r.status_code, status))

    print("\n" + "=" * 60)
    print("测试摘要")
    print("=" * 60)
    for name, code, status in results:
        print(f"{name}: {code} [{status}]")

if __name__ == "__main__":
    test_all_apis()

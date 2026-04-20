import sys
sys.path.insert(0, 'f:/college/sophomore/服务外包')

from fastapi import FastAPI
from fastapi.testclient import TestClient
from backend.app.api.v1.endpoints import retrieval

app = FastAPI()
app.include_router(retrieval.router)

client = TestClient(app)

def test_retrieve_endpoint():
    response = client.post(
        "/qa/retrieve",
        json={"query": "什么是轴向拉伸", "lesson_id": "lesson_mm_001", "top_k": 3}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Code: {data.get('code')}")
    print(f"Has answer: {bool(data.get('data', {}).get('answer'))}")
    print(f"Has bbox_list: {len(data.get('data', {}).get('bbox_list', [])) > 0}")
    print(f"Has sources: {len(data.get('data', {}).get('sources', [])) > 0}")

def test_missing_lesson_id():
    response = client.post(
        "/qa/retrieve",
        json={"query": "test"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Code: {data.get('code')}")
    print(f"Message: {data.get('message')}")

def test_missing_query():
    response = client.post(
        "/qa/retrieve",
        json={"lesson_id": "lesson_mm_001"}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Code: {data.get('code')}")
    print(f"Message: {data.get('message')}")

if __name__ == "__main__":
    print("=== Test 1: 正常请求 ===")
    test_retrieve_endpoint()
    print("\n=== Test 2: 缺少 lesson_id ===")
    test_missing_lesson_id()
    print("\n=== Test 3: 缺少 query ===")
    test_missing_query()

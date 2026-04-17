import requests
import json

# 测试 Embedding 服务
EMBEDDING_URL = "http://localhost:8000/embedding"

def test_embedding_service():
    print("=" * 60)
    print("测试 Embedding 服务连接...")
    print("=" * 60)

    try:
        # 测试向量生成
        response = requests.post(
            EMBEDDING_URL,
            json={"data": ["测试向量"], "bDense": True, "bSparse": False},
            timeout=30
        )
        print(f"状态码: {response.status_code}")
        print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        return True
    except requests.exceptions.ConnectionError as e:
        print(f"❌ 连接失败: {e}")
        return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

if __name__ == "__main__":
    test_embedding_service()

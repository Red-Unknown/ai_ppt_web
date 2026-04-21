import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import importlib
from backend.app.core import config as core_config
from backend.app.core.config import Settings

settings = Settings()
print(f"QWEN_API_KEY: {settings.QWEN_API_KEY[:10]}..." if settings.QWEN_API_KEY else "QWEN_API_KEY: None")
print(f"QWEN_MODEL: {settings.QWEN_MODEL}")
print(f"QWEN_VISION_MODEL: {settings.QWEN_VISION_MODEL}")
print(f"QWEN_BASE_URL: {settings.QWEN_BASE_URL}")

core_config.settings = settings

from backend.app.utils import llm_pool as llm_pool_module
from backend.app.utils.llm_pool import initialize_pool, get_llm_client, release_llm_client, shutdown_pool
from langchain_core.messages import HumanMessage

llm_pool_module._global_pool = None


async def test_qwen_text():
    print("\n" + "=" * 50)
    print("测试 1: Qwen 文本模型")
    print("=" * 50)
    
    client = get_llm_client(model="qwen")
    try:
        response = await client.ainvoke([HumanMessage(content="你好，请用一句话介绍你自己")])
        print(f"回复: {response.content}")
        print("✅ 文本模型测试成功!")
    except Exception as e:
        print(f"❌ 文本模型测试失败: {e}")
    finally:
        release_llm_client(client)


async def test_qwen_vision():
    print("\n" + "=" * 50)
    print("测试 2: Qwen VL 视觉模型 (图片识别)")
    print("=" * 50)
    
    image_path = Path(__file__).parent / "sandbox" / "test.png"
    print(f"图片路径: {image_path}")
    print(f"图片存在: {image_path.exists()}")
    
    if not image_path.exists():
        print("❌ 图片文件不存在!")
        return
    
    import base64
    
    def encode_image_to_base64(image_path: Path) -> str:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    image_base64 = encode_image_to_base64(image_path)
    print(f"图片 base64 长度: {len(image_base64)}")
    
    client = get_llm_client(model="qwen-vl")
    try:
        message = HumanMessage(
            content=[
                {"type": "text", "text": "请描述这张图片的内容"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{image_base64}"}
                }
            ]
        )
        response = await client.ainvoke([message])
        print(f"回复: {response.content}")
        print("✅ 视觉模型测试成功!")
    except Exception as e:
        print(f"❌ 视觉模型测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        release_llm_client(client)


async def main():
    print("初始化 LLM 连接池...")
    initialize_pool()
    
    try:
        await test_qwen_text()
        await test_qwen_vision()
    finally:
        print("\n关闭连接池...")
        shutdown_pool()
    
    print("\n所有测试完成!")


if __name__ == "__main__":
    asyncio.run(main())

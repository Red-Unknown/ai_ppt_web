import asyncio
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT_DIR))

from backend.app.utils.llm_pool import (
    initialize_pool,
    get_llm_client,
    release_llm_client,
    shutdown_pool,
    LLMInvoker,
)


async def test_original_interface():
    print("=" * 60)
    print("测试1: 原有接口使用正常")
    print("=" * 60)

    initialize_pool()
    print("✓ 连接池初始化成功")

    client = get_llm_client("qa", timeout=30.0)
    try:
        from langchain_core.messages import HumanMessage
        response = await client.ainvoke([
            HumanMessage(content="你好，请用一句话介绍自己")
        ])
        print(f"✓ 调用成功: {response.content[:100]}")
        return True
    except Exception as e:
        print(f"✗ 调用失败: {str(e)[:200]}")
        return False
    finally:
        release_llm_client(client)


async def test_llm_invoker_stream():
    print("\n" + "=" * 60)
    print("测试2: LLMInvoker 流式调用")
    print("=" * 60)

    invoker = LLMInvoker(scenario="qa")
    try:
        from langchain_core.messages import HumanMessage

        print("开始流式调用...")
        result_content = ""
        async for chunk in invoker.astream_chat([HumanMessage(content="写一首关于春天的诗")]):
            if chunk.content:
                print(chunk.content, end="", flush=True)
                result_content += chunk.content

        print("\n✓ 流式调用成功")
        return True
    except Exception as e:
        print(f"\n✗ 流式调用失败: {str(e)[:200]}")
        return False
    finally:
        invoker.close()


async def test_deepseek_reasoner():
    print("\n" + "=" * 60)
    print("测试3: DeepSeek Reasoner 模式返回思考过程")
    print("=" * 60)

    invoker = LLMInvoker(scenario="reasoner", model="deepseek-reasoner")
    try:
        from langchain_core.messages import HumanMessage

        print("开始推理模型调用...")
        print("-" * 40)

        reasoning_content = ""
        answer_content = ""

        async for chunk in invoker.astream_reasoning([HumanMessage(content="计算 25 * 78 = ?")]):
            if chunk.reasoning:
                reasoning_content += chunk.reasoning
                print(f"[思考] {chunk.reasoning}", end="", flush=True)

            if chunk.content:
                answer_content += chunk.content
                print(f"[回答] {chunk.content}", end="", flush=True)

        print("\n" + "-" * 40)

        if reasoning_content:
            print(f"✓ 成功获取思考过程，长度: {len(reasoning_content)} 字符")
            print(f"思考过程预览: {reasoning_content[:200]}...")
        else:
            print("⚠ 未获取到思考过程")

        if answer_content:
            print(f"✓ 成功获取回答: {answer_content}")

        return bool(reasoning_content or answer_content)

    except Exception as e:
        print(f"\n✗ Reasoner 调用失败: {str(e)[:200]}")
        return False
    finally:
        invoker.close()


async def main():
    try:
        results = []

        result1 = await test_original_interface()
        results.append(("原有接口", result1))

        result2 = await test_llm_invoker_stream()
        results.append(("LLMInvoker流式", result2))

        result3 = await test_deepseek_reasoner()
        results.append(("DeepSeek Reasoner", result3))

        print("\n" + "=" * 60)
        print("测试结果汇总")
        print("=" * 60)
        for name, result in results:
            status = "✓ 通过" if result else "✗ 失败"
            print(f"{name}: {status}")

        all_passed = all(r for _, r in results)
        print("\n" + ("全部测试通过!" if all_passed else "有测试失败!"))

    finally:
        shutdown_pool()
        print("\n✓ 连接池已关闭")


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
根据解析文本生成思维导图（可脚本执行，也可被服务调用）
"""
import asyncio
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Tuple

from backend.app.core.config import settings


SYSTEM_PROMPT = """你是一个专业的教育内容分析专家。你的任务是根据提供的课程讲义内容，分析其知识结构并生成树状思维导图。

要求：
1. 提取核心主题作为根节点
2. 识别主要章节作为一级子节点
3. 提取每个章节的关键概念、公式、原理作为二级及以下子节点
4. 保持内容的逻辑层次关系
5. 输出标准JSON格式，符合以下结构：
{
  "root": {
    "name": "主题名称",
    "children": [
      {"name": "章节1", "children": [{"name": "概念1"}]}
    ]
  }
}
只输出JSON，不要其他说明。
"""


def _extract_json(text: str) -> Dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("无法从模型输出中提取JSON")
    return json.loads(text[start : end + 1])


def _collect_keywords(mind_map: Dict[str, Any], limit: int = 30) -> List[str]:
    out: List[str] = []

    def walk(node: Dict[str, Any]) -> None:
        name = (node.get("name") or "").strip()
        if name and name not in out:
            out.append(name)
        for child in node.get("children", []) or []:
            if isinstance(child, dict):
                walk(child)

    root = (mind_map or {}).get("root")
    if isinstance(root, dict):
        walk(root)
    return out[:limit]


def generate_mindmap_sync(content: str) -> Tuple[Dict[str, Any], List[str]]:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage, SystemMessage

    api_key = settings.DEEPSEEK_API_KEY or os.getenv("DEEPSEEK_API_KEY", "")
    if not api_key:
        raise RuntimeError("未配置 DEEPSEEK_API_KEY")
    base_url = settings.DEEPSEEK_BASE_URL or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    llm = ChatOpenAI(
        model="deepseek-reasoner",
        api_key=api_key,
        base_url=base_url,
        temperature=0.3,
        max_tokens=4000,
    )
    prompt = f"请分析以下课程文本并生成思维导图JSON：\n\n{content[:12000]}"
    messages = [SystemMessage(content=SYSTEM_PROMPT), HumanMessage(content=prompt)]
    response = llm.invoke(messages)
    mind_map = _extract_json(str(response.content or ""))
    keywords = _collect_keywords(mind_map)
    return mind_map, keywords


async def generate_mindmap_async(content: str) -> Tuple[Dict[str, Any], List[str]]:
    return await asyncio.to_thread(generate_mindmap_sync, content)


def main() -> None:
    input_path = Path("sandbox/out_put.txt")
    output_path = Path("sandbox/mind_map.json")
    if not input_path.exists():
        raise FileNotFoundError(f"文件不存在: {input_path}")
    content = input_path.read_text(encoding="utf-8")
    mind_map, keywords = generate_mindmap_sync(content)
    payload = {"mind_map": mind_map, "keywords": keywords}
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ 思维导图已生成: {output_path}")


if __name__ == "__main__":
    main()

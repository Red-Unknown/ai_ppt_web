import os
import sys
import json
import asyncio
import time
from typing import List, Dict, Any

sys.path.insert(0, os.path.abspath("."))

from backend.app.services.qa.service import QAService
from backend.app.schemas.qa import ChatRequest
from langchain_core.documents import Document


def gen_mock_course() -> Dict[str, Any]:
    course = {
        "course_id": "phys101",
        "title": "大学物理·力学",
        "slides": [
            {"id": "s1", "title": "牛顿第二定律", "text": "F=ma 是力学的核心定律。"},
            {"id": "s2", "title": "功与能", "text": "功、动能、势能之间存在守恒关系。"},
            {"id": "s3", "title": "摩擦力", "text": "摩擦力方向与相对运动方向相反。"}
        ],
        "graph": {
            "nodes": [
                {"id": "n1", "path": "力学/牛顿定律/二定律", "content": "F=ma 描述力与加速度的关系。", "score": 0.92},
                {"id": "n2", "path": "力学/能量/功与能", "content": "能量守恒是重要定律。", "score": 0.88}
            ],
            "edges": [
                {"from": "n1", "to": "n2", "type": "relates"}
            ]
        }
    }
    return course


def mock_docs_from_course(course: Dict[str, Any]) -> List[Document]:
    docs = []
    for node in course["graph"]["nodes"]:
        docs.append(Document(page_content=node["content"], metadata={"id": node["id"], "score": node["score"]}))
    return docs


async def run_flow():
    os.environ.setdefault("DEEPSEEK_API_KEY", "sk-mock-key")
    os.environ.setdefault("DEEPSEEK_MODEL", "deepseek-chat")
    service = QAService()

    course = gen_mock_course()
    docs = mock_docs_from_course(course)

    # Monkeypatch retriever.invoke
    service.retriever.invoke = lambda q: docs

    # Assertions for mock integrity
    assert len(course["slides"]) > 0
    assert len(course["graph"]["nodes"]) >= 2
    assert docs[0].metadata.get("score", 0) > 0

    request = ChatRequest(query="牛顿第二定律是什么？", session_id="sess_xzh", current_path="力学/牛顿定律", top_k=3)
    chunks = []
    async for chunk in service.stream_answer_question(request, user_id="xzh_user"):
        chunks.append(json.loads(chunk))

    tokens = "".join([c.get("content", "") for c in chunks if c.get("type") == "token"])
    assert isinstance(tokens, str)

    suggestions = None
    for c in chunks:
        if c.get("type") == "suggestions":
            suggestions = c.get("content")
    assert suggestions and len(suggestions) == 3

    # Second call to check disk cache hit
    chunks2 = []
    async for chunk in service.stream_answer_question(request, user_id="xzh_user"):
        chunks2.append(json.loads(chunk))
    actions = [c.get("action") for c in chunks2 if c.get("type") == "start"]
    assert "DISK_CACHE_HIT" in actions

    print("Flow OK. Tokens length:", len(tokens))
    print("Suggestions:", suggestions)


if __name__ == "__main__":
    asyncio.run(run_flow())

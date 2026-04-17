import logging
import asyncio
from typing import Dict, Any, List
from backend.app.services.qa.tools.base import BaseSkill
from backend.app.services.qa.retrieval.two_layer_retriever import TwoLayerRetriever
from langchain_openai import ChatOpenAI
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class LocalKnowledgeTool(BaseSkill):
    def __init__(self, retriever: TwoLayerRetriever, llm: ChatOpenAI):
        self.retriever = retriever
        self.llm = llm

    @property
    def name(self) -> str:
        return "local_knowledge"

    @property
    def description(self) -> str:
        return (
            "Search the local course knowledge base (RAG). "
            "Use this for questions about course content, definitions, comparisons, or specific details. "
            "Automatically handles complex queries by breaking them down."
        )

    async def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Enhanced RAG Execution using TwoLayerRetriever:
        1. Decompose query (if complex).
        2. Multi-path retrieval.
        3. Aggregation.
        """
        try:
            lesson_id = kwargs.get("lesson_id", "lesson_mm_001")
            top_k = kwargs.get("top_k", 3)
            
            result = await self.retriever.retrieve(
                query=query,
                lesson_id=lesson_id,
                top_k=top_k
            )
            
            sources = result.get("sources", [])
            answer = result.get("answer", "")
            
            source_nodes = [s.get("node_id") for s in sources if s.get("node_id")]
            
            context_str = "\n\n".join([
                f"【来源：{s.get('path', '未知路径')}】\n内容：{s.get('content', '')}"
                for s in sources[:3]
            ])
            
            if not context_str:
                context_str = "No relevant information found in the knowledge base."
            
            return {
                "status": "success",
                "content": context_str,
                "details": {
                    "sub_queries": [query],
                    "source_nodes": source_nodes,
                    "answer": answer
                }
            }
        except Exception as e:
            logger.error(f"LocalKnowledgeTool error: {e}")
            return {"status": "error", "content": f"Error retrieving knowledge: {str(e)}"}

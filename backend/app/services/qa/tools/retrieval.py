import logging
import asyncio
from typing import Dict, Any, List
from backend.app.services.qa.tools.base import BaseSkill
from backend.app.services.qa.retrieval.tree_retriever import TreeStructureRetriever
from langchain_openai import ChatOpenAI
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

class LocalKnowledgeTool(BaseSkill):
    def __init__(self, retriever: TreeStructureRetriever, llm: ChatOpenAI):
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
        Enhanced RAG Execution:
        1. Decompose query (if complex).
        2. Multi-path retrieval.
        3. Aggregation.
        """
        try:
            # 1. Decompose
            sub_queries = await self._decompose_query(query)
            logger.info(f"Decomposed '{query}' into: {sub_queries}")

            # 2. Multi-path Retrieval (Parallel)
            # Use ainvoke for async retrieval if available, else wrap
            # Note: retriever.ainvoke returns List[Document]
            tasks = [self.retriever.ainvoke(q) for q in sub_queries]
            results = await asyncio.gather(*tasks)
            
            # Extract source node IDs safely
            source_nodes = []
            for result_list in results:
                for doc in result_list:
                    # Document objects might not have node_id, use metadata or hash
                    node_id = doc.metadata.get("id") or doc.metadata.get("source") or str(hash(doc.page_content))
                    source_nodes.append(node_id)

            # 3. Aggregate & Deduplicate
            aggregated_context = self._aggregate_results(results)
            
            return {
                "status": "success",
                "content": aggregated_context,
                "details": {
                    "sub_queries": sub_queries,
                    "source_nodes": source_nodes
                }
            }
        except Exception as e:
            logger.error(f"LocalKnowledgeTool error: {e}")
            return {"status": "error", "content": f"Error retrieving knowledge: {str(e)}"}

    async def _decompose_query(self, query: str) -> List[str]:
        """
        Decompose complex query into 2-3 sub-queries using LLM.
        """
        # Simple heuristic: if query is short, don't decompose
        if len(query) < 10:
            return [query]

        prompt = (
            f"Break down the following student question into 2-3 simple, independent search queries "
            f"to fully answer it. If the question is simple, just return it as is.\n"
            f"Question: {query}\n"
            f"Output ONLY the queries, one per line."
        )
        
        try:
            response = await self.llm.ainvoke(prompt)
            content = response.content.strip()
            queries = [q.strip("- ").strip() for q in content.split("\n") if q.strip()]
            return queries[:3] # Limit to 3
        except Exception as e:
            logger.warning(f"Decomposition failed: {e}. Using original query.")
            return [query]

    def _aggregate_results(self, results_list: List[List[Any]]) -> str:
        """
        Combine results from multiple retrievals.
        """
        seen_content = set()
        aggregated_text = []
        
        # Flatten and deduplicate
        all_nodes = []
        for nodes in results_list:
            for node in nodes:
                # Handle LangChain Document object
                content = getattr(node, "page_content", getattr(node, "text", str(node)))
                
                # Simple deduplication by content hash
                content_hash = hash(content)
                
                if content_hash not in seen_content:
                    seen_content.add(content_hash)
                    all_nodes.append(node)
        
        if not all_nodes:
            return "No relevant information found in the knowledge base."

        for i, node in enumerate(all_nodes, 1):
            content = getattr(node, "page_content", getattr(node, "text", str(node)))
            aggregated_text.append(f"[{i}] {content}")
            
        return "\n\n".join(aggregated_text)

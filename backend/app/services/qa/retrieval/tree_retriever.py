import json
from pathlib import Path
from typing import List, Optional, Any, Dict
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from pydantic import Field

class TreeStructureRetriever(BaseRetriever):
    """
    A custom retriever that combines vector similarity search with 
    tree-based structure expansion and path-aware reranking.
    """
    
    vector_store: Optional[Any] = None
    db_session: Optional[Any] = None
    top_k: int = 3
    current_path: Optional[str] = None
    
    def _load_knowledge_base(self) -> List[Dict]:
        """Load knowledge base from JSON file."""
        try:
            # backend/app/services/qa/retrieval/tree_retriever.py -> backend/app/core/knowledge_base.json
            # parent=retrieval, parent.parent=qa, parent.parent.parent=services, parent.parent.parent.parent=app
            kb_path = Path(__file__).resolve().parent.parent.parent.parent / "core" / "knowledge_base.json"
            
            if not kb_path.exists():
                print(f"Knowledge base not found at: {kb_path}")
                return []
            
            with open(kb_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            documents = []
            
            def traverse(node, current_path=""):
                if isinstance(node, dict):
                    # Check if it's a leaf node (has content)
                    if "content" in node and "path" in node:
                        documents.append(node)
                    else:
                        # Recursive traversal
                        for key, value in node.items():
                            traverse(value, current_path)
                elif isinstance(node, list):
                    for item in node:
                        traverse(item, current_path)
                            
            traverse(data.get("knowledge_tree", {}))
            return documents
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return []

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """
        Main retrieval logic:
        1. Keyword/Vector Search (Anchor Points)
        2. Tree Expansion (Context Enrichment)
        3. Path-aware Reranking (Relevance Tuning)
        """
        # 1. Search
        candidates = self._vector_search(query)
        
        # 2. Tree Expansion (Simplified for now)
        # expanded_candidates = self._expand_with_tree_context(candidates)
        
        # 3. Path Reranking
        final_results = self._rerank_by_path(candidates, self.current_path)
        
        return final_results[:self.top_k]

    def _vector_search(self, query: str) -> List[Document]:
        """
        Perform simple keyword search on local knowledge base if vector_store is not set.
        """
        if not self.vector_store:
            kb_docs = self._load_knowledge_base()
            results = []
            
            query_terms = query.lower().split()
            
            for doc in kb_docs:
                score = 0
                content = doc.get("content", "").lower()
                title = doc.get("title", "").lower()
                path = doc.get("path", "").lower()
                
                # Simple keyword matching scoring
                for term in query_terms:
                    if term in title:
                        score += 3  # Higher weight for title match
                    if term in content:
                        score += 1
                    if term in path:
                        score += 1
                        
                if score > 0:
                    results.append(
                        Document(
                            page_content=f"【{doc.get('title')}】\n{doc.get('content')}\n示例：{', '.join(doc.get('examples', []))}",
                            metadata={
                                "node_id": doc.get("id"),
                                "path": doc.get("path"),
                                "score": score,
                                "title": doc.get("title")
                            }
                        )
                    )
            
            # Sort by score
            results.sort(key=lambda x: x.metadata["score"], reverse=True)
            return results[:10]  # Return top 10 candidates
            
        return []

    def _expand_with_tree_context(self, candidates: List[Document]) -> List[Document]:
        """
        Enrich documents with parent context and sibling summaries.
        MOCKED: Adds dummy context.
        """
        for doc in candidates:
            # In real implementation, query PG for parent/siblings using doc.metadata['node_id']
            doc.metadata["context"] = {
                "parent": "Neural Network Optimization",
                "siblings": ["Learning Rate", "Activation Functions"]
            }
            # Append context to content or keep in metadata? 
            # Usually better to prepend context string for LLM.
            doc.page_content = f"[Context: {doc.metadata['context']['parent']}]\n{doc.page_content}"
        return candidates

    def _rerank_by_path(self, candidates: List[Document], current_path: Optional[str]) -> List[Document]:
        """
        Rerank documents based on path similarity with current_path.
        Formula: Score = alpha * VectorScore + beta * PathMatchScore
        """
        if not current_path:
            return candidates
            
        # Mock logic: Boost score if path starts with current_path
        for doc in candidates:
            doc_path = doc.metadata.get("path", "")
            if doc_path.startswith(current_path):
                # Simple boost
                doc.metadata["score"] = doc.metadata.get("score", 0) + 0.1
                doc.metadata["reranked"] = True
        
        # Sort by score descending
        candidates.sort(key=lambda x: x.metadata.get("score", 0), reverse=True)
        return candidates

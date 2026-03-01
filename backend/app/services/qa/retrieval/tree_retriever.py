import json
from pathlib import Path
from typing import List, Optional, Any, Dict
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from pydantic import Field, PrivateAttr

from .bm25 import SimpleBM25
from .embedding import SimpleEmbedder

class TreeStructureRetriever(BaseRetriever):
    """
    A custom retriever that combines vector similarity search with 
    tree-based structure expansion and path-aware reranking.
    Supports Hybrid Search: Dense + Sparse (BM25) + Keyword.
    """
    
    vector_store: Optional[Any] = None
    db_session: Optional[Any] = None
    top_k: int = 5
    current_path: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True
        extra = "allow"

    # Internal components
    _bm25: Optional[Any] = PrivateAttr(default=None)
    _embedder: Optional[Any] = PrivateAttr(default=None)
    _kb_docs: List[Dict] = PrivateAttr(default_factory=list)
    _doc_embeddings: List[List[float]] = PrivateAttr(default_factory=list)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Private attributes are initialized by Pydantic's PrivateAttr default_factory
        # We don't need to manually set them in __dict__ unless we want to reset them.
        # Calling _initialize_components will populate them.
        self._initialize_components()

    def _initialize_components(self) -> None:
        """Initialize KB, BM25, and Embedder."""
        self._kb_docs = self._load_knowledge_base()
        
        # Prepare corpus for BM25 (Title + Content)
        corpus = [
            f"{doc.get('title', '')} {doc.get('content', '')} {doc.get('synonyms', '')}" 
            for doc in self._kb_docs
        ]
        if corpus:
            self._bm25 = SimpleBM25(corpus)
            
        # Initialize Embedder
        self._embedder = SimpleEmbedder()
        
        # Pre-compute embeddings for KB docs (Mock or Real)
        # For real scenarios, this should be cached or stored in VectorDB.
        # Here we compute on startup (slow for large KB, okay for demo).
        if self._kb_docs:
            # We only embed titles + small content for speed in this demo
            self._doc_embeddings = [
                self._embedder.embed_query(f"{doc.get('title', '')} {doc.get('content', '')[:50]}")
                for doc in self._kb_docs
            ]

    def _load_knowledge_base(self) -> List[Dict]:
        """Load knowledge base from JSON file."""
        try:
            # backend/app/services/qa/retrieval/tree_retriever.py -> backend/app/core/knowledge_base.json
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
                        # Normalize synonyms
                        if "synonyms" not in node:
                            node["synonyms"] = []
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
        1. Hybrid Search (Dense + BM25 + Keyword)
        2. Tree Expansion (Context Enrichment)
        3. Path-aware Reranking (Relevance Tuning)
        """
        # 1. Search
        candidates = self._hybrid_search(query)
        
        # 2. Tree Expansion (Simplified for now)
        # expanded_candidates = self._expand_with_tree_context(candidates)
        
        # 3. Path Reranking
        final_results = self._rerank_by_path(candidates, self.current_path)
        
        return final_results[:self.top_k]

    def _hybrid_search(self, query: str) -> List[Document]:
        """
        Perform hybrid search: Dense (Vector) + Sparse (BM25) + Keyword (Fuzzy).
        """
        if not self._kb_docs:
            return []

        # Weights
        ALPHA = 0.4  # Dense
        BETA = 0.4   # BM25
        GAMMA = 0.2  # Keyword/Typo
        
        # 1. Dense Search
        query_embedding = self._embedder.embed_query(query)
        dense_scores = self._cosine_similarity(query_embedding, self._doc_embeddings)
        
        # 2. BM25 Search
        bm25_scores = self._bm25.get_scores(query) if self._bm25 else [0] * len(self._kb_docs)
        # Normalize BM25 scores (simple min-max or log)
        max_bm25 = max(bm25_scores) if bm25_scores else 1
        if max_bm25 > 0:
            bm25_scores = [s / max_bm25 for s in bm25_scores]
            
        # 3. Keyword/Typo Search
        keyword_scores = self._keyword_search(query)
        
        # Combine Scores
        combined_results = []
        for i, doc in enumerate(self._kb_docs):
            # Ensure dense score is non-negative
            d_score = max(0, dense_scores[i])
            
            final_score = (
                ALPHA * d_score +
                BETA * bm25_scores[i] +
                GAMMA * keyword_scores[i]
            )
            
            # Heuristic Confidence Threshold
            # 0.75 is high confidence
            
            if final_score > 0.05: # Low Threshold for candidates
                combined_results.append(
                    Document(
                        page_content=f"【{doc.get('title')}】\n{doc.get('content')}\n示例：{', '.join(doc.get('examples', []))}",
                        metadata={
                            "node_id": doc.get("id"),
                            "path": doc.get("path"),
                            "score": round(final_score, 4), # Keep 4 decimal places
                            "title": doc.get("title"),
                            "synonyms": doc.get("synonyms", [])
                        }
                    )
                )
        
        # Sort by score
        combined_results.sort(key=lambda x: x.metadata["score"], reverse=True)
        return combined_results[:10] # Top 10 candidates

    def _cosine_similarity(self, vec1: List[float], vecs: List[List[float]]) -> List[float]:
        """Compute cosine similarity between vec1 and a list of vectors."""
        scores = []
        norm1 = sum(x*x for x in vec1) ** 0.5
        for vec2 in vecs:
            dot = sum(a*b for a, b in zip(vec1, vec2))
            norm2 = sum(x*x for x in vec2) ** 0.5
            if norm1 > 0 and norm2 > 0:
                scores.append(dot / (norm1 * norm2))
            else:
                scores.append(0.0)
        return scores

    def _keyword_search(self, query: str) -> List[float]:
        """
        Keyword search with typo tolerance (Fuzzy matching on Title).
        """
        scores = []
        query_lower = query.lower()
        
        for doc in self._kb_docs:
            score = 0.0
            title = doc.get("title", "").lower()
            synonyms = [s.lower() for s in doc.get("synonyms", [])]
            
            # Exact match
            if query_lower in title:
                score = 1.0
            elif title in query_lower:
                score = 0.8
            
            # Synonym match
            for syn in synonyms:
                if query_lower in syn or syn in query_lower:
                    score = max(score, 0.9)
            
            # Typo tolerance (Simple char overlap / Levenshtein approximation)
            # If > 70% characters match, give some score
            if score < 0.5:
                common_chars = set(query_lower) & set(title)
                overlap = len(common_chars) / max(len(query_lower), len(title), 1)
                if overlap > 0.6:
                    score = 0.5 * overlap
            
            scores.append(score)
        return scores
            
    def _vector_search(self, query: str) -> List[Document]:
        """Legacy method kept for compatibility, redirects to hybrid search."""
        return self._hybrid_search(query)

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

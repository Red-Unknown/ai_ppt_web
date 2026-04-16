import json
from pathlib import Path
from typing import List, Optional, Any, Dict
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from pydantic import Field, PrivateAttr
import logging

logger = logging.getLogger(__name__)

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
                logger.warning(f"[MOCK_DATA] Knowledge base not found at: {kb_path}, using mock data")
                return self._get_mock_knowledge_base()

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
            logger.warning(f"[MOCK_DATA] Error loading knowledge base: {e}, using mock data")
            return self._get_mock_knowledge_base()

    def _get_mock_knowledge_base(self) -> List[Dict]:
        """Return mock knowledge base data when real KB is unavailable."""
        logger.info("[MOCK_DATA] Loading mock knowledge base for retrieval")
        return [
            {
                "id": "mock_node_001",
                "title": "课程介绍",
                "content": "[MOCK_DATA] 本课程是《大学物理》，主要涵盖力学、热学、电磁学、光学和量子力学等基础内容。课程目标是培养学生理解自然界的基本规律和分析问题的能力。",
                "path": "/course/intro",
                "synonyms": ["课程简介", "课程大纲"],
                "examples": ["力学基础", "热学原理"]
            },
            {
                "id": "mock_node_002",
                "title": "评分标准",
                "content": "[MOCK_DATA] 平时成绩占40%（包含作业、课堂签到、互动讨论），期末考试占60%。作业需要在每周周五前提交，迟到扣分。",
                "path": "/course/grading",
                "synonyms": ["成绩评定", "考核方式"],
                "examples": ["平时成绩", "期末考试"]
            },
            {
                "id": "mock_node_003",
                "title": "第一讲：质点运动学",
                "content": "[MOCK_DATA] 质点运动学主要研究质点的位置、速度和加速度随时间的变化关系。描述质点运动需要参考系、坐标系和时间。",
                "path": "/course/mechanics/kinematics",
                "synonyms": ["运动学", "位移速度"],
                "examples": ["匀速直线运动", "匀加速直线运动"]
            }
        ]

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """
        Main retrieval logic:
        1. Hybrid Search (Dense + BM25 + Keyword)
        2. Tree Expansion (Context Enrichment)
        3. Path-aware Reranking (Relevance Tuning)
        4. Visual Data Injection (Mock for Demo)
        """
        # 1. Search
        candidates = self._hybrid_search(query)
        
        # 2. Tree Expansion (Simplified for now)
        # expanded_candidates = self._expand_with_tree_context(candidates)
        
        # 3. Path Reranking
        final_results = self._rerank_by_path(candidates, self.current_path)
        
        # 4. Inject Visual Mock Data (For "Show, Don't Just Tell")
        final_results = self._inject_visual_mock_data(final_results)
        
        return final_results[:self.top_k]

    def _inject_visual_mock_data(self, documents: List[Document]) -> List[Document]:
        """
        Injects mock bounding boxes and image URLs for visual grounding.
        If real data is missing, this ensures the frontend has something to display.
        """
        import random
        
        # Mock Slide Images (Placeholder Service)
        BASE_SLIDE_URL = "https://cdn.example.com/slides/course_101"
        
        for i, doc in enumerate(documents):
            # 1. Page Number (Mock if missing)
            if "page_num" not in doc.metadata:
                # Deterministic pseudo-random based on title length
                doc.metadata["page_num"] = (len(doc.metadata.get("title", "")) % 20) + 1
            
            # 2. Image URL
            if "image_url" not in doc.metadata:
                page = doc.metadata["page_num"]
                doc.metadata["image_url"] = f"{BASE_SLIDE_URL}/slide_{page:02d}.jpg"
                
            # 3. Bounding Box [x, y, w, h] (Normalized 0-1)
            # Mocking different regions: Header, Content, Footer
            if "bbox" not in doc.metadata:
                region_type = i % 3
                if region_type == 0: # Top (Header/Title)
                    doc.metadata["bbox"] = [0.1, 0.1, 0.8, 0.15]
                elif region_type == 1: # Middle (Main Content)
                    doc.metadata["bbox"] = [0.1, 0.3, 0.8, 0.4]
                else: # Specific Chart/Diagram area
                    doc.metadata["bbox"] = [0.5, 0.4, 0.4, 0.3]
                    
        return documents

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

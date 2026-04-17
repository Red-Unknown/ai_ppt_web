from typing import List, Dict, Optional, Any
import math
from collections import Counter
import logging

logger = logging.getLogger(__name__)

class SimpleEmbedder:
    def __init__(self, api_key: str = None, base_url: str = None):
        import os
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.base_url = base_url or os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.use_openai = False

        if self.api_key:
            try:
                from langchain_openai import OpenAIEmbeddings
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=self.api_key,
                    openai_api_base=self.base_url,
                    model="deepseek-chat"
                )
                self.use_openai = True
            except ImportError:
                pass
            except Exception:
                pass

    def embed_query(self, text: str) -> List[float]:
        if self.use_openai:
            try:
                return self.embeddings.embed_query(text)
            except Exception:
                return self._mock_embed(text)
        return self._mock_embed(text)

    def _mock_embed(self, text: str, dim: int = 128) -> List[float]:
        vector = [0.0] * dim
        for i, char in enumerate(text):
            idx = ord(char) % dim
            vector[idx] += 1.0 / (i + 1)

        norm = sum(x*x for x in vector) ** 0.5
        if norm > 0:
            vector = [x/norm for x in vector]
        logger.debug(f"[MOCK_DATA] Generated mock embedding vector for: {text[:50]}")
        return vector


class SimpleBM25:
    def __init__(self, corpus: List[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus)
        self.avgdl = 0
        self.doc_freqs = []
        self.idf = {}
        self.doc_len = []
        self.corpus = corpus

        self._initialize()

    def _initialize(self):
        total_len = 0
        for doc in self.corpus:
            tokens = self._tokenize(doc)
            self.doc_len.append(len(tokens))
            total_len += len(tokens)

            frequencies = Counter(tokens)
            self.doc_freqs.append(frequencies)

            for token in frequencies:
                self.idf[token] = self.idf.get(token, 0) + 1

        self.avgdl = total_len / self.corpus_size if self.corpus_size > 0 else 0

        for token, freq in self.idf.items():
            self.idf[token] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1)

    def _tokenize(self, text: str) -> List[str]:
        if all(ord(c) < 128 for c in text[:50]):
            return text.lower().split()

        tokens = list(text)
        for i in range(len(text) - 1):
            tokens.append(text[i:i+2])
        return tokens

    def get_scores(self, query: str) -> List[float]:
        query_tokens = self._tokenize(query)
        scores = [0.0] * self.corpus_size

        for i in range(self.corpus_size):
            score = 0
            doc_freq = self.doc_freqs[i]
            doc_len = self.doc_len[i]

            for token in query_tokens:
                if token not in doc_freq:
                    continue

                freq = doc_freq[token]
                numerator = self.idf.get(token, 0) * freq * (self.k1 + 1)
                denominator = freq + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
                score += numerator / denominator

            scores[i] = score
        return scores


class HybridSearchEngine:
    def __init__(self):
        self.embedder = SimpleEmbedder()
        self.bm25 = None
        self.corpus_cache: Dict[str, List[str]] = {}

    def _normalize_scores(self, scores: List[float]) -> List[float]:
        if not scores:
            return []
        min_s = min(scores)
        max_s = max(scores)
        if max_s == min_s:
            return [1.0] * len(scores)
        return [(s - min_s) / (max_s - min_s) for s in scores]

    def _cosine_similarity(self, query_vec: List[float], doc_vectors: List[List[float]]) -> List[float]:
        scores = []
        norm1 = sum(x*x for x in query_vec) ** 0.5
        for vec2 in doc_vectors:
            dot = sum(a*b for a, b in zip(query_vec, vec2))
            norm2 = sum(x*x for x in vec2) ** 0.5
            if norm1 > 0 and norm2 > 0:
                scores.append(dot / (norm1 * norm2))
            else:
                scores.append(0.0)
        return scores

    def _keyword_search(self, query: str, documents: List[Dict]) -> List[float]:
        scores = []
        query_lower = query.lower()

        for doc in documents:
            score = 0.0
            search_text = ""
            if isinstance(doc, dict):
                for key in doc:
                    val = doc[key]
                    if isinstance(val, str):
                        search_text += val.lower() + " "
                    elif isinstance(val, list):
                        for item in val:
                            if isinstance(item, str):
                                search_text += item.lower() + " "
                            elif isinstance(item, dict):
                                for v in item.values():
                                    if isinstance(v, str):
                                        search_text += v.lower() + " "

            if query_lower in search_text:
                score = 1.0

            common_chars = set(query_lower) & set(search_text)
            overlap = len(common_chars) / max(len(query_lower), len(search_text), 1)
            if overlap > 0.3:
                score = max(score, overlap * 0.5)

            scores.append(score)
        return scores

    def _prepare_doc_text(self, doc: Dict, fields: List[str]) -> str:
        parts = []
        for field in fields:
            if field in doc:
                val = doc[field]
                if isinstance(val, list):
                    parts.append(" ".join(str(v) for v in val))
                elif val:
                    parts.append(str(val))
        return " ".join(parts)

    def search(
        self,
        query: str,
        documents: List[Dict],
        search_fields: List[str],
        top_k: int = 5,
        alpha: float = 0.4,
        beta: float = 0.4,
        gamma: float = 0.2
    ) -> List[Dict]:
        if not documents:
            return []

        corpus = [self._prepare_doc_text(d, search_fields) for d in documents]

        query_vec = self.embedder.embed_query(query)
        doc_vectors = [self.embedder.embed_query(text) for text in corpus]
        dense_scores = self._cosine_similarity(query_vec, doc_vectors)

        if self.bm25 is None or len(self.bm25.corpus) != len(corpus):
            self.bm25 = SimpleBM25(corpus)
        bm25_scores = self.bm25.get_scores(query)

        keyword_scores = self._keyword_search(query, documents)

        norm_dense = self._normalize_scores(dense_scores)
        norm_bm25 = self._normalize_scores(bm25_scores)

        results = []
        for i, doc in enumerate(documents):
            d_score = norm_dense[i] if i < len(norm_dense) else 0
            b_score = norm_bm25[i] if i < len(norm_bm25) else 0
            k_score = keyword_scores[i] if i < len(keyword_scores) else 0

            final_score = alpha * d_score + beta * b_score + gamma * k_score

            result = {**doc, "score": round(final_score, 4)}
            results.append(result)

        results.sort(key=lambda x: x.get("score", 0), reverse=True)
        return results[:top_k]

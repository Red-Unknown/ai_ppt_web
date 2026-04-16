from typing import List
import os
import requests
import logging
import hashlib

logger = logging.getLogger(__name__)


class SimpleEmbedder:
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url
        self.embedding_url = os.getenv("EMBEDDING_SERVICE_URL", "http://localhost:8000/embedding")

    def embed_query(self, text: str) -> List[float]:
        try:
            response = requests.post(
                self.embedding_url,
                json={"data": [text], "bDense": True, "bSparse": False},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            if result.get("success") and result.get("data"):
                return result["data"][0]
            raise ValueError(f"Embedding service returned error: {result}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"[MOCK_EMBED] Embedding service unavailable: {e}, using mock vector")
            return self._mock_embed(text)
        except Exception as e:
            logger.warning(f"[MOCK_EMBED] Embedding service error: {e}, using mock vector")
            return self._mock_embed(text)

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        try:
            response = requests.post(
                self.embedding_url,
                json={"data": texts, "bDense": True, "bSparse": False},
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            if result.get("success") and result.get("data"):
                return result["data"]
            raise ValueError(f"Embedding service returned error: {result}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"[MOCK_EMBED] Embedding service unavailable: {e}, using mock vectors")
            return [self._mock_embed(text) for text in texts]
        except Exception as e:
            logger.warning(f"[MOCK_EMBED] Embedding service error: {e}, using mock vectors")
            return [self._mock_embed(text) for text in texts]

    def _mock_embed(self, text: str, dim: int = 128) -> List[float]:
        hash_input = f"{text}_mock" if not text.endswith("_mock") else text
        hash_bytes = hashlib.sha256(hash_input.encode()).digest()
        vector = []
        for i in range(dim):
            if i < len(hash_bytes):
                vector.append((hash_bytes[i] / 255.0) * 2 - 1)
            else:
                vector.append(0.0)
        norm = sum(x*x for x in vector) ** 0.5
        if norm > 0:
            vector = [x/norm for x in vector]
        logger.debug(f"[MOCK_EMBED] Generated mock vector for text: {text[:50]}")
        return vector

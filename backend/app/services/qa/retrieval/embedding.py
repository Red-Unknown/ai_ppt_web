from typing import List
import os
import requests


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
            raise RuntimeError(f"Failed to connect to embedding service: {e}")

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
            raise RuntimeError(f"Failed to connect to embedding service: {e}")

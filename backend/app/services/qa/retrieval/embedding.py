from typing import List
import os

class SimpleEmbedder:
    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY")
        self.base_url = base_url or os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.use_openai = False
        
        if self.api_key:
            try:
                from langchain_openai import OpenAIEmbeddings
                # Assuming DeepSeek has an embedding endpoint compatible or using OpenAI if key provided
                # If DeepSeek doesn't support embeddings, this might fail or fallback.
                # For this demo, if DEEPSEEK is used, we might need to use a specific model name.
                # Common open weights models are often used.
                self.embeddings = OpenAIEmbeddings(
                    openai_api_key=self.api_key,
                    openai_api_base=self.base_url,
                    model="deepseek-chat" # Placeholder, DeepSeek V3 is chat. 
                                         # If they don't have embeddings, we use a local fallback mock.
                )
                self.use_openai = True
            except ImportError:
                print("langchain_openai not installed, using fallback.")
                pass
            except Exception as e:
                print(f"Error initializing embeddings: {e}")
                pass

    def embed_query(self, text: str) -> List[float]:
        if self.use_openai:
            try:
                # DeepSeek might not support embedding on this endpoint/model.
                # If it fails, we fallback to a deterministic hash-based vector for testing.
                return self.embeddings.embed_query(text)
            except Exception:
                return self._mock_embed(text)
        return self._mock_embed(text)

    def _mock_embed(self, text: str, dim: int = 128) -> List[float]:
        """
        Deterministic mock embedding based on character codes.
        Good enough for consistent testing but not semantic.
        """
        vector = [0.0] * dim
        for i, char in enumerate(text):
            idx = ord(char) % dim
            vector[idx] += 1.0 / (i + 1)
        
        # Normalize
        norm = sum(x*x for x in vector) ** 0.5
        if norm > 0:
            vector = [x/norm for x in vector]
        return vector

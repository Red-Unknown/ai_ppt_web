import math
from collections import Counter
from typing import List, Dict

class SimpleBM25:
    """
    A simple implementation of BM25 (Best Match 25) ranking algorithm.
    """
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
        
        # Calculate IDF
        for token, freq in self.idf.items():
            self.idf[token] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1)

    def _tokenize(self, text: str) -> List[str]:
        """
        Simple tokenizer. For Chinese, use character n-grams (1-gram + 2-gram).
        For English, split by space.
        """
        # Simple detection: if mostly ascii, treat as English-like
        if all(ord(c) < 128 for c in text[:50]):
            return text.lower().split()
        
        # Chinese: character based + bigrams
        tokens = list(text)
        # Add bigrams
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

    def get_top_n(self, query: str, n: int = 5) -> List[int]:
        scores = self.get_scores(query)
        # Return indices of top n scores
        return sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:n]

import sqlite3
import json
import hashlib
import os
import time
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

class LocalDiskCache:
    """
    A simple SQLite-based local disk cache for LLM responses.
    Implements LRU-like eviction policy based on last_accessed time.
    """
    def __init__(self, db_path: str = "cache.db", ttl_hours: int = 24):
        self.db_path = db_path
        self.ttl = ttl_hours * 3600
        self._init_db()
        self.metrics = {"hits": 0, "misses": 0}

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS llm_cache (
                    key TEXT PRIMARY KEY,
                    response TEXT,
                    created_at REAL,
                    last_accessed REAL
                )
            """)
            conn.commit()

    def _generate_key(self, prompt: str, params: Dict[str, Any]) -> str:
        """Generate a unique key based on prompt and parameters."""
        content = f"{prompt}|{json.dumps(params, sort_keys=True)}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get(self, prompt: str, params: Dict[str, Any]) -> Optional[str]:
        key = self._generate_key(prompt, params)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT response, created_at FROM llm_cache WHERE key = ?", (key,))
            row = cursor.fetchone()
            
            if row:
                response, created_at = row
                if time.time() - created_at > self.ttl:
                    # Expired
                    self.delete(key)
                    self.metrics["misses"] += 1
                    return None
                
                # Update last_accessed
                cursor.execute("UPDATE llm_cache SET last_accessed = ? WHERE key = ?", (time.time(), key))
                conn.commit()
                self.metrics["hits"] += 1
                return response
            
        self.metrics["misses"] += 1
        return None

    def set(self, prompt: str, params: Dict[str, Any], response: str):
        key = self._generate_key(prompt, params)
        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO llm_cache (key, response, created_at, last_accessed)
                VALUES (?, ?, ?, ?)
            """, (key, response, now, now))
            conn.commit()

    def delete(self, key: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM llm_cache WHERE key = ?", (key,))
            conn.commit()

    def clear(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM llm_cache")
            conn.commit()

    def get_metrics(self) -> Dict[str, Any]:
        total = self.metrics["hits"] + self.metrics["misses"]
        hit_rate = (self.metrics["hits"] / total) * 100 if total > 0 else 0.0
        return {
            "hits": self.metrics["hits"],
            "misses": self.metrics["misses"],
            "total_requests": total,
            "hit_rate": f"{hit_rate:.2f}%"
        }

# Singleton instance
local_cache = LocalDiskCache()

import asyncio
from typing import Dict, Any, List, Optional
import logging
import os
import json
import hashlib
from datetime import datetime, timedelta
from backend.app.core.context import session_id_ctx, request_id_ctx
from backend.app.services.session.manager import SessionManager
from backend.app.core.config import settings
from backend.app.services.qa.tools.base import BaseSkill

logger = logging.getLogger(__name__)

# Cache for frequent queries
_query_cache = {}
_CACHE_TTL = timedelta(hours=1)
_CACHE_MAX_SIZE = 1000


class WebSearchSkill(BaseSkill):
    """
    Web Search Skill using Tavily API for DeepSeek LLM.
    Provides real-time web search capabilities.
    """

    def __init__(self):
        self.engine = "tavily"
        # 从环境变量获取 Tavily API Key
        self.tavily_api_key = os.environ.get("TAVILY_API_KEY")
        
        if not self.tavily_api_key:
            logger.warning("TAVILY_API_KEY not configured. Web search will be unavailable.")
            self.engine = "none"
        else:
            masked_key = self.tavily_api_key[:8] + "..." if len(self.tavily_api_key) > 8 else "***"
            logger.info(f"WebSearchSkill initialized with Tavily API. API Key: {masked_key}")

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web for real-time information using Tavily API."

    def _get_cache_key(self, query: str) -> str:
        """Generate cache key for query."""
        return hashlib.md5(query.encode()).hexdigest()

    def _get_from_cache(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached result for query."""
        cache_key = self._get_cache_key(query)
        if cache_key in _query_cache:
            cached_data, timestamp = _query_cache[cache_key]
            if datetime.now() - timestamp < _CACHE_TTL:
                logger.info(f"Cache hit for query: {query}")
                return cached_data
            else:
                del _query_cache[cache_key]
        return None

    def _save_to_cache(self, query: str, result: Dict[str, Any]):
        """Save result to cache."""
        if len(_query_cache) >= _CACHE_MAX_SIZE:
            oldest_key = min(_query_cache.keys(), key=lambda k: _query_cache[k][1])
            del _query_cache[oldest_key]

        cache_key = self._get_cache_key(query)
        _query_cache[cache_key] = (result, datetime.now())
        logger.info(f"Saved to cache: {query}")

    async def _call_tavily_search(self, query: str) -> Dict[str, Any]:
        """
        Call Tavily API for web search.
        """
        import aiohttp

        headers = {
            "Content-Type": "application/json"
        }

        payload = {
            "api_key": self.tavily_api_key,
            "query": query,
            "search_depth": "basic",
            "include_answer": True,
            "include_raw_content": False,
            "max_results": 5
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.tavily.com/search",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Tavily API error: {response.status} - {error_text}")

                return await response.json()

    def _parse_tavily_response(self, response: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """
        Parse Tavily API response.
        """
        answer = response.get("answer", "")
        results = response.get("results", [])
        
        sources = []
        for result in results:
            sources.append({
                "title": result.get("title", "Untitled"),
                "link": result.get("url", ""),
                "snippet": result.get("content", "")
            })

        process_steps = [
            f"Query sent to Tavily API: {original_query}",
            f"Retrieved {len(results)} search results"
        ]

        return {
            "content": answer,
            "sources": sources,
            "process_steps": process_steps,
            "raw_response": response
        }

    async def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Execute web search using Tavily API.
        """
        import time
        start_time = time.time()
        request_id = request_id_ctx.get() or kwargs.get("request_id", "unknown")

        # Check cache first
        cached_result = self._get_from_cache(query)
        if cached_result:
            cached_result["details"]["cache_hit"] = True
            cached_result["details"]["latency_ms"] = 1
            return cached_result

        # Check session quota
        session_id = session_id_ctx.get()
        if not session_id:
            logger.error(f"[ReqID:{request_id}] No session_id found in context.")
            return {
                "status": "success",
                "content": "System Error: Session context missing.",
                "details": {"error": "Missing Session ID"}
            }

        if not SessionManager.try_acquire_search_quota(session_id):
            logger.warning(f"[ReqID:{request_id}] Search quota exceeded for session {session_id}.")
            return {
                "status": "success",
                "content": "System Notification: Web search quota for this session is exhausted (Limit: 1).",
                "details": {
                    "error_message": "Search limit reached",
                    "type": "limit_exceeded"
                }
            }

        if self.engine == "none":
            return {
                "status": "success",
                "content": "Web search is not configured. Please set TAVILY_API_KEY environment variable.",
                "details": {
                    "error": "Tavily API not configured",
                    "type": "web_search_results",
                    "engine": "none",
                    "sources": []
                }
            }

        try:
            logger.info(f"[ReqID:{request_id}] Executing web search via Tavily API: {query}")

            # Call Tavily API
            tavily_response = await self._call_tavily_search(query)

            # Parse response
            parsed = self._parse_tavily_response(tavily_response, query)

            latency_ms = int((time.time() - start_time) * 1000)
            logger.info(f"[ReqID:{request_id}] Tavily search completed. Latency: {latency_ms}ms")

            result = {
                "status": "success",
                "content": parsed["content"],
                "details": {
                    "raw_output": json.dumps(parsed["raw_response"], ensure_ascii=False),
                    "sources": parsed["sources"],
                    "type": "web_search_results",
                    "engine": "tavily",
                    "latency_ms": latency_ms,
                    "status_code": 200,
                    "request_id": request_id,
                    "process": parsed["process_steps"],
                    "cache_hit": False
                }
            }

            # Save to cache
            self._save_to_cache(query, result)

            return result

        except Exception as e:
            logger.error(f"[ReqID:{request_id}] Tavily Web Search Error: {e}")
            latency_ms = int((time.time() - start_time) * 1000)

            return {
                "status": "success",
                "content": f"Web search encountered an error: {str(e)}.",
                "details": {
                    "error": str(e),
                    "type": "web_search_results",
                    "engine": "tavily",
                    "latency_ms": latency_ms,
                    "status_code": 500,
                    "request_id": request_id,
                    "sources": []
                }
            }

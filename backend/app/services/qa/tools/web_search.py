import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
import logging
import os
from bs4 import BeautifulSoup
from backend.app.core.context import session_id_ctx, request_id_ctx
from backend.app.services.session.manager import SessionManager
from backend.app.core.rate_limiter import tavily_limiter

try:
    import html2text
except ImportError:
    html2text = None
from backend.app.services.qa.tools.base import BaseSkill

# Try importing LangChain Community tools, but handle if missing
try:
    from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
    from langchain_community.tools import DuckDuckGoSearchResults
    HAS_DDG = True
except ImportError:
    HAS_DDG = False
    DuckDuckGoSearchAPIWrapper = None
    DuckDuckGoSearchResults = None

import warnings

# Suppress LangChain deprecation warnings for Tavily
warnings.filterwarnings("ignore", category=UserWarning, module="langchain_community.tools.tavily_search")
warnings.filterwarnings("ignore", message=".*TavilySearchResults.*deprecated.*")

try:
    from langchain_community.tools.tavily_search import TavilySearchResults
    HAS_TAVILY = True
except ImportError:
    HAS_TAVILY = False
    TavilySearchResults = None

try:
    from langchain_tavily import TavilySearchResults as TavilySearchResultsV2
    HAS_TAVILY_V2 = True
except ImportError:
    HAS_TAVILY_V2 = False
    TavilySearchResultsV2 = None

logger = logging.getLogger(__name__)

class WebSearchSkill(BaseSkill):
    def __init__(self):
        self.search_tool = None
        self.engine = "none"
        self._session = None
        
        # Priority 1: Tavily (Better for RAG/LLM)
        if os.environ.get("TAVILY_API_KEY"):
            try:
                # Disable include_answer to speed up search (Agent will handle the answer)
                if HAS_TAVILY_V2 and TavilySearchResultsV2:
                    self.search_tool = TavilySearchResultsV2(max_results=5, include_answer=False)
                    self.engine = "tavily"
                    logger.info("WebSearchSkill initialized with Tavily Search V2 (include_answer=False).")
                elif HAS_TAVILY and TavilySearchResults:
                    self.search_tool = TavilySearchResults(max_results=5, include_answer=False)
                    self.engine = "tavily"
                    logger.info("WebSearchSkill initialized with Tavily Search (include_answer=False).")
            except Exception as e:
                logger.warning(f"Failed to initialize Tavily Search: {e}")

        # Priority 2: DuckDuckGo (Free, no key)
        if not self.search_tool and HAS_DDG:
            try:
                # Use DuckDuckGoSearchResults to get list of dicts instead of string
                # Note: 'backend' parameter "api" is often more stable for structured data
                self.wrapper = DuckDuckGoSearchAPIWrapper(region="cn-zh", time="y", max_results=5)
                # Remove backend='api' as it might be deprecated/unstable
                self.search_tool = DuckDuckGoSearchResults(api_wrapper=self.wrapper)
                self.engine = "duckduckgo"
                logger.info("WebSearchSkill initialized with DuckDuckGo Search.")
            except Exception as e:
                logger.warning(f"Failed to initialize DuckDuckGo Search: {e}")
                self.search_tool = None
        
        if not self.search_tool:
            logger.warning("No web search tool available (Tavily or DuckDuckGo). Web Search will be mocked.")

    @property
    def name(self) -> str:
        return "web_search"

    @property
    def description(self) -> str:
        return "Search the web for real-time information. Supports noun explanation and general queries."

    def _optimize_query(self, query: str) -> str:
        """
        Optimize query for noun explanation or liberal arts search.
        """
        query_lower = query.lower().strip()
        
        # Check for noun explanation intent
        noun_indicators = ["what is", "define", "explain", "meaning of", "什么是", "解释", "定义", "含义"]
        is_noun_query = any(query_lower.startswith(ind) for ind in noun_indicators) or len(query.split()) <= 3
        
        if is_noun_query:
            # Append keywords to bias towards encyclopedic results
            if any("\u4e00" <= char <= "\u9fff" for char in query): # Contains Chinese
                return f"{query} 定义 百科 解释"
            else:
                return f"{query} definition encyclopedia explanation"
        
        return query

    async def _get_session(self):
        if self._session is None or self._session.closed:
            # Use TCPConnector with DNS caching (300s) and large pool (limit=50)
            connector = aiohttp.TCPConnector(limit=50, ttl_dns_cache=300)
            self._session = aiohttp.ClientSession(connector=connector)
        return self._session

    async def _scrape_content(self, url: str) -> str:
        """
        Scrape content from a URL using aiohttp and BeautifulSoup.
        Includes retry mechanism.
        """
        retries = 3
        backoff = 1.0
        
        for attempt in range(retries):
            try:
                session = await self._get_session()
                async with session.get(url, timeout=15) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                            
                        # Convert to markdown using html2text for cleaner LLM input
                        h = html2text.HTML2Text()
                        h.ignore_links = True
                        h.ignore_images = True
                        markdown_text = h.handle(html)
                        
                        # Limit length
                        return markdown_text[:2000]
                    else:
                        if attempt == retries - 1:
                            return f"Failed to retrieve content (Status: {response.status})"
            except Exception as e:
                if attempt == retries - 1:
                    return f"Scraping error: {str(e)}"
            
            # Wait before retry
            await asyncio.sleep(backoff)
            backoff *= 2
            
        return "Failed to scrape content after retries."

    async def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Execute web search with retry mechanism and strict session limit.
        """
        import time
        start_time = time.time()
        # Use context request_id if available, fallback to kwargs
        request_id = request_id_ctx.get() or kwargs.get("request_id", "unknown")
        
        # --- Strict Search Limit Check (Atomic) ---
        session_id = session_id_ctx.get()
        if not session_id:
            logger.error(f"[ReqID:{request_id}] No session_id found in context. Blocking search for safety.")
            return {
                "status": "success",  # Return success to stop agent from retrying
                "content": "System Error: Session context missing. Search is disabled for security reasons. \n\nINSTRUCTION: You MUST stop searching immediately and answer based on your existing knowledge.",
                "details": {"error": "Missing Session ID"}
            }

        # Try to acquire the lock. If False, it means search was already used.
        if not SessionManager.try_acquire_search_quota(session_id):
            logger.warning(f"[ReqID:{request_id}] Search quota exceeded for session {session_id}.")
            return {
                "status": "success",  # Return success to stop agent from retrying
                "content": "System Notification: Web search quota for this session is exhausted (Limit: 1). \n\nINSTRUCTION: You MUST stop searching immediately. Use the information collected from the previous search to answer the user's question. If the information is insufficient, state what is missing and append '如需更详细的内容请继续讨论' to the end of your response.",
                "details": {
                    "error_message": "Search limit reached",
                    "error_details": "Single session search limit exceeded.",
                    "type": "limit_exceeded"
                }
            }

        process_steps = []
        process_steps.append(f"Received query: {query}")
        
        optimized_query = self._optimize_query(query)
        if optimized_query != query:
            process_steps.append(f"Optimized query to: {optimized_query}")
            
        logger.info(f"[ReqID:{request_id}] Executing web search with engine: {self.engine}, query: {optimized_query}")

        if not self.search_tool:
            process_steps.append("Search tool unavailable. Using mock fallback.")
            return self._mock_result(query, "Library not installed", process_steps, start_time)
            
        try:
            loop = asyncio.get_event_loop()
            
            # Execute search with retry
            structured_results = []
            raw_output = ""
            process_steps.append(f"Searching with engine: {self.engine}...")

            retries = 3
            backoff = 1.0
            last_error = None

            for attempt in range(retries):
                try:
                    if self.engine == "tavily":
                        # Tavily returns a list of dicts directly via invoke
                        async with tavily_limiter:
                            results = await self.search_tool.ainvoke(optimized_query)
                        structured_results = [
                            {
                                "title": res.get("url", "Tavily Result"), 
                                "link": res.get("url"),
                                "snippet": res.get("content")
                            }
                            for res in results
                        ]
                        raw_output = str(results)
                        break # Success

                    elif self.engine == "duckduckgo":
                        # DDGSearchResults returns a stringified list of results like "[snippet: ..., title: ..., link: ...], ..."
                        if hasattr(self, "wrapper"):
                            try:
                                results = await loop.run_in_executor(None, lambda: self.wrapper.results(optimized_query, max_results=5))
                            except Exception as wrapper_error:
                                logger.warning(f"Wrapper results failed: {wrapper_error}, falling back to tool run.")
                                process_steps.append(f"Wrapper failed: {wrapper_error}. Trying fallback.")
                                results = None
                            
                            if results:
                                structured_results = [
                                    {
                                        "title": res.get("title", "No Title"),
                                        "link": res.get("link", ""),
                                        "snippet": res.get("snippet", "")
                                    }
                                    for res in results
                                ]
                                raw_output = str(results)
                                break # Success
                            else:
                                # Fallback to tool run if wrapper access fails or returns empty
                                raw_output = await loop.run_in_executor(None, self.search_tool.run, optimized_query)
                                # Check for empty/error string
                                if not raw_output or "error" in raw_output.lower():
                                     raise Exception(f"Tool run returned error or empty: {raw_output}")
                                structured_results = [{"title": "Search Result", "link": "", "snippet": raw_output[:200]}]
                                break # Success
                        else:
                             # Fallback to tool run if wrapper access fails
                             raw_output = await loop.run_in_executor(None, self.search_tool.run, optimized_query)
                             structured_results = [{"title": "Search Result", "link": "", "snippet": raw_output[:200]}]
                             break # Success
                except Exception as e:
                    last_error = e
                    if attempt < retries - 1:
                        process_steps.append(f"Attempt {attempt+1} failed: {str(e)}. Retrying...")
                        await asyncio.sleep(backoff)
                        backoff *= 2
                    else:
                        raise e

            if not structured_results:
                 raise Exception("No results found from search engine.")

            process_steps.append(f"Found {len(structured_results)} results.")

            # Deep Scraping Logic (Phase 3) - Parallel with 3s timeout
            process_steps.append("Starting parallel deep scraping for top results...")
            
            async def scrape_task(res):
                url = res.get('link')
                if url:
                    try:
                        content = await self._scrape_content(url)
                        res['scraped_content'] = content
                        return True
                    except Exception:
                        return False
                return False

            # Limit to top 5
            tasks = [scrape_task(res) for res in structured_results[:5]]
            
            try:
                await asyncio.wait_for(asyncio.gather(*tasks), timeout=3.0)
                process_steps.append("Parallel scraping completed.")
            except asyncio.TimeoutError:
                process_steps.append("Parallel scraping timed out (partial results kept).")
            except Exception as e:
                process_steps.append(f"Parallel scraping error: {e}")

            # Summarize content (simple concatenation for now, LLM will process later)
            summary = "\n".join([f"[{i+1}] {res['snippet']} { '(Full Content Available)' if 'scraped_content' in res else ''}" for i, res in enumerate(structured_results)])
            
            latency_ms = int((time.time() - start_time) * 1000)
            logger.info(f"[ReqID:{request_id}] Search completed. Engine: {self.engine}, Latency: {latency_ms}ms, Results: {len(structured_results)}")

            return {
                "status": "success",
                "content": f"Found {len(structured_results)} results:\n{summary[:500]}...",
                "details": {
                    "raw_output": raw_output,
                    "sources": structured_results,
                    "type": "web_search_results",
                    "engine": self.engine,
                    "latency_ms": latency_ms,
                    "status_code": 200,
                    "request_id": request_id,
                    "process": process_steps
                }
            }
            
        except Exception as e:
            logger.error(f"[ReqID:{request_id}] Web Search Error: {e}")
            process_steps.append(f"Search failed: {str(e)}")
            # Fallback to Mock if search fails (e.g., rate limit, block)
            return self._mock_result(query, f"Search Failed ({str(e)}), using Mock Data", process_steps, start_time)

    def _mock_result(self, query: str, reason: str, process_steps: List[str] = None, start_time: float = 0) -> Dict[str, Any]:
        """Return a mock result for demo/fallback purposes."""
        import time
        if process_steps is None:
            process_steps = []
        process_steps.append("Generating mock data.")
        
        latency_ms = int((time.time() - start_time) * 1000) if start_time else 0
            
        return {
            "status": "success", # Return success so UI shows something, but content indicates it's a simulation
            "content": f"[Simulation] Web search unavailable ({reason}). Simulated results for: {query}",
            "details": {
                "raw_output": "Mock search result 1\nMock search result 2",
                "sources": [
                    {"title": "Simulated Search Result 1", "link": "https://example.com/1", "snippet": f"Information about {query} found here. (Mock Data)"},
                    {"title": "Simulated Search Result 2", "link": "https://example.com/2", "snippet": "More details... (Mock Data)"}
                ],
                "type": "web_search_results",
                "engine": "mock",
                "latency_ms": latency_ms,
                "status_code": 200, # Mock is technically a success response from the system
                "process": process_steps
            }
        }

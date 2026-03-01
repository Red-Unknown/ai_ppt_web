import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
import logging
import os
from bs4 import BeautifulSoup
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

try:
    from langchain_community.tools.tavily_search import TavilySearchResults
    HAS_TAVILY = True
except ImportError:
    HAS_TAVILY = False
    TavilySearchResults = None

logger = logging.getLogger(__name__)

class WebSearchSkill(BaseSkill):
    def __init__(self):
        self.search_tool = None
        self.engine = "none"
        
        # Priority 1: Tavily (Better for RAG/LLM)
        if HAS_TAVILY and os.environ.get("TAVILY_API_KEY"):
            try:
                # Enable include_answer for direct answers
                self.search_tool = TavilySearchResults(max_results=5, include_answer=True)
                self.engine = "tavily"
                logger.info("WebSearchSkill initialized with Tavily Search.")
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

    async def _scrape_content(self, url: str) -> str:
        """
        Scrape content from a URL using aiohttp and BeautifulSoup.
        Includes retry mechanism.
        """
        retries = 3
        backoff = 1.0
        
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10) as response:
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
        Execute web search with retry mechanism.
        """
        import time
        start_time = time.time()
        request_id = kwargs.get("request_id", "unknown")
        
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

            # Deep Scraping Logic (Phase 3)
            # Only scrape the top result if snippets are very short (< 100 chars) or if it's a noun explanation
            # to provide more context.
            if structured_results and len(structured_results[0]['snippet']) < 150:
                 process_steps.append("Top result snippet is short. Attempting deep scraping...")
                 top_url = structured_results[0]['link']
                 if top_url:
                     scraped_content = await self._scrape_content(top_url)
                     structured_results[0]['scraped_content'] = scraped_content
                     process_steps.append(f"Scraped content from {top_url} ({len(scraped_content)} chars).")

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

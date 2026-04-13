from typing import List, Optional, AsyncGenerator, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai import ChatOpenAI

from backend.app.core.config import settings
from backend.app.core import prompt_loader
from backend.app.schemas.qa import ChatRequest, ChatResponse, SourceNode, Intent, AdaptScriptRequest, AdaptScriptResponse
from backend.app.services.qa.retrieval.tree_retriever import TreeStructureRetriever
from backend.app.services.qa.analysis.router import DialogueRouter
from backend.app.services.qa.analysis.intent import QAAnalyzer
from backend.app.services.qa.tools.manager import SkillManager
from backend.app.services.teacher.agent import TeacherAgent
from backend.app.services.student.state_manager import StudentStateManager
from backend.app.services.session.manager import SessionManager
from backend.app.utils.cache import local_cache
from backend.app.services.qa.tools.retrieval import LocalKnowledgeTool
from backend.app.services.qa.agents.react import ReActAgent
import time
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

import tiktoken
from backend.app.core.rate_limiter import deepseek_limiter
from openai import AsyncOpenAI
from langchain_community.adapters.openai import convert_message_to_dict

class ConfigurationError(Exception):
    """Raised when required configuration is missing."""
    pass

class RateLimitedChatOpenAI(ChatOpenAI):
    """Wrapper around ChatOpenAI that enforces rate limits."""
    async def ainvoke(self, input, config=None, **kwargs):
        async with deepseek_limiter:
            return await super().ainvoke(input, config, **kwargs)

    async def astream(self, input, config=None, **kwargs):
        async with deepseek_limiter:
            async for chunk in super().astream(input, config, **kwargs):
                yield chunk

from backend.app.core.context import AppContext, session_id_ctx

class QAService:

    SCENARIO_CONFIGS = {
        "qa": {"temperature": 0.7, "max_tokens": 4000},
        "reasoner": {"temperature": 0.6, "max_tokens": 4000},
        "summary": {"temperature": 0.3, "max_tokens": 4000},
        "translation": {"temperature": 0.1, "max_tokens": 4000},
    }

    def __init__(self):
        self._validate_config()
        
        # Initialize Core Components
        self.retriever = TreeStructureRetriever()
        self.router = DialogueRouter(llm_model=settings.DEEPSEEK_MODEL)
        self.analyzer = QAAnalyzer(llm_model=settings.DEEPSEEK_MODEL)
        self.skill_manager = SkillManager()
        self.teacher = TeacherAgent(llm_model=settings.DEEPSEEK_MODEL)
        
        # Current Prompt Version
        self.current_prompt_version = "v5_enhanced_zh"
        self._init_llm()
        
        # Initialize ReAct Agent
        self._init_agent()
        
        # Simple Intent Cache (In-Memory) - kept for high-speed common queries
        self.intent_cache = {
            "课程介绍": "本课程是《大学物理》，主要涵盖力学、热学、电磁学等基础内容。",
            "评分标准": "平时成绩占 40%（含作业、签到、互动），期末考试占 60%。",
            "老师是谁": "我是您的 AI 助教，由 Role D 模块驱动。"
        }

    def _validate_config(self):
        missing_keys = []
        if not settings.DEEPSEEK_API_KEY:
            missing_keys.append("DEEPSEEK_API_KEY")
        
        # Check Tavily only if we plan to use it, but user wants strict validation?
        # Let's warn for Tavily, error for DeepSeek.
        if not settings.TAVILY_API_KEY:
             logger.warning("TAVILY_API_KEY is missing. Web search will use Mock/DDG mode.")

        if missing_keys:
            error_msg = (
                f"Missing required configuration: {', '.join(missing_keys)}! \n"
                "Please set them in your environment variables or .env file.\n"
                "Examples:\n"
                "  Linux/MacOS: export DEEPSEEK_API_KEY='sk-your-key'\n"
                "  Windows: setx DEEPSEEK_API_KEY 'sk-your-key'"
            )
            logger.error(error_msg)
            raise ConfigurationError(error_msg)

    def _init_llm(self):
        """Initialize LLM clients with current settings."""
        self.llm_clients = {}
        
        # Initialize DeepSeek Clients (Default)
        for scenario, config in self.SCENARIO_CONFIGS.items():
            model_name = settings.DEEPSEEK_MODEL
            if scenario == "reasoner":
                model_name = settings.DEEPSEEK_REASONER_MODEL
                
            self.llm_clients[scenario] = RateLimitedChatOpenAI(
                model=model_name,
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
                temperature=config.get("temperature", settings.DEEPSEEK_TEMPERATURE),
                max_tokens=config.get("max_tokens", settings.DEEPSEEK_MAX_TOKENS),
                streaming=True,
                max_retries=3,
                extra_body={"include_reasoning": True} if scenario == "reasoner" else None
            )

        # Initialize Kimi Clients (for tool calling with web search)
        if settings.KIMI_API_KEY:
            for scenario, config in self.SCENARIO_CONFIGS.items():
                self.llm_clients[f"{scenario}_kimi"] = ChatOpenAI(
                    model=settings.KIMI_MODEL,
                    api_key=settings.KIMI_API_KEY,
                    base_url=settings.KIMI_BASE_URL,
                    temperature=config.get("temperature", settings.KIMI_TEMPERATURE),
                    max_tokens=config.get("max_tokens", settings.KIMI_MAX_TOKENS),
                    streaming=True,
                    max_retries=3
                )
            logger.info("Kimi LLM clients initialized for tool calling.")
            
        # Initialize GPT Clients (if available)
        if settings.OPENAI_API_KEY:
            for scenario in self.SCENARIO_CONFIGS:
                self.llm_clients[f"{scenario}_gpt"] = ChatOpenAI(
                    model="gpt-4o",
                    api_key=settings.OPENAI_API_KEY,
                    temperature=self.SCENARIO_CONFIGS[scenario].get("temperature", 0.7),
                    max_tokens=self.SCENARIO_CONFIGS[scenario].get("max_tokens", 2048),
                    streaming=True
                )
        
        # Default LLM (can be switched via parameter)
        self.llm = self.llm_clients["qa"]

    def _init_agent(self, llm_key: str = "qa"):
        """Initialize ReAct Agent with skills.
        
        Args:
            llm_key: Key to select LLM from llm_clients dict. 
                     Options: "qa" (DeepSeek), "qa_kimi", "qa_gpt"
        """
        # Select LLM (default to "qa" if key not found)
        llm = self.llm_clients.get(llm_key, self.llm_clients["qa"])
        
        # 1. Local Knowledge Tool (Enhanced RAG)
        local_rag = LocalKnowledgeTool(retriever=self.retriever, llm=llm)
        
        # 2. Get other skills from SkillManager
        # Note: When using Kimi, web_search skill is not needed as Kimi has built-in search
        other_skills = list(self.skill_manager.skills.values())
        
        # Combine tools
        # For Kimi: Don't add web_search tool (Kimi will decide internally)
        # For DeepSeek/GPT: Add web_search tool for Tavily integration
        if "kimi" in llm_key.lower():
            tools = [local_rag]  # Kimi has built-in web search
        else:
            tools = [local_rag] + other_skills  # Include Tavily web search
        
        # Get System Prompt
        system_prompt = prompt_loader.get_prompt("v5_enhanced_zh", "system")
        if not system_prompt:
            system_prompt = (
                "You are a helpful teaching assistant.\n"
                "Answer using ONLY the provided context.\n"
                "If unknown, reply: \"I don't know based on the course material.\"\n"
            )

        # Create Agent
        self.agent = ReActAgent(
            llm=llm,
            tools=tools,
            max_iterations=15,
            system_prompt=system_prompt
        )
        logger.info(f"ReAct Agent initialized with tools: {[t.name for t in tools]} using LLM: {llm_key}")

    def reload_config(self):
        """Hot reload configuration (re-initialize LLMs)."""
        logger.info("Reloading QAService configuration...")
        self._validate_config()
        self._init_llm()
        logger.info("Configuration reloaded.")

    def get_prompt_template(self, version: str = "default") -> ChatPromptTemplate:
        system_text = prompt_loader.get_prompt(version, "system")
        user_text = prompt_loader.get_prompt(version, "user")
        if not system_text:
            system_text = (
                "You are a helpful teaching assistant.\n"
                "Answer using ONLY the provided context.\n"
                "If unknown, reply: \"I don't know based on the course material.\"\n\n"
                "Context:\n{context}\n\n"
                "Safety:\n- No fabrication\n- Ask for clarification when unsure\n- Neutral tone"
            )
        if "{question}" not in user_text or "{context}" not in system_text:
            user_text = "Student Question: {question}"
        
        # Inject history if available
        if "{history}" in system_text or "{history}" in user_text:
            pass 
        else:
            # Append history to user text if not present
            user_text += "\n\nHistory:\n{history}"
            
        messages = [("system", system_text), ("user", user_text)]
        return ChatPromptTemplate.from_messages(messages)

    def _truncate_history_by_tokens(self, history: List[Dict], max_tokens: int = 2000) -> str:
        """
        Truncate history to fit within token limit, keeping most recent messages.
        Uses tiktoken for accurate counting (cl100k_base for GPT-4/DeepSeek).
        """
        encoding = tiktoken.get_encoding("cl100k_base")
        total_tokens = 0
        truncated_history = []
        
        # Iterate backwards
        for msg in reversed(history):
            content = msg.get("content", "")
            tokens = len(encoding.encode(content))
            if total_tokens + tokens > max_tokens:
                break
            truncated_history.insert(0, msg)
            total_tokens += tokens
            
        return json.dumps(truncated_history, ensure_ascii=False)

    async def predict_next_questions(self, query: str, answer: str = "", context: Optional[str] = None) -> List[str]:
        """
        Generate 2 follow-up questions based on the user's query and the assistant's answer.
        """
        if not settings.ENABLE_SUGGESTIONS:
            return []

        try:
            # Simple prompt for suggestions
            prompt = ChatPromptTemplate.from_messages([
                ("system", "你是一个善于引导学生深入思考的助教。请基于用户的提问和你的回答，生成2个后续可能被追问的问题。要求简短、相关且有深度。直接以JSON列表格式返回，例如：[\"问题1\", \"问题2\"]。不要包含Markdown代码块。"),
                ("user", "用户提问: {query}\n\n你的回答: {answer}\n\n相关上下文: {context}")
            ])
            
            # Use the 'summary' model for speed/stability (temperature 0.3)
            # If unavailable, fallback to default llm
            llm = self.llm_clients.get("summary", self.llm)
            
            chain = prompt | llm | StrOutputParser()
            
            # Truncate inputs to save tokens/time
            safe_answer = answer[:1000] if answer else ""
            safe_context = context[:500] if context else "无"
            
            result = await chain.ainvoke({
                "query": query,
                "answer": safe_answer,
                "context": safe_context
            })
            
            # Clean up result if it contains markdown
            result = result.strip()
            if result.startswith("```json"):
                result = result[7:]
            elif result.startswith("```"):
                result = result[3:]
            if result.endswith("```"):
                result = result[:-3]
            
            try:
                suggestions = json.loads(result.strip())
                if isinstance(suggestions, list):
                    return suggestions[:2] # Ensure only 2
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse suggestions JSON: {result}")
                # Fallback splitting by newline if JSON fails
                lines = [line.strip().lstrip("-").lstrip("*").strip() for line in result.split("\n") if line.strip()]
                return lines[:2]
                
        except Exception as e:
            logger.error(f"Error generating suggestions: {e}")
            return []
        
        return []

    async def _direct_rag_stream(self, query: str, context_str: str, history_list: List[Dict], session_id: str = None) -> AsyncGenerator[str, None]:
        """
        Stream answer using Direct RAG (No ReAct loop).
        """
        history_str = self._truncate_history_by_tokens(history_list, max_tokens=2000)
        
        prompt_template = self.get_prompt_template("v5_enhanced_zh")
        chain_input = {
            "context": context_str, 
            "question": query, 
            "history": history_str
        }
        
        yield self._emit_event(session_id, {"type": "start", "action": "QA_ANSWER"})
        
        try:
            # Manually format messages
            formatted_messages = prompt_template.format_messages(**chain_input)
            
            async for chunk in self.llm.astream(formatted_messages):
                if chunk.content:
                    yield self._emit_event(session_id, {"type": "token", "content": chunk.content})
            
        except Exception as e:
            logger.error(f"Direct RAG error: {e}")
            yield self._emit_event(session_id, {"type": "error", "content": f"Generation Error: {str(e)}"})

    def _emit_event(self, session_id: str, event: Dict[str, Any]) -> str:
        """Helper to save event to history and return JSON string."""
        if session_id:
            StudentStateManager.append_event(session_id, event)
        return json.dumps(event)

    def _create_resume_event(self, timestamp: float) -> Dict[str, Any]:
        """Create a resume event to jump back to video timestamp."""
        return {
            "type": "resume",
            "data": {
                "timestamp": timestamp,
                "message": "已为您解答完毕，点击继续学习",
                "strategy": "auto_resume"
            }
        }

    async def stream_answer_question(self, request: ChatRequest, user_id: str = "student_001") -> AsyncGenerator[str, None]:
        """
        Stream response for WebSocket using Server-Sent Events style JSON chunks.
        
        Args:
            request: Chat request with model parameter (deepseek, kimi, gpt-4o)
            user_id: User identifier
        """
        # Set ContextVar for session_id to ensure tools can access it safely
        with AppContext.scope(session_id=request.session_id, user_id=user_id):
            try:
                # Select LLM based on model parameter
                model_lower = request.model.lower() if request.model else "deepseek"
                if "kimi" in model_lower:
                    llm_key = "qa_kimi"
                elif "gpt" in model_lower:
                    llm_key = "qa_gpt"
                else:
                    llm_key = "qa"  # Default to DeepSeek
                
                # Re-initialize agent with selected LLM if needed
                if not hasattr(self, 'current_llm_key') or self.current_llm_key != llm_key:
                    self._init_agent(llm_key)
                    self.current_llm_key = llm_key
                
                # 0. Reset Search Quota for this new turn (Single Session = One Q&A Pair)
                if request.session_id:
                    SessionManager.reset_search_quota(request.session_id)

                # 1. Intent Cache Hit (Zero Latency - In-Memory)
                if request.query in self.intent_cache:
                    answer = self.intent_cache[request.query]
                    yield self._emit_event(request.session_id, {"type": "start", "action": "QA_CACHE"})
                    yield self._emit_event(request.session_id, {"type": "token", "content": answer})
                
                    suggestions = await self.predict_next_questions(request.query, answer=answer)
                    yield self._emit_event(request.session_id, {"type": "suggestions", "content": suggestions})
                    
                    if request.video_timestamp:
                        yield self._emit_event(request.session_id, self._create_resume_event(request.video_timestamp))
                        
                    yield self._emit_event(request.session_id, {"type": "end"})
                    return

                # 2. Single Chat Cache (Session Level)
                cached_docs = None
                if request.session_id:
                    cached_docs = SessionManager.get_cached_docs(request.session_id, request.query)
                    if cached_docs:
                        yield self._emit_event(request.session_id, {"type": "status", "content": "已命中会话缓存，跳过检索..."})
                        logger.info(f"Session {request.session_id} cache hit for query: {request.query}")
        
                # 3. Get/Init Student Profile & State
                profile = StudentStateManager.get_profile(user_id)
                if not profile:
                    profile = StudentStateManager.create_or_update_profile(user_id, {})
                    
                session_id = request.session_id or "default_session"
                state = StudentStateManager.get_state(session_id)
                if not state:
                    state = StudentStateManager.init_state(session_id, request.current_path or "unknown_topic")
        
                # 4. Route Intent
                intent = self.router.route(request.query)
                
                if intent == Intent.CONTROL:
                    yield self._emit_event(request.session_id, {"type": "start", "action": "CONTROL"})
                    yield self._emit_event(request.session_id, {"type": "token", "content": "执行控制指令: " + request.query})
                    yield self._emit_event(request.session_id, {"type": "action", "data": {"command": request.query}})
                    yield self._emit_event(request.session_id, {"type": "end"})
                    return
        
                elif intent == Intent.FEEDBACK:
                    # Retrieve context first
                    self.retriever.current_path = request.current_path
                    
                    # IMPROVED: Use last successful QA query for context retrieval if available
                    search_query = request.query
                    if state.last_qa_query and len(request.query) < 10:
                        search_query = state.last_qa_query
                        logger.info(f"Using last QA query for feedback context: {search_query}")
                        
                    docs = self.retriever.invoke(search_query)
                    context_str = "\n".join([d.page_content[:200] for d in docs])
                    
                    yield self._emit_event(request.session_id, {"type": "status", "content": "正在分析反馈..."})
                    
                    # Use last_qa_query as topic if available, otherwise use state.current_topic
                    original_topic = state.current_topic
                    if state.last_qa_query:
                        # Temporarily update state for feedback handling
                        state.current_topic = state.last_qa_query
                    
                    feedback_result = await self.teacher.handle_feedback(
                        request.query, state, profile, context_str
                    )
                    
                    # Restore state
                    state.current_topic = original_topic
                    
                    if feedback_result.get("action") in ["SUPPLEMENT", "FALLBACK_VIDEO"]:
                        StudentStateManager.increment_confusion(session_id)
                    else:
                        StudentStateManager.reset_confusion(session_id)
        
                    yield self._emit_event(request.session_id, {"type": "start", "action": feedback_result.get("action")})
                    
                    # Emit Strategy Log (State Transition)
                    if "strategy_log" in feedback_result:
                        yield self._emit_event(request.session_id, {"type": "strategy", "content": feedback_result["strategy_log"]})
                    
                    if feedback_result.get("action") == "FALLBACK_VIDEO":
                        yield self._emit_event(request.session_id, {"type": "action", "data": feedback_result})
                        yield self._emit_event(request.session_id, {"type": "token", "content": feedback_result.get("message")})
                    else:
                        content = feedback_result.get("message") or feedback_result.get("content", "")
                        chunk_size = 5
                        for i in range(0, len(content), chunk_size):
                            yield self._emit_event(request.session_id, {"type": "token", "content": content[i:i+chunk_size]})
                            await asyncio.sleep(0.02)
                            
                        if "audio_text" in feedback_result:
                             yield self._emit_event(request.session_id, {"type": "action", "data": {"audio_text": feedback_result["audio_text"]}})
        
                    if request.video_timestamp:
                        yield self._emit_event(request.session_id, self._create_resume_event(request.video_timestamp))
                        
                    yield self._emit_event(request.session_id, {"type": "end"})
                    return
        
                else: # Intent.QA
                    yield self._emit_event(request.session_id, {"type": "status", "content": "正在分析意图..."})
                    StudentStateManager.reset_confusion(session_id)
                    
                    # Analyze QA Type for Instruction Injection
                    qa_type = await self.analyzer.analyze(request.query)
                    logger.info(f"QA Type: {qa_type}")
        
                    # --- DUAL STREAM REASONING START ---
                    if request.enable_reasoning:
                        yield self._emit_event(request.session_id, {"type": "status", "content": "启动双流推理模式..."})
                        
                        # Task A: Quick Answer (Direct RAG)
                        # We run this in a background task but we need to stream it FIRST.
                        # Actually, we can just run it sequentially for the user perception, 
                        # or better: asyncio.gather if we can handle interleaved streams.
                        # But for simplicity and clarity:
                        # 1. Quick Answer Stream
                        # 2. Deep Reasoning Stream (Async)
                        
                        # Let's do Quick Answer first (Blocking but fast)
                        yield self._emit_event(request.session_id, {"type": "status", "content": "正在生成快速回答..."})
                        
                        # Quick RAG (Standard DeepSeek-Chat)
                        # 1. Retrieve (Fast)
                        docs = self.retriever.invoke(request.query)
                        context_str = "\n\n".join([f"【来源：{d.metadata.get('path', '未知路径')}】\n内容：{d.page_content}" for d in docs])
                        
                        # Emit Sources
                        if docs:
                            source_nodes = []
                            for d in docs:
                                source_nodes.append({
                                    "node_id": d.metadata.get("node_id", "unknown"),
                                    "content": d.page_content[:200] + "...",
                                    "path": d.metadata.get("path", ""),
                                    "relevance_score": d.metadata.get("score", 0.0),
                                    "bbox": d.metadata.get("bbox"),
                                    "image_url": d.metadata.get("image_url"),
                                    "page_num": d.metadata.get("page_num")
                                })
                            yield self._emit_event(request.session_id, {"type": "sources", "content": source_nodes})
                        
                        # 2. Generate Quick Answer
                        history_list = StudentStateManager.get_history(session_id, limit=5) # Less history for speed
                        history_str = self._truncate_history_by_tokens(history_list, max_tokens=1000)
                        
                        prompt_template = self.get_prompt_template("v5_enhanced_zh")
                        chain_input = {"context": context_str, "question": request.query, "history": history_str}
                        formatted_messages = prompt_template.format_messages(**chain_input)
                        
                        quick_answer_acc = ""
                        llm_quick = self.llm_clients["qa"] # Standard model
                        
                        try:
                            async for chunk in llm_quick.astream(formatted_messages):
                                if chunk.content:
                                    content_str = str(chunk.content)
                                    quick_answer_acc += content_str
                                    # Send as quick_answer event
                                    yield self._emit_event(request.session_id, {"type": "quick_answer", "content": content_str})
                        except Exception as e:
                            logger.error(f"Quick answer failed: {e}")
                            
                        # 3. Start Deep Reasoning (DeepSeek Reasoner)
                        yield self._emit_event(request.session_id, {"type": "status", "content": "正在进行深度思考..."})
                        yield self._emit_event(request.session_id, {"type": "reasoning_start"})
                        
                        llm_reasoner = self.llm_clients.get("reasoner", self.llm_clients["qa"])
                        full_reasoning = ""
                        full_deep_answer = ""
                        
                        try:
                            # Use same context but maybe more history?
                            history_list_deep = StudentStateManager.get_history(session_id, limit=20)
                            history_str_deep = self._truncate_history_by_tokens(history_list_deep, max_tokens=2000)
                            chain_input_deep = {"context": context_str, "question": request.query, "history": history_str_deep}
                            formatted_messages_deep = prompt_template.format_messages(**chain_input_deep)
                            
                            # Use raw OpenAI client to capture reasoning_content (DeepSeek R1)
                            # LangChain currently might strip unknown fields from delta
                            openai_messages = [convert_message_to_dict(m) for m in formatted_messages_deep]
                            
                            client = AsyncOpenAI(
                                api_key=settings.DEEPSEEK_API_KEY,
                                base_url=settings.DEEPSEEK_BASE_URL
                            )

                            async with deepseek_limiter:
                                stream = await client.chat.completions.create(
                                    model=settings.DEEPSEEK_REASONER_MODEL,
                                    messages=openai_messages,
                                    stream=True
                                )
                                
                                async for chunk in stream:
                                    if not chunk.choices:
                                        continue
                                        
                                    delta = chunk.choices[0].delta
                                    
                                    # Extract reasoning
                                    reasoning = ""
                                    if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                                        reasoning = delta.reasoning_content
                                    
                                    if reasoning:
                                        reasoning_str = str(reasoning)
                                        full_reasoning += reasoning_str
                                        yield self._emit_event(request.session_id, {"type": "reasoning_content", "content": reasoning_str})
                                    
                                    if delta.content:
                                        content_str = str(delta.content)
                                        full_deep_answer += content_str
                                        yield self._emit_event(request.session_id, {"type": "enhanced_answer", "content": content_str})
                            
                            yield self._emit_event(request.session_id, {"type": "reasoning_end"})
                            
                            # Finalize
                            # Save History (Prefer Deep Answer)
                            final_answer = full_deep_answer if full_deep_answer else quick_answer_acc
                            try:
                                StudentStateManager.add_history(session_id, "user", request.query)
                                StudentStateManager.add_history(
                                    session_id, 
                                    "assistant", 
                                    final_answer,
                                    reasoning=full_reasoning if full_reasoning else None
                                )
                                if full_reasoning:
                                    StudentStateManager.save_session_context(session_id, thinking_path=full_reasoning)
                            except Exception as e:
                                logger.error(f"Failed to save history: {e}")
                                
                            # Suggestions
                            try:
                                suggestions = await self.predict_next_questions(request.query, answer=final_answer, context=context_str)
                                yield self._emit_event(request.session_id, {"type": "suggestions", "content": suggestions})
                            except Exception:
                                pass

                            if request.video_timestamp:
                                yield self._emit_event(request.session_id, self._create_resume_event(request.video_timestamp))

                            yield self._emit_event(request.session_id, {"type": "end"})
                            return
                            
                        except Exception as e:
                            logger.error(f"Deep reasoning failed: {e}")
                            yield self._emit_event(request.session_id, {"type": "error", "content": f"Deep Reasoning Error: {str(e)}"})
                            yield self._emit_event(request.session_id, {"type": "end"})
                            return

                    # --- DUAL STREAM REASONING END ---

                    # --- DEEPSEEK REASONER BYPASS START (Legacy/Single Stream) ---
                    if request.model == "deepseek-reasoner":
                        yield self._emit_event(request.session_id, {"type": "status", "content": "已切换至深度思考模式 (Reasoning)..."})
                        
                        # 1. Retrieve
                        yield self._emit_event(request.session_id, {"type": "status", "content": "正在检索知识库..."})
                        docs = self.retriever.invoke(request.query)
                        # Cache the results if session exists
                        if request.session_id:
                            SessionManager.cache_docs(request.session_id, request.query, docs)
                        context_str = "\n\n".join([f"【来源：{d.metadata.get('path', '未知路径')}】\n内容：{d.page_content}" for d in docs])
                        
                        # Emit Sources Event (Visual Grounding)
                        if docs:
                            source_nodes = []
                            for d in docs:
                                source_nodes.append({
                                    "node_id": d.metadata.get("node_id", "unknown"),
                                    "content": d.page_content[:200] + "...",
                                    "path": d.metadata.get("path", ""),
                                    "relevance_score": d.metadata.get("score", 0.0),
                                    "bbox": d.metadata.get("bbox"),
                                    "image_url": d.metadata.get("image_url"),
                                    "page_num": d.metadata.get("page_num")
                                })
                            yield self._emit_event(request.session_id, {"type": "sources", "content": source_nodes})
                        
                        # 2. Prepare Input
                        history_list = StudentStateManager.get_history(session_id, limit=20)
                        history_str = self._truncate_history_by_tokens(history_list, max_tokens=2000)
                        
                        prompt_template = self.get_prompt_template("v5_enhanced_zh") # Default to ZH
                        chain_input = {
                            "context": context_str, 
                            "question": request.query, 
                            "history": history_str
                        }
                        
                        yield self._emit_event(request.session_id, {"type": "start", "action": "QA_ANSWER"})
                        
                        # 3. Stream
                        llm = self.llm_clients.get("reasoner", self.llm_clients["qa"])
                        full_answer = ""
                        full_reasoning = ""
                        
                        try:
                            # Manually format messages
                            formatted_messages = prompt_template.format_messages(**chain_input)
                            async for chunk in llm.astream(formatted_messages):
                                # Extract reasoning content
                                reasoning = ""
                                # Handle different chunk structures
                                if hasattr(chunk, 'additional_kwargs'):
                                    reasoning = chunk.additional_kwargs.get("reasoning_content", "")
                                
                                # Fallback: some providers put it in message content with tags or different fields
                                # If reasoning is empty, check if it's in content with <think> tags (DeepSeek style raw)
                                # But typically langchain parses it. 
                                
                                if not reasoning and hasattr(chunk, 'response_metadata'):
                                    reasoning = chunk.response_metadata.get("reasoning_content", "")
                                
                                if reasoning:
                                    full_reasoning += reasoning
                                    yield self._emit_event(request.session_id, {"type": "reasoning", "content": reasoning})
                                
                                if chunk.content:
                                    full_answer += chunk.content
                                    yield self._emit_event(request.session_id, {"type": "token", "content": chunk.content})
                            
                            yield self._emit_event(request.session_id, {"type": "reasoning_end"})
                            
                            # Generate Suggestions
                            try:
                                suggestions = await self.predict_next_questions(request.query, answer=full_answer, context=context_str)
                                yield self._emit_event(request.session_id, {"type": "suggestions", "content": suggestions})
                            except Exception:
                                pass

                            if request.video_timestamp:
                                yield self._emit_event(request.session_id, self._create_resume_event(request.video_timestamp))

                            yield self._emit_event(request.session_id, {"type": "end"})
                            
                            # Save History
                            try:
                                StudentStateManager.add_history(session_id, "user", request.query)
                                StudentStateManager.add_history(
                                    session_id, 
                                    "assistant", 
                                    full_answer,
                                    reasoning=full_reasoning if full_reasoning else None
                                )
                                # Save Thinking Path (accumulated from stream)
                                if full_reasoning:
                                    StudentStateManager.save_session_context(session_id, thinking_path=full_reasoning)
                            except Exception as e:
                                logger.error(f"Failed to save history: {e}")
                            return
                            
                        except Exception as e:
                            logger.error(f"Reasoner error: {e}")
                            yield self._emit_event(request.session_id, {"type": "error", "content": f"Reasoning Error: {str(e)}"})
                            yield self._emit_event(request.session_id, {"type": "end"})
                            return
                    # --- DEEPSEEK REASONER BYPASS END ---
        
                    # 1. Retrieve & Confidence Check
                    if cached_docs:
                        docs = cached_docs
                        top_score = docs[0].metadata.get("score", 0.0) if docs else 0.0
                    else:
                        yield self._emit_event(request.session_id, {"type": "status", "content": "正在检索本地知识库..."})
                        docs = self.retriever.invoke(request.query)
                        # Cache the results if session exists
                        if request.session_id:
                            SessionManager.cache_docs(request.session_id, request.query, docs)
                        
                        # Extract confidence from top-1 doc
                        top_score = 0.0
                        if docs:
                            top_score = docs[0].metadata.get("score", 0.0)
                    
                    context_str = "\n\n".join([f"【来源：{d.metadata.get('path', '未知路径')}】\n内容：{d.page_content}" for d in docs])
                    logger.info(f"Retrieval Confidence: {top_score:.4f}")

                    # Emit Sources Event (Visual Grounding)
                    if docs:
                        source_nodes = []
                        for d in docs:
                            source_nodes.append({
                                "node_id": d.metadata.get("node_id", "unknown"),
                                "content": d.page_content[:200] + "...",
                                "path": d.metadata.get("path", ""),
                                "relevance_score": d.metadata.get("score", 0.0),
                                "bbox": d.metadata.get("bbox"),
                                "image_url": d.metadata.get("image_url"),
                                "page_num": d.metadata.get("page_num")
                            })
                        yield self._emit_event(request.session_id, {"type": "sources", "content": source_nodes})

                    # 2. Decision Logic (Heuristics)
                    use_react = False
                    use_web_search = False
                    
                    # Check Search Limit
                    search_allowed = True
                    if request.session_id and SessionManager.is_search_used(request.session_id):
                        search_allowed = False
                        logger.info(f"Session {request.session_id} search quota exhausted.")
                    
                    # Trigger Conditions
                    is_time_sensitive = any(k in request.query for k in ["最新", "今天", "2024", "股价", "汇率", "天气"])
                    is_complex_intent = qa_type in ["MATH_CALCULATION", "LOGIC_PUZZLE", "FACT_CHECK"]
                    is_low_confidence = top_score < 0.75 
                    
                    # Safety / Guardrails
                    if "删除" in request.query and ("脚本" in request.query or "文件" in request.query):
                        yield self._emit_event(request.session_id, {"type": "status", "content": "触发安全拦截..."})
                        yield self._emit_event(request.session_id, {"type": "token", "content": "抱歉，我不能执行删除文件等危险操作。"})
                        yield self._emit_event(request.session_id, {"type": "end"})
                        return
        
                    # Web Search Logic
                    if search_allowed:
                        if is_time_sensitive or qa_type == "DYNAMIC_DATA":
                            use_web_search = True
                        elif is_low_confidence and not is_complex_intent:
                            use_web_search = True
                    else:
                        use_web_search = False # Force disable if quota exhausted
                    
                    # Suppression Logic
                    if top_score >= 0.85 and not is_time_sensitive:
                        use_web_search = False
                    
                    # COMPARISON Optimization: Prefer Direct RAG if not too low confidence
                    if qa_type == "COMPARISON" and top_score > 0.4:
                        use_web_search = False
                        
                    # ReAct Logic
                    if is_complex_intent:
                        use_react = True
                    if use_web_search:
                        use_react = True
                    if "逐步" in request.query or "分析" in request.query:
                        use_react = True
                    
                    # Whitelist (Fast Path)
                    if len(request.query) < 10 and qa_type == "FACTOID":
                        use_react = False
                        use_web_search = False
                    
                    # Demo Hardcode: Force Direct RAG for specific demo questions
                    if "对比" in request.query and "适用条件" in request.query:
                        use_react = False
                        use_web_search = False
        
                    # Prepare Query with Instructions
                    final_query = request.query
                    if qa_type == "MULTI_STEP":
                        final_query += "\n\n(Instruction: This is a multi-step reasoning question. Please break down your answer logically and integrate information from multiple sources.)"
                    elif qa_type == "COMPARISON":
                        final_query += "\n\n(Instruction: This is a comparison question. Please use a table or clear list to compare the concepts.)"
                    elif qa_type == "PROOF":
                        final_query += "\n\n(Instruction: This is a proof/verification question. Please provide a step-by-step logical proof or derivation.)"
                    elif qa_type == "EXAMPLE":
                        final_query += "\n\n(Instruction: The student is asking for examples. If the knowledge base lacks examples, please provide a general real-world example and mark it as 'General Knowledge'.)"
                    
                    if use_web_search:
                        final_query += "\n\n(Instruction: Local knowledge might be insufficient or time-sensitive data is required. Please use WebSearch tool if needed.)"
                        
                    # Inject Context for ReAct to avoid double retrieval
                    if use_react and context_str:
                        final_query += f"\n\n[Provided Local Context]:\n{context_str}\n\n(Instruction: You may use the provided context above. If it's insufficient, use tools to search.)"
        
                    # Prepare History
                    history_list = StudentStateManager.get_history(session_id, limit=20)
                    
                    full_answer_accumulator = ""
                    
                    # Accumulate tool calls and reasoning for history
                    captured_tool_calls = []
                    
                    try:
                        if use_react:
                            yield self._emit_event(request.session_id, {"type": "status", "content": "正在规划多步推理..."})
                            yield self._emit_event(request.session_id, {"type": "start", "action": "QA_ANSWER"})
                            
                            # Filter tools based on search_allowed
                            original_tools = self.agent.tools
                            if not search_allowed:
                                self.agent.tools = [t for t in original_tools if t.name != "web_search"]
                            
                            try:
                                async for event_str in self.agent.run(final_query, history=history_list):
                                     event = json.loads(event_str)
                                     evt_type = event.get("type")
                                     
                                     if evt_type == "thought_stream":
                                         # Stream thought/answer content directly as tokens
                                         content = event.get("content", "")
                                         full_answer_accumulator += content
                                         yield self._emit_event(request.session_id, {"type": "token", "content": content})
                                     elif evt_type == "iteration":
                                         yield self._emit_event(request.session_id, {"type": "status", "content": f"正在进行第 {event.get('iteration')} 步推理..."})
                                     elif evt_type == "tool_start":
                                         # Capture tool call
                                         captured_tool_calls.append(event)
                                         
                                         tool_name = event.get("tool_name", "")
                                         desc = f"正在调用工具: {tool_name}"
                                         
                                         if tool_name == "web_search":
                                             query = event.get("inputs", {}).get("query", "")
                                             desc = f"正在调用连网查询工具，搜索...{query[:15]}"
                                         elif tool_name in ["calculator", "math_solver"]:
                                             desc = "正在调用计算工具 （显示代码）"
                                         
                                         yield self._emit_event(request.session_id, {"type": "status", "content": desc})
                                         if request.session_id:
                                             StudentStateManager.append_event(request.session_id, event)
                                         yield event_str
                                     elif evt_type in ["tool_result", "tool_error", "usage"]:
                                         if request.session_id:
                                             StudentStateManager.append_event(request.session_id, event)
                                         yield event_str
                                     elif evt_type == "error":
                                         yield self._emit_event(request.session_id, {"type": "error", "content": event.get("content")})
                                     elif evt_type == "done":
                                         yield self._emit_event(request.session_id, {"type": "end"})
                            except Exception as e:
                                logger.error(f"ReAct execution failed: {e}", exc_info=True)
                                yield self._emit_event(request.session_id, {"type": "error", "content": f"System Error: {str(e)}"})
                                yield self._emit_event(request.session_id, {"type": "end"})
                            finally:
                                # Restore tools
                                self.agent.tools = original_tools
            
                        else:
                            yield self._emit_event(request.session_id, {"type": "status", "content": "使用直接回答模式..."})
                            
                            # We need to manually iterate and accumulate
                            async for chunk_str in self._direct_rag_stream(final_query, context_str, history_list, session_id=request.session_id):
                                event = json.loads(chunk_str)
                                
                                if event.get("type") == "token":
                                    full_answer_accumulator += event.get("content", "")
                                yield chunk_str
                                
                            # Append "Local Knowledge" hint if needed
                            if top_score >= 0.75 and not is_time_sensitive:
                                 hint = "\n\n（注：答案基于本地知识库）"
                                 full_answer_accumulator += hint
                                 yield self._emit_event(request.session_id, {"type": "token", "content": hint})
                            
                            # Send End
                            yield self._emit_event(request.session_id, {"type": "end"})
                    
                    finally:
                        # Save Interaction (Even if cancelled)
                        try:
                            # Avoid saving duplicate if user query already saved?
                            # Add check if needed, but append is safe.
                            StudentStateManager.add_history(session_id, "user", request.query)
                            if full_answer_accumulator:
                                StudentStateManager.add_history(
                                    session_id, 
                                    "assistant", 
                                    full_answer_accumulator,
                                    tool_calls=captured_tool_calls if captured_tool_calls else None
                                )
                                # Update last successful QA query for context tracking
                                StudentStateManager.update_last_query(session_id, request.query)
                                
                                # Save Thinking Path (accumulated from stream)
                                # Note: DeepSeek reasoner path is accumulated in full_reasoning if using that branch
                                # ReAct path is implicitly in tool_calls
                                # If we want explicit thinking path string, we need to capture it
                                # For now, let's save what we have if any
                                # StudentStateManager.save_session_context(session_id, thinking_path=...)
                        except Exception as e:
                            logger.error(f"Failed to save history: {e}")
                    
                    # Generate Suggestions (Post-Response)
                    try:
                        suggestions = await self.predict_next_questions(request.query, answer=full_answer_accumulator, context=context_str)
                        yield self._emit_event(request.session_id, {"type": "suggestions", "content": suggestions})
                        
                        # Save Session Context (Expected Questions)
                        # Ensure we save even if it's empty, but usually it's not.
                        if suggestions:
                            # Mock Evaluation Generation
                            import random
                            evaluation = {
                                "score": random.randint(3, 5),
                                "comment": "Great question! This helps clarify key concepts.",
                                "dimensions": {
                                    "clarity": random.randint(4, 5),
                                    "depth": random.randint(3, 5),
                                    "relevance": 5
                                }
                            }
                            StudentStateManager.save_session_context(request.session_id, expect_questions=suggestions, evaluation=evaluation)
                            yield self._emit_event(request.session_id, {"type": "evaluation", "content": evaluation})
                        
                    except Exception as e:
                        logger.error(f"Failed to generate suggestions: {e}")

                    if request.video_timestamp:
                        yield self._emit_event(request.session_id, self._create_resume_event(request.video_timestamp))

                    return

            except Exception as e:
                logger.error(f"QAService Error: {e}", exc_info=True)
                yield self._emit_event(request.session_id, {"type": "error", "content": f"Critical Service Error: {str(e)}"})
                yield self._emit_event(request.session_id, {"type": "end"})

    async def adapt_script(self, request: AdaptScriptRequest, user_id: str = "student_001") -> AdaptScriptResponse:
        """
        Adapt the next script segment based on student profile and learning style.
        Uses 'summary' or 'translation' scenario configs if needed, or default.
        """
        # Example: Use summary config for adaptation to be concise
        llm = self.llm_clients.get("summary", self.llm)
        return AdaptScriptResponse(
            script_id="mock_script",
            adapted_content="Mock adapted content based on profile."
        )

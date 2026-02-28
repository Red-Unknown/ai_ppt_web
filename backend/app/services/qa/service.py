from typing import List, Optional, AsyncGenerator, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai import ChatOpenAI

from backend.app.core.config import settings
from backend.app.core import prompt_loader
from backend.app.schemas.qa import ChatRequest, ChatResponse, SourceNode, Intent, AdaptScriptRequest, AdaptScriptResponse
from backend.app.services.qa.retriever import TreeStructureRetriever
from backend.app.services.qa.router import DialogueRouter
from backend.app.services.teacher.agent import TeacherAgent
from backend.app.services.student.state_manager import StudentStateManager
from backend.app.utils.cache import local_cache
import time
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class ConfigurationError(Exception):
    """Raised when required configuration is missing."""
    pass

class QAService:

    SCENARIO_CONFIGS = {
        "qa": {"temperature": 0.7, "max_tokens": 2048},
        "summary": {"temperature": 0.3, "max_tokens": 4096},
        "translation": {"temperature": 0.1, "max_tokens": 4096},
    }

    def __init__(self):
        self._validate_config()
        
        # Initialize Core Components
        self.retriever = TreeStructureRetriever()
        self.router = DialogueRouter(llm_model=settings.DEEPSEEK_MODEL)
        self.teacher = TeacherAgent(llm_model=settings.DEEPSEEK_MODEL)
        
        # Current Prompt Version
        self.current_prompt_version = "v5_enhanced_zh"
        self._init_llm()
        
        # Simple Intent Cache (In-Memory) - kept for high-speed common queries
        self.intent_cache = {
            "课程介绍": "本课程是《大学物理》，主要涵盖力学、热学、电磁学等基础内容。",
            "评分标准": "平时成绩占 40%（含作业、签到、互动），期末考试占 60%。",
            "老师是谁": "我是您的 AI 助教，由 Role D 模块驱动。"
        }

    def _validate_config(self):
        if not settings.DEEPSEEK_API_KEY:
            error_msg = (
                "DEEPSEEK_API_KEY is missing! \n"
                "Please set it in your environment variables or .env file.\n"
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
            self.llm_clients[scenario] = ChatOpenAI(
                model=settings.DEEPSEEK_MODEL,
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
                temperature=config.get("temperature", settings.DEEPSEEK_TEMPERATURE),
                max_tokens=config.get("max_tokens", settings.DEEPSEEK_MAX_TOKENS),
                streaming=True,
                max_retries=3
            )
            
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
        
        # Default LLM
        self.llm = self.llm_clients["qa"]

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

    async def predict_next_questions(self, query: str) -> List[str]:
        """
        Intelligent Prediction: Predict next 3 likely questions.
        """
        # Mock logic based on keywords
        if "Newton" in query or "Law" in query:
            return ["What is the First Law?", "What is the Third Law?", "Real-world examples?"]
        elif "课程" in query:
            return ["如何考核?", "教材是什么?", "联系方式?"]
        else:
            return [f"More details about {query}?", "Examples?", "Related concepts?"]

    async def stream_answer_question(self, request: ChatRequest, user_id: str = "student_001") -> AsyncGenerator[str, None]:
        """
        Stream response for WebSocket using Server-Sent Events style JSON chunks.
        """
        # 1. Intent Cache Hit (Zero Latency - In-Memory)
        if request.query in self.intent_cache:
            yield json.dumps({"type": "start", "action": "QA_CACHE"})
            yield json.dumps({"type": "token", "content": self.intent_cache[request.query]})
            
            suggestions = await self.predict_next_questions(request.query)
            yield json.dumps({"type": "suggestions", "content": suggestions})
            yield json.dumps({"type": "end"})
            return

        # 2. Local Disk Cache Hit (Persistent) - DISABLED per user request
        # cached_response = local_cache.get(request.query, {"user_id": user_id, "top_k": request.top_k})
        # if cached_response:
        #    ...

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
            yield json.dumps({"type": "start", "action": "CONTROL"})
            yield json.dumps({"type": "token", "content": "执行控制指令: " + request.query})
            yield json.dumps({"type": "action", "data": {"command": request.query}})
            yield json.dumps({"type": "end"})
            return

        elif intent == Intent.FEEDBACK:
            # Retrieve context first
            self.retriever.current_path = request.current_path
            docs = self.retriever.invoke(request.query)
            context_str = "\n".join([d.page_content[:200] for d in docs])
            
            yield json.dumps({"type": "status", "content": "正在分析反馈..."})
            
            feedback_result = await self.teacher.handle_feedback(
                request.query, state, profile, context_str
            )
            
            if feedback_result.get("action") in ["SUPPLEMENT", "FALLBACK_VIDEO"]:
                StudentStateManager.increment_confusion(session_id)
            else:
                StudentStateManager.reset_confusion(session_id)

            yield json.dumps({"type": "start", "action": feedback_result.get("action")})
            
            if feedback_result.get("action") == "FALLBACK_VIDEO":
                yield json.dumps({"type": "action", "data": feedback_result})
                yield json.dumps({"type": "token", "content": feedback_result.get("message")})
            else:
                content = feedback_result.get("message") or feedback_result.get("content", "")
                chunk_size = 5
                for i in range(0, len(content), chunk_size):
                    yield json.dumps({"type": "token", "content": content[i:i+chunk_size]})
                    await asyncio.sleep(0.02)
                    
                if "audio_text" in feedback_result:
                     yield json.dumps({"type": "action", "data": {"audio_text": feedback_result["audio_text"]}})

            yield json.dumps({"type": "end"})
            return

        else: # Intent.QA
            yield json.dumps({"type": "status", "content": "正在检索知识库..."})
            StudentStateManager.reset_confusion(session_id)
            
            # 1. Update retriever context
            self.retriever.current_path = request.current_path
            self.retriever.top_k = request.top_k
            
            # 2. Retrieve documents
            docs = self.retriever.invoke(request.query)
            context_str = "\n\n".join([f"【来源：{d.metadata.get('path', '未知路径')}】\n内容：{d.page_content}" for d in docs])
            
            # Send Source Nodes
            sources = []
            for doc in docs:
                source = {
                    "node_id": doc.metadata.get("id", "unknown"),
                    "content": doc.page_content[:50] + "...",
                    "relevance": doc.metadata.get("score", 0.0)
                }
                sources.append(source)
                if "image" in doc.page_content.lower():
                     yield json.dumps({"type": "multimedia", "data": {"type": "image", "url": "http://mock.img/1.png"}})
            
            yield json.dumps({"type": "sources", "data": sources})
            yield json.dumps({"type": "start", "action": "QA_ANSWER"})

            # 3. Generate Answer (Streaming)
            # Determine prompt version and language
            style_map = {
                "default": "v5_enhanced",
                "creative": "v2_creative",
                "socratic": "v3_socratic"
            }
            # Handle prompt style selection
            base_style = style_map.get(request.prompt_style, "v5_enhanced")
            
            # Select LLM and Language
            if request.model == "gpt-4o":
                llm_key = "qa_gpt"
                lang_suffix = "_en"
                if llm_key not in self.llm_clients:
                    llm_key = "qa"
                    lang_suffix = "_zh"
            else:
                llm_key = "qa"
                lang_suffix = "_zh"
                
            prompt_version = f"{base_style}{lang_suffix}"

            # Use selected scenario LLM
            llm = self.llm_clients.get(llm_key, self.llm_clients["qa"])
            prompt = self.get_prompt_template(prompt_version)
            chain = prompt | llm | StrOutputParser()
            
            # Retrieve history
            history_list = StudentStateManager.get_history(session_id, limit=5)
            history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history_list])
            
            # Sandwich Defense
            final_query = request.query
            if lang_suffix == "_en":
                final_query += "\n\n(System Reminder: Please answer in Chinese)"
            else:
                final_query += "\n\n(系统提示：请务必使用中文回答)"

            chain_input = {
                "context": context_str, 
                "question": final_query,
                "history": history_str
            }
            
            start_time = time.time()
            full_answer = ""
            
            # Save User Query immediately
            try:
                StudentStateManager.add_history(session_id, "user", request.query)
            except Exception as e:
                logger.error(f"Failed to save user history: {e}")

            try:
                async for chunk in chain.astream(chain_input):
                    full_answer += chunk
                    yield json.dumps({"type": "token", "content": chunk})
            except Exception as e:
                logger.error(f"Error during LLM streaming: {e}")
                yield json.dumps({"type": "error", "content": "Sorry, I encountered an error while generating the response."})
            finally:
                # Save Assistant Response (Partial or Full)
                if full_answer:
                    try:
                        StudentStateManager.add_history(session_id, "assistant", full_answer)
                    except Exception as e:
                        logger.error(f"Failed to save assistant history: {e}")
            
            # Cache - DISABLED
            # local_cache.set(...)

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

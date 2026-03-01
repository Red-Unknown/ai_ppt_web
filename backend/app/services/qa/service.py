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
from backend.app.utils.cache import local_cache
from backend.app.services.qa.tools.retrieval import LocalKnowledgeTool
from backend.app.services.qa.agents.react import ReActAgent
import time
import json
import asyncio
import logging

logger = logging.getLogger(__name__)

import tiktoken

class ConfigurationError(Exception):
    """Raised when required configuration is missing."""
    pass

class QAService:

    SCENARIO_CONFIGS = {
        "qa": {"temperature": 0.7, "max_tokens": 10000},
        "reasoner": {"temperature": 0.6, "max_tokens": 10000},
        "summary": {"temperature": 0.3, "max_tokens": 10000},
        "translation": {"temperature": 0.1, "max_tokens": 4096},
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
                
            self.llm_clients[scenario] = ChatOpenAI(
                model=model_name,
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
                temperature=config.get("temperature", settings.DEEPSEEK_TEMPERATURE),
                max_tokens=config.get("max_tokens", settings.DEEPSEEK_MAX_TOKENS),
                streaming=True,
                max_retries=3,
                model_kwargs={"extra_body": {"include_reasoning": True}} if scenario == "reasoner" else {}
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

    def _init_agent(self):
        """Initialize ReAct Agent with skills."""
        # 1. Local Knowledge Tool (Enhanced RAG)
        local_rag = LocalKnowledgeTool(retriever=self.retriever, llm=self.llm_clients["qa"])
        
        # 2. Get other skills from SkillManager
        other_skills = list(self.skill_manager.skills.values())
        
        # Combine tools
        tools = [local_rag] + other_skills
        
        # Get System Prompt
        system_prompt = prompt_loader.get_prompt("v5_enhanced", "system")
        if not system_prompt:
            system_prompt = (
                "You are a helpful teaching assistant.\n"
                "Answer using ONLY the provided context.\n"
                "If unknown, reply: \"I don't know based on the course material.\"\n"
            )

        # Create Agent
        self.agent = ReActAgent(
            llm=self.llm_clients["qa"],
            tools=tools,
            max_iterations=8,
            system_prompt=system_prompt
        )
        logger.info(f"ReAct Agent initialized with tools: {[t.name for t in tools]}")

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
        try:
            encoding = tiktoken.get_encoding("cl100k_base")
        except Exception:
            # Fallback to gpt2 if cl100k_base not found
            encoding = tiktoken.get_encoding("gpt2")
            
        processed_msgs = []
        current_tokens = 0
        
        # Process from newest to oldest
        for msg in reversed(history):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            msg_str = f"{role}: {content}"
            
            # Count tokens
            tokens = len(encoding.encode(msg_str))
            
            # Reserve space for at least one message if possible, but strict limit applies
            if current_tokens + tokens > max_tokens and processed_msgs:
                break
                
            processed_msgs.append(msg_str)
            current_tokens += tokens
            
        # Reverse back to chronological order
        return "\n".join(reversed(processed_msgs))

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

        else: # Intent.QA (Handled by ReAct Agent)
            yield json.dumps({"type": "status", "content": "正在启动思维链 (ReAct)..."})
            StudentStateManager.reset_confusion(session_id)
            
            # Analyze QA Type for Instruction Injection
            qa_type = await self.analyzer.analyze(request.query)
            logger.info(f"QA Type: {qa_type}")

            # --- DEEPSEEK REASONER BYPASS START ---
            if request.model == "deepseek-reasoner":
                yield json.dumps({"type": "status", "content": "已切换至深度思考模式 (Reasoning)..."})
                
                # 1. Retrieve
                yield json.dumps({"type": "status", "content": "正在检索知识库..."})
                docs = self.retriever.invoke(request.query)
                context_str = "\n\n".join([f"【来源：{d.metadata.get('path', '未知路径')}】\n内容：{d.page_content}" for d in docs])
                
                # 2. Prepare Input
                history_list = StudentStateManager.get_history(session_id, limit=20)
                history_str = self._truncate_history_by_tokens(history_list, max_tokens=2000)
                
                prompt_template = self.get_prompt_template("v5_enhanced_zh") # Default to ZH
                chain_input = {
                    "context": context_str, 
                    "question": request.query, 
                    "history": history_str
                }
                
                yield json.dumps({"type": "start", "action": "QA_ANSWER"})
                
                # 3. Stream
                llm = self.llm_clients.get("reasoner", self.llm_clients["qa"])
                full_answer = ""
                
                try:
                    # Manually format messages
                    formatted_messages = prompt_template.format_messages(**chain_input)
                    async for chunk in llm.astream(formatted_messages):
                        # Extract reasoning content
                        reasoning = chunk.additional_kwargs.get("reasoning_content", "")
                        # Fallback for some proxies
                        if not reasoning:
                             reasoning = chunk.response_metadata.get("reasoning_content", "")
                        
                        if reasoning:
                            yield json.dumps({"type": "reasoning", "content": reasoning})
                        
                        if chunk.content:
                            full_answer += chunk.content
                            yield json.dumps({"type": "token", "content": chunk.content})
                    
                    yield json.dumps({"type": "end"})
                    
                    # Save History
                    try:
                        StudentStateManager.add_history(session_id, "user", request.query)
                        StudentStateManager.add_history(session_id, "assistant", full_answer)
                    except Exception as e:
                        logger.error(f"Failed to save history: {e}")
                    return
                    
                except Exception as e:
                    logger.error(f"Reasoner error: {e}")
                    yield json.dumps({"type": "error", "content": f"Reasoning Error: {str(e)}"})
                    yield json.dumps({"type": "end"})
                    return
            # --- DEEPSEEK REASONER BYPASS END ---

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
            
            # Prepare History
            history_list = StudentStateManager.get_history(session_id, limit=20)
            
            yield json.dumps({"type": "start", "action": "QA_ANSWER"})

            # Execute ReAct Loop
            full_answer_accumulator = ""
            try:
                async for event_str in self.agent.run(final_query, history=history_list):
                    event = json.loads(event_str)
                    evt_type = event.get("type")
                    
                    if evt_type == "thought":
                        # Display thought process as status or debug info
                        yield json.dumps({"type": "status", "content": f"Thinking: {event.get('content')}"})
                        
                    elif evt_type in ["tool_start", "tool_result", "tool_error"]:
                        # MCP Events - Pass through directly
                        yield event_str
                        
                    elif evt_type == "answer":
                        content = event.get("content", "")
                        full_answer_accumulator += content
                        # Simulate streaming for better UX since ReActAgent returns bulk answer
                        chunk_size = 5
                        for i in range(0, len(content), chunk_size):
                            yield json.dumps({"type": "token", "content": content[i:i+chunk_size]})
                            await asyncio.sleep(0.01)
                            
                    elif evt_type == "error":
                        yield json.dumps({"type": "error", "content": event.get("content")})
                        
                    elif evt_type == "done":
                        yield json.dumps({"type": "end"})
                        
            except Exception as e:
                logger.error(f"ReAct execution failed: {e}", exc_info=True)
                yield json.dumps({"type": "error", "content": f"System Error: {str(e)}"})
                yield json.dumps({"type": "end"})
            
            # Save Interaction
            try:
                StudentStateManager.add_history(session_id, "user", request.query)
                if full_answer_accumulator:
                    StudentStateManager.add_history(session_id, "assistant", full_answer_accumulator)
            except Exception as e:
                logger.error(f"Failed to save history: {e}")
            return

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

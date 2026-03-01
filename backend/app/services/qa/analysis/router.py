import re
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from backend.app.core.config import settings
from backend.app.schemas.qa import Intent

class DialogueRouter:
    """
    Routes user input to the appropriate handler (QA, Feedback, or Control)
    using a hybrid approach: Regex (Fast) + LLM (Smart).
    """

    def __init__(self, llm_model: str = "gpt-3.5-turbo"):
        # Use DeepSeek settings if available, otherwise fallback to defaults (which might fail if no key)
        self.llm = ChatOpenAI(
            model=llm_model, 
            temperature=0,
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        
        # Regex Patterns
        self.control_patterns = [
            r"暂停", r"停止", r"继续", r"开始", r"跳过", r"上一页", r"下一页"
        ]
        self.feedback_patterns = [
            r"没听懂", r"不懂", r"太快了", r"太慢了", r"再讲一遍", r"不明白", r"有点晕"
        ]
        
        # LLM Prompt
        self.prompt = ChatPromptTemplate.from_template(
            """
            Classify the student's input into one of the following categories:
            - QA: Questions about the course content (e.g., "What is a gradient?", "Why use ReLU?").
            - FEEDBACK: Feedback about their learning state or the lecture pace (e.g., "I'm confused", "Too fast", "I don't understand").
            - CONTROL: Commands to control the playback (e.g., "Pause", "Resume", "Next").
            
            Input: {query}
            
            Return ONLY the category name (QA, FEEDBACK, CONTROL).
            """
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

    def route(self, query: str) -> Intent:
        """
        Determine the intent of the user query.
        """
        # 1. Try Regex first (Fast Path)
        intent = self._route_regex(query)
        if intent:
            return intent
            
        # 2. Fallback to LLM (Smart Path)
        return self._route_llm(query)

    def _route_regex(self, query: str) -> Optional[Intent]:
        # Clean query
        q = query.strip()
        
        # Control Patterns (Strict Matching)
        # Check first because commands are usually short and specific
        for pattern in self.control_patterns:
            if re.search(pattern, q):
                return Intent.CONTROL

        # Feedback Patterns
        for pattern in self.feedback_patterns:
            if re.search(pattern, q):
                # "太快了" / "太慢了" / "再讲一遍" can be seen as CONTROL or FEEDBACK.
                # If we want to strictly follow the doc where "太快了" -> CONTROL, we should map it here.
                if "太快" in q or "太慢" in q or "再讲一遍" in q:
                     return Intent.CONTROL
                return Intent.FEEDBACK

        # QA Patterns (Priority High for Questions)
        qa_keywords = ["什么", "为什么", "怎么", "解释", "含义", "意思", "who", "what", "why", "how"]
        if any(k in q for k in qa_keywords) or "?" in q or "？" in q:
            # Even if it contains "暂停", "为什么暂停" is a QA.
            # Unless it is exactly "为什么要暂停？" which is ambiguous but usually QA.
            return Intent.QA
                
        return None

    def _route_llm(self, query: str) -> Intent:
        try:
            result = self.chain.invoke({"query": query}).strip().upper()
            if "QA" in result:
                return Intent.QA
            elif "FEEDBACK" in result:
                return Intent.FEEDBACK
            elif "CONTROL" in result:
                return Intent.CONTROL
            else:
                return Intent.QA # Default fallback
        except Exception as e:
            print(f"Router LLM Error: {e}")
            return Intent.QA # Fallback on error

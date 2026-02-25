from typing import List, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai import ChatOpenAI

from backend.app.schemas.qa import ChatRequest, ChatResponse, SourceNode, Intent
from backend.app.services.qa.retriever import TreeStructureRetriever
from backend.app.services.qa.router import DialogueRouter
from backend.app.services.teacher.agent import TeacherAgent
from backend.app.services.student.state_manager import StudentStateManager

class QAService:
    def __init__(self, llm_model: str = "gpt-3.5-turbo"):
        # Initialize LLM (Mock for now or use Env Var)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.3)
        self.retriever = TreeStructureRetriever()
        self.router = DialogueRouter(llm_model=llm_model)
        self.teacher = TeacherAgent(llm_model=llm_model)
        
        # Define Prompt Template for QA
        self.qa_prompt = ChatPromptTemplate.from_template(
            """You are an intelligent teaching assistant for an online course. 
            Answer the student's question based ONLY on the following context. 
            If the answer is not in the context, say "I don't know based on the course material."
            
            Context:
            {context}
            
            Student Question: {question}
            """
        )

    async def answer_question(self, request: ChatRequest, user_id: str = "student_001") -> ChatResponse:
        """
        Process a user query using Router -> (QA | Teacher | Control) logic.
        """
        # 1. Get/Init Student Profile & State
        profile = StudentStateManager.get_profile(user_id)
        if not profile:
            profile = StudentStateManager.create_or_update_profile(user_id, {})
            
        session_id = request.session_id or "default_session"
        state = StudentStateManager.get_state(session_id)
        if not state:
            state = StudentStateManager.init_state(session_id, request.current_path or "unknown_topic")

        # 2. Route Intent
        intent = self.router.route(request.query)
        
        if intent == Intent.CONTROL:
            return ChatResponse(
                answer="执行控制指令",
                session_id=session_id,
                action="CONTROL",
                action_data={"command": request.query}
            )
            
        elif intent == Intent.FEEDBACK:
            # Retrieve context to help teacher agent understand what student is reacting to
            self.retriever.current_path = request.current_path
            docs = self.retriever.invoke(request.query) # Use query to find relevant context if possible
            context_str = "\n".join([d.page_content[:200] for d in docs])
            
            feedback_result = await self.teacher.handle_feedback(
                feedback_text=request.query,
                state=state,
                profile=profile,
                context_content=context_str
            )
            
            # Update state if confused
            if feedback_result.get("action") in ["SUPPLEMENT", "FALLBACK_VIDEO"]:
                StudentStateManager.increment_confusion(session_id)
            else:
                StudentStateManager.reset_confusion(session_id)
                
            return ChatResponse(
                answer=feedback_result.get("message", "正在为您生成补充讲解..."),
                session_id=session_id,
                action=feedback_result.get("action"),
                action_data=feedback_result
            )

        else: # Intent.QA
            # Reset confusion on valid QA
            StudentStateManager.reset_confusion(session_id)
            
            # 1. Update retriever context
            self.retriever.current_path = request.current_path
            self.retriever.top_k = request.top_k
            
            # 2. Retrieve documents
            docs = self.retriever.invoke(request.query)
            context_str = "\n\n".join([d.page_content for d in docs])
            
            # 3. Generate Answer
            chain_input = {"context": context_str, "question": request.query}
            answer_text = self.qa_prompt.format_messages(**chain_input)
            response_msg = self.llm.invoke(answer_text)
            answer = response_msg.content

            # 4. Format Response
            sources = [
                SourceNode(
                    node_id=doc.metadata.get("node_id", "unknown"),
                    content=doc.page_content[:100] + "...",
                    path=doc.metadata.get("path", "unknown"),
                    relevance_score=doc.metadata.get("score", 0.0),
                    context=doc.metadata.get("context", {})
                ) for doc in docs
            ]

            return ChatResponse(
                answer=answer,
                source_nodes=sources,
                session_id=session_id,
                action="QA_ANSWER"
            )

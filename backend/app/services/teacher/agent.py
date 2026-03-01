from typing import Optional, Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from backend.app.schemas.student import StudentProfile, StudentState, InteractionMode
from backend.app.core.config import settings

class TeacherAgent:
    """
    Intelligent Teacher Agent responsible for:
    1. Generating supplementary explanations (analogies).
    2. Adapting lecture scripts based on student profile.
    3. Handling student feedback.
    """

    def __init__(self, llm_model: str = "gpt-4o"):
        self.llm = ChatOpenAI(
            model=llm_model, 
            temperature=0.7,
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        
        # Prompt for Supplementary Explanation
        self.supplement_prompt = ChatPromptTemplate.from_template(
            """
            You are an expert tutor. The student is confused about the current topic: "{topic}".
            
            Student Profile:
            - Weaknesses: {weaknesses}
            - Learning Style: {learning_style}
            
            Task: Generate a short (30-60 seconds read time) supplementary explanation.
            Strategy: Use an analogy related to daily life or history to explain the concept.
            Tone: Encouraging, clear, and simple.
            Language: Chinese (Simplified) unless the topic or context is explicitly in English.
            
            Current Context Content:
            {context_content}
            
            Output ONLY the explanation text.
            """
        )

        # Prompt for Script Adaptation
        self.adaptation_prompt = ChatPromptTemplate.from_template(
            """
            You are an expert educational content adaptor.
            Rewrite the following lecture script segment to match the student's needs.
            
            Student Profile:
            - Weaknesses: {weaknesses}
            - Learning Style: {learning_style}
            
            Original Script:
            {original_script}
            
            Requirements:
            1. Keep the core technical facts unchanged.
            2. Adjust the tone to be more accessible.
            3. If the student is visual, use descriptive language.
            4. Keep the length similar to the original.
            
            Output ONLY the rewritten script.
            """
        )

    async def handle_feedback(
        self, 
        feedback_text: str, 
        state: StudentState, 
        profile: StudentProfile,
        context_content: str
    ) -> Dict[str, Any]:
        """
        Analyze feedback and decide on action (Supplement or Resume).
        """
        # Simple sentiment analysis (Mock or LLM)
        # For now, assume if routed here as FEEDBACK, we check for confusion keywords
        confusion_keywords = ["不懂", "没听懂", "困惑", "难", "confused", "hard", "没懂", "不明白", "看不懂", "不明"]
        is_confused = any(k in feedback_text for k in confusion_keywords)
        
        if is_confused:
            # Check fallback condition
            if state.confusion_count >= 2:
                return {
                    "action": "FALLBACK_VIDEO",
                    "message": "我看这部分确实比较难，建议你直接观看详细视频讲解。",
                    "video_jump_link": f"/course/video/{state.current_topic}?t=120" # Mock link
                }
            
            # Generate Supplement
            explanation = await self._generate_supplement(state.current_topic, profile, context_content)
            return {
                "action": "SUPPLEMENT",
                "content": explanation,
                "audio_text": explanation
            }
        
        return {"action": "RESUME", "message": "好的，我们继续。"}

    async def _generate_supplement(self, topic: str, profile: StudentProfile, context_content: str) -> str:
        """
        Generate supplementary explanation using LLM.
        """
        # If context is empty or very short, fallback to using the topic itself for context generation
        if not context_content or len(context_content) < 50:
             # This happens if RAG failed or topic is not in KB. 
             # We rely on the LLM's internal knowledge but prompt it to be careful.
             context_content = f"Topic to explain: {topic}. (Note: Local knowledge base lacks specific details, please provide general educational explanation)"

        chain = self.supplement_prompt | self.llm | StrOutputParser()
        try:
            return await chain.ainvoke({
                "topic": topic, # Ensure 'topic' is passed correctly
                "weaknesses": ",".join(profile.weaknesses),
                "learning_style": profile.learning_style,
                "context_content": context_content
            })
        except Exception as e:
            return f"Error generating explanation: {e}"

    async def adapt_next_segment(
        self, 
        original_script: str, 
        profile: StudentProfile,
        force_adapt: bool = False
    ) -> str:
        """
        Adapt the next script segment using LLM.
        """
        if not force_adapt and profile.interaction_mode != InteractionMode.ADAPTIVE:
            return original_script
            
        chain = self.adaptation_prompt | self.llm | StrOutputParser()
        try:
            return await chain.ainvoke({
                "weaknesses": ",".join(profile.weaknesses),
                "learning_style": profile.learning_style,
                "original_script": original_script
            })
        except Exception as e:
            return original_script

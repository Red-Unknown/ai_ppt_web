from typing import Dict, Optional, Any
import logging
from backend.app.core.config import settings
from backend.app.services.qa.tools.base import BaseSkill
from backend.app.services.qa.tools.calculator import MathSkill
from backend.app.services.qa.tools.web_search import WebSearchSkill

logger = logging.getLogger(__name__)

class SkillManager:
    """
    Manages loading, registration, and dispatching of skills.
    Acts as the 'Rule Engine' for skill selection based on intent and priority.
    """
    
    def __init__(self):
        self.skills: Dict[str, BaseSkill] = {}
        self.skill_priorities: Dict[str, int] = {}
        self.token_usage: Dict[str, int] = {} # Track token usage per skill
        self._initialize_skills()
        
    def _initialize_skills(self):
        """Register available skills."""
        # 1. Math Skill (High Priority for Calculation)
        try:
            # Pass the model from settings, default to what's configured
            model = settings.DEEPSEEK_MODEL if hasattr(settings, "DEEPSEEK_MODEL") else "gpt-3.5-turbo"
            math_skill = MathSkill(llm_model=model)
            self.register_skill(math_skill, priority=90)
        except Exception as e:
            logger.error(f"Failed to initialize MathSkill: {e}")
            
        # 2. Web Search Skill (High Priority for Real-time Info)
        try:
            search_skill = WebSearchSkill()
            self.register_skill(search_skill, priority=80)
        except Exception as e:
            logger.error(f"Failed to initialize WebSearchSkill: {e}")
            
    def register_skill(self, skill: BaseSkill, priority: int = 50):
        """Register a skill instance with priority (higher is better)."""
        self.skills[skill.name] = skill
        self.skill_priorities[skill.name] = priority
        self.token_usage[skill.name] = 0
        logger.info(f"Skill registered: {skill.name} (Priority: {priority})")
        
    def get_skill(self, intent: str, query: str = "") -> Optional[BaseSkill]:
        """
        Dispatch skill based on intent and rules.
        
        Rules:
        1. Explicit Keyword Overrides (Highest Priority)
        2. Intent Classification (High Priority)
        3. Fallback to None (Standard QA)
        
        Returns:
            The selected BaseSkill instance, or None if no skill matches.
        """
        query_lower = query.lower()
        candidates = []

        # Rule 1: Keyword Overrides
        if "calculate" in query_lower or "compute" in query_lower or "solve" in query_lower:
            if "math_solver" in self.skills:
                candidates.append(("math_solver", self.skill_priorities["math_solver"] + 10)) # Boost priority

        if "search" in query_lower or "find online" in query_lower or "latest" in query_lower:
            if "web_search" in self.skills:
                candidates.append(("web_search", self.skill_priorities["web_search"] + 10))

        # Rule 2: Intent Classification
        if intent == "CALCULATION" and "math_solver" in self.skills:
             candidates.append(("math_solver", self.skill_priorities["math_solver"]))
        
        if intent == "WEB_SEARCH" and "web_search" in self.skills:
             candidates.append(("web_search", self.skill_priorities["web_search"]))

        # Select best candidate
        if candidates:
            # Sort by priority desc
            candidates.sort(key=lambda x: x[1], reverse=True)
            best_skill_name = candidates[0][0]
            logger.info(f"Skill dispatched: {best_skill_name} (Score: {candidates[0][1]})")
            return self.skills[best_skill_name]

        return None

    def record_usage(self, skill_name: str, tokens: int):
        """Record token usage for a skill."""
        if skill_name in self.token_usage:
            self.token_usage[skill_name] += tokens

    async def execute_skill(self, skill_name: str, query: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a specific skill by name.
        Useful for direct invocation or testing.
        """
        skill = self.skills.get(skill_name)
        if not skill:
            return {"status": "error", "message": f"Skill '{skill_name}' not found."}
            
        try:
            result = await skill.execute(query, **kwargs)
            # Estimate token usage (simplified: 1 token ~ 4 chars)
            # In production, this should come from the LLM response usage stats
            content = result.get("content", "")
            code = result.get("details", {}).get("code", "")
            estimated_tokens = (len(content) + len(code)) // 4
            self.record_usage(skill_name, estimated_tokens)
            
            return result
        except Exception as e:
            logger.error(f"Error executing skill '{skill_name}': {e}")
            return {"status": "error", "message": str(e)}

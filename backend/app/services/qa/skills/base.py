from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseSkill(ABC):
    """
    Abstract base class for all QA skills.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the unique name of the skill."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """Return a description of what the skill does."""
        pass

    @abstractmethod
    async def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Execute the skill.
        
        Args:
            query: The user's query or specific input for the skill.
            
        Returns:
            A dictionary containing the results. 
            Must include "status" ("success" or "error") and "content" (the result).
            Can include "details" (intermediate steps, code, etc.).
        """
        pass

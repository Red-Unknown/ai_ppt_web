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

    def to_tool_schema(self) -> Dict[str, Any]:
        """
        Convert skill to OpenAI tool schema.
        Can be overridden by subclasses for more complex arguments.
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The input query or command for the tool."
                        }
                    },
                    "required": ["query"]
                }
            }
        }

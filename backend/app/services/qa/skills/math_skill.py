from typing import Dict, Any
from backend.app.services.qa.skills.base import BaseSkill
from backend.app.services.qa.math_solver import MathSolver
from backend.app.core.config import settings

class MathSkill(BaseSkill):
    def __init__(self, llm_model: str = "gpt-3.5-turbo"):
        self.solver = MathSolver(llm_model=llm_model)
        
    @property
    def name(self) -> str:
        return "math_solver"
        
    @property
    def description(self) -> str:
        return "Solves mathematical problems by generating and executing Python code."
        
    async def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        result = await self.solver.solve(query)
        
        status = "success" if result.get("result") != "Error" else "error"
        
        return {
            "status": status,
            "content": result.get("answer", ""),
            "details": {
                "code": result.get("code", ""),
                "execution_result": result.get("result", ""),
                "type": "python_code"
            }
        }

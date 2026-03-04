from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from backend.app.core.config import settings
from backend.app.utils.sandbox import SafeCodeExecutor, SecurityError, ExecutionError
import logging
import ast

logger = logging.getLogger(__name__)

class MathSolver:
    """
    Handles numerical calculation questions by generating and executing Python code.
    """
    
    def __init__(self, llm_model: str = "gpt-3.5-turbo"):
        # Use DeepSeek settings if available
        # Note: Using settings.DEEPSEEK_MODEL passed from service
        self.llm = ChatOpenAI(
            model=llm_model, 
            temperature=0,
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        
        self.code_gen_prompt = ChatPromptTemplate.from_template(
            """
            You are a Python code generator for mathematical problems.
            Write a Python script to solve the following problem.
            
            Problem: {query}
            
            Rules:
            1. Use ONLY standard libraries (math, random, datetime).
            2. Do NOT use input(), print(), or external libraries.
            3. Store the final result in a variable named `result`.
            4. The code must be concise and safe.
            5. If the problem is "Solve 2x + 3 = 7", output code to calculate x.
            
            Output ONLY the Python code. No markdown formatting.
            """
        )
        self.code_gen_chain = self.code_gen_prompt | self.llm | StrOutputParser()

        self.explanation_prompt = ChatPromptTemplate.from_template(
            """
            You are a helpful math tutor.
            Based on the user's question and the calculated result, provide a clear, natural language answer.
            
            Question: {query}
            Code Used: {code}
            Calculation Result: {result}
            
            Explain the steps briefly if needed.
            """
        )
        self.explanation_chain = self.explanation_prompt | self.llm | StrOutputParser()

    async def solve(self, query: str) -> dict:
        """
        Solves a math problem end-to-end.
        Returns: {"answer": str, "code": str, "result": str}
        """
        try:
            # 1. Generate Code
            raw_code = await self.code_gen_chain.ainvoke({"query": query})
            # Clean up markdown if present
            code = raw_code.replace("```python", "").replace("```", "").strip()
            
            # 2. Execute Code
            try:
                # Use a separate process wrapper or just call the static method
                # Since we are async, ideally we should run this in a thread executor to avoid blocking
                # But for simplicity in this MVP, we call it directly (it spawns a process internally)
                result = SafeCodeExecutor.execute(code)
            except (ExecutionError, SecurityError) as e:
                return {
                    "answer": f"I couldn't calculate the answer due to an error: {str(e)}",
                    "code": code,
                    "result": "Error"
                }

            # 3. Generate Explanation
            explanation = await self.explanation_chain.ainvoke({
                "query": query,
                "code": code,
                "result": result
            })
            
            return {
                "answer": explanation,
                "code": code,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"MathSolver Error: {e}")
            return {
                "answer": "Sorry, I encountered an internal error while processing your calculation.",
                "code": "",
                "result": "Error"
            }

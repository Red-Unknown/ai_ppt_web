from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from backend.app.core.config import settings
from typing import List, Optional
import json
import logging

logger = logging.getLogger(__name__)

class QAAnalyzer:
    """
    Analyzes the user query to determine the specific QA type.
    Supported types:
    - STANDARD: Default QA
    - MULTI_STEP: Requires reasoning or combining multiple concepts (Type 5)
    - COMPARISON: Requires comparing concepts (Type 17)
    - PROOF: Requires proof or verification (Type 19)
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
        
        self.prompt = ChatPromptTemplate.from_template(
            """
            Analyze the student's question and classify it into one of the following categories:
            
            1. MULTI_STEP: Requires multi-step reasoning, combining multiple concepts, or solving a complex problem.
               Example: "How to use quadratic functions to solve optimization problems?"
               
            2. COMPARISON: Requires comparing two or more concepts, definitions, or methods.
               Example: "What is the difference between sine and cosine?"
               
            3. PROOF: Requires proving a theorem, deriving a formula, or verifying a statement.
               Example: "Prove that the sum of angles in a triangle is 180 degrees."
               
            4. EXAMPLE: Requests for examples, real-world applications, or scenarios.
               Example: "Give me an example of Newton's Third Law."

            5. CALCULATION: Requires numerical calculation, solving math equations, or quantitative analysis.
               Example: "Calculate the area of a circle with radius 5." or "Solve 2x + 3 = 7."

            6. WEB_SEARCH: Requires real-time information, current events, or external knowledge not in the course.
               Example: "What is the latest version of Python?" or "Who won the Nobel Prize in Physics 2024?"

            7. STANDARD: Simple definition lookup, fact retrieval, or single-concept question from course material.
               Example: "What is a function?"
            
            Return ONLY the category name (MULTI_STEP, COMPARISON, PROOF, EXAMPLE, CALCULATION, WEB_SEARCH, STANDARD).
            """
        )
        self.chain = self.prompt | self.llm | StrOutputParser()

        # Query decomposition prompt for MULTI_STEP and COMPARISON
        self.decomposition_prompt = ChatPromptTemplate.from_template(
            """
            Break down the following complex question into 2-3 simple search queries to retrieve relevant information from a knowledge base.
            
            Question: {query}
            Type: {type}
            
            Return ONLY a JSON list of strings. Do not include markdown formatting.
            Example: ["definition of sine", "definition of cosine", "differences between sine and cosine"]
            """
        )
        self.decomposition_chain = self.decomposition_prompt | self.llm | StrOutputParser()

    async def analyze(self, query: str) -> str:
        try:
            result = await self.chain.ainvoke({"query": query})
            category = result.strip().upper()
            # Normalize just in case
            if "MULTI_STEP" in category: return "MULTI_STEP"
            if "COMPARISON" in category: return "COMPARISON"
            if "PROOF" in category: return "PROOF"
            if "EXAMPLE" in category: return "EXAMPLE"
            if "CALCULATION" in category: return "CALCULATION"
            if "WEB_SEARCH" in category: return "WEB_SEARCH"
            return "STANDARD"
        except Exception as e:
            logger.error(f"Analyzer Error: {e}")
            return "STANDARD"

    async def decompose_query(self, query: str, type: str) -> List[str]:
        try:
            result = await self.decomposition_chain.ainvoke({"query": query, "type": type})
            # Clean up the result to ensure valid JSON
            cleaned_result = result.replace("```json", "").replace("```", "").strip()
            # Handle potential trailing commas or formatting issues simply by try-catch
            queries = json.loads(cleaned_result)
            if isinstance(queries, list):
                return queries
            return [query]
        except Exception as e:
            logger.error(f"Decomposition Error: {e}")
            return [query]

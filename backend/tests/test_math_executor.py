import asyncio
import pytest
import math
import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.app.utils.sandbox import SafeCodeExecutor, ExecutionError, SecurityError
from backend.app.services.qa.math_solver import MathSolver

def test_sandbox_simple_math():
    code = "result = 2 + 2"
    assert SafeCodeExecutor.execute(code) == "4"

def test_sandbox_advanced_math():
    code = "import math\nresult = math.sqrt(16)"
    assert float(SafeCodeExecutor.execute(code)) == 4.0

def test_sandbox_forbidden_import():
    code = "import os\nresult = os.listdir('.')"
    with pytest.raises(SecurityError):
        SafeCodeExecutor.execute(code)

def test_sandbox_forbidden_open():
    code = "result = open('test.txt', 'r').read()"
    with pytest.raises(SecurityError):
        SafeCodeExecutor.execute(code)

def test_sandbox_infinite_loop():
    # This might take 5 seconds to timeout
    code = "while True: pass"
    with pytest.raises(ExecutionError, match="Execution timed out"):
        SafeCodeExecutor.execute(code, timeout=1)

@pytest.mark.asyncio
async def test_math_solver_flow():
    with patch('backend.app.core.config.settings') as mock_settings:
        mock_settings.DEEPSEEK_API_KEY = "mock"
        mock_settings.DEEPSEEK_BASE_URL = "http://mock"
        mock_settings.DEEPSEEK_MODEL = "deepseek"
        
        # Patch ChatOpenAI within the module where it's used
        with patch('backend.app.services.qa.math_solver.ChatOpenAI') as MockLLM:
            solver = MathSolver()
            
            # Mock Code Gen Chain
            solver.code_gen_chain = AsyncMock()
            solver.code_gen_chain.ainvoke.return_value = "result = 10 * 10"
            
            # Mock Explanation Chain
            solver.explanation_chain = AsyncMock()
            solver.explanation_chain.ainvoke.return_value = "The answer is 100."
            
            result = await solver.solve("Calculate 10 times 10")
            
            assert str(result["result"]) == "100"
            assert result["answer"] == "The answer is 100."
            assert "result = 10 * 10" in result["code"]

@pytest.mark.asyncio
async def test_multistep_math_problem():
    """
    Test a complex multi-step calculation:
    Problem: Calculate the area of a circle whose radius is the hypotenuse of a right triangle with legs 3 and 4.
    """
    with patch('backend.app.core.config.settings') as mock_settings:
        mock_settings.DEEPSEEK_API_KEY = "mock"
        mock_settings.DEEPSEEK_BASE_URL = "http://mock"
        mock_settings.DEEPSEEK_MODEL = "deepseek"
        
        with patch('backend.app.services.qa.math_solver.ChatOpenAI') as MockLLM:
            solver = MathSolver()
            
            # Mock Code Gen Chain: Simulating the LLM output for a multi-step problem
            solver.code_gen_chain = AsyncMock()
            code_snippet = """
import math
leg_a = 3
leg_b = 4
hypotenuse = math.sqrt(leg_a**2 + leg_b**2)
radius = hypotenuse
result = math.pi * (radius ** 2)
"""
            solver.code_gen_chain.ainvoke.return_value = code_snippet
            
            # Mock Explanation Chain
            solver.explanation_chain = AsyncMock()
            solver.explanation_chain.ainvoke.return_value = "The hypotenuse is 5, so the radius is 5. The area is 25π ≈ 78.54."
            
            query = "Calculate the area of a circle with a radius equal to the hypotenuse of a right triangle with sides 3 and 4."
            result = await solver.solve(query)
            
            # Verification
            expected_val = math.pi * (5**2)
            actual_val = float(result["result"])
            
            assert abs(actual_val - expected_val) < 0.0001
            assert "math.sqrt" in result["code"]
            assert "math.pi" in result["code"]
            print(f"\n[Multi-step Test]\nQuery: {query}\nCode Generated:\n{result['code']}\nResult: {result['result']}\nExplanation: {result['answer']}")

if __name__ == "__main__":
    test_sandbox_simple_math()
    test_sandbox_advanced_math()
    try:
        test_sandbox_forbidden_import()
        print("Security check (import) passed")
    except Exception as e:
        print(f"Security check (import) failed: {e}")

    try:
        test_sandbox_forbidden_open()
        print("Security check (open) passed")
    except Exception as e:
        print(f"Security check (open) failed: {e}")
        
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(test_math_solver_flow())
    print("MathSolver flow passed")
    
    loop.run_until_complete(test_multistep_math_problem())
    print("Multi-step Math Problem passed")

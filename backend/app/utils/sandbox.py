import ast
import multiprocessing
import math
import sys
import io
import contextlib
import logging

logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Raised when code violates security policies."""
    pass

class ExecutionError(Exception):
    """Raised when code execution fails."""
    pass

def _restricted_execute(code_str: str, result_queue: multiprocessing.Queue):
    """
    Executes Python code in a restricted environment.
    Designed to run in a separate process.
    """
    # 1. Capture stdout
    stdout_capture = io.StringIO()
    
    # 2. Define Restricted Globals
    safe_globals = {
        "__builtins__": {
            "abs": abs, "all": all, "any": any, "bin": bin, "bool": bool,
            "chr": chr, "complex": complex, "dict": dict, "divmod": divmod,
            "enumerate": enumerate, "filter": filter, "float": float,
            "format": format, "frozenset": frozenset, "hex": hex,
            "int": int, "len": len, "list": list, "map": map, "max": max,
            "min": min, "oct": oct, "ord": ord, "pow": pow, "range": range,
            "reversed": reversed, "round": round, "set": set, "slice": slice,
            "sorted": sorted, "str": str, "sum": sum, "tuple": tuple,
            "zip": zip, "print": print,
            "__import__": __import__  # Allowed but restricted by AST check
        },
        "math": math,
    }

    try:
        # Redirect stdout
        with contextlib.redirect_stdout(stdout_capture):
            exec(code_str, safe_globals)
            
        output = stdout_capture.getvalue()
        # Check if result variable exists, otherwise use stdout
        if "result" in safe_globals:
            final_result = safe_globals["result"]
        else:
            final_result = output.strip()
            
        result_queue.put({"status": "success", "output": str(final_result)})
        
    except Exception as e:
        result_queue.put({"status": "error", "error": str(e)})

class SafeCodeExecutor:
    """
    Executes Python code in a sandboxed environment with timeouts and restrictions.
    """
    
    FORBIDDEN_KEYWORDS = [
        "import os", "import sys", "import subprocess", "import shutil",
        "open(", "eval(", "exec(", "os.", "sys.", "subprocess."
    ]

    @staticmethod
    def validate_code(code: str):
        """
        Static analysis to block obvious malicious patterns.
        """
        # 1. Keyword check
        for keyword in SafeCodeExecutor.FORBIDDEN_KEYWORDS:
            if keyword in code:
                raise SecurityError(f"Forbidden keyword detected: {keyword}")

        # 2. AST Analysis (More robust)
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.name not in ["math", "random", "datetime"]:
                            raise SecurityError(f"Importing module '{alias.name}' is not allowed.")
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in ["open", "eval", "exec"]:
                         raise SecurityError(f"Function '{node.func.id}' is forbidden.")
        except SyntaxError as e:
            raise ExecutionError(f"Syntax Error: {e}")

    @staticmethod
    def execute(code: str, timeout: int = 5) -> str:
        """
        Execute code with timeout protection.
        """
        # 1. Validate
        SafeCodeExecutor.validate_code(code)
        
        # 2. Run in Process
        result_queue = multiprocessing.Queue()
        process = multiprocessing.Process(target=_restricted_execute, args=(code, result_queue))
        
        process.start()
        process.join(timeout)
        
        if process.is_alive():
            process.terminate()
            raise ExecutionError("Execution timed out.")
            
        if result_queue.empty():
            raise ExecutionError("No result returned (Process crashed or silent).")
            
        result = result_queue.get()
        if result["status"] == "error":
            raise ExecutionError(result["error"])
            
        return result["output"]

import ast
import multiprocessing
import math
import sys
import io
import contextlib
import logging
import queue
import time
import uuid
from typing import Optional, Dict, Any, Tuple

logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Raised when code violates security policies."""
    pass

class ExecutionError(Exception):
    """Raised when code execution fails."""
    pass

def _execute_code_in_isolation(code_str: str) -> Dict[str, Any]:
    """
    Executes Python code in a restricted environment.
    Returns a dictionary with 'status', 'output', or 'error'.
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
    
    # Optional: Inject sympy if available
    try:
        import sympy
        safe_globals["sympy"] = sympy
    except ImportError:
        pass

    # Optional: Inject numpy if available
    try:
        import numpy
        safe_globals["numpy"] = numpy
    except ImportError:
        pass

    # Optional: Inject pandas if available
    try:
        import pandas
        safe_globals["pandas"] = pandas
    except ImportError:
        pass

    # Optional: Inject scipy if available
    try:
        import scipy
        safe_globals["scipy"] = scipy
    except ImportError:
        pass
    
    # Optional: Inject matplotlib.pyplot if available
    try:
        import matplotlib.pyplot
        safe_globals["plt"] = matplotlib.pyplot
    except ImportError:
        pass

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
            
        return {"status": "success", "output": str(final_result)}
        
    except Exception as e:
        return {"status": "error", "error": str(e)}

def _worker_loop(input_queue: multiprocessing.Queue, output_queue: multiprocessing.Queue):
    """
    Long-running worker loop.
    Constantly reads (req_id, code) from input_queue, executes it, and puts (req_id, result) to output_queue.
    """
    while True:
        try:
            item = input_queue.get()
            if item is None: # Sentinel to stop
                break
            
            req_id, code = item
            result = _execute_code_in_isolation(code)
            output_queue.put((req_id, result))
            
        except Exception as e:
            # Should not happen ideally
            try:
                # Try to report fatal error
                if 'req_id' in locals():
                    output_queue.put((req_id, {"status": "error", "error": f"Worker Critical Error: {str(e)}"}))
            except:
                pass

class Worker:
    """
    Manages a single persistent worker process.
    """
    def __init__(self):
        self.input_queue = multiprocessing.Queue()
        self.output_queue = multiprocessing.Queue()
        self.process = multiprocessing.Process(
            target=_worker_loop, 
            args=(self.input_queue, self.output_queue),
            daemon=True
        )
        self.process.start()
        self.busy = False
        self.created_at = time.time()

    def restart(self):
        """Terminates the current process and starts a new one."""
        if self.process.is_alive():
            self.process.terminate()
            self.process.join(timeout=1)
        
        # Close queues to release resources
        try:
            self.input_queue.close()
            self.output_queue.close()
        except:
            pass
            
        self.__init__()

    def is_alive(self):
        return self.process.is_alive()

class SafeCodeExecutor:
    """
    Executes Python code in a sandboxed environment with timeouts and restrictions.
    Now uses a persistent process pool to reduce overhead.
    """
    
    FORBIDDEN_KEYWORDS = [
        "import os", "import sys", "import subprocess", "import shutil",
        "open(", "eval(", "exec(", "os.", "sys.", "subprocess."
    ]
    
    _workers = []
    _max_workers = 3 # Small pool for math tasks
    _initialized = False

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
                        if alias.name not in ["math", "random", "datetime", "sympy", "numpy", "pandas", "scipy", "matplotlib.pyplot", "matplotlib"]:
                            raise SecurityError(f"Importing module '{alias.name}' is not allowed.")
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in ["open", "eval", "exec"]:
                         raise SecurityError(f"Function '{node.func.id}' is forbidden.")
        except SyntaxError as e:
            raise ExecutionError(f"Syntax Error: {e}")

    @classmethod
    def _get_worker(cls) -> Worker:
        """
        Retrieves an available worker from the pool or creates a new one.
        """
        # 1. Try to find an idle worker in the pool
        for w in cls._workers:
            if not w.busy:
                if not w.is_alive():
                    w.restart()
                w.busy = True
                return w
        
        # 2. If pool not full, create new worker
        if len(cls._workers) < cls._max_workers:
            w = Worker()
            w.busy = True
            cls._workers.append(w)
            return w
            
        # 3. If pool full, create a temporary worker (overflow)
        # We don't add it to the pool to avoid growing indefinitely
        logger.warning("Worker pool full, creating temporary worker")
        w = Worker()
        w.busy = True
        return w

    @classmethod
    def execute(cls, code: str, timeout: int = 5) -> str:
        """
        Execute code with timeout protection using persistent workers.
        """
        # 1. Validate
        cls.validate_code(code)
        
        # 2. Get Worker
        worker = cls._get_worker()
        req_id = str(uuid.uuid4())
        is_temp_worker = worker not in cls._workers
        
        try:
            # 3. Submit Task
            worker.input_queue.put((req_id, code))
            
            # 4. Wait for Result
            try:
                # We expect the next result to be ours since worker was marked busy
                res_id, result = worker.output_queue.get(timeout=timeout)
                
                if res_id != req_id:
                     # This implies a sync error, should restart worker
                     raise ExecutionError("Internal Worker Synchronization Error")
                     
                if result["status"] == "error":
                    raise ExecutionError(result["error"])
                    
                return result["output"]
                
            except queue.Empty:
                # Timeout occurred
                logger.warning(f"Worker timed out after {timeout}s. Restarting.")
                worker.restart()
                raise ExecutionError("Execution timed out.")
                
        finally:
            if is_temp_worker:
                # Cleanup temp worker
                if worker.is_alive():
                    worker.process.terminate()
            else:
                # Return to pool
                worker.busy = False

    @classmethod
    def warmup(cls):
        """
        Initialize the worker pool and pre-load libraries to reduce cold start latency.
        Should be called at application startup.
        """
        logger.info("Warming up SafeCodeExecutor workers...")
        if cls._initialized:
             return

        # Initialize workers up to max capacity
        for _ in range(cls._max_workers):
            cls._get_worker().busy = False # Create and mark as free immediately
            
        cls._initialized = True
        logger.info(f"Initialized {len(cls._workers)} workers.")
        
        # Optional: Run a dummy task to force library loading in each worker
        # This is important for heavy libs like pandas/numpy
        dummy_code = "import numpy; import pandas; import sympy; result = 'warm'"
        
        for w in cls._workers:
             w.busy = True
             try:
                 req_id = "warmup"
                 w.input_queue.put((req_id, dummy_code))
                 # Wait for completion (short timeout)
                 w.output_queue.get(timeout=10)
             except Exception as e:
                 logger.warning(f"Worker warmup failed: {e}")
                 w.restart()
             finally:
                 w.busy = False
                 
        logger.info("Worker warmup completed.")

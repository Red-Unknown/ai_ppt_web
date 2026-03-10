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

def _create_safe_globals():
    """Creates a new dictionary with safe globals."""
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

    # Optional: Inject math_kernels if available
    try:
        from backend.app.core.math_optimization import math_kernels
        safe_globals["math_kernels"] = math_kernels
    except ImportError:
        pass
        
    return safe_globals

# Global session store for the worker process
_worker_sessions = {}

def _execute_code_in_isolation(code_str: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Executes Python code in a restricted environment.
    Returns a dictionary with 'status', 'output', or 'error'.
    """
    # 1. Capture stdout
    stdout_capture = io.StringIO()
    
    # 2. Get or create globals
    global _worker_sessions
    
    if session_id:
        if session_id not in _worker_sessions:
            _worker_sessions[session_id] = _create_safe_globals()
        safe_globals = _worker_sessions[session_id]
        # Important: When executing in a session, we must also UPDATE the session with new locals
        # But exec(code, safe_globals) uses safe_globals as both globals and locals, so updates are preserved.
        # The issue might be that we are creating a NEW Worker process for each request?
        # No, workers are persistent.
        # BUT, the global `_worker_sessions` is PER PROCESS.
        # If requests with the same session_id land on DIFFERENT workers, state is lost.
        # We need sticky sessions or a shared state store (redis/plasma).
        # For MVP with persistent workers, we must ensure session affinity or just use 1 worker for tests.
        # SafeCodeExecutor._get_worker() does round robin/random.
        # We need to modify _get_worker to support session affinity or just use 1 worker for now.
    else:
        safe_globals = _create_safe_globals()

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
    Constantly reads (req_id, code, session_id) from input_queue, executes it, and puts (req_id, result) to output_queue.
    """
    while True:
        try:
            item = input_queue.get()
            if item is None: # Sentinel to stop
                break
            
            # Handle backward compatibility or new format
            if len(item) == 3:
                req_id, code, session_id = item
            else:
                req_id, code = item
                session_id = None
                
            result = _execute_code_in_isolation(code, session_id)
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
                        if alias.name not in ["math", "random", "datetime", "sympy", "numpy", "pandas", "scipy", "matplotlib.pyplot", "matplotlib", "math_kernels"]:
                            raise SecurityError(f"Importing module '{alias.name}' is not allowed.")
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in ["open", "eval", "exec"]:
                         raise SecurityError(f"Function '{node.func.id}' is forbidden.")
        except SyntaxError as e:
            raise ExecutionError(f"Syntax Error: {e}")

    _session_worker_map = {} # Map session_id -> worker_index

    @classmethod
    def _get_worker(cls, session_id: Optional[str] = None) -> Worker:
        """
        Retrieves an available worker.
        If session_id is provided, try to return the same worker for affinity.
        """
        if not cls._initialized:
            cls._initialized = True
            
        # Clean up dead workers
        # Be careful if a worker died, session data is lost.
        cls._workers = [w for w in cls._workers if w.is_alive()]
        
        # Ensure minimum pool
        while len(cls._workers) < cls._max_workers:
            w = Worker()
            cls._workers.append(w)
            
        if session_id:
            # Check if we have an assigned worker
            if session_id in cls._session_worker_map:
                idx = cls._session_worker_map[session_id]
                if idx < len(cls._workers) and cls._workers[idx].is_alive():
                    return cls._workers[idx]
            
            # Assign new worker (simple modulo hashing for stability)
            # hash(session_id) might vary between runs, but consistent within run.
            # Or just pick random and store.
            if len(cls._workers) > 0:
                idx = abs(hash(session_id)) % len(cls._workers)
                cls._session_worker_map[session_id] = idx
                return cls._workers[idx]
            
        # Pick least busy (for now just random or round robin)
        if len(cls._workers) > 0:
            for w in cls._workers:
                if not w.busy:
                    return w
            return cls._workers[0]
        
        # Fallback (should not happen due to while loop above)
        w = Worker()
        cls._workers.append(w)
        return w

    @classmethod
    def execute(cls, code: str, timeout: int = 5, session_id: Optional[str] = None) -> str:
        """
        Executes code in a sandbox worker with timeout.
        """
        cls.validate_code(code)
        
        worker = cls._get_worker(session_id)
        worker.busy = True
        
        req_id = str(uuid.uuid4())
        
        try:
            # Send code to worker
            if session_id:
                worker.input_queue.put((req_id, code, session_id))
            else:
                worker.input_queue.put((req_id, code))
            
            # Wait for result
            # We must poll output_queue because it's shared by all requests on this worker?
            # Actually, if we reuse workers, we need to handle multiplexing.
            # But here _get_worker just returns a worker. If multiple threads call execute, they might race on output_queue.
            # For this MVP, we assume simple usage or we should lock the worker.
            
            # Simplified: Wait for specific req_id (could block other requests if using shared queue)
            # A better approach is one queue per request, or a dict of pending requests.
            # Since we are inside a blocking call 'execute', we can just wait.
            # NOTE: If multiple concurrent execute calls share a worker, this 'get' might steal someone else's result.
            # Ideally each worker handles one task at a time or we implement proper correlation.
            # Given _max_workers=3 and low concurrency, we might get away with it, 
            # BUT to be safe, we should loop until we get OUR req_id.
            
            start_time = time.time()
            while True:
                if time.time() - start_time > timeout:
                    worker.restart() # Kill stuck worker
                    raise TimeoutError("Execution timed out.")
                
                try:
                    # Non-blocking get to allow timeout check
                    res_req_id, result = worker.output_queue.get(timeout=0.1)
                    if res_req_id == req_id:
                        if result["status"] == "success":
                            return result["output"]
                        else:
                            raise ExecutionError(result.get("error", "Unknown error"))
                    else:
                        # Put back other's result (Naive handling for concurrency)
                        worker.output_queue.put((res_req_id, result))
                except queue.Empty:
                    continue
                    
        finally:
            worker.busy = False

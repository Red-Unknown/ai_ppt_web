import time
import sys
import os

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from backend.app.utils.sandbox import SafeCodeExecutor

def benchmark():
    code = "result = 2 + 2"
    
    print("--- Run 1 (Cold Start) ---")
    start = time.time()
    res = SafeCodeExecutor.execute(code)
    print(f"Result: {res}, Time: {time.time() - start:.4f}s")
    
    print("\n--- Run 2 (Warm Start) ---")
    start = time.time()
    res = SafeCodeExecutor.execute(code)
    print(f"Result: {res}, Time: {time.time() - start:.4f}s")
    
    print("\n--- Run 3 (Warm Start) ---")
    start = time.time()
    res = SafeCodeExecutor.execute(code)
    print(f"Result: {res}, Time: {time.time() - start:.4f}s")

if __name__ == "__main__":
    benchmark()

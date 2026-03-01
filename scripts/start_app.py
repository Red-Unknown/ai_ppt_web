import os
import sys
import subprocess
import time
import socket
import argparse
import shutil
import re
from pathlib import Path

# Configuration
ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
FRONTEND_DIR = ROOT_DIR / "frontend"
BACKEND_PORT = 8000
FRONTEND_PORT = 5173

def check_port(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_port(port):
    """Attempt to kill process on port (Windows/Linux)."""
    print(f"Port {port} is in use. Attempting to free it...")
    try:
        if sys.platform == "win32":
            # Find PID
            cmd = f"netstat -ano | findstr :{port}"
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        if pid != '0':
                            print(f"Killing process {pid} on port {port}...")
                            subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(f"lsof -ti:{port} | xargs kill -9", shell=True)
            
        # Verify
        time.sleep(1)
        if check_port(port):
            print(f"Warning: Failed to free port {port}. Please manually stop the process.")
        else:
            print(f"Port {port} freed.")
            
    except Exception as e:
        print(f"Error checking/killing port {port}: {e}")

def check_dependencies():
    """Check if python, npm are available and dependencies are installed."""
    print("Checking system dependencies...")
    
    # Check Python
    print(f"Using Python: {sys.executable}")
    if not os.path.exists(sys.executable):
        print("Error: Python executable not found.")
        sys.exit(1)
        
    # Check NPM
    if not shutil.which("npm"):
        print("Error: NPM not found in PATH. Please install Node.js.")
        sys.exit(1)

    print("Checking backend dependencies...")
    # Check Backend Deps (fastapi, uvicorn, redis)
    try:
        subprocess.run(
            [sys.executable, "-c", "import fastapi; import uvicorn; import redis"], 
            check=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError:
        print("Error: Backend dependencies missing (fastapi, uvicorn, or redis).")
        print("Run 'scripts/bootstrap.bat' or 'conda env update -f environment.yml'")
        sys.exit(1)

    print("Checking frontend dependencies...")
    # Check Frontend Deps
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print("Frontend dependencies (node_modules) missing. Installing...")
        try:
            subprocess.run(["npm", "install"], cwd=FRONTEND_DIR, shell=True, check=True)
            print("Frontend dependencies installed.")
        except subprocess.CalledProcessError:
            print("Error: Failed to install frontend dependencies.")
            sys.exit(1)
    else:
        print("Frontend dependencies found.")

def check_api_key():
    """Check if DEEPSEEK_API_KEY is set in environment variables."""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    
    if api_key:
        print("API Key found in environment.")
        return True
    
    print("DEEPSEEK_API_KEY not found in environment variables.")
    try:
        user_input = input("Please enter your DeepSeek API Key (or press Enter to exit): ").strip()
        if user_input:
            os.environ["DEEPSEEK_API_KEY"] = user_input
            print("API Key set for this session.")
            return True
    except (EOFError, KeyboardInterrupt):
        pass

    error_msg = (
        "\nERROR: DEEPSEEK_API_KEY is missing!\n"
        "Please set it using one of the following methods:\n"
        "  Windows (temporary): set DEEPSEEK_API_KEY=your-api-key\n"
        "  Windows (permanent): setx DEEPSEEK_API_KEY your-api-key\n"
        "  Linux/MacOS: export DEEPSEEK_API_KEY=your-api-key\n"
        "\nAfter setting, restart your terminal or run: conda activate ai_ppt_web"
    )
    print(error_msg)
    sys.exit(1)

def start_backend(mode="dev"):
    print(f"Starting Backend (Mode: {mode})...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR)
    
    cmd = [
        sys.executable, "-m", "uvicorn", 
        "backend.main:app", 
        "--host", "0.0.0.0", 
        "--port", str(BACKEND_PORT)
    ]
    if mode == "dev":
        cmd.append("--reload")
    
    # Return process handle
    return subprocess.Popen(cmd, cwd=ROOT_DIR, env=env)

def start_frontend():
    print("Starting Frontend...")
    cmd = ["npm", "run", "dev"]
    # Shell=True needed for npm on Windows
    return subprocess.Popen(cmd, cwd=FRONTEND_DIR, shell=True)

def main():
    parser = argparse.ArgumentParser(description="Start FWWB A12 System")
    parser.add_argument("--mode", choices=["dev", "prod"], default="dev", help="Run mode")
    parser.add_argument("--api-key", help="DeepSeek API Key (overrides environment variable)")
    args = parser.parse_args()

    # 1. Pre-flight Checks
    check_dependencies()
    
    # Set API key from command line if provided
    if args.api_key:
        os.environ["DEEPSEEK_API_KEY"] = args.api_key
        print(f"API Key set from command line argument")
    
    check_api_key()
    
    # 2. Port Management
    if check_port(BACKEND_PORT):
        kill_port(BACKEND_PORT)
    
    if check_port(FRONTEND_PORT):
        kill_port(FRONTEND_PORT)

    # 3. Start Services
    backend_proc = start_backend(args.mode)
    
    # Wait a bit for backend to initialize
    print("Waiting for backend to start...")
    time.sleep(3)
    if backend_proc.poll() is not None:
        print("Backend failed to start.")
        sys.exit(1)
        
    frontend_proc = start_frontend()

    print("\n" + "="*40)
    print(f"System Running in {args.mode.upper()} mode")
    print(f"Backend API: http://localhost:{BACKEND_PORT}")
    print(f"Frontend UI: http://localhost:{FRONTEND_PORT}")
    print("Press Ctrl+C to stop.")
    print("="*40 + "\n")

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("Backend process exited unexpectedly.")
                break
            if frontend_proc.poll() is not None:
                print("Frontend process exited unexpectedly.")
                break
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        # Cleanup
        if backend_proc.poll() is None:
            backend_proc.terminate()
            
        print("Cleaning up frontend processes...")
        if sys.platform == "win32":
            subprocess.run("taskkill /F /IM node.exe", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            if frontend_proc.poll() is None:
                frontend_proc.terminate()
        
        backend_proc.wait()
        print("Services stopped.")

if __name__ == "__main__":
    main()

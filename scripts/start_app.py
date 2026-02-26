import os
import sys
import subprocess
import time
import signal
import socket
import argparse
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
    try:
        if sys.platform == "win32":
            subprocess.run(f"netstat -ano | findstr :{port}", shell=True)
            # This is complex to automate safely without admin, so we just warn
            print(f"Warning: Port {port} seems to be in use. Please free it manually.")
        else:
            subprocess.run(f"lsof -ti:{port} | xargs kill -9", shell=True)
    except Exception as e:
        print(f"Error checking port {port}: {e}")

def check_dependencies():
    """Check if python, npm are available."""
    print("Checking dependencies...")
    try:
        subprocess.run(["python", "--version"], check=True, stdout=subprocess.PIPE)
        subprocess.run(["npm", "--version"], check=True, shell=True, stdout=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: Python or NPM not found. Please install them.")
        sys.exit(1)
    
    # Check Backend Deps (simplified)
    # In a real scenario, we might check if 'fastapi' is importable
    try:
        subprocess.run(["python", "-c", "import fastapi; import uvicorn"], check=True, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError:
        print("Error: Backend dependencies missing. Run 'pip install -r requirements.txt'")
        sys.exit(1)

def start_backend(mode="dev"):
    print(f"Starting Backend (Mode: {mode})...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR)
    
    cmd = [
        "python", "-m", "uvicorn", 
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
    args = parser.parse_args()

    # 1. Pre-flight Checks
    check_dependencies()
    
    if check_port(BACKEND_PORT):
        print(f"Port {BACKEND_PORT} is in use.")
        kill_port(BACKEND_PORT)
    
    if check_port(FRONTEND_PORT):
        print(f"Port {FRONTEND_PORT} is in use.")
        kill_port(FRONTEND_PORT)

    # 2. Start Services
    backend_proc = start_backend(args.mode)
    
    # Wait a bit for backend to initialize
    time.sleep(2)
    if backend_proc.poll() is not None:
        print("Backend failed to start.")
        sys.exit(1)
        
    frontend_proc = start_frontend()

    print("\n" + "="*30)
    print(f"System Running in {args.mode.upper()} mode")
    print(f"Backend: http://localhost:{BACKEND_PORT}")
    print(f"Frontend: http://localhost:{FRONTEND_PORT}")
    print("Press Ctrl+C to stop.")
    print("="*30 + "\n")

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("Backend process exited unexpected.")
                break
            if frontend_proc.poll() is not None:
                print("Frontend process exited unexpected.")
                break
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        # Cleanup
        backend_proc.terminate()
        # Frontend on Windows with shell=True is tricky to kill via Popen object
        # We might need taskkill if simple terminate doesn't work
        if sys.platform == "win32":
            subprocess.run("taskkill /F /IM node.exe", shell=True, stderr=subprocess.PIPE)
        else:
            frontend_proc.terminate()
        
        backend_proc.wait()
        print("Services stopped.")

if __name__ == "__main__":
    main()

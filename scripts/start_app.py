import os
import sys
import subprocess
import time
import socket
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
BACKEND_PORT = 8001

CONDA_ENV_NAME = "ai_ppt_web"

def get_conda_python():
    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix and CONDA_ENV_NAME in conda_prefix:
        return sys.executable
    user_profile = os.environ.get("USERPROFILE", os.environ.get("HOME", ""))
    conda_env_path = Path(user_profile) / ".conda" / "envs" / CONDA_ENV_NAME / "python.exe"
    if conda_env_path.exists():
        return str(conda_env_path)
    return sys.executable

PYTHON_EXE = get_conda_python()

SILENT = False

def log(msg):
    if not SILENT:
        print(msg)

def check_port(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_port(port):
    log(f"Port {port} is in use. Attempting to free it...")
    try:
        if sys.platform == "win32":
            cmd = f"netstat -ano | findstr :{port}"
            result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) > 4:
                        pid = parts[-1]
                        if pid != '0':
                            log(f"Killing process {pid} on port {port}...")
                            subprocess.run(f"taskkill /F /PID {pid}", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(f"lsof -ti:{port} | xargs kill -9", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(1)
        if check_port(port):
            log(f"Warning: Failed to free port {port}. Please manually stop the process.")
        else:
            log(f"Port {port} freed.")
            
    except Exception as e:
        log(f"Error checking/killing port {port}: {e}")

def check_dependencies():
    log("Checking system dependencies...")
    
    log(f"Using Python: {PYTHON_EXE}")
    if not os.path.exists(PYTHON_EXE):
        if not SILENT:
            print(f"Error: Python executable not found: {PYTHON_EXE}")
        sys.exit(1)

    log("Checking backend dependencies...")
    try:
        subprocess.run(
            [PYTHON_EXE, "-c", "import fastapi; import uvicorn; import redis"], 
            check=True, 
            stdout=subprocess.DEVNULL if SILENT else subprocess.PIPE, 
            stderr=subprocess.DEVNULL if SILENT else subprocess.PIPE
        )
    except subprocess.CalledProcessError:
        if not SILENT:
            print("Error: Backend dependencies missing (fastapi, uvicorn, or redis).")
        sys.exit(1)
    
    log("Backend dependencies OK.")

def start_backend():
    log(f"Starting Backend on port {BACKEND_PORT}...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT_DIR)
    env["PYTHONWARNINGS"] = "ignore"
    
    cmd = [
        PYTHON_EXE,
        "-c",
        f"import uvicorn; uvicorn.run('backend.main:app', host='0.0.0.0', port={BACKEND_PORT})"
    ]
    
    if SILENT:
        stdout_dest = subprocess.DEVNULL
        stderr_dest = subprocess.DEVNULL
    else:
        stdout_dest = None
        stderr_dest = None
    
    return subprocess.Popen(cmd, cwd=ROOT_DIR, env=env, stdout=stdout_dest, stderr=stderr_dest)

def wait_for_port_available(port, timeout=60):
    log(f"Waiting for port {port} to become available...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        if not check_port(port):
            time.sleep(2)
            if not check_port(port):
                log(f"Port {port} is now available.")
                return True
        time.sleep(2)
    log(f"Timeout waiting for port {port} to become available.")
    return False

def ensure_port_free(port):
    if check_port(port):
        log(f"Port {port} is occupied. Terminating existing process...")
        kill_port(port)
        wait_for_port_available(port)

def monitor_and_restart():
    global SILENT
    
    check_dependencies()
    
    ensure_port_free(BACKEND_PORT)
    
    log(f"Starting Backend service on port {BACKEND_PORT}...")
    
    backend_proc = None
    restart_count = 0
    max_restarts = 10
    
    try:
        while True:
            if backend_proc is None or backend_proc.poll() is not None:
                if backend_proc and backend_proc.poll() is not None:
                    exit_code = backend_proc.poll()
                    log(f"Backend process exited with code {exit_code}")
                    if exit_code != 0:
                        ensure_port_free(BACKEND_PORT)
                
                if restart_count >= max_restarts:
                    log(f"Max restart count ({max_restarts}) reached. Exiting.")
                    break
                
                restart_count += 1
                log(f"Starting backend (attempt {restart_count})...")
                backend_proc = start_backend()
                
                time.sleep(3)
                if backend_proc.poll() is not None:
                    log("Backend failed to start. Waiting before retry...")
                    time.sleep(5)
                    continue
                
                log(f"Backend started successfully on port {BACKEND_PORT}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        log("\nStopping services...")
    finally:
        if backend_proc and backend_proc.poll() is None:
            backend_proc.terminate()
            backend_proc.wait()
        log("Service stopped.")

def main():
    global SILENT
    parser = argparse.ArgumentParser(description="Start Backend Service")
    parser.add_argument("--silent", action="store_true", help="Run in silent mode (no console output)")
    args = parser.parse_args()

    if args.silent:
        SILENT = True

    if not SILENT:
        print("\n" + "="*40)
        print(f"Backend Service Running")
        print(f"Backend API: http://localhost:{BACKEND_PORT}")
        print("Press Ctrl+C to stop.")
        print("="*40 + "\n")

    monitor_and_restart()

if __name__ == "__main__":
    main()

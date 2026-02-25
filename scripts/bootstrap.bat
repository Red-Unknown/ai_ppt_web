@echo off
setlocal

echo [INFO] Starting Environment Bootstrap...

REM Check if Conda is installed
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Conda is not installed or not in PATH.
    exit /b 1
)

REM Check environment.yml
if not exist environment.yml (
    echo [ERROR] environment.yml not found!
    exit /b 1
)

REM Create or Update Environment
echo [INFO] Creating/Updating Conda environment 'ai_ppt_web'...
call conda env update -f environment.yml --prune
if %errorlevel% neq 0 (
    echo [ERROR] Failed to update environment.
    exit /b 1
)

echo [INFO] Environment bootstrap completed successfully.
echo [INFO] Activate with: conda activate ai_ppt_web
endlocal

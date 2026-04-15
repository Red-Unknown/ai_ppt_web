$env:KMP_DUPLICATE_LIB_OK = "TRUE"
$env:PYTHONUNBUFFERED = "1"

$env:EMBEDDING_HOST = if ($env:EMBEDDING_HOST) { $env:EMBEDDING_HOST } else { "0.0.0.0" }
$env:EMBEDDING_PORT = if ($env:EMBEDDING_PORT) { $env:EMBEDDING_PORT } else { "8000" }
$env:EMBEDDING_MODEL_NAME = if ($env:EMBEDDING_MODEL_NAME) { $env:EMBEDDING_MODEL_NAME } else { "BAAI/bge-m3" }
$env:EMBEDDING_DEVICE = if ($env:EMBEDDING_DEVICE) { $env:EMBEDDING_DEVICE } else { "cuda" }
$env:EMBEDDING_USE_FP16 = if ($env:EMBEDDING_USE_FP16) { $env:EMBEDDING_USE_FP16 } else { "true" }
$env:EMBEDDING_MAX_BATCH_SIZE = if ($env:EMBEDDING_MAX_BATCH_SIZE) { $env:EMBEDDING_MAX_BATCH_SIZE } else { "32" }
$env:EMBEDDING_BATCH_TIMEOUT = if ($env:EMBEDDING_BATCH_TIMEOUT) { $env:EMBEDDING_BATCH_TIMEOUT } else { "0.05" }
$env:EMBEDDING_MAX_LENGTH = if ($env:EMBEDDING_MAX_LENGTH) { $env:EMBEDDING_MAX_LENGTH } else { "8192" }
$env:EMBEDDING_LOG_LEVEL = if ($env:EMBEDDING_LOG_LEVEL) { $env:EMBEDDING_LOG_LEVEL } else { "INFO" }

$PORT = $env:EMBEDDING_PORT

function Get-PortProcess {
    param([int]$Port)
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    if ($connections) {
        $pids = $connections | Select-Object -ExpandProperty OwningProcess -Unique
        return $pids
    }
    return $null
}

function Stop-PortProcess {
    param([int]$Port)
    $pids = Get-PortProcess -Port $Port
    if ($pids) {
        foreach ($pid in $pids) {
            try {
                $process = Get-Process -Id $pid -ErrorAction Stop
                Write-Host "Stopping existing process (PID: $pid) on port $Port..." -ForegroundColor Yellow
                Stop-Process -Id $pid -Force -ErrorAction Stop
                Write-Host "Process stopped." -ForegroundColor Green
            } catch {
                Write-Host "Failed to stop process: $_" -ForegroundColor Red
            }
        }
        Start-Sleep -Milliseconds 500
    }
}

Write-Host "Starting Embedding Service with GPU acceleration..." -ForegroundColor Green
Write-Host "Host: $env:EMBEDDING_HOST"
Write-Host "Port: $PORT"
Write-Host "Model: $env:EMBEDDING_MODEL_NAME"
Write-Host "Device: $env:EMBEDDING_DEVICE"
Write-Host "FP16: $env:EMBEDDING_USE_FP16"

Stop-PortProcess -Port $PORT

conda run -n ai_ppt_web --no-capture-output python -m uvicorn main:app --host $env:EMBEDDING_HOST --port $PORT --log-level $env:EMBEDDING_LOG_LEVEL.ToLower()

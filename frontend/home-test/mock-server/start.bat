@echo off
chcp 65001 >nul
title PPT Parser Mock Server

echo ╔══════════════════════════════════════════════════════════════╗
echo ║          PPT Parser Mock Server 启动脚本                     ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

REM 检查是否安装了依赖
if not exist "node_modules" (
    echo [INFO] 首次运行，正在安装依赖...
    call npm install
    if errorlevel 1 (
        echo [ERROR] 依赖安装失败，请检查npm配置
        pause
        exit /b 1
    )
    echo [INFO] 依赖安装完成
    echo.
)

echo [INFO] 正在启动 Mock Server...
echo [INFO] 服务地址: ws://127.0.0.1:8001/api/v1/ws/script
echo [INFO] 测试页面: http://127.0.0.1:8001/test/
echo.
echo 按 Ctrl+C 停止服务
echo.

npm start

pause

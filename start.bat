@echo off
chcp 65001 >nul
title B站视频播放器

echo.
echo ╔═══════════════════════════════════════════════════════════╗
echo ║                                                           ║
echo ║     🎬 B站视频播放器 - 启动中...                          ║
echo ║                                                           ║
echo ╚═══════════════════════════════════════════════════════════╝
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

:: 检查依赖
echo [1/2] 检查依赖...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [安装] 正在安装依赖...
    pip install -r requirements.txt
)

:: 启动服务器
echo [2/2] 启动服务器...
echo.
echo ════════════════════════════════════════════════════════════
echo   服务已启动，请访问: http://localhost:5000
echo   按 Ctrl+C 停止服务器
echo ════════════════════════════════════════════════════════════
echo.

python server.py
pause


@echo off
setlocal

echo ========================================================
echo   DarkChuang Development Environment Launcher
echo ========================================================

:: 设置 Hugging Face 镜像，解决国内下载模型连接问题
set HF_ENDPOINT=https://hf-mirror.com

:: 检查虚拟环境是否存在
if exist "venv\Scripts\activate.bat" (
    set "VENV_ACTIVATE=venv\Scripts\activate.bat"
) else (
    echo [ERROR] Virtual environment not found in .\venv
    echo Please run setup first or ensure venv is created in the root directory.
    pause
    exit /b 1
)

echo.
echo [1/2] Starting Backend Server (FastAPI)...
:: 打开新窗口启动后端
start "DarkChuang Backend" cmd /k "call %VENV_ACTIVATE% && cd backend && python -m uvicorn app.main:app --reload"

echo.
echo [2/2] Starting Frontend Server (Vite)...
:: 打开新窗口启动前端
start "DarkChuang Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================================
echo   Services are starting in separate windows.
echo   - Backend API: http://localhost:8000/docs
echo   - Frontend UI: http://localhost:5173 (or check console)
echo ========================================================
echo.

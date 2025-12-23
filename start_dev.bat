@echo off
setlocal EnableDelayedExpansion

title DarkChuang Launcher

echo ========================================================
echo   DarkChuang Intelligent Chemistry Assistant
echo   One-Click Launcher (v2.3)
echo ========================================================
echo.

:: ----------------------------------------------------------
:: 1. 环境自检 (Prerequisites Check)
:: ----------------------------------------------------------
echo [*] Step 1/4: Checking prerequisites...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
) else (
    for /f "delims=" %%i in ('python --version') do echo     - Found %%i
)

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo Please install Node.js LTS from https://nodejs.org/
    pause
    exit /b 1
) else (
    for /f "delims=" %%i in ('node --version') do echo     - Found Node.js %%i
)

:: ----------------------------------------------------------
:: 2. 后端环境配置 (Backend Setup)
:: ----------------------------------------------------------
echo.
echo [*] Step 2/4: Setting up Backend environment...

:: 检查/创建虚拟环境
if not exist "venv" (
    echo     - Creating virtual environment venv...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: 激活虚拟环境
call venv\Scripts\activate.bat

:: 检查 .env 文件
if not exist "backend\.env" (
    if exist "backend\.env.example" (
        echo     - Creating .env from example...
        copy "backend\.env.example" "backend\.env" >nul
        echo.
        echo [IMPORTANT] A new .env file was created in 'backend/'.
        echo             Please edit it to add your SILICONFLOW_API_KEY before using AI features.
        echo.
        pause
    ) else (
        echo [WARN] backend\.env.example not found. Skipping .env creation.
    )
)

:: 安装依赖 (使用清华源加速)
echo     - Checking/Installing backend dependencies...
echo       (Using Tsinghua PyPI mirror for speed)
pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN] Fast installation failed, retrying with verbose output...
    pip install -r backend/requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install backend dependencies.
        pause
        exit /b 1
    )
)
echo     - Backend dependencies are ready.

:: ----------------------------------------------------------
:: 3. 前端环境配置 (Frontend Setup)
:: ----------------------------------------------------------
echo.
echo [*] Step 3/4: Setting up Frontend environment...

cd frontend
if not exist "node_modules" (
    echo     - Installing frontend dependencies...
    echo       This may take a few minutes for the first time...
    call npm install --registry=https://registry.npmmirror.com
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install frontend dependencies.
        cd ..
        pause
        exit /b 1
    )
) else (
    echo     - Frontend dependencies found.
)
cd ..

:: ----------------------------------------------------------
:: 4. 启动服务 (Start Services)
:: ----------------------------------------------------------
echo.
echo [*] Step 4/4: Starting services...

:: 设置环境变量
set HF_ENDPOINT=https://hf-mirror.com

:: 启动后端 (新窗口)
start "DarkChuang Backend" cmd /k "call venv\Scripts\activate.bat && cd backend && echo Starting FastAPI... && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

:: 启动前端 (新窗口)
start "DarkChuang Frontend" cmd /k "cd frontend && echo Starting Vite... && npm run dev"

echo.
echo ========================================================
echo   DarkChuang is running!
echo.
echo   [Backend API]  http://localhost:8000/docs
echo   [Frontend UI]  http://localhost:5173
echo.
echo   * Services are running in separate windows.
echo   * Close those windows to stop the application.
echo ========================================================
echo.
pause

#!/bin/bash

echo "========================================================"
echo "  DarkChuang Intelligent Chemistry Assistant"
echo "  One-Click Launcher (macOS/Linux)"
echo "========================================================"
echo ""

# 1. Prerequisites Check
echo "[*] Step 1/4: Checking prerequisites..."

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed."
    echo "        Please install Python 3.10+ (brew install python3)"
    exit 1
else
    echo "    - Found $(python3 --version)"
fi

if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed."
    echo "        Please install Node.js (brew install node)"
    exit 1
else
    echo "    - Found $(node --version)"
fi

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 2. Backend Setup
echo ""
echo "[*] Step 2/4: Setting up Backend environment..."

cd "$PROJECT_ROOT/backend" || exit

# Check/Create venv
# Check specifically for the activation script to ensure it's a valid POSIX venv
if [ ! -f "venv/bin/activate" ]; then
    if [ -d "venv" ]; then
        echo "    [WARN] 'venv' folder exists but is not compatible (possibly created on Windows)."
        echo "           Recreating virtual environment..."
        rm -rf venv
    else
        echo "    - Creating virtual environment (venv)..."
    fi
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Check .env
if [ ! -f ".env" ]; then
    if [ -f "../.env.example" ]; then
        echo "    - Creating .env from project root example..."
        cp ../.env.example .env
        echo ""
        echo "    [IMPORTANT] A new .env file was created in 'backend/'."
        echo "                Please edit it to add your SILICONFLOW_API_KEY."
        echo "                Press any key to continue..."
        read -n 1 -s -r
    elif [ -f ".env.example" ]; then
        echo "    - Creating .env from example..."
        cp .env.example .env
        echo ""
        echo "    [IMPORTANT] A new .env file was created in 'backend/'."
        echo "                Please edit it to add your SILICONFLOW_API_KEY."
        echo "                Press any key to continue..."
        read -n 1 -s -r
    fi
fi

# Install dependencies
echo "    - Checking/Installing backend dependencies..."
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo "    - Backend dependencies are ready."

# 3. Frontend Setup
echo ""
echo "[*] Step 3/4: Setting up Frontend environment..."

cd "$PROJECT_ROOT/frontend" || exit

if [ ! -d "node_modules" ]; then
    echo "    - Installing frontend dependencies..."
    npm install --registry=https://registry.npmmirror.com
else
    echo "    - Frontend dependencies found."
fi

# 4. Start Services
echo ""
echo "[*] Step 4/4: Starting services..."

export HF_ENDPOINT=https://hf-mirror.com

# Detect OS for launching terminals
OS="$(uname)"

if [ "$OS" == "Darwin" ]; then
    # macOS
    echo "    - Launching Backend in new Terminal window..."
    osascript -e "tell application \"Terminal\" to do script \"cd \\\"$PROJECT_ROOT/backend\\\" && source venv/bin/activate && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000\""
    
    echo "    - Launching Frontend in new Terminal window..."
    osascript -e "tell application \"Terminal\" to do script \"cd \\\"$PROJECT_ROOT/frontend\\\" && npm run dev\""

elif [ "$OS" == "Linux" ]; then
    # Linux (Try common terminal emulators)
    if command -v gnome-terminal &> /dev/null; then
        gnome-terminal -- bash -c "cd \"$PROJECT_ROOT/backend\" && source venv/bin/activate && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; exec bash"
        gnome-terminal -- bash -c "cd \"$PROJECT_ROOT/frontend\" && npm run dev; exec bash"
    elif command -v x-terminal-emulator &> /dev/null; then
        x-terminal-emulator -e bash -c "cd \"$PROJECT_ROOT/backend\" && source venv/bin/activate && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000; exec bash"
        x-terminal-emulator -e bash -c "cd \"$PROJECT_ROOT/frontend\" && npm run dev; exec bash"
    else
        echo "[WARN] Could not detect a supported terminal emulator (gnome-terminal, x-terminal-emulator)."
        echo "       Starting services in background..."
        cd "$PROJECT_ROOT/backend" && source venv/bin/activate && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
        cd "$PROJECT_ROOT/frontend" && npm run dev &
    fi
else
    echo "[ERROR] Unsupported OS: $OS"
    exit 1
fi

echo ""
echo "========================================================"
echo "  DarkChuang is running!"
echo ""
echo "  [Backend API]  http://localhost:8000/docs"
echo "  [Frontend UI]  http://localhost:5173"
echo ""
echo "  * Services are running in separate windows."
echo "========================================================"

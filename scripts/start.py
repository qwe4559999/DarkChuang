#!/usr/bin/env python3
"""
化学问答机器人启动脚本

这个脚本用于启动整个应用程序，包括后端API服务和前端开发服务器。
支持开发模式和生产模式。
"""

import os
import sys
import subprocess
import argparse
import time
import signal
import threading
from pathlib import Path
from typing import List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

class ProcessManager:
    """进程管理器"""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.running = True
        
    def add_process(self, process: subprocess.Popen) -> None:
        """添加进程到管理器"""
        self.processes.append(process)
        
    def terminate_all(self) -> None:
        """终止所有进程"""
        self.running = False
        print("\n正在停止所有服务...")
        
        for process in self.processes:
            if process.poll() is None:  # 进程仍在运行
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception as e:
                    print(f"停止进程时出错: {e}")
                    
        print("所有服务已停止")
        
    def wait_for_processes(self) -> None:
        """等待所有进程结束"""
        try:
            while self.running and any(p.poll() is None for p in self.processes):
                time.sleep(1)
        except KeyboardInterrupt:
            self.terminate_all()

def check_dependencies() -> bool:
    """检查依赖是否安装"""
    print("检查依赖...")
    
    # 检查Python依赖
    backend_requirements = project_root / "backend" / "requirements.txt"
    if backend_requirements.exists():
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "check"],
                capture_output=True,
                text=True,
                cwd=project_root / "backend"
            )
            if result.returncode != 0:
                print("Python依赖检查失败，请运行: pip install -r backend/requirements.txt")
                return False
        except Exception as e:
            print(f"检查Python依赖时出错: {e}")
            return False
    
    # 检查Node.js依赖
    frontend_package_json = project_root / "frontend" / "package.json"
    if frontend_package_json.exists():
        node_modules = project_root / "frontend" / "node_modules"
        if not node_modules.exists():
            print("Node.js依赖未安装，请运行: cd frontend && npm install")
            return False
    
    print("依赖检查通过")
    return True

def setup_environment() -> None:
    """设置环境变量"""
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        print("创建环境配置文件...")
        import shutil
        shutil.copy(env_example, env_file)
        print("请编辑 .env 文件配置您的环境变量")
    
    # 加载环境变量
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

def create_directories() -> None:
    """创建必要的目录"""
    directories = [
        project_root / "data",
        project_root / "data" / "chemistry_books",
        project_root / "data" / "papers",
        project_root / "data" / "images",
        project_root / "backend" / "logs",
        project_root / "backend" / "uploads",
        project_root / "models" / "image_recognition",
        project_root / "models" / "embeddings",
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

def start_backend(dev_mode: bool = True) -> subprocess.Popen:
    """启动后端服务"""
    print("启动后端服务...")
    
    backend_dir = project_root / "backend"
    
    if dev_mode:
        # 开发模式：使用uvicorn的热重载
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--reload",
            "--reload-dir", "app"
        ]
    else:
        # 生产模式
        cmd = [
            sys.executable, "-m", "uvicorn",
            "app.main:app",
            "--host", "0.0.0.0",
            "--port", "8000",
            "--workers", "4"
        ]
    
    env = os.environ.copy()
    env["PYTHONPATH"] = str(backend_dir)
    
    process = subprocess.Popen(
        cmd,
        cwd=backend_dir,
        env=env
    )
    
    return process

def start_frontend(dev_mode: bool = True) -> Optional[subprocess.Popen]:
    """启动前端服务"""
    frontend_dir = project_root / "frontend"
    
    if not frontend_dir.exists():
        print("前端目录不存在，跳过前端启动")
        return None
    
    if dev_mode:
        print("启动前端开发服务器...")
        npm_cmd = "npm.cmd" if os.name == 'nt' else "npm"
        cmd = [npm_cmd, "run", "dev"]
    else:
        print("构建前端生产版本...")
        npm_cmd = "npm.cmd" if os.name == 'nt' else "npm"
        # 先构建
        build_process = subprocess.run(
            [npm_cmd, "run", "build"],
            cwd=frontend_dir
        )
        if build_process.returncode != 0:
            print("前端构建失败")
            return None
        
        # 使用serve启动
        cmd = ["npx", "serve", "-s", "build", "-l", "3000"]
    
    try:
        process = subprocess.Popen(
            cmd,
            cwd=frontend_dir
        )
        return process
    except FileNotFoundError:
        print("npm未找到，请确保Node.js已安装")
        return None

def wait_for_service(url: str, timeout: int = 60) -> bool:
    """等待服务启动"""
    import requests
    import time
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(2)
    
    return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="化学问答机器人启动脚本")
    parser.add_argument(
        "--mode",
        choices=["dev", "prod"],
        default="dev",
        help="运行模式 (dev: 开发模式, prod: 生产模式)"
    )
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="仅启动后端服务"
    )
    parser.add_argument(
        "--frontend-only",
        action="store_true",
        help="仅启动前端服务"
    )
    parser.add_argument(
        "--skip-deps-check",
        action="store_true",
        help="跳过依赖检查"
    )
    
    args = parser.parse_args()
    
    print(f"启动化学问答机器人 ({args.mode}模式)")
    print("=" * 50)
    
    # 检查依赖
    if not args.skip_deps_check and not check_dependencies():
        sys.exit(1)
    
    # 设置环境
    setup_environment()
    create_directories()
    
    # 创建进程管理器
    pm = ProcessManager()
    
    # 设置信号处理
    def signal_handler(signum, frame):
        pm.terminate_all()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    dev_mode = args.mode == "dev"
    
    try:
        # 启动后端
        if not args.frontend_only:
            backend_process = start_backend(dev_mode)
            pm.add_process(backend_process)
            
            # 等待后端启动
            if wait_for_service("http://localhost:8000/api/v1/health"):
                print("✅ 后端服务启动成功")
            else:
                print("❌ 后端服务启动失败")
        
        # 启动前端
        if not args.backend_only:
            frontend_process = start_frontend(dev_mode)
            if frontend_process:
                pm.add_process(frontend_process)
                5173"):
                    print("✅ 前端服务启动成功")
                elif not dev_mode:
                    print("✅ 前端构建完成")
        
        print("\n" + "=" * 50)
        print("🚀 服务启动完成!")
        if not args.frontend_only:
            print("📡 后端API: http://localhost:8000")
            print("📋 API文档: http://localhost:8000/docs")
        if not args.backend_only and dev_mode:
            print("🌐 前端界面: http://localhost:51730/docs")
        if not args.backend_only and dev_mode:
            print("🌐 前端界面: http://localhost:3000")
        print("\n按 Ctrl+C 停止服务")
        print("=" * 50)
        
        # 等待进程
        pm.wait_for_processes()
        
    except Exception as e:
        print(f"启动失败: {e}")
        pm.terminate_all()
        sys.exit(1)

if __name__ == "__main__":
    main()
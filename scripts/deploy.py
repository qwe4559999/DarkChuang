#!/usr/bin/env python3
"""
化学问答机器人部署脚本

这个脚本用于部署应用到不同的环境（开发、测试、生产）。
"""

import os
import sys
import subprocess
import shutil
import time
import yaml
from pathlib import Path
from typing import List, Optional, Dict, Any
import argparse

# 项目根目录
project_root = Path(__file__).parent.parent

class Colors:
    """终端颜色"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_step(message: str) -> None:
    """打印步骤信息"""
    print(f"{Colors.BLUE}[INFO]{Colors.ENDC} {message}")

def print_success(message: str) -> None:
    """打印成功信息"""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.ENDC} {message}")

def print_warning(message: str) -> None:
    """打印警告信息"""
    print(f"{Colors.YELLOW}[WARNING]{Colors.ENDC} {message}")

def print_error(message: str) -> None:
    """打印错误信息"""
    print(f"{Colors.RED}[ERROR]{Colors.ENDC} {message}")

def run_command(cmd: List[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    """运行命令"""
    print_step(f"运行命令: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd or project_root,
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"命令执行失败: {e}")
        if e.stderr:
            print(e.stderr)
        if check:
            raise
        return e

class Deployer:
    """部署器"""
    
    def __init__(self, environment: str = "development"):
        self.environment = environment
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """加载部署配置"""
        config_file = project_root / "deploy" / f"{self.environment}.yml"
        
        if not config_file.exists():
            # 创建默认配置
            return self.create_default_config()
        
        with open(config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def create_default_config(self) -> Dict[str, Any]:
        """创建默认配置"""
        configs = {
            "development": {
                "docker": {
                    "compose_file": "docker-compose.yml",
                    "build": True,
                    "services": ["backend", "frontend", "redis"]
                },
                "environment_vars": {
                    "ENVIRONMENT": "development",
                    "DEBUG": "true",
                    "LOG_LEVEL": "debug"
                },
                "health_check": {
                    "backend_url": "http://localhost:8000/health",
                    "frontend_url": "http://localhost:3000",
                    "timeout": 60
                }
            },
            "production": {
                "docker": {
                    "compose_file": "docker-compose.prod.yml",
                    "build": True,
                    "services": ["backend", "frontend", "redis", "nginx"]
                },
                "environment_vars": {
                    "ENVIRONMENT": "production",
                    "DEBUG": "false",
                    "LOG_LEVEL": "info"
                },
                "health_check": {
                    "backend_url": "http://localhost:8000/health",
                    "frontend_url": "http://localhost:80",
                    "timeout": 120
                },
                "backup": {
                    "enabled": True,
                    "data_dirs": ["data", "backend/logs"]
                }
            }
        }
        
        # 创建配置目录
        deploy_dir = project_root / "deploy"
        deploy_dir.mkdir(exist_ok=True)
        
        # 保存配置文件
        for env, config in configs.items():
            config_file = deploy_dir / f"{env}.yml"
            with open(config_file, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
        
        return configs.get(self.environment, configs["development"])
    
    def check_prerequisites(self) -> bool:
        """检查部署前提条件"""
        print_step("检查部署前提条件...")
        
        # 检查Docker
        try:
            result = run_command(["docker", "--version"], check=False)
            if result.returncode != 0:
                print_error("Docker未安装或不可用")
                return False
            print("  ✓ Docker可用")
        except FileNotFoundError:
            print_error("Docker未找到")
            return False
        
        # 检查Docker Compose
        try:
            result = run_command(["docker-compose", "--version"], check=False)
            if result.returncode != 0:
                # 尝试新版本命令
                result = run_command(["docker", "compose", "version"], check=False)
                if result.returncode != 0:
                    print_error("Docker Compose未安装或不可用")
                    return False
            print("  ✓ Docker Compose可用")
        except FileNotFoundError:
            print_error("Docker Compose未找到")
            return False
        
        # 检查环境文件
        env_file = project_root / ".env"
        if not env_file.exists():
            print_warning("未找到.env文件，将使用默认配置")
        else:
            print("  ✓ 环境配置文件存在")
        
        # 检查必要文件
        required_files = [
            "docker-compose.yml",
            "backend/Dockerfile",
            "frontend/Dockerfile"
        ]
        
        for file_path in required_files:
            if not (project_root / file_path).exists():
                print_error(f"缺少必要文件: {file_path}")
                return False
        
        print("  ✓ 必要文件检查通过")
        print_success("前提条件检查通过")
        return True
    
    def backup_data(self) -> bool:
        """备份数据"""
        if not self.config.get("backup", {}).get("enabled", False):
            return True
        
        print_step("备份数据...")
        
        backup_dir = project_root / "backups" / f"{self.environment}_{int(time.time())}"
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        data_dirs = self.config["backup"]["data_dirs"]
        
        for data_dir in data_dirs:
            source_dir = project_root / data_dir
            if source_dir.exists():
                dest_dir = backup_dir / data_dir
                shutil.copytree(source_dir, dest_dir)
                print(f"  ✓ 备份 {data_dir}")
            else:
                print_warning(f"数据目录不存在: {data_dir}")
        
        print_success(f"数据备份完成: {backup_dir}")
        return True
    
    def build_images(self) -> bool:
        """构建Docker镜像"""
        if not self.config["docker"]["build"]:
            print_step("跳过镜像构建")
            return True
        
        print_step("构建Docker镜像...")
        
        compose_file = self.config["docker"]["compose_file"]
        
        try:
            # 构建镜像
            run_command([
                "docker-compose", "-f", compose_file, "build", "--no-cache"
            ])
            
            print_success("Docker镜像构建完成")
            return True
            
        except subprocess.CalledProcessError:
            print_error("Docker镜像构建失败")
            return False
    
    def deploy_services(self) -> bool:
        """部署服务"""
        print_step("部署服务...")
        
        compose_file = self.config["docker"]["compose_file"]
        services = self.config["docker"]["services"]
        
        try:
            # 停止现有服务
            print_step("停止现有服务...")
            run_command([
                "docker-compose", "-f", compose_file, "down"
            ], check=False)
            
            # 启动服务
            print_step("启动服务...")
            cmd = ["docker-compose", "-f", compose_file, "up", "-d"]
            if services:
                cmd.extend(services)
            
            run_command(cmd)
            
            print_success("服务部署完成")
            return True
            
        except subprocess.CalledProcessError:
            print_error("服务部署失败")
            return False
    
    def health_check(self) -> bool:
        """健康检查"""
        print_step("执行健康检查...")
        
        health_config = self.config.get("health_check", {})
        backend_url = health_config.get("backend_url")
        frontend_url = health_config.get("frontend_url")
        timeout = health_config.get("timeout", 60)
        
        import requests
        
        # 等待服务启动
        print_step(f"等待服务启动（最多{timeout}秒）...")
        
        start_time = time.time()
        backend_ok = False
        frontend_ok = False
        
        while time.time() - start_time < timeout:
            # 检查后端
            if backend_url and not backend_ok:
                try:
                    response = requests.get(backend_url, timeout=5)
                    if response.status_code == 200:
                        print("  ✓ 后端服务健康")
                        backend_ok = True
                except requests.RequestException:
                    pass
            
            # 检查前端
            if frontend_url and not frontend_ok:
                try:
                    response = requests.get(frontend_url, timeout=5)
                    if response.status_code == 200:
                        print("  ✓ 前端服务健康")
                        frontend_ok = True
                except requests.RequestException:
                    pass
            
            # 如果都检查通过，退出循环
            if (not backend_url or backend_ok) and (not frontend_url or frontend_ok):
                break
            
            time.sleep(2)
        
        # 检查结果
        success = True
        if backend_url and not backend_ok:
            print_error("后端服务健康检查失败")
            success = False
        
        if frontend_url and not frontend_ok:
            print_error("前端服务健康检查失败")
            success = False
        
        if success:
            print_success("健康检查通过")
        
        return success
    
    def show_status(self) -> None:
        """显示部署状态"""
        print_step("获取部署状态...")
        
        compose_file = self.config["docker"]["compose_file"]
        
        try:
            # 显示服务状态
            result = run_command([
                "docker-compose", "-f", compose_file, "ps"
            ], check=False)
            
            # 显示日志
            print_step("最近的日志:")
            run_command([
                "docker-compose", "-f", compose_file, "logs", "--tail=20"
            ], check=False)
            
        except Exception as e:
            print_error(f"获取状态失败: {e}")
    
    def deploy(self) -> bool:
        """执行完整部署"""
        print(f"{Colors.BOLD}{Colors.CYAN}开始部署到 {self.environment} 环境{Colors.ENDC}")
        print("=" * 60)
        
        try:
            # 1. 检查前提条件
            if not self.check_prerequisites():
                return False
            
            # 2. 备份数据
            if not self.backup_data():
                return False
            
            # 3. 构建镜像
            if not self.build_images():
                return False
            
            # 4. 部署服务
            if not self.deploy_services():
                return False
            
            # 5. 健康检查
            if not self.health_check():
                print_warning("健康检查失败，但部署已完成")
            
            # 6. 显示状态
            self.show_status()
            
            print("\n" + "=" * 60)
            print_success(f"🎉 部署到 {self.environment} 环境完成！")
            
            # 显示访问信息
            health_config = self.config.get("health_check", {})
            if health_config.get("frontend_url"):
                print(f"前端访问地址: {health_config['frontend_url']}")
            if health_config.get("backend_url"):
                print(f"后端API地址: {health_config['backend_url']}")
            
            print("=" * 60)
            return True
            
        except KeyboardInterrupt:
            print("\n部署被用户中断")
            return False
        except Exception as e:
            print_error(f"部署失败: {e}")
            return False

def create_production_compose():
    """创建生产环境的docker-compose文件"""
    prod_compose_content = '''
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
    volumes:
      - ./data:/app/data
      - ./backend/logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - app-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3
    networks:
      - app-network

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - backend
      - frontend
    restart: unless-stopped
    networks:
      - app-network

volumes:
  redis_data:

networks:
  app-network:
    driver: bridge
'''
    
    prod_compose_file = project_root / "docker-compose.prod.yml"
    with open(prod_compose_file, 'w', encoding='utf-8') as f:
        f.write(prod_compose_content)
    
    print_success(f"生产环境配置文件已创建: {prod_compose_file}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="化学问答机器人部署脚本")
    parser.add_argument(
        "environment",
        choices=["development", "staging", "production"],
        help="部署环境"
    )
    parser.add_argument(
        "--no-build",
        action="store_true",
        help="跳过镜像构建"
    )
    parser.add_argument(
        "--status-only",
        action="store_true",
        help="仅显示状态"
    )
    parser.add_argument(
        "--create-prod-config",
        action="store_true",
        help="创建生产环境配置文件"
    )
    
    args = parser.parse_args()
    
    if args.create_prod_config:
        create_production_compose()
        return
    
    deployer = Deployer(args.environment)
    
    if args.no_build:
        deployer.config["docker"]["build"] = False
    
    if args.status_only:
        deployer.show_status()
        return
    
    success = deployer.deploy()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
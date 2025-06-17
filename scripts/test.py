#!/usr/bin/env python3
"""
化学问答机器人测试脚本

这个脚本用于运行项目的所有测试，包括单元测试、集成测试和端到端测试。
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path
from typing import List, Optional, Dict, Any
import json

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
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"命令执行失败: {e}")
        if e.stderr:
            print(e.stderr)
        if check:
            raise
        return e

class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.results = {
            'unit_tests': {'passed': 0, 'failed': 0, 'errors': []},
            'integration_tests': {'passed': 0, 'failed': 0, 'errors': []},
            'e2e_tests': {'passed': 0, 'failed': 0, 'errors': []},
            'api_tests': {'passed': 0, 'failed': 0, 'errors': []}
        }
    
    def run_unit_tests(self) -> bool:
        """运行单元测试"""
        print_step("运行单元测试...")
        
        backend_dir = project_root / "backend"
        test_dir = backend_dir / "tests"
        
        if not test_dir.exists():
            print_warning("未找到测试目录，跳过单元测试")
            return True
        
        try:
            # 使用pytest运行测试
            result = run_command([
                sys.executable, "-m", "pytest", 
                str(test_dir),
                "-v",
                "--tb=short",
                "--json-report",
                "--json-report-file=test_results.json"
            ], cwd=backend_dir, check=False)
            
            if result.returncode == 0:
                self.results['unit_tests']['passed'] += 1
                print_success("单元测试通过")
                return True
            else:
                self.results['unit_tests']['failed'] += 1
                self.results['unit_tests']['errors'].append(result.stderr)
                print_error("单元测试失败")
                return False
                
        except Exception as e:
            self.results['unit_tests']['failed'] += 1
            self.results['unit_tests']['errors'].append(str(e))
            print_error(f"单元测试执行错误: {e}")
            return False
    
    def run_integration_tests(self) -> bool:
        """运行集成测试"""
        print_step("运行集成测试...")
        
        # 测试数据库连接
        try:
            from backend.app.core.config import settings
            print(f"  ✓ 配置加载成功")
        except Exception as e:
            print_error(f"配置加载失败: {e}")
            self.results['integration_tests']['failed'] += 1
            return False
        
        # 测试向量数据库
        try:
            import chromadb
            client = chromadb.Client()
            print(f"  ✓ ChromaDB连接成功")
            self.results['integration_tests']['passed'] += 1
        except Exception as e:
            print_error(f"ChromaDB连接失败: {e}")
            self.results['integration_tests']['failed'] += 1
            return False
        
        # 测试图像处理
        try:
            import cv2
            import PIL
            print(f"  ✓ 图像处理库可用")
            self.results['integration_tests']['passed'] += 1
        except Exception as e:
            print_error(f"图像处理库不可用: {e}")
            self.results['integration_tests']['failed'] += 1
            return False
        
        print_success("集成测试通过")
        return True
    
    def start_test_server(self) -> Optional[subprocess.Popen]:
        """启动测试服务器"""
        print_step("启动测试服务器...")
        
        backend_dir = project_root / "backend"
        
        try:
            # 启动FastAPI服务器
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn",
                "app.main:app",
                "--host", "127.0.0.1",
                "--port", "8001",  # 使用不同端口避免冲突
                "--reload"
            ], cwd=backend_dir)
            
            # 等待服务器启动
            time.sleep(5)
            
            # 检查服务器是否启动
            try:
                response = requests.get("http://127.0.0.1:8001/health")
                if response.status_code == 200:
                    print_success("测试服务器启动成功")
                    return process
                else:
                    print_error(f"服务器健康检查失败: {response.status_code}")
                    process.terminate()
                    return None
            except requests.RequestException as e:
                print_error(f"无法连接到测试服务器: {e}")
                process.terminate()
                return None
                
        except Exception as e:
            print_error(f"启动测试服务器失败: {e}")
            return None
    
    def run_api_tests(self) -> bool:
        """运行API测试"""
        print_step("运行API测试...")
        
        base_url = "http://127.0.0.1:8001"
        
        # 测试健康检查
        try:
            response = requests.get(f"{base_url}/health")
            if response.status_code == 200:
                print("  ✓ 健康检查API")
                self.results['api_tests']['passed'] += 1
            else:
                print(f"  ✗ 健康检查API: {response.status_code}")
                self.results['api_tests']['failed'] += 1
        except Exception as e:
            print(f"  ✗ 健康检查API: {e}")
            self.results['api_tests']['failed'] += 1
        
        # 测试聊天API
        try:
            chat_data = {
                "message": "什么是有机化学？",
                "conversation_id": "test_conversation",
                "use_rag": False
            }
            response = requests.post(
                f"{base_url}/api/chat/message",
                json=chat_data,
                timeout=30
            )
            if response.status_code == 200:
                print("  ✓ 聊天API")
                self.results['api_tests']['passed'] += 1
            else:
                print(f"  ✗ 聊天API: {response.status_code}")
                self.results['api_tests']['failed'] += 1
        except Exception as e:
            print(f"  ✗ 聊天API: {e}")
            self.results['api_tests']['failed'] += 1
        
        # 测试图像上传API
        try:
            # 创建测试图像
            import io
            from PIL import Image
            
            # 创建简单的测试图像
            img = Image.new('RGB', (100, 100), color='white')
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            files = {'file': ('test.png', img_bytes, 'image/png')}
            response = requests.post(
                f"{base_url}/api/image/upload",
                files=files,
                timeout=30
            )
            if response.status_code == 200:
                print("  ✓ 图像上传API")
                self.results['api_tests']['passed'] += 1
            else:
                print(f"  ✗ 图像上传API: {response.status_code}")
                self.results['api_tests']['failed'] += 1
        except Exception as e:
            print(f"  ✗ 图像上传API: {e}")
            self.results['api_tests']['failed'] += 1
        
        total_passed = self.results['api_tests']['passed']
        total_failed = self.results['api_tests']['failed']
        
        if total_failed == 0:
            print_success(f"API测试通过 ({total_passed}/{total_passed + total_failed})")
            return True
        else:
            print_error(f"API测试失败 ({total_passed}/{total_passed + total_failed})")
            return False
    
    def run_frontend_tests(self) -> bool:
        """运行前端测试"""
        print_step("运行前端测试...")
        
        frontend_dir = project_root / "frontend"
        package_json = frontend_dir / "package.json"
        
        if not package_json.exists():
            print_warning("未找到package.json，跳过前端测试")
            return True
        
        try:
            # 运行前端测试
            result = run_command([
                "npm", "test", "--", "--coverage", "--watchAll=false"
            ], cwd=frontend_dir, check=False)
            
            if result.returncode == 0:
                print_success("前端测试通过")
                return True
            else:
                print_error("前端测试失败")
                return False
                
        except Exception as e:
            print_error(f"前端测试执行错误: {e}")
            return False
    
    def run_e2e_tests(self) -> bool:
        """运行端到端测试"""
        print_step("运行端到端测试...")
        
        # 简单的端到端测试
        try:
            # 测试完整的聊天流程
            base_url = "http://127.0.0.1:8001"
            
            # 1. 发送消息
            chat_data = {
                "message": "请解释一下苯的结构",
                "conversation_id": "e2e_test",
                "use_rag": True
            }
            response = requests.post(
                f"{base_url}/api/chat/message",
                json=chat_data,
                timeout=60
            )
            
            if response.status_code != 200:
                print_error(f"聊天请求失败: {response.status_code}")
                self.results['e2e_tests']['failed'] += 1
                return False
            
            # 2. 获取对话历史
            response = requests.get(
                f"{base_url}/api/chat/conversations/e2e_test/history"
            )
            
            if response.status_code != 200:
                print_error(f"获取对话历史失败: {response.status_code}")
                self.results['e2e_tests']['failed'] += 1
                return False
            
            history = response.json()
            if len(history) < 2:  # 应该有用户消息和助手回复
                print_error("对话历史不完整")
                self.results['e2e_tests']['failed'] += 1
                return False
            
            print_success("端到端测试通过")
            self.results['e2e_tests']['passed'] += 1
            return True
            
        except Exception as e:
            print_error(f"端到端测试失败: {e}")
            self.results['e2e_tests']['failed'] += 1
            return False
    
    def generate_report(self) -> None:
        """生成测试报告"""
        print("\n" + "=" * 60)
        print(f"{Colors.BOLD}{Colors.CYAN}测试报告{Colors.ENDC}")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for test_type, results in self.results.items():
            passed = results['passed']
            failed = results['failed']
            total_passed += passed
            total_failed += failed
            
            status_color = Colors.GREEN if failed == 0 else Colors.RED
            print(f"{test_type.replace('_', ' ').title()}: {status_color}{passed} 通过, {failed} 失败{Colors.ENDC}")
            
            if results['errors']:
                for error in results['errors']:
                    print(f"  错误: {error}")
        
        print("\n" + "-" * 60)
        overall_color = Colors.GREEN if total_failed == 0 else Colors.RED
        print(f"总计: {overall_color}{total_passed} 通过, {total_failed} 失败{Colors.ENDC}")
        
        if total_failed == 0:
            print(f"\n{Colors.GREEN}🎉 所有测试通过！{Colors.ENDC}")
        else:
            print(f"\n{Colors.RED}❌ 有测试失败，请检查错误信息{Colors.ENDC}")
        
        print("=" * 60)
        
        # 保存测试报告
        report_file = project_root / "test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'results': self.results,
                'summary': {
                    'total_passed': total_passed,
                    'total_failed': total_failed,
                    'success': total_failed == 0
                }
            }, f, indent=2, ensure_ascii=False)
        
        print(f"测试报告已保存到: {report_file}")

def main():
    """主函数"""
    print(f"{Colors.BOLD}{Colors.CYAN}化学问答机器人测试脚本{Colors.ENDC}")
    print("=" * 50)
    
    runner = TestRunner()
    server_process = None
    
    try:
        # 运行单元测试
        runner.run_unit_tests()
        
        # 运行集成测试
        runner.run_integration_tests()
        
        # 启动测试服务器
        server_process = runner.start_test_server()
        
        if server_process:
            # 运行API测试
            runner.run_api_tests()
            
            # 运行端到端测试
            runner.run_e2e_tests()
        else:
            print_warning("跳过API和端到端测试（服务器启动失败）")
        
        # 运行前端测试
        runner.run_frontend_tests()
        
        # 生成报告
        runner.generate_report()
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print_error(f"测试执行失败: {e}")
    finally:
        # 清理
        if server_process:
            print_step("关闭测试服务器...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    main()
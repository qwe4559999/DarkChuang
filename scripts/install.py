#!/usr/bin/env python3
"""
化学问答机器人安装脚本

这个脚本用于自动安装项目的所有依赖和进行初始化设置。
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional

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
        raise

def check_python_version() -> bool:
    """检查Python版本"""
    print_step("检查Python版本...")
    
    if sys.version_info < (3, 8):
        print_error(f"需要Python 3.8或更高版本，当前版本: {sys.version}")
        return False
    
    print_success(f"Python版本检查通过: {sys.version}")
    return True

def check_node_version() -> bool:
    """检查Node.js版本"""
    print_step("检查Node.js版本...")
    
    try:
        result = subprocess.run(
            ["node", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print_success(f"Node.js版本: {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("Node.js未安装或不在PATH中")
        print("请从 https://nodejs.org/ 下载并安装Node.js")
        return False

def check_git() -> bool:
    """检查Git"""
    print_step("检查Git...")
    
    try:
        result = subprocess.run(
            ["git", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        version = result.stdout.strip()
        print_success(f"Git版本: {version}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_warning("Git未安装，某些功能可能不可用")
        return False

def create_directories() -> None:
    """创建必要的目录"""
    print_step("创建项目目录...")
    
    directories = [
        "data",
        "data/chemistry_books",
        "data/papers",
        "data/images",
        "backend/logs",
        "backend/uploads",
        "models/image_recognition",
        "models/embeddings",
        "docs",
    ]
    
    for directory in directories:
        dir_path = project_root / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {directory}")
    
    print_success("目录创建完成")

def setup_environment() -> None:
    """设置环境文件"""
    print_step("设置环境配置...")
    
    env_file = project_root / ".env"
    env_example = project_root / ".env.example"
    
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print_success("环境配置文件已创建: .env")
        print_warning("请编辑 .env 文件配置您的API密钥和其他设置")
    elif env_file.exists():
        print_success("环境配置文件已存在")
    else:
        print_warning("未找到环境配置模板文件")

def install_python_dependencies() -> None:
    """安装Python依赖"""
    print_step("安装Python依赖...")
    
    backend_dir = project_root / "backend"
    requirements_file = backend_dir / "requirements.txt"
    
    if not requirements_file.exists():
        print_error(f"未找到requirements.txt文件: {requirements_file}")
        return
    
    # 升级pip
    run_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    
    # 安装依赖
    run_command([
        sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
    ])
    
    print_success("Python依赖安装完成")

def install_node_dependencies() -> None:
    """安装Node.js依赖"""
    print_step("安装Node.js依赖...")
    
    frontend_dir = project_root / "frontend"
    package_json = frontend_dir / "package.json"
    
    if not package_json.exists():
        print_warning("未找到package.json文件，跳过Node.js依赖安装")
        return
    
    # 检查npm
    try:
        run_command(["npm", "--version"])
    except subprocess.CalledProcessError:
        print_error("npm不可用")
        return
    
    # 安装依赖
    run_command(["npm", "install"], cwd=frontend_dir)
    
    print_success("Node.js依赖安装完成")

def setup_git_hooks() -> None:
    """设置Git钩子"""
    print_step("设置Git钩子...")
    
    git_dir = project_root / ".git"
    if not git_dir.exists():
        print_warning("不是Git仓库，跳过Git钩子设置")
        return
    
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    # 创建pre-commit钩子
    pre_commit_hook = hooks_dir / "pre-commit"
    pre_commit_content = '''#!/bin/sh
# Pre-commit hook for chemistry bot

echo "Running pre-commit checks..."

# Check Python code style
if command -v black >/dev/null 2>&1; then
    echo "Checking Python code formatting..."
    black --check backend/app/ || {
        echo "Python code formatting issues found. Run 'black backend/app/' to fix."
        exit 1
    }
fi

# Check for common issues
echo "Checking for common issues..."
grep -r "TODO\|FIXME\|XXX" backend/app/ && {
    echo "Found TODO/FIXME/XXX comments. Please resolve before committing."
    exit 1
}

echo "Pre-commit checks passed!"
'''
    
    with open(pre_commit_hook, 'w', encoding='utf-8') as f:
        f.write(pre_commit_content)
    
    # 设置执行权限
    if os.name != 'nt':  # 非Windows系统
        os.chmod(pre_commit_hook, 0o755)
    
    print_success("Git钩子设置完成")

def download_sample_data() -> None:
    """下载示例数据"""
    print_step("设置示例数据...")
    
    # 创建示例化学文档
    sample_docs = [
        {
            "filename": "organic_chemistry_basics.txt",
            "content": """有机化学基础知识

有机化学是研究含碳化合物的化学分支。碳原子具有独特的成键能力，可以形成长链、环状结构和复杂的三维分子。

基本概念：
1. 烷烃：只含C-C单键和C-H键的饱和烃类
2. 烯烃：含有C=C双键的不饱和烃类
3. 炔烃：含有C≡C三键的不饱和烃类
4. 芳香烃：含有苯环结构的化合物

官能团：
- 羟基(-OH)：醇类化合物的特征基团
- 羰基(C=O)：醛、酮类化合物的特征基团
- 羧基(-COOH)：羧酸类化合物的特征基团
- 氨基(-NH2)：胺类化合物的特征基团

反应类型：
1. 取代反应：一个原子或基团被另一个原子或基团取代
2. 加成反应：不饱和化合物与其他分子结合
3. 消除反应：从分子中除去小分子
4. 重排反应：分子内原子或基团的重新排列
"""
        },
        {
            "filename": "inorganic_chemistry_basics.txt",
            "content": """无机化学基础知识

无机化学研究除有机化合物以外的所有化学元素及其化合物的性质、结构和反应。

元素周期表：
- 周期：水平行，表示电子壳层数
- 族：垂直列，表示最外层电子数
- 金属、非金属和半金属的分布规律

化学键类型：
1. 离子键：金属与非金属间的电子转移
2. 共价键：非金属间的电子共享
3. 金属键：金属原子间的电子海模型

酸碱理论：
1. 阿伦尼乌斯理论：酸产生H+，碱产生OH-
2. 布朗斯特-劳里理论：酸是质子给体，碱是质子受体
3. 路易斯理论：酸是电子对受体，碱是电子对给体

氧化还原反应：
- 氧化：失去电子，氧化数升高
- 还原：得到电子，氧化数降低
- 氧化剂：得到电子的物质
- 还原剂：失去电子的物质

配位化合物：
- 中心离子：接受电子对的金属离子
- 配体：提供电子对的分子或离子
- 配位数：中心离子周围配体的数目
"""
        }
    ]
    
    data_dir = project_root / "data" / "chemistry_books"
    for doc in sample_docs:
        file_path = data_dir / doc["filename"]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(doc["content"])
        print(f"  ✓ {doc['filename']}")
    
    print_success("示例数据创建完成")

def verify_installation() -> bool:
    """验证安装"""
    print_step("验证安装...")
    
    success = True
    
    # 检查Python模块
    python_modules = [
        "fastapi", "uvicorn", "langchain", "openai", 
        "chromadb", "opencv-python", "pillow"
    ]
    
    for module in python_modules:
        try:
            __import__(module.replace("-", "_"))
            print(f"  ✓ {module}")
        except ImportError:
            print(f"  ✗ {module}")
            success = False
    
    # 检查前端依赖
    frontend_dir = project_root / "frontend"
    node_modules = frontend_dir / "node_modules"
    if node_modules.exists():
        print("  ✓ Node.js依赖")
    else:
        print("  ✗ Node.js依赖")
        success = False
    
    if success:
        print_success("安装验证通过")
    else:
        print_error("安装验证失败")
    
    return success

def main():
    """主函数"""
    print(f"{Colors.BOLD}{Colors.CYAN}化学问答机器人安装脚本{Colors.ENDC}")
    print("=" * 50)
    
    try:
        # 检查系统要求
        if not check_python_version():
            sys.exit(1)
        
        check_node_version()
        check_git()
        
        # 创建目录结构
        create_directories()
        
        # 设置环境
        setup_environment()
        
        # 安装依赖
        install_python_dependencies()
        install_node_dependencies()
        
        # 设置开发工具
        setup_git_hooks()
        
        # 创建示例数据
        download_sample_data()
        
        # 验证安装
        if verify_installation():
            print("\n" + "=" * 50)
            print_success("🎉 安装完成！")
            print("\n下一步：")
            print("1. 编辑 .env 文件配置您的API密钥")
            print("2. 运行 'python scripts/start.py' 启动应用")
            print("3. 访问 http://localhost:3000 使用应用")
            print("=" * 50)
        else:
            print_error("安装过程中出现问题，请检查错误信息")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print_error(f"安装失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
化学问答机器人文档生成脚本

这个脚本用于自动生成项目文档，包括API文档、代码文档和用户手册。
"""

import os
import sys
import subprocess
import json
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
import re
from datetime import datetime

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

class DocumentationGenerator:
    """文档生成器"""
    
    def __init__(self):
        self.docs_dir = project_root / "docs"
        self.docs_dir.mkdir(exist_ok=True)
        
        # 创建文档子目录
        (self.docs_dir / "api").mkdir(exist_ok=True)
        (self.docs_dir / "code").mkdir(exist_ok=True)
        (self.docs_dir / "user").mkdir(exist_ok=True)
        (self.docs_dir / "images").mkdir(exist_ok=True)
    
    def generate_api_docs(self) -> bool:
        """生成API文档"""
        print_step("生成API文档...")
        
        try:
            # 检查FastAPI应用
            backend_dir = project_root / "backend"
            main_file = backend_dir / "app" / "main.py"
            
            if not main_file.exists():
                print_error("未找到FastAPI主文件")
                return False
            
            # 生成OpenAPI规范
            print_step("生成OpenAPI规范...")
            
            # 启动临时服务器获取OpenAPI JSON
            import requests
            import time
            import threading
            
            # 在后台启动服务器
            server_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn",
                "app.main:app",
                "--host", "127.0.0.1",
                "--port", "8002"
            ], cwd=backend_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # 等待服务器启动
            time.sleep(5)
            
            try:
                # 获取OpenAPI规范
                response = requests.get("http://127.0.0.1:8002/openapi.json")
                if response.status_code == 200:
                    openapi_spec = response.json()
                    
                    # 保存OpenAPI规范
                    with open(self.docs_dir / "api" / "openapi.json", 'w', encoding='utf-8') as f:
                        json.dump(openapi_spec, f, indent=2, ensure_ascii=False)
                    
                    # 生成Markdown格式的API文档
                    self.generate_api_markdown(openapi_spec)
                    
                    print_success("API文档生成完成")
                    return True
                else:
                    print_error(f"获取OpenAPI规范失败: {response.status_code}")
                    return False
                    
            except requests.RequestException as e:
                print_error(f"连接API服务器失败: {e}")
                return False
            finally:
                # 关闭服务器
                server_process.terminate()
                server_process.wait()
                
        except Exception as e:
            print_error(f"生成API文档失败: {e}")
            return False
    
    def generate_api_markdown(self, openapi_spec: Dict[str, Any]) -> None:
        """生成Markdown格式的API文档"""
        api_doc = []
        api_doc.append("# API 文档\n")
        api_doc.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 基本信息
        info = openapi_spec.get('info', {})
        api_doc.append(f"## {info.get('title', '化学问答机器人API')}\n")
        api_doc.append(f"版本: {info.get('version', '1.0.0')}\n")
        api_doc.append(f"{info.get('description', '')}\n")
        
        # 服务器信息
        servers = openapi_spec.get('servers', [])
        if servers:
            api_doc.append("## 服务器\n")
            for server in servers:
                api_doc.append(f"- {server.get('url', '')}: {server.get('description', '')}\n")
        
        # API端点
        paths = openapi_spec.get('paths', {})
        if paths:
            api_doc.append("## API 端点\n")
            
            for path, methods in paths.items():
                api_doc.append(f"### {path}\n")
                
                for method, details in methods.items():
                    if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                        api_doc.append(f"#### {method.upper()}\n")
                        
                        # 描述
                        summary = details.get('summary', '')
                        description = details.get('description', '')
                        if summary:
                            api_doc.append(f"**摘要**: {summary}\n")
                        if description:
                            api_doc.append(f"**描述**: {description}\n")
                        
                        # 参数
                        parameters = details.get('parameters', [])
                        if parameters:
                            api_doc.append("**参数**:\n")
                            for param in parameters:
                                name = param.get('name', '')
                                param_type = param.get('schema', {}).get('type', '')
                                required = '必需' if param.get('required', False) else '可选'
                                description = param.get('description', '')
                                api_doc.append(f"- `{name}` ({param_type}, {required}): {description}\n")
                        
                        # 请求体
                        request_body = details.get('requestBody', {})
                        if request_body:
                            api_doc.append("**请求体**:\n")
                            content = request_body.get('content', {})
                            for content_type, schema_info in content.items():
                                api_doc.append(f"- Content-Type: `{content_type}`\n")
                        
                        # 响应
                        responses = details.get('responses', {})
                        if responses:
                            api_doc.append("**响应**:\n")
                            for status_code, response_info in responses.items():
                                description = response_info.get('description', '')
                                api_doc.append(f"- `{status_code}`: {description}\n")
                        
                        api_doc.append("\n")
        
        # 数据模型
        components = openapi_spec.get('components', {})
        schemas = components.get('schemas', {})
        if schemas:
            api_doc.append("## 数据模型\n")
            for schema_name, schema_def in schemas.items():
                api_doc.append(f"### {schema_name}\n")
                
                properties = schema_def.get('properties', {})
                if properties:
                    api_doc.append("| 字段 | 类型 | 描述 |\n")
                    api_doc.append("|------|------|------|\n")
                    for prop_name, prop_def in properties.items():
                        prop_type = prop_def.get('type', '')
                        prop_desc = prop_def.get('description', '')
                        api_doc.append(f"| {prop_name} | {prop_type} | {prop_desc} |\n")
                
                api_doc.append("\n")
        
        # 保存文档
        with open(self.docs_dir / "api" / "README.md", 'w', encoding='utf-8') as f:
            f.writelines(api_doc)
    
    def generate_code_docs(self) -> bool:
        """生成代码文档"""
        print_step("生成代码文档...")
        
        try:
            # 使用pydoc生成Python代码文档
            backend_dir = project_root / "backend"
            app_dir = backend_dir / "app"
            
            if not app_dir.exists():
                print_warning("未找到应用代码目录")
                return True
            
            # 生成模块文档
            modules = [
                "app.main",
                "app.api.chat",
                "app.api.image",
                "app.services.rag_service",
                "app.services.llm_service",
                "app.services.image_service",
                "app.core.config"
            ]
            
            for module in modules:
                try:
                    result = run_command([
                        sys.executable, "-m", "pydoc", "-w", module
                    ], cwd=backend_dir, check=False)
                    
                    if result.returncode == 0:
                        print(f"  ✓ {module}")
                    else:
                        print(f"  ✗ {module}")
                        
                except Exception as e:
                    print(f"  ✗ {module}: {e}")
            
            # 移动生成的HTML文件到文档目录
            for html_file in backend_dir.glob("*.html"):
                shutil.move(html_file, self.docs_dir / "code" / html_file.name)
            
            # 生成代码结构文档
            self.generate_code_structure_doc()
            
            print_success("代码文档生成完成")
            return True
            
        except Exception as e:
            print_error(f"生成代码文档失败: {e}")
            return False
    
    def generate_code_structure_doc(self) -> None:
        """生成代码结构文档"""
        structure_doc = []
        structure_doc.append("# 代码结构\n")
        structure_doc.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 后端结构
        structure_doc.append("## 后端结构\n")
        structure_doc.append("```\n")
        structure_doc.append("backend/\n")
        
        backend_dir = project_root / "backend"
        if backend_dir.exists():
            self.add_directory_tree(structure_doc, backend_dir, "backend", 0)
        
        structure_doc.append("```\n\n")
        
        # 前端结构
        structure_doc.append("## 前端结构\n")
        structure_doc.append("```\n")
        structure_doc.append("frontend/\n")
        
        frontend_dir = project_root / "frontend"
        if frontend_dir.exists():
            self.add_directory_tree(structure_doc, frontend_dir, "frontend", 0)
        
        structure_doc.append("```\n\n")
        
        # 主要模块说明
        structure_doc.append("## 主要模块说明\n")
        
        modules_info = {
            "app/main.py": "FastAPI应用主入口",
            "app/api/": "API路由定义",
            "app/services/": "业务逻辑服务",
            "app/core/": "核心配置和工具",
            "app/models/": "数据模型定义",
            "frontend/src/components/": "React组件",
            "frontend/src/services/": "前端服务和API调用",
            "data/": "数据文件存储",
            "scripts/": "项目脚本"
        }
        
        for module, description in modules_info.items():
            structure_doc.append(f"- **{module}**: {description}\n")
        
        # 保存文档
        with open(self.docs_dir / "code" / "structure.md", 'w', encoding='utf-8') as f:
            f.writelines(structure_doc)
    
    def add_directory_tree(self, doc: List[str], directory: Path, prefix: str, level: int) -> None:
        """添加目录树到文档"""
        if level > 3:  # 限制深度
            return
        
        try:
            items = sorted(directory.iterdir())
            for item in items:
                if item.name.startswith('.') or item.name == '__pycache__':
                    continue
                
                indent = "  " * level
                if item.is_dir():
                    doc.append(f"{indent}├── {item.name}/\n")
                    self.add_directory_tree(doc, item, f"{prefix}/{item.name}", level + 1)
                else:
                    doc.append(f"{indent}├── {item.name}\n")
        except PermissionError:
            pass
    
    def generate_user_docs(self) -> bool:
        """生成用户文档"""
        print_step("生成用户文档...")
        
        try:
            # 用户手册
            user_manual = self.create_user_manual()
            with open(self.docs_dir / "user" / "manual.md", 'w', encoding='utf-8') as f:
                f.write(user_manual)
            
            # 安装指南
            installation_guide = self.create_installation_guide()
            with open(self.docs_dir / "user" / "installation.md", 'w', encoding='utf-8') as f:
                f.write(installation_guide)
            
            # 常见问题
            faq = self.create_faq()
            with open(self.docs_dir / "user" / "faq.md", 'w', encoding='utf-8') as f:
                f.write(faq)
            
            print_success("用户文档生成完成")
            return True
            
        except Exception as e:
            print_error(f"生成用户文档失败: {e}")
            return False
    
    def create_user_manual(self) -> str:
        """创建用户手册"""
        return '''
# 化学问答机器人用户手册

## 概述

化学问答机器人是一个基于人工智能的化学知识问答系统，能够回答化学相关问题，识别化学结构，并提供准确的化学信息。

## 主要功能

### 1. 智能问答
- 回答化学基础知识问题
- 解释化学反应机理
- 提供化合物性质信息
- 支持中英文问答

### 2. 图像识别
- 识别化学结构式
- 提取化学公式
- 分析实验图片
- 支持多种图片格式

### 3. 知识检索
- 基于RAG技术的知识检索
- 从化学文献中获取信息
- 提供可靠的参考来源

## 使用方法

### 文本问答

1. 在聊天界面输入您的化学问题
2. 选择是否启用RAG检索
3. 点击发送按钮
4. 查看AI回复和相关资料

**示例问题**：
- "苯的分子结构是什么？"
- "请解释SN2反应机理"
- "碳酸钠的化学性质有哪些？"

### 图像识别

1. 点击图像上传区域
2. 选择或拖拽图片文件
3. 等待系统分析
4. 查看识别结果

**支持的图片类型**：
- PNG, JPG, JPEG
- GIF, BMP
- 最大文件大小：10MB

## 高级功能

### RAG检索

RAG（Retrieval-Augmented Generation）功能可以从知识库中检索相关信息，提供更准确的答案。

**使用建议**：
- 对于专业问题，建议启用RAG
- 对于基础问题，可以关闭RAG以获得更快响应

### 对话管理

- 系统会自动保存对话历史
- 可以查看之前的对话记录
- 支持清除对话历史

## 注意事项

1. **准确性**：AI回答仅供参考，重要决策请咨询专业人士
2. **安全性**：请勿上传包含敏感信息的图片
3. **网络**：某些功能需要稳定的网络连接
4. **浏览器**：建议使用现代浏览器以获得最佳体验

## 技术支持

如果您遇到问题，请：
1. 查看常见问题解答
2. 检查网络连接
3. 刷新页面重试
4. 联系技术支持
'''
    
    def create_installation_guide(self) -> str:
        """创建安装指南"""
        return '''
# 安装指南

## 系统要求

### 最低要求
- Python 3.8+
- Node.js 16+
- 4GB RAM
- 10GB 可用磁盘空间

### 推荐配置
- Python 3.11+
- Node.js 18+
- 8GB RAM
- 20GB 可用磁盘空间
- GPU（可选，用于加速推理）

## 快速安装

### 1. 克隆项目
```bash
git clone <repository-url>
cd DarkChuang
```

### 2. 运行安装脚本
```bash
python scripts/install.py
```

### 3. 配置环境
编辑 `.env` 文件，设置必要的配置项：
```
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
```

### 4. 启动应用
```bash
python scripts/start.py
```

## 手动安装

### 后端安装

1. 创建虚拟环境
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 启动后端
```bash
uvicorn app.main:app --reload
```

### 前端安装

1. 安装依赖
```bash
cd frontend
npm install
```

2. 启动前端
```bash
npm start
```

## Docker 部署

### 开发环境
```bash
docker-compose up -d
```

### 生产环境
```bash
python scripts/deploy.py production
```

## 配置说明

### 环境变量

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| OPENAI_API_KEY | OpenAI API密钥 | 必需 |
| OPENAI_BASE_URL | OpenAI API地址 | https://api.openai.com/v1 |
| REDIS_URL | Redis连接地址 | redis://localhost:6379 |
| LOG_LEVEL | 日志级别 | info |

### 数据目录

- `data/chemistry_books/`: 化学教材和参考书
- `data/papers/`: 学术论文
- `data/images/`: 上传的图片
- `backend/logs/`: 应用日志

## 故障排除

### 常见问题

1. **端口冲突**
   - 检查8000和3000端口是否被占用
   - 修改配置文件中的端口设置

2. **依赖安装失败**
   - 升级pip: `pip install --upgrade pip`
   - 使用国内镜像: `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple`

3. **API密钥错误**
   - 检查`.env`文件中的API密钥
   - 确认API密钥有效且有足够额度

4. **内存不足**
   - 关闭其他应用程序
   - 考虑使用更小的模型

### 日志查看

```bash
# 查看后端日志
tail -f backend/logs/app.log

# 查看Docker日志
docker-compose logs -f
```
'''
    
    def create_faq(self) -> str:
        """创建常见问题解答"""
        return '''
# 常见问题解答 (FAQ)

## 一般问题

### Q: 这个系统支持哪些语言？
A: 系统主要支持中文和英文，可以理解和回答中英文化学问题。

### Q: 系统的回答准确性如何？
A: 系统基于大型语言模型和化学知识库，准确性较高，但建议将回答作为参考，重要决策请咨询专业人士。

### Q: 可以处理哪些类型的化学问题？
A: 系统可以回答：
- 基础化学概念
- 化学反应机理
- 化合物性质
- 实验方法
- 化学计算

## 技术问题

### Q: 为什么系统响应很慢？
A: 可能的原因：
- 网络连接不稳定
- API服务器负载高
- 启用了RAG检索（需要更多时间）
- 处理复杂问题需要更多计算时间

### Q: 图像识别不准确怎么办？
A: 建议：
- 确保图片清晰度足够
- 避免图片中有过多干扰元素
- 尝试不同角度或光照条件的图片
- 检查图片格式是否支持

### Q: 如何提高回答质量？
A: 建议：
- 问题描述要具体明确
- 启用RAG检索获取更准确信息
- 提供足够的上下文信息
- 使用专业术语

## 配置问题

### Q: 如何配置OpenAI API？
A: 
1. 在`.env`文件中设置`OPENAI_API_KEY`
2. 如果使用其他服务，修改`OPENAI_BASE_URL`
3. 重启应用使配置生效

### Q: 如何添加自定义知识库？
A: 
1. 将文档放入`data/chemistry_books/`目录
2. 支持的格式：txt, pdf, docx
3. 重启应用以重新索引

### Q: 如何修改模型参数？
A: 在`.env`文件中修改：
- `OPENAI_MODEL`: 模型名称
- `MAX_TOKENS`: 最大输出长度
- `TEMPERATURE`: 创造性参数

## 部署问题

### Q: Docker部署失败怎么办？
A: 检查：
- Docker和Docker Compose是否正确安装
- 端口是否被占用
- 磁盘空间是否充足
- 网络连接是否正常

### Q: 如何在生产环境部署？
A: 
1. 使用`python scripts/deploy.py production`
2. 配置HTTPS证书
3. 设置防火墙规则
4. 配置监控和日志

### Q: 如何备份数据？
A: 
- 数据文件位于`data/`目录
- 使用`scripts/deploy.py`会自动备份
- 手动备份：复制整个`data/`目录

## 性能优化

### Q: 如何提高系统性能？
A: 
- 使用SSD存储
- 增加内存
- 使用GPU加速
- 优化数据库索引
- 启用Redis缓存

### Q: 如何减少API调用成本？
A: 
- 启用缓存机制
- 使用更便宜的模型
- 优化提示词长度
- 设置合理的超时时间

## 安全问题

### Q: 如何保护API密钥？
A: 
- 不要将密钥提交到版本控制
- 使用环境变量存储
- 定期轮换密钥
- 设置API使用限制

### Q: 上传的图片是否安全？
A: 
- 图片仅用于分析，不会永久存储
- 不要上传包含敏感信息的图片
- 系统会自动清理临时文件

## 联系支持

如果以上解答无法解决您的问题，请：

1. 查看系统日志获取详细错误信息
2. 在GitHub上提交Issue
3. 发送邮件至技术支持
4. 加入用户交流群

请在求助时提供：
- 操作系统和版本
- Python和Node.js版本
- 错误信息和日志
- 复现步骤
'''
    
    def generate_readme(self) -> bool:
        """生成主README文件"""
        print_step("生成主README文件...")
        
        try:
            readme_content = f'''
# 化学问答机器人

一个基于人工智能的化学知识问答系统，支持文本问答和图像识别。

## 功能特点

- 🤖 **智能问答**: 基于大型语言模型的化学知识问答
- 🔍 **RAG检索**: 从化学文献中检索相关信息
- 📷 **图像识别**: 识别化学结构式和公式
- 💬 **对话管理**: 支持多轮对话和历史记录
- 🌐 **Web界面**: 现代化的React前端界面
- 🐳 **容器化**: 支持Docker部署

## 快速开始

### 安装

```bash
# 克隆项目
git clone <repository-url>
cd DarkChuang

# 运行安装脚本
python scripts/install.py

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置您的API密钥

# 启动应用
python scripts/start.py
```

### 访问应用

- 前端界面: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

## 项目结构

```
DarkChuang/
├── backend/                 # 后端服务
│   ├── app/                # FastAPI应用
│   │   ├── api/           # API路由
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据模型
│   │   └── services/      # 业务服务
│   ├── requirements.txt   # Python依赖
│   └── Dockerfile        # 后端Docker配置
├── frontend/               # 前端应用
│   ├── src/               # React源码
│   │   ├── components/    # React组件
│   │   └── services/      # 前端服务
│   ├── package.json      # Node.js依赖
│   └── Dockerfile        # 前端Docker配置
├── data/                  # 数据文件
├── docs/                  # 项目文档
├── scripts/               # 项目脚本
└── docker-compose.yml     # Docker Compose配置
```

## 技术栈

### 后端
- **FastAPI**: 现代Python Web框架
- **LangChain**: LLM应用开发框架
- **ChromaDB**: 向量数据库
- **OpenCV**: 图像处理
- **Redis**: 缓存和会话存储

### 前端
- **React**: 用户界面库
- **Material-UI**: UI组件库
- **TypeScript**: 类型安全的JavaScript
- **Axios**: HTTP客户端

### 部署
- **Docker**: 容器化
- **Nginx**: 反向代理
- **Uvicorn**: ASGI服务器

## 配置说明

主要配置项在 `.env` 文件中：

```env
# OpenAI配置
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# 应用配置
APP_NAME=化学问答机器人
DEBUG=false
LOG_LEVEL=info

# 数据库配置
REDIS_URL=redis://localhost:6379
```

## 开发指南

### 本地开发

```bash
# 后端开发
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端开发
cd frontend
npm install
npm start
```

### 运行测试

```bash
python scripts/test.py
```

### 生成文档

```bash
python scripts/generate_docs.py
```

## 部署

### Docker部署

```bash
# 开发环境
docker-compose up -d

# 生产环境
python scripts/deploy.py production
```

### 手动部署

详细部署说明请参考 [部署文档](docs/user/installation.md)。

## 文档

- [用户手册](docs/user/manual.md)
- [安装指南](docs/user/installation.md)
- [API文档](docs/api/README.md)
- [代码文档](docs/code/structure.md)
- [常见问题](docs/user/faq.md)

## 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 支持

如果您遇到问题或有建议，请：

- 查看 [常见问题](docs/user/faq.md)
- 提交 [Issue](https://github.com/your-repo/issues)
- 发送邮件至 support@example.com

## 更新日志

### v1.0.0 ({datetime.now().strftime('%Y-%m-%d')})
- 初始版本发布
- 支持化学问答功能
- 支持图像识别功能
- 提供Web界面
- 支持Docker部署
'''
            
            with open(project_root / "README.md", 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            print_success("主README文件生成完成")
            return True
            
        except Exception as e:
            print_error(f"生成README文件失败: {e}")
            return False
    
    def generate_all(self) -> bool:
        """生成所有文档"""
        print(f"{Colors.BOLD}{Colors.CYAN}开始生成项目文档{Colors.ENDC}")
        print("=" * 50)
        
        success = True
        
        # 生成各类文档
        if not self.generate_api_docs():
            success = False
        
        if not self.generate_code_docs():
            success = False
        
        if not self.generate_user_docs():
            success = False
        
        if not self.generate_readme():
            success = False
        
        if success:
            print("\n" + "=" * 50)
            print_success("🎉 所有文档生成完成！")
            print(f"文档位置: {self.docs_dir}")
            print("=" * 50)
        else:
            print_error("文档生成过程中出现错误")
        
        return success

def main():
    """主函数"""
    generator = DocumentationGenerator()
    success = generator.generate_all()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
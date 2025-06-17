# DarkChuang

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![SvelteKit](https://img.shields.io/badge/SvelteKit-1.20.4-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)
![Version](https://img.shields.io/badge/Version-1.0.0-blue.svg)

![RAG](https://img.shields.io/badge/RAG-LangChain-purple.svg)
![Vector DB](https://img.shields.io/badge/VectorDB-ChromaDB-red.svg)
![AI](https://img.shields.io/badge/AI-Transformers-lightblue.svg)
![OCR](https://img.shields.io/badge/OCR-PaddleOCR-darkgreen.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)

</div>

基于RAG技术的智能化学知识问答和图谱识别系统

## 项目简介

**DarkChuang** 是一个现代化的化学问答机器人系统，结合了检索增强生成(RAG)技术和先进的图像识别能力。项目致力于为化学学习者和研究人员提供智能化的知识查询和图像分析服务。

### 核心功能
- 🤖 **智能问答**: 基于大语言模型的化学知识问答，支持多轮对话和上下文理解
- 🔍 **RAG检索**: 集成ChromaDB向量数据库，提供精准的化学文献检索和知识增强
- 📷 **图像识别**: 化学分子结构图、化学方程式、实验装置图识别，支持PaddleOCR文字提取
- 🔬 **光谱分析**: 专业的化学光谱数据分析界面，支持交互式图表和数据可视化
- 🌐 **现代界面**: 基于SvelteKit的响应式Web界面，采用现代化设计语言
- 📚 **API文档**: 完整的RESTful API文档和交互式测试界面
- 🐳 **容器化部署**: 完整的Docker支持，一键部署和扩展

## 技术栈

### 后端技术
- **框架**: Python 3.8+ + FastAPI 0.104.1
- **RAG技术**: LangChain 0.0.350 + ChromaDB 0.4.18 + Sentence Transformers 2.2.2
- **AI模型**: Transformers 4.36.0 + PyTorch 2.6.0+
- **图像处理**: OpenCV 4.8.1 + PaddleOCR 2.7.0 + Pillow 10.1.0+
- **数据处理**: Pandas 2.1.4 + NumPy 1.24.3+ + Scikit-learn 1.3.2
- **数据库**: ChromaDB (向量数据库) + SQLAlchemy 2.0.23
- **文档处理**: PyPDF2 3.0.1 + python-docx 1.1.0 + Markdown 3.5.1
- **异步处理**: Uvicorn + Aiofiles

### 前端技术
- **框架**: SvelteKit 1.20.4 + TypeScript 5.0.0
- **构建工具**: Vite 4.4.2
- **样式**: CSS3 + 现代化渐变设计 + 毛玻璃效果
- **HTTP客户端**: Axios 1.10.0
- **开发工具**: ESLint + Prettier + Svelte Check

### 部署技术
- **容器化**: Docker + Docker Compose
- **Web服务器**: Nginx (生产环境)
- **进程管理**: Uvicorn (ASGI服务器)
- **环境管理**: Python venv + Node.js 16+

## 项目结构

```
DarkChuang/
├── backend/                 # 后端服务
│   ├── app/                # FastAPI 应用
│   │   ├── api/           # API 路由
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据模型
│   │   ├── schemas/       # Pydantic 模式
│   │   ├── services/      # 业务服务
│   │   └── utils/         # 工具函数
│   ├── data/              # 数据存储
│   │   ├── uploads/       # 上传文件
│   │   └── vector_db/     # 向量数据库
│   ├── tests/             # 测试文件
│   ├── requirements.txt   # Python 依赖
│   └── Dockerfile         # Docker 配置
├── frontend/               # SvelteKit 前端
│   ├── src/               # 源代码
│   │   ├── lib/           # 组件库
│   │   └── routes/        # 页面路由
│   │       ├── +page.svelte      # 首页
│   │       ├── spectrum/         # 光谱分析页面
│   │       └── api-docs/         # API 文档页面
│   ├── static/            # 静态资源
│   ├── package.json       # Node.js 依赖
│   └── svelte.config.js   # Svelte 配置
├── models/                 # AI 模型
│   ├── embeddings/        # 嵌入模型
│   └── image_recognition/ # 图像识别模型
├── data/                   # 原始数据
│   ├── chemistry_books/   # 化学教材
│   ├── papers/            # 学术论文
│   └── images/            # 化学图像数据
├── docs/                   # 项目文档
│   ├── DEPLOYMENT.md      # 详细部署指南
│   └── DEVELOPMENT_HISTORY.md # 开发历史
├── scripts/                # 自动化脚本
│   ├── install.py         # 安装脚本
│   ├── start.py           # 启动脚本
│   └── deploy.py          # 部署脚本
├── docker-compose.yml      # Docker Compose 配置
├── quick-deploy.sh         # 快速部署脚本 (Linux/macOS)
├── quick-deploy.bat        # 快速部署脚本 (Windows)
└── .env.example           # 环境变量示例
```

## 开发进度

### 已完成功能 ✅
- [x] **项目架构设计** - 完整的前后端分离架构，支持微服务扩展
- [x] **后端API开发** - FastAPI + 异步处理，包含聊天、图像、健康检查等API
- [x] **RAG系统实现** - LangChain + ChromaDB 完整集成，支持文档检索和知识增强
- [x] **图像识别模块** - OpenCV + PaddleOCR 完整实现，支持多格式图像处理
- [x] **光谱分析系统** - 专业的化学光谱数据分析，包含双模型架构支持
- [x] **前端界面开发** - SvelteKit + TypeScript，包含聊天、图像上传、光谱分析等页面
- [x] **现代化UI设计** - 蓝紫色渐变主题、毛玻璃效果、流畅动画、响应式布局
- [x] **API文档系统** - 交互式API文档页面，支持实时测试和代码示例
- [x] **容器化部署** - 完整的Docker + Docker Compose配置
- [x] **自动化脚本** - Python安装、启动、部署脚本，支持跨平台
- [x] **测试系统** - 完整的功能测试套件，包含RAG、光谱、聊天等模块测试
- [x] **日志系统** - 结构化日志记录和错误追踪
- [x] **环境配置** - 完善的环境变量管理和配置系统

### 开发中功能 🚧
- [ ] **多模型支持** - 集成更多开源AI模型（ChatGLM、Qwen等）
- [ ] **用户系统** - 用户注册、登录、权限管理、使用统计
- [ ] **数据管理后台** - 化学数据库管理界面、文档上传管理
- [ ] **性能优化** - Redis缓存机制、异步队列、并发优化
- [ ] **监控系统** - Prometheus + Grafana 性能监控
- [ ] **安全增强** - API限流、身份验证、数据加密

### 计划功能 📋
- [ ] **移动端适配** - PWA支持、原生App开发
- [ ] **多语言支持** - 国际化(i18n)、多语言界面
- [ ] **插件系统** - 可扩展的功能模块、第三方集成
- [ ] **高级分析** - 化学反应预测、分子性质计算
- [ ] **协作功能** - 团队工作空间、共享笔记
- [ ] **离线模式** - 本地模型部署、离线数据处理
- [ ] **API生态** - 开放API平台、第三方开发者支持

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- Git

### 自动安装（推荐）
```bash
# 克隆项目
git clone https://github.com/your-username/DarkChuang.git
cd DarkChuang

# 运行自动安装脚本
python scripts/install.py

# 启动服务
python scripts/start.py
```

### 手动安装

#### 1. 后端设置
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

#### 2. 前端设置
```bash
cd frontend
npm install
```

#### 3. 环境配置
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，设置必要的API密钥
# OPENAI_API_KEY=your_openai_api_key
```

#### 4. 启动服务
```bash
# 启动后端（在 backend 目录）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动前端（在 frontend 目录）
npm run dev
```

### 访问应用
- **前端界面**: http://localhost:5173
- **聊天界面**: http://localhost:5173/chat
- **图像识别**: http://localhost:5173/image
- **光谱分析**: http://localhost:5173/spectrum
- **API文档**: http://localhost:5173/api-docs
- **后端API**: http://localhost:8000
- **Swagger文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

### Docker 部署（推荐）

#### 快速部署
```bash
# 方式1: 使用快速部署脚本
./quick-deploy.sh      # Linux/macOS
# 或
quick-deploy.bat       # Windows

# 方式2: 直接使用 Docker Compose
docker-compose up -d

# 方式3: 使用Python部署脚本
python scripts/deploy.py --environment development
```

#### 部署前准备
1. 确保已安装 Docker 和 Docker Compose
2. 配置环境变量文件 `.env`（特别是API密钥）
3. 查看完整部署指南: [📖 部署文档](docs/DEPLOYMENT.md)

#### 服务访问
- 前端应用: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

#### 生产环境部署
```bash
# 启用监控服务
docker-compose --profile monitoring up -d

# 访问监控面板
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001
```

> 💡 **提示**: 详细的部署指南、故障排除和生产环境配置请参考 [完整部署文档](docs/DEPLOYMENT.md)

## 主要功能

### 🤖 智能问答
- 支持化学相关问题的智能回答，涵盖有机化学、无机化学、物理化学等领域
- 多轮对话能力，支持上下文理解和对话历史
- 基于RAG的知识检索增强，结合向量数据库提供精准答案
- 支持中英文问答，自动语言检测
- 实时流式响应，提升用户体验

### 📷 图像识别
- **化学结构式识别**: 自动识别分子结构图并提取化学信息
- **化学方程式提取**: 从图片中提取化学方程式和反应式
- **实验装置图分析**: 识别实验设备和装置配置
- **多格式支持**: PNG、JPG、GIF、BMP等主流图片格式
- **拖拽上传**: 便捷的文件上传界面
- **OCR文字提取**: 基于PaddleOCR的高精度文字识别

### 🔬 光谱分析
- **专业分析界面**: 化学光谱数据的专业分析工具
- **交互式图表**: 支持缩放、标注、数据点查看
- **多种光谱类型**: 支持红外、紫外、核磁等多种光谱
- **数据处理**: 光谱数据的预处理和特征提取
- **双模型架构**: 支持多种AI模型的光谱分析
- **结果导出**: 分析结果的导出和报告生成

### 📚 API文档
- **完整API文档**: 涵盖所有后端API接口的详细说明
- **交互式测试**: 在线测试API接口，实时查看响应
- **代码示例**: 多语言的API调用示例代码
- **参数说明**: 详细的请求参数和响应格式说明
- **错误处理**: 完整的错误代码和处理建议
- **实时更新**: API文档与代码同步更新

## 贡献

我们欢迎各种形式的贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解详细信息。

### 贡献方式
- 🐛 报告错误
- 💡 提出功能建议
- 📝 改进文档
- 🔧 提交代码修复
- ✨ 添加新功能

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 项目特色

### 🎨 现代化设计
- **视觉效果**: 蓝紫色渐变主题，毛玻璃效果，流畅动画
- **用户体验**: 响应式设计，完美适配桌面和移动设备
- **交互设计**: 直观的操作界面，丰富的视觉反馈

### ⚡ 高性能架构
- **异步处理**: FastAPI + Uvicorn 高性能异步框架
- **智能缓存**: 向量数据库缓存，提升检索速度
- **容器化**: Docker部署，支持水平扩展

### 🔒 安全可靠
- **数据安全**: 本地部署，数据完全可控
- **错误处理**: 完善的异常处理和日志记录
- **健康监控**: 实时健康检查和状态监控

### 🛠️ 开发友好
- **完整文档**: 详细的部署和开发文档
- **自动化脚本**: 一键安装、启动、部署
- **测试覆盖**: 完整的功能测试套件
- **代码质量**: TypeScript + Python类型提示

## 版本信息

- **当前版本**: v1.0.0
- **最后更新**: 2024-12-19
- **开发状态**: 活跃开发中
- **许可证**: MIT License

## 🏗️ 系统架构

### 系统架构图
![系统架构图](https://raw.githubusercontent.com/qwe4559999/DarkChuang/main/DarkChuang_Architecture.png)

### 数据流程图
![数据流程图](https://raw.githubusercontent.com/qwe4559999/DarkChuang/main/DarkChuang_DataFlow.png)

系统采用前后端分离的微服务架构，主要包括：
- **前端**: SvelteKit + TypeScript 构建的现代化Web界面
- **后端**: FastAPI + Python 构建的高性能API服务
- **AI服务**: 集成多种AI模型提供智能分析能力
- **数据存储**: 向量数据库 + 文件存储的混合存储方案

## 联系我们

如果您有任何问题或建议，请：
- 创建 [Issue](https://github.com/qwe4559999/DarkChuang/issues)
- 发送邮件至: heyrhaho123@126.com
- 查看 [项目文档](docs/)
- 查看 [更新日志](CHANGELOG.md)

---

**DarkChuang** - 让化学学习更智能 🧪✨

*基于现代AI技术，为化学教育和研究提供智能化解决方案*
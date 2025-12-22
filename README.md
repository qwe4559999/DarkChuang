# DarkChuang

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![Svelte](https://img.shields.io/badge/Svelte-4.0+-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Status](https://img.shields.io/badge/Status-Active-brightgreen.svg)
![Version](https://img.shields.io/badge/Version-2.0.0-blue.svg)

![RDKit](https://img.shields.io/badge/Chemistry-RDKit-red.svg)
![GLM-4.6V](https://img.shields.io/badge/Model-GLM--4.6V-purple.svg)
![TailwindCSS](https://img.shields.io/badge/UI-TailwindCSS-lightblue.svg)
![Docker](https://img.shields.io/badge/Docker-Supported-blue.svg)

</div>

基于 **GLM-4.6V 多模态大模型** 和 **RDKit 化学计算引擎** 的新一代智能化学助手。

## 项目简介

**DarkChuang** 是一个现代化的化学问答机器人系统。相较于传统的大模型对话，本项目深度集成了专业的化学工具链，能够提供精准的分子计算、结构可视化和光谱分析能力，解决了通用大模型在化学领域"幻觉"严重的问题。

### 核心亮点 (v2.0)

- 🧪 **专业化学计算**: 内置 **RDKit** 引擎，支持分子量、LogP、TPSA等物理属性的精确计算，告别大模型"瞎猜"。
- 🧬 **实时结构可视化**: 自动识别对话中的化学物质（如"Aspirin"），实时生成 2D/3D 分子结构图。
- 👁️ **全能多模态分析**: 采用 SiliconFlow 提供的 **GLM-4.6V** 模型，单模型同时处理复杂的化学对话和光谱图像识别（IR/NMR/MS）。
- ⚛️ **极简交互**: 全新重构的 Svelte + TailwindCSS 前端，专注于沉浸式化学探索体验。
- 🚀 **Docker化部署**: 开箱即用，一键启动完整环境。

## 技术栈

### 后端技术
- **框架**: Python 3.8+ + FastAPI
- **AI模型**: zai-org/GLM-4.6V (via SiliconFlow API)
- **化学引擎**: RDKit (分子计算与绘图)
- **图像处理**: OpenCV
- **异步处理**: Uvicorn + Aiofiles

### 前端技术
- **框架**: Svelte 4 + Vite
- **语言**: TypeScript
- **样式**: Tailwind CSS
- **图标**: Lucide Icons
- **HTTP**: Fetch API

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/qwe4559999/DarkChuang.git
cd DarkChuang
```

### 2. 后端启动
```bash
cd backend
# 安装依赖
pip install -r requirements.txt

# 配置 API Key
# 修改 .env 文件或设置环境变量
export SILICONFLOW_API_KEY="your-api-key"

# 启动服务
uvicorn app.main:app --reload
```

### 3. 前端启动
```bash
cd frontend
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用
打开浏览器访问: `http://localhost:5173`

## 功能演示

### 1. 分子查询与计算
用户输入: *"Show me the structure of Caffeine"*
系统响应:
- 自动提取 "Caffeine"
- 调用 RDKit 生成咖啡因的分子结构图
- 计算并展示 MW (194.19), LogP (-0.07) 等属性

### 2. 光谱图谱分析
用户上传一张红外光谱图。
系统响应:
- GLM-4.6V 识别光谱类型
- 自动标注特征峰位
- 推断可能的官能团和分子结构

## 贡献

欢迎提交 Pull Request 或 Issue！

## 许可证

MIT License

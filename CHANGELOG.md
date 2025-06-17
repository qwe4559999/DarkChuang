# 更新日志

本文档记录了化学问答机器人项目的所有重要更改。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [未发布]

### 新增
- 🎨 **现代化UI设计**
  - 全新的渐变背景设计，采用蓝紫色主题
  - 毛玻璃效果和柔和阴影，提升视觉层次
  - 流畅的悬停动画和交互反馈
  - 响应式设计，完美适配各种屏幕尺寸
- 📚 **交互式API文档页面**
  - 完整的RESTful API文档展示
  - 实时代码示例和参数说明
  - 一键复制功能，提升开发体验
  - 错误代码参考和状态码说明
- 🔬 **光谱分析界面**
  - 专业的化学光谱数据分析页面
  - 交互式图表和数据可视化
  - 支持多种光谱数据格式

### 改进
- 🕒 **超时时间优化**
  - 将前端 API 请求超时时间从 5 分钟增加到 10 分钟
  - 改善复杂分析任务的用户体验
  - 减少因处理时间较长导致的超时错误
- 🎯 **界面优化**
  - 移除首页不必要的交互式计数器组件
  - 简化页面布局，突出核心功能
  - 优化导航栏设计，增加滑动光效
  - 改进按钮和卡片的视觉效果
- 📱 **响应式设计增强**
  - 完善移动端样式适配
  - 优化小屏幕下的布局和交互
  - 改进触摸设备的用户体验

### 技术改进
- 🔧 **前端架构升级**
  - 从React迁移到SvelteKit，提升性能
  - 采用TypeScript增强代码质量
  - 使用Vite构建工具，加快开发速度
- 🎨 **样式系统重构**
  - 采用CSS3现代特性，减少依赖
  - 统一设计语言和组件规范
  - 优化CSS性能和加载速度

### 计划添加
- 支持更多化学数据库集成
- 增强的图像识别功能
- 多语言支持扩展
- 移动端PWA支持
- 离线模式支持
- 用户系统和权限管理

### 计划改进
- 优化响应速度和缓存机制
- 增强错误处理和用户反馈
- 完善测试覆盖率
- 添加性能监控和日志分析

## [1.0.0] - 2024-12-19

### 新增
- 🎉 **初始版本发布**
- 🤖 **智能问答系统**
  - 基于 GPT 模型的化学知识问答
  - 支持中英文问答
  - 多轮对话支持
  - 对话历史管理
- 🔍 **RAG 检索增强**
  - 集成 ChromaDB 向量数据库
  - 化学文献知识检索
  - 智能相关性排序
  - 来源引用显示
- 📷 **图像识别功能**
  - 化学结构式识别
  - 化学公式提取
  - 实验图片分析
  - 支持多种图片格式 (PNG, JPG, GIF, BMP)
  - 拖拽上传支持
- 🌐 **现代化 Web 界面**
  - React + TypeScript 前端
  - Material-UI 组件库
  - 响应式设计
  - 暗色主题支持
  - 实时消息流
- 🚀 **高性能后端**
  - FastAPI 框架
  - 异步处理
  - RESTful API 设计
  - 自动 API 文档生成
  - 请求验证和错误处理
- 🐳 **容器化部署**
  - Docker 支持
  - Docker Compose 配置
  - 多环境部署 (开发/生产)
  - Nginx 反向代理
  - Redis 缓存支持
- 📊 **监控和日志**
  - 结构化日志记录
  - 性能监控
  - 健康检查端点
  - 可选的 Prometheus + Grafana 监控
- 🛠 **开发工具**
  - 自动化安装脚本
  - 测试套件
  - 代码格式化
  - 文档生成
  - 部署脚本

### 技术栈

#### 后端
- **框架**: FastAPI 0.104.1
- **AI/ML**: 
  - OpenAI GPT API
  - LangChain 0.0.350
  - ChromaDB 0.4.18
  - OpenCV 4.8.1
- **数据库**: 
  - ChromaDB (向量数据库)
  - Redis (缓存)
- **其他**: 
  - Uvicorn (ASGI 服务器)
  - Pydantic (数据验证)
  - python-multipart (文件上传)

#### 前端
- **框架**: SvelteKit 1.20.4
- **语言**: TypeScript 5.0.0
- **构建工具**: Vite 4.4.2
- **HTTP 客户端**: Axios 1.10.0
- **样式**: CSS3 + 响应式设计
- **组件**: Svelte 4.0.5

#### 部署
- **容器化**: Docker, Docker Compose
- **Web 服务器**: Nginx
- **监控**: Prometheus, Grafana (可选)

### 项目结构
```
DarkChuang/
├── backend/                 # 后端服务
│   ├── app/                # FastAPI 应用
│   │   ├── api/           # API 路由
│   │   ├── core/          # 核心配置
│   │   ├── models/        # 数据模型
│   │   └── services/      # 业务服务
│   ├── requirements.txt   # Python 依赖
│   └── Dockerfile        # 后端 Docker 配置
├── frontend/               # 前端应用
│   ├── src/               # React 源码
│   │   ├── components/    # React 组件
│   │   └── services/      # 前端服务
│   ├── package.json      # Node.js 依赖
│   └── Dockerfile        # 前端 Docker 配置
├── data/                  # 数据文件
├── docs/                  # 项目文档
├── scripts/               # 项目脚本
└── docker-compose.yml     # Docker Compose 配置
```

### 主要功能模块

#### API 端点
- `POST /api/chat/send` - 发送消息
- `GET /api/chat/history/{conversation_id}` - 获取对话历史
- `GET /api/chat/conversations` - 列出所有对话
- `DELETE /api/chat/conversations/{conversation_id}` - 删除对话
- `POST /api/image/upload` - 上传图片
- `POST /api/image/analyze` - 分析图片
- `GET /api/image/{image_id}` - 获取图片信息
- `DELETE /api/image/{image_id}` - 删除图片
- `GET /api/health` - 健康检查
- `GET /api/health/ping` - 简单 ping

#### 前端页面
- `+page.svelte` - 首页组件
- `spectrum/+page.svelte` - 光谱分析页面
- `api-docs/+page.svelte` - API文档页面
- `app.html` - 应用模板
- `app.css` - 全局样式

#### 核心服务
- `RAGService` - 检索增强生成服务
- `LLMService` - 大语言模型服务
- `ImageService` - 图像处理服务

### 配置选项

#### 环境变量
- `OPENAI_API_KEY` - OpenAI API 密钥
- `OPENAI_MODEL` - 使用的模型名称
- `REDIS_URL` - Redis 连接地址
- `LOG_LEVEL` - 日志级别
- `DEBUG` - 调试模式

#### 功能开关
- RAG 检索可选启用/禁用
- 图像识别功能
- 对话历史保存
- 缓存机制

### 性能特性
- 异步处理提高并发性能
- Redis 缓存减少重复计算
- 向量数据库快速检索
- 前端组件懒加载
- 图片压缩和优化

### 安全特性
- API 密钥安全存储
- 文件上传大小限制
- 输入验证和清理
- CORS 配置
- 安全头设置

### 文档
- 用户手册
- 安装指南
- API 文档
- 开发者文档
- 常见问题解答

### 测试
- 单元测试
- 集成测试
- API 测试
- 前端测试
- 端到端测试

### 已知限制
- 需要 OpenAI API 密钥
- 图像识别准确性依赖于图片质量
- 大文件上传可能较慢
- 某些复杂化学结构识别可能不准确

### 兼容性
- **操作系统**: Windows, macOS, Linux
- **浏览器**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- **Python**: 3.8+
- **Node.js**: 16+

---

## 版本说明

### 版本号格式
本项目使用语义化版本号 `MAJOR.MINOR.PATCH`：

- **MAJOR**: 不兼容的 API 更改
- **MINOR**: 向后兼容的功能添加
- **PATCH**: 向后兼容的错误修复

### 更改类型
- **新增**: 新功能
- **更改**: 现有功能的更改
- **弃用**: 即将移除的功能
- **移除**: 已移除的功能
- **修复**: 错误修复
- **安全**: 安全相关的修复

### 发布周期
- **主要版本**: 根据需要发布
- **次要版本**: 每月发布
- **补丁版本**: 根据需要发布

---

## 贡献

感谢所有为这个项目做出贡献的开发者！

如果您想为项目做出贡献，请查看我们的 [贡献指南](CONTRIBUTING.md)。

## 支持

如果您遇到问题或有建议，请：

1. 查看 [常见问题](docs/user/faq.md)
2. 搜索现有的 [Issues](https://github.com/your-repo/issues)
3. 创建新的 Issue
4. 联系维护者

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。
# DarkChuang Frontend

基于 Svelte + SvelteKit 构建的化学光谱分析平台前端应用。

## 🚀 特性

- ⚡ **快速开发体验** - 基于 Vite 的极速热重载
- 🎯 **现代框架** - 使用 Svelte 4 和 SvelteKit 1.x
- 📱 **响应式设计** - 完美适配桌面端和移动端
- 🎨 **优雅UI** - 现代化的用户界面设计
- 🔧 **TypeScript 支持** - 完整的类型安全
- 📦 **组件化架构** - 可复用的组件系统

## 📋 功能模块

### 🏠 首页
- 平台介绍和功能展示
- 交互式分子动画
- 快速导航入口

### 📤 文件上传
- 拖拽上传支持
- 多文件批量上传
- 实时上传进度
- 支持格式：CSV, TXT, JSON, XLSX

### ℹ️ 关于页面
- 平台详细介绍
- 技术栈展示
- 使命和愿景

## 🛠️ 技术栈

- **框架**: Svelte 4 + SvelteKit 1.x
- **构建工具**: Vite 4
- **语言**: TypeScript
- **样式**: CSS3 + CSS Variables
- **HTTP客户端**: Axios
- **代码规范**: ESLint + Prettier

## 📦 安装和运行

### 环境要求
- Node.js 16.x 或更高版本
- npm 或 yarn

### 安装依赖
```bash
npm install
```

### 开发模式
```bash
npm run dev
```
应用将在 `http://localhost:5173` 启动

### 构建生产版本
```bash
npm run build
```

### 预览生产版本
```bash
npm run preview
```

### 代码检查
```bash
# 类型检查
npm run check

# 代码格式化
npm run format

# 代码检查
npm run lint
```

## 📁 项目结构

```
src/
├── lib/
│   └── components/          # 可复用组件
│       ├── Header.svelte    # 页面头部
│       ├── Footer.svelte    # 页面底部
│       ├── Welcome.svelte   # 欢迎动画
│       └── Counter.svelte   # 计数器示例
├── routes/                  # 页面路由
│   ├── +layout.svelte      # 根布局
│   ├── +page.svelte        # 首页
│   ├── about/              # 关于页面
│   │   └── +page.svelte
│   └── upload/             # 上传页面
│       └── +page.svelte
├── app.html                # HTML 模板
└── app.css                 # 全局样式
```

## 🎨 设计系统

### 颜色主题
- **主色调**: `#ff3e00` (Svelte Orange)
- **次要色**: `#4075a6` (Blue)
- **背景色**: 渐变背景
- **文本色**: `rgba(0, 0, 0, 0.7)`

### 组件特性
- 响应式设计
- 平滑动画过渡
- 无障碍访问支持
- 现代化交互体验

## 🔗 API 集成

前端通过 Axios 与后端 FastAPI 服务通信：

- **基础URL**: `http://localhost:8000`
- **上传接口**: `POST /api/upload`
- **文件格式**: multipart/form-data

## 📱 响应式支持

- **桌面端**: 1200px+
- **平板端**: 768px - 1199px
- **移动端**: < 768px

## 🚀 部署

### 静态部署
```bash
npm run build
# 将 build/ 目录部署到静态服务器
```

### Node.js 部署
```bash
npm run build
npm run preview
```

## 🤝 开发指南

### 添加新页面
1. 在 `src/routes/` 下创建新目录
2. 添加 `+page.svelte` 文件
3. 可选：添加 `+layout.svelte` 布局文件

### 创建新组件
1. 在 `src/lib/components/` 下创建 `.svelte` 文件
2. 导出组件供其他页面使用
3. 遵循命名约定和代码规范

### 样式规范
- 使用 CSS Variables 定义主题色彩
- 组件样式使用 `<style>` 标签
- 响应式设计使用媒体查询

## 📄 许可证

MIT License

## 🔗 相关链接

- [Svelte 官方文档](https://svelte.dev/)
- [SvelteKit 官方文档](https://kit.svelte.dev/)
- [Vite 官方文档](https://vitejs.dev/)
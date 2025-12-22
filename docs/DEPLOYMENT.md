# 化学问答机器人部署指南

本文档详细介绍如何部署化学问答机器人项目，包括开发环境和生产环境的部署方式。

## 目录

- [系统要求](#系统要求)
- [快速开始](#快速开始)
- [环境配置](#环境配置)
- [Docker部署](#docker部署)
- [生产环境部署](#生产环境部署)
- [监控和日志](#监控和日志)
- [故障排除](#故障排除)
- [维护和更新](#维护和更新)

## 系统要求

### 最低配置
- **CPU**: 2核心
- **内存**: 4GB RAM
- **存储**: 10GB 可用空间
- **操作系统**: Linux/Windows/macOS

### 推荐配置
- **CPU**: 4核心或更多
- **内存**: 8GB RAM 或更多
- **存储**: 20GB 可用空间
- **GPU**: 支持CUDA的显卡（可选，用于加速AI模型）

### 软件依赖
- Docker 20.10+
- Docker Compose 2.0+
- Git

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/qwe4559999/DarkChuang.git
cd DarkChuang
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量（必须配置 SiliconFlow API 密钥）
nano .env
```

**重要配置项：**
```env
# SiliconFlow API 配置 (核心)
SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
UNIFIED_MODEL_NAME=zai-org/GLM-4.6V

# RAG 配置
SILICONFLOW_EMBEDDING_MODEL=BAAI/bge-m3
```

### 3. 启动服务

#### 方式一：Docker Compose (推荐)
```bash
docker-compose up -d
```

#### 方式二：手动启动
**后端**
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**前端**
```bash
cd frontend
npm install
npm run dev
```

MAIN_MODEL_NAME=deepseek-ai/DeepSeek-R1-Distill-Qwen-32B

# 视觉模型
VISION_MODEL_NAME=Qwen/Qwen2.5-VL-72B-Instruct
```

### 3. 启动服务

```bash
# 开发环境（推荐用于测试）
docker-compose up -d

# 或使用部署脚本
python scripts/deploy.py --environment development
```

### 4. 验证部署

访问以下地址验证服务是否正常：

- **前端应用**: http://localhost:3000
- **后端API**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

## 环境配置

### 开发环境

开发环境适用于本地开发和测试：

```bash
# 启动开发环境
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 生产环境

生产环境包含完整的服务栈和监控：

```bash
# 启动生产环境（包含监控）
docker-compose --profile monitoring up -d

# 或使用部署脚本
python scripts/deploy.py --environment production
```

生产环境额外包含：
- Nginx反向代理
- Prometheus监控
- Grafana仪表板
- 自动备份

## Docker部署

### 服务架构

项目包含以下Docker服务：

1. **backend**: FastAPI后端服务
2. **frontend**: SvelteKit前端应用
3. **redis**: 缓存服务
4. **nginx**: 反向代理（生产环境）
5. **prometheus**: 监控服务（可选）
6. **grafana**: 监控仪表板（可选）

### 构建和启动

```bash
# 构建所有服务
docker-compose build

# 启动基础服务
docker-compose up -d backend frontend redis

# 启动所有服务（包含监控）
docker-compose --profile monitoring up -d
```

### 服务端口

| 服务 | 端口 | 描述 |
|------|------|------|
| Frontend | 3000 | 前端应用 |
| Backend | 8000 | 后端API |
| Redis | 6379 | 缓存服务 |
| Nginx | 80 | 反向代理 |
| Prometheus | 9090 | 监控服务 |
| Grafana | 3001 | 监控仪表板 |

## 生产环境部署

### 1. 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. 部署应用

```bash
# 克隆项目
git clone https://github.com/qwe4559999/DarkChuang.git
cd DarkChuang

# 配置生产环境变量
cp .env.example .env
nano .env

# 使用部署脚本
python scripts/deploy.py --environment production
```

### 3. 配置域名和SSL（可选）

如果有域名，可以配置SSL证书：

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取SSL证书
sudo certbot --nginx -d your-domain.com
```

### 4. 设置自动备份

```bash
# 创建备份脚本
sudo crontab -e

# 添加每日备份任务
0 2 * * * /path/to/DarkChuang/scripts/backup.sh
```

## 监控和日志

### Prometheus监控

访问 http://localhost:9090 查看Prometheus监控界面。

主要监控指标：
- 应用响应时间
- 请求成功率
- 系统资源使用
- 错误率统计

### Grafana仪表板

访问 http://localhost:3001 查看Grafana仪表板。

默认登录信息：
- 用户名: admin
- 密码: admin123（可在.env中修改）

### 日志查看

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend

# 查看最近的日志
docker-compose logs --tail=100 backend
```

## 故障排除

### 常见问题

#### 1. 服务启动失败

```bash
# 检查服务状态
docker-compose ps

# 查看错误日志
docker-compose logs backend

# 重启服务
docker-compose restart backend
```

#### 2. API密钥配置错误

确保在`.env`文件中正确配置了API密钥：

```env
SILICONFLOW_API_KEY=your_actual_api_key
```

#### 3. 端口冲突

如果端口被占用，可以修改`docker-compose.yml`中的端口映射：

```yaml
ports:
  - "8001:8000"  # 将8000改为8001
```

#### 4. 内存不足

```bash
# 检查系统资源
docker stats

# 清理未使用的镜像和容器
docker system prune -a
```

### 性能优化

#### 1. 调整容器资源限制

在`docker-compose.yml`中添加资源限制：

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
```

#### 2. 启用Redis缓存

确保Redis服务正常运行并在应用中启用缓存。

#### 3. 配置负载均衡

对于高并发场景，可以启动多个后端实例：

```bash
docker-compose up -d --scale backend=3
```

## 维护和更新

### 更新应用

```bash
# 拉取最新代码
git pull origin main

# 重新构建和部署
docker-compose build
docker-compose up -d
```

### 数据备份

```bash
# 手动备份
python scripts/backup.py

# 恢复备份
python scripts/restore.py --backup-file backup_20240101.tar.gz
```

### 清理和维护

```bash
# 清理未使用的Docker资源
docker system prune -a

# 查看磁盘使用
df -h
du -sh data/

# 清理日志文件
find backend/logs -name "*.log" -mtime +30 -delete
```

## 安全建议

1. **定期更新**: 保持Docker镜像和系统更新
2. **密钥管理**: 使用强密码和定期轮换API密钥
3. **网络安全**: 配置防火墙和限制访问
4. **备份策略**: 定期备份重要数据
5. **监控告警**: 设置监控告警机制

## 支持和帮助

如果遇到问题，可以：

1. 查看项目文档和FAQ
2. 检查GitHub Issues
3. 提交新的Issue报告问题
4. 联系项目维护者

---

**注意**: 首次部署前请确保已正确配置所有必要的环境变量，特别是API密钥配置。
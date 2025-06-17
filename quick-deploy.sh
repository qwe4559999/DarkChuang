#!/bin/bash

# 化学问答机器人快速部署脚本
# 适用于Linux/macOS系统

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 检查Docker
check_docker() {
    print_info "检查Docker安装..."
    if ! command_exists docker; then
        print_error "Docker未安装，请先安装Docker"
        echo "安装指南: https://docs.docker.com/get-docker/"
        exit 1
    fi
    
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker服务未运行，请启动Docker服务"
        exit 1
    fi
    
    print_success "Docker检查通过"
}

# 检查Docker Compose
check_docker_compose() {
    print_info "检查Docker Compose安装..."
    if ! command_exists docker-compose && ! docker compose version >/dev/null 2>&1; then
        print_error "Docker Compose未安装，请先安装Docker Compose"
        echo "安装指南: https://docs.docker.com/compose/install/"
        exit 1
    fi
    print_success "Docker Compose检查通过"
}

# 检查环境文件
check_env_file() {
    print_info "检查环境配置文件..."
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            print_warning "未找到.env文件，正在从.env.example创建..."
            cp .env.example .env
            print_warning "请编辑.env文件并配置必要的API密钥"
            print_warning "特别是SILICONFLOW_API_KEY配置项"
        else
            print_error "未找到.env.example文件"
            exit 1
        fi
    else
        print_success "环境配置文件存在"
    fi
}

# 检查API密钥配置
check_api_key() {
    print_info "检查API密钥配置..."
    if grep -q "your_api_key_here" .env || ! grep -q "SILICONFLOW_API_KEY=" .env; then
        print_warning "请在.env文件中配置正确的SILICONFLOW_API_KEY"
        print_warning "当前配置可能不完整，部署后可能无法正常使用AI功能"
        read -p "是否继续部署？(y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "部署已取消，请配置API密钥后重试"
            exit 0
        fi
    else
        print_success "API密钥配置检查通过"
    fi
}

# 构建和启动服务
deploy_services() {
    print_info "开始构建和部署服务..."
    
    # 停止现有服务
    print_info "停止现有服务..."
    docker-compose down 2>/dev/null || true
    
    # 构建镜像
    print_info "构建Docker镜像..."
    docker-compose build
    
    # 启动服务
    print_info "启动服务..."
    docker-compose up -d
    
    print_success "服务部署完成"
}

# 等待服务启动
wait_for_services() {
    print_info "等待服务启动..."
    
    # 等待后端服务
    print_info "等待后端服务启动..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            print_success "后端服务已启动"
            break
        fi
        if [ $i -eq 30 ]; then
            print_warning "后端服务启动超时，请检查日志"
        fi
        sleep 2
    done
    
    # 等待前端服务
    print_info "等待前端服务启动..."
    for i in {1..30}; do
        if curl -s http://localhost:3000 >/dev/null 2>&1; then
            print_success "前端服务已启动"
            break
        fi
        if [ $i -eq 30 ]; then
            print_warning "前端服务启动超时，请检查日志"
        fi
        sleep 2
    done
}

# 显示部署结果
show_deployment_info() {
    echo
    print_success "=== 部署完成 ==="
    echo
    echo "服务访问地址:"
    echo "  前端应用:    http://localhost:3000"
    echo "  后端API:     http://localhost:8000"
    echo "  API文档:     http://localhost:8000/docs"
    echo "  健康检查:    http://localhost:8000/health"
    echo
    echo "常用命令:"
    echo "  查看日志:    docker-compose logs -f"
    echo "  停止服务:    docker-compose down"
    echo "  重启服务:    docker-compose restart"
    echo "  查看状态:    docker-compose ps"
    echo
    print_info "如需启用监控服务，请运行:"
    echo "  docker-compose --profile monitoring up -d"
    echo
}

# 主函数
main() {
    echo "=== 化学问答机器人快速部署脚本 ==="
    echo
    
    # 检查前提条件
    check_docker
    check_docker_compose
    check_env_file
    check_api_key
    
    # 部署服务
    deploy_services
    
    # 等待服务启动
    wait_for_services
    
    # 显示部署信息
    show_deployment_info
}

# 运行主函数
main "$@"
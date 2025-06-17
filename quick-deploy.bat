@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM 化学问答机器人快速部署脚本 (Windows版本)

echo ===== 化学问答机器人快速部署脚本 =====
echo.

REM 检查Docker
echo [INFO] 检查Docker安装...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker未安装，请先安装Docker Desktop
    echo 下载地址: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM 检查Docker服务
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker服务未运行，请启动Docker Desktop
    pause
    exit /b 1
)
echo [SUCCESS] Docker检查通过

REM 检查Docker Compose
echo [INFO] 检查Docker Compose安装...
docker-compose --version >nul 2>&1
if errorlevel 1 (
    docker compose version >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Docker Compose未安装
        pause
        exit /b 1
    )
)
echo [SUCCESS] Docker Compose检查通过

REM 检查环境文件
echo [INFO] 检查环境配置文件...
if not exist ".env" (
    if exist ".env.example" (
        echo [WARNING] 未找到.env文件，正在从.env.example创建...
        copy ".env.example" ".env" >nul
        echo [WARNING] 请编辑.env文件并配置必要的API密钥
        echo [WARNING] 特别是SILICONFLOW_API_KEY配置项
    ) else (
        echo [ERROR] 未找到.env.example文件
        pause
        exit /b 1
    )
) else (
    echo [SUCCESS] 环境配置文件存在
)

REM 检查API密钥配置
echo [INFO] 检查API密钥配置...
findstr /C:"your_api_key_here" .env >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] 请在.env文件中配置正确的SILICONFLOW_API_KEY
    echo [WARNING] 当前配置可能不完整，部署后可能无法正常使用AI功能
    set /p "continue=是否继续部署？(y/N): "
    if /i not "!continue!"=="y" (
        echo [INFO] 部署已取消，请配置API密钥后重试
        pause
        exit /b 0
    )
) else (
    findstr /C:"SILICONFLOW_API_KEY=" .env >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] 未找到SILICONFLOW_API_KEY配置
        set /p "continue=是否继续部署？(y/N): "
        if /i not "!continue!"=="y" (
            echo [INFO] 部署已取消，请配置API密钥后重试
            pause
            exit /b 0
        )
    ) else (
        echo [SUCCESS] API密钥配置检查通过
    )
)

REM 停止现有服务
echo [INFO] 停止现有服务...
docker-compose down >nul 2>&1

REM 构建镜像
echo [INFO] 构建Docker镜像...
docker-compose build
if errorlevel 1 (
    echo [ERROR] 镜像构建失败
    pause
    exit /b 1
)

REM 启动服务
echo [INFO] 启动服务...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] 服务启动失败
    pause
    exit /b 1
)
echo [SUCCESS] 服务部署完成

REM 等待服务启动
echo [INFO] 等待服务启动...
set /a count=0
:wait_backend
set /a count+=1
if %count% gtr 30 (
    echo [WARNING] 后端服务启动超时，请检查日志
    goto wait_frontend
)
curl -s http://localhost:8000/health >nul 2>&1
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    goto wait_backend
)
echo [SUCCESS] 后端服务已启动

:wait_frontend
set /a count=0
:wait_frontend_loop
set /a count+=1
if %count% gtr 30 (
    echo [WARNING] 前端服务启动超时，请检查日志
    goto show_info
)
curl -s http://localhost:3000 >nul 2>&1
if errorlevel 1 (
    timeout /t 2 /nobreak >nul
    goto wait_frontend_loop
)
echo [SUCCESS] 前端服务已启动

:show_info
echo.
echo [SUCCESS] === 部署完成 ===
echo.
echo 服务访问地址:
echo   前端应用:    http://localhost:3000
echo   后端API:     http://localhost:8000
echo   API文档:     http://localhost:8000/docs
echo   健康检查:    http://localhost:8000/health
echo.
echo 常用命令:
echo   查看日志:    docker-compose logs -f
echo   停止服务:    docker-compose down
echo   重启服务:    docker-compose restart
echo   查看状态:    docker-compose ps
echo.
echo [INFO] 如需启用监控服务，请运行:
echo   docker-compose --profile monitoring up -d
echo.
echo 按任意键退出...
pause >nul
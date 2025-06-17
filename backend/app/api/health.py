from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from app.core.config import settings
import psutil
import os

router = APIRouter()

class HealthResponse(BaseModel):
    """健康检查响应模型"""
    status: str
    timestamp: datetime
    version: str
    uptime: float
    system_info: dict

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    
    # 获取系统信息
    system_info = {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
        "python_version": f"{psutil.version_info[0]}.{psutil.version_info[1]}.{psutil.version_info[2]}"
    }
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        version=settings.VERSION,
        uptime=psutil.boot_time(),
        system_info=system_info
    )

@router.get("/ping")
async def ping():
    """简单的ping接口"""
    return {"message": "pong"}
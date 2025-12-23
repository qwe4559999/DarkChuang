from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import chat, health, chemistry, knowledge, upload
from app.api.v1 import spectrum
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.base import engine, Base
from app.models import sql_models
import os

# 设置 Hugging Face 镜像 (针对国内网络环境)
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 设置日志
setup_logging()

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="Chemistry QA Bot API",
    description="基于RAG技术的化学问答机器人API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保上传目录存在
os.makedirs("data/uploads", exist_ok=True)
# 确保静态目录存在
os.makedirs("static", exist_ok=True)

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="data/uploads"), name="uploads")

# 注册路由
app.include_router(health.router, prefix="/api/v1", tags=["健康检查"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["问答聊天"])
app.include_router(upload.router, prefix="/api/v1", tags=["文件上传"])
app.include_router(spectrum.router, prefix="/api/v1", tags=["光谱分析"])
app.include_router(chemistry.router, prefix="/api/v1/chemistry", tags=["化学工具"])
app.include_router(knowledge.router, prefix="/api/v1", tags=["知识库管理"])

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "Chemistry QA Bot API",
        "version": "1.0.0",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
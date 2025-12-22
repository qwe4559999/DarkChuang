from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import chat, health, chemistry
from app.api.v1 import spectrum
from app.core.config import settings
from app.core.logging import setup_logging

# 设置日志
setup_logging()

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

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(health.router, prefix="/api/v1", tags=["健康检查"])
app.include_router(chat.router, prefix="/api/v1", tags=["问答聊天"])
app.include_router(spectrum.router, prefix="/api/v1", tags=["光谱分析"])
app.include_router(chemistry.router, prefix="/api/v1/chemistry", tags=["化学工具"])

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
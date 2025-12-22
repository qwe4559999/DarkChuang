import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置"""
    
    # 基本配置
    APP_NAME: str = "Chemistry QA Bot"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_HOSTS: List[str] = ["*"]
    

    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./chemistry_bot.db"
    
    # RAG配置
    EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    VECTOR_DB_PATH: str = "./data/vector_db"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    # LLM配置
    LLM_MODEL: str = "chatglm3-6b"  # 或者使用OpenAI API
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    
    # 多模型配置
    LLM_API_KEY: str = ""  # DeepSeek-R1 API Key
    LLM_BASE_URL: str = "https://api.deepseek.com/v1"  # DeepSeek-R1 API URL
    LLM_MODEL: str = "deepseek-ai/DeepSeek-R1"  # DeepSeek模型名称
    
    # 视觉模型配置
    VISION_API_KEY: str = ""  # Qwen2.5-VL API Key
    VISION_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # Qwen2.5-VL API URL
    VISION_MODEL: str = "Qwen/Qwen2.5-VL-72B-Instruct"  # 视觉模型名称
    
    # 图像识别配置
    OCR_MODEL_PATH: str = "./models/paddleocr"
    IMAGE_RECOGNITION_MODEL_PATH: str = "./models/image_recognition"
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/gif"]
    
    # 文件上传配置
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/app.log"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # SiliconFlow 配置
    SILICONFLOW_API_KEY: str = ""
    SILICONFLOW_API_BASE: str = "https://api.siliconflow.cn/v1"

    # 单一全能模型配置 (GLM-4.6V)
    # 用户指定模型: zai-org/GLM-4.6V
    UNIFIED_MODEL_NAME: str = "zai-org/GLM-4.6V"


    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

# 创建全局设置实例
settings = Settings()

# 确保必要的目录存在
os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.VECTOR_DB_PATH, exist_ok=True)
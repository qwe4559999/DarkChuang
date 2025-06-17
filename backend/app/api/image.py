from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import aiofiles
import os
from app.services.image_service import ImageService
from app.core.config import settings
from loguru import logger
import uuid

router = APIRouter()

class ImageAnalysisResult(BaseModel):
    """图像分析结果模型"""
    text_content: str
    chemical_formulas: List[str]
    chemical_structures: List[dict]
    confidence_scores: dict
    processing_time: float
    timestamp: datetime = datetime.now()

class ImageUploadResponse(BaseModel):
    """图像上传响应模型"""
    file_id: str
    filename: str
    file_size: int
    upload_time: datetime = datetime.now()
    analysis_result: Optional[ImageAnalysisResult] = None

# 依赖注入
def get_image_service() -> ImageService:
    return ImageService()

def validate_image_file(file: UploadFile) -> bool:
    """验证图像文件"""
    # 检查文件类型
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}. 支持的类型: {settings.ALLOWED_IMAGE_TYPES}"
        )
    
    # 检查文件大小（这里只能检查声明的大小，实际大小需要在读取时检查）
    return True

@router.post("/upload-image", response_model=ImageUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    analyze: bool = True,
    image_service: ImageService = Depends(get_image_service)
):
    """上传并分析图像"""
    start_time = datetime.now()
    
    try:
        # 验证文件
        validate_image_file(file)
        
        # 生成唯一文件ID
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1]
        saved_filename = f"{file_id}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIR, saved_filename)
        
        # 读取文件内容并检查大小
        file_content = await file.read()
        if len(file_content) > settings.MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"文件大小超过限制: {len(file_content)} bytes > {settings.MAX_IMAGE_SIZE} bytes"
            )
        
        # 保存文件
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(file_content)
        
        logger.info(f"图像文件已保存: {file_path}")
        
        analysis_result = None
        if analyze:
            # 分析图像
            logger.info(f"开始分析图像: {file_id}")
            analysis_result = await image_service.analyze_image(file_path)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            analysis_result.processing_time = processing_time
            
            logger.info(f"图像分析完成，耗时: {processing_time:.2f}秒")
        
        return ImageUploadResponse(
            file_id=file_id,
            filename=file.filename,
            file_size=len(file_content),
            analysis_result=analysis_result
        )
        
    except Exception as e:
        logger.error(f"图像上传处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理图像时发生错误: {str(e)}")

@router.post("/analyze-image/{file_id}", response_model=ImageAnalysisResult)
async def analyze_uploaded_image(
    file_id: str,
    image_service: ImageService = Depends(get_image_service)
):
    """分析已上传的图像"""
    start_time = datetime.now()
    
    try:
        # 查找文件
        file_path = None
        for ext in ['.jpg', '.jpeg', '.png', '.gif']:
            potential_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")
            if os.path.exists(potential_path):
                file_path = potential_path
                break
        
        if not file_path:
            raise HTTPException(status_code=404, detail=f"未找到文件: {file_id}")
        
        logger.info(f"开始分析图像: {file_id}")
        
        # 分析图像
        result = await image_service.analyze_image(file_path)
        
        processing_time = (datetime.now() - start_time).total_seconds()
        result.processing_time = processing_time
        
        logger.info(f"图像分析完成，耗时: {processing_time:.2f}秒")
        
        return result
        
    except Exception as e:
        logger.error(f"图像分析失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析图像时发生错误: {str(e)}")

@router.get("/image/{file_id}")
async def get_image_info(file_id: str):
    """获取图像信息"""
    try:
        # 查找文件
        file_path = None
        for ext in ['.jpg', '.jpeg', '.png', '.gif']:
            potential_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")
            if os.path.exists(potential_path):
                file_path = potential_path
                break
        
        if not file_path:
            raise HTTPException(status_code=404, detail=f"未找到文件: {file_id}")
        
        # 获取文件信息
        file_stat = os.stat(file_path)
        
        return {
            "file_id": file_id,
            "file_path": file_path,
            "file_size": file_stat.st_size,
            "created_time": datetime.fromtimestamp(file_stat.st_ctime),
            "modified_time": datetime.fromtimestamp(file_stat.st_mtime)
        }
        
    except Exception as e:
        logger.error(f"获取图像信息失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取图像信息时发生错误: {str(e)}")

@router.delete("/image/{file_id}")
async def delete_image(file_id: str):
    """删除图像文件"""
    try:
        # 查找并删除文件
        deleted = False
        for ext in ['.jpg', '.jpeg', '.png', '.gif']:
            potential_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}{ext}")
            if os.path.exists(potential_path):
                os.remove(potential_path)
                deleted = True
                logger.info(f"已删除图像文件: {potential_path}")
                break
        
        if not deleted:
            raise HTTPException(status_code=404, detail=f"未找到文件: {file_id}")
        
        return {"message": f"文件 {file_id} 已成功删除"}
        
    except Exception as e:
        logger.error(f"删除图像失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"删除图像时发生错误: {str(e)}")
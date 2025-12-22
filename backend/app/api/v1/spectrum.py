from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
from pathlib import Path
import os
import uuid
from loguru import logger

from app.services.spectrum_service import SpectrumAnalysisService
from app.core.config import settings
from app.schemas.spectrum import (
    SpectrumAnalysisRequest,
    SpectrumAnalysisResponse,
    BatchSpectrumAnalysisRequest,
    BatchSpectrumAnalysisResponse,
    SupportedTypesResponse
)

router = APIRouter(prefix="/spectrum", tags=["spectrum"])

# 创建图像服务实例
image_service = SpectrumAnalysisService()

@router.post("/analyze", response_model=SpectrumAnalysisResponse)
async def analyze_spectrum(
    file: UploadFile = File(...),
    spectrum_type: str = Form("auto"),
    additional_info: Optional[str] = Form(None)
):
    """
    分析单个光谱图像

    Args:
        file: 上传的光谱图像文件
        spectrum_type: 光谱类型 (auto为自动识别, 或指定IR, NMR, UV, 红外, 核磁, 紫外等)
        additional_info: 额外的上下文信息

    Returns:
        光谱分析结果
    """
    try:
        logger.info(f"接收到光谱分析请求: {spectrum_type}")

        # 验证文件类型
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="只支持图像文件"
            )

        # 验证光谱类型（允许auto自动识别）
        if spectrum_type.lower() != "auto":
            supported_types = image_service.get_supported_spectrum_types()
            if spectrum_type.upper() not in [t.upper() for t in supported_types]:
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的光谱类型: {spectrum_type}。支持的类型: auto(自动识别), {', '.join(supported_types)}"
                )

        # 保存上传的文件
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)

        file_extension = Path(file.filename).suffix
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = upload_dir / unique_filename

        # 写入文件
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        logger.info(f"文件已保存: {file_path}")

        # 进行光谱分析
        analysis_result = await image_service.analyze_spectrum(
            image_path=str(file_path),
            spectrum_type=spectrum_type,
            additional_info=additional_info
        )

        # 清理临时文件
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"清理临时文件失败: {str(e)}")

        if not analysis_result['success']:
            raise HTTPException(
                status_code=500,
                detail=f"光谱分析失败: {analysis_result.get('error', '未知错误')}"
            )

        # 处理 image_quality，防止空字典导致的验证错误
        img_quality = analysis_result.get('image_quality')
        if img_quality == {}:
            img_quality = None

        return SpectrumAnalysisResponse(
            success=True,
            spectrum_type=spectrum_type,
            analysis_result=analysis_result['parsed_result'],
            raw_analysis=analysis_result['raw_analysis'],
            image_quality=img_quality,
            message="光谱分析完成"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"光谱分析API错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.post("/batch-analyze", response_model=BatchSpectrumAnalysisResponse)
async def batch_analyze_spectrum(
    files: List[UploadFile] = File(...),
    spectrum_types: List[str] = Form(...),
    additional_info: Optional[str] = Form(None)
):
    """
    批量分析多个光谱图像
    
    Args:
        files: 上传的光谱图像文件列表
        spectrum_types: 对应的光谱类型列表
        additional_info: 额外的上下文信息
    
    Returns:
        批量光谱分析结果
    """
    try:
        logger.info(f"接收到批量光谱分析请求: {len(files)}个文件")
        
        # 验证输入
        if len(files) != len(spectrum_types):
            raise HTTPException(
                status_code=400,
                detail="文件数量与光谱类型数量不匹配"
            )
        
        if len(files) > 10:  # 限制批量处理数量
            raise HTTPException(
                status_code=400,
                detail="批量处理最多支持10个文件"
            )
        
        # 验证所有文件类型
        for file in files:
            if not file.content_type.startswith('image/'):
                raise HTTPException(
                    status_code=400,
                    detail=f"文件 {file.filename} 不是图像文件"
                )
        
        # 验证所有光谱类型
        supported_types = image_service.get_supported_spectrum_types()
        for spectrum_type in spectrum_types:
            if spectrum_type.upper() not in [t.upper() for t in supported_types]:
                raise HTTPException(
                    status_code=400,
                    detail=f"不支持的光谱类型: {spectrum_type}"
                )
        
        # 保存所有上传的文件
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)
        
        file_paths = []
        try:
            for file in files:
                file_extension = Path(file.filename).suffix
                unique_filename = f"{uuid.uuid4()}{file_extension}"
                file_path = upload_dir / unique_filename

                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)

                file_paths.append(str(file_path))

            logger.info(f"批量文件已保存: {len(file_paths)}个")

            # 进行批量光谱分析
            batch_result = await image_service.batch_analyze_spectra(
                image_paths=file_paths,
                spectrum_types=spectrum_types,
                additional_info=additional_info
            )

            if not batch_result['success']:
                raise HTTPException(
                    status_code=500,
                    detail=f"批量光谱分析失败: {batch_result.get('error', '未知错误')}"
                )

            return BatchSpectrumAnalysisResponse(
                success=True,
                total_count=batch_result['total_count'],
                success_count=batch_result['success_count'],
                results=batch_result['batch_results'],
                message="批量光谱分析完成"
            )

        finally:
            # 清理所有临时文件
            for file_path in file_paths:
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except Exception as e:
                    logger.warning(f"清理临时文件失败 {file_path}: {str(e)}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量光谱分析API错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.get("/supported-types", response_model=SupportedTypesResponse)
async def get_supported_types():
    """
    获取支持的光谱类型列表
    
    Returns:
        支持的光谱类型列表
    """
    try:
        spectrum_types = image_service.get_supported_spectrum_types()
        image_formats = image_service.get_supported_formats()
        
        return SupportedTypesResponse(
            spectrum_types=spectrum_types,
            image_formats=image_formats,
            max_file_size_mb=10,  # 10MB限制
            max_batch_size=10     # 最多10个文件批量处理
        )
    except Exception as e:
        logger.error(f"获取支持类型API错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.post("/visualize-result")
async def visualize_analysis_result(
    analysis_data: dict
):
    """
    将分析结果进行可视化格式化

    Args:
        analysis_data: 包含分析结果的JSON数据

    Returns:
        格式化后的可视化分析结果
    """
    try:
        logger.info("接收到分析结果可视化请求")

        # 使用图像服务来格式化分析结果
        visualization_result = await image_service.format_analysis_for_visualization(analysis_data)

        # 处理返回结果，确保它是字典格式
        if isinstance(visualization_result, dict) and 'visualization' not in visualization_result:
            # 如果返回的是直接的可视化数据，包装一下
            visualization_result = {
                'success': True,
                'visualization': visualization_result
            }
        elif isinstance(visualization_result, dict) and 'visualization' in visualization_result:
             # 已经是正确的格式
             visualization_result['success'] = True
        else:
             # 其他情况，作为可视化内容
             visualization_result = {
                'success': True,
                'visualization': visualization_result
             }

        return JSONResponse(content={
            "success": True,
            "visualization": visualization_result['visualization'],
            "message": "分析结果可视化完成"
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"分析结果可视化API错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"服务器内部错误: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    健康检查端点
    
    Returns:
        服务状态信息
    """
    try:
        # 检查服务状态
        status = {
            "status": "healthy",
            "service": "spectrum_analysis",
            "supported_types": len(image_service.get_supported_spectrum_types()),
            "supported_formats": len(image_service.get_supported_formats())
        }
        
        return JSONResponse(content=status)
        
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )
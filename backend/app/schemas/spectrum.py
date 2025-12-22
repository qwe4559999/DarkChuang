from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class SpectrumAnalysisRequest(BaseModel):
    """
    光谱分析请求模型
    """
    spectrum_type: str = Field(..., description="光谱类型 (IR, NMR, UV, 红外, 核磁, 紫外)")
    additional_info: Optional[str] = Field(None, description="额外的上下文信息")
    
    class Config:
        schema_extra = {
            "example": {
                "spectrum_type": "IR",
                "additional_info": "这是一个有机化合物的红外光谱"
            }
        }

class ImageQuality(BaseModel):
    """
    图像质量评估结果
    """
    quality_score: Optional[float] = Field(None, description="质量评分 (0.0-1.0)")
    issues: List[str] = Field(default_factory=list, description="发现的问题列表")
    metrics: Dict[str, Any] = Field(default_factory=dict, description="质量指标")

class KeyFinding(BaseModel):
    """
    关键发现
    """
    type: str = Field(..., description="发现类型")
    content: List[str] = Field(..., description="发现内容")

class ParsedAnalysisResult(BaseModel):
    """
    解析后的分析结果
    """
    spectrum_type: str = Field(..., description="光谱类型")
    analysis_sections: Dict[str, List[str]] = Field(default_factory=dict, description="分析章节")
    key_findings: List[KeyFinding] = Field(default_factory=list, description="关键发现")
    confidence_level: str = Field(default="medium", description="置信度级别")

class SpectrumAnalysisResponse(BaseModel):
    """
    光谱分析响应模型
    """
    success: bool = Field(..., description="分析是否成功")
    spectrum_type: str = Field(..., description="光谱类型")
    analysis_result: Optional[ParsedAnalysisResult] = Field(None, description="解析后的分析结果")
    raw_analysis: Optional[str] = Field(None, description="原始分析文本")
    image_quality: Optional[ImageQuality] = Field(None, description="图像质量评估")
    message: str = Field(..., description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="分析时间")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "spectrum_type": "IR",
                "analysis_result": {
                    "spectrum_type": "IR",
                    "analysis_sections": {
                        "基本信息": ["这是一个红外光谱图"],
                        "特征峰分析": ["3000-3500 cm⁻¹区域显示O-H伸缩振动"]
                    },
                    "key_findings": [
                        {
                            "type": "functional_groups",
                            "content": ["O-H", "C=O"]
                        }
                    ],
                    "confidence_level": "high"
                },
                "raw_analysis": "详细的光谱分析文本...",
                "image_quality": {
                    "quality_score": 0.85,
                    "issues": [],
                    "metrics": {
                        "width": 800,
                        "height": 600,
                        "sharpness": 150.5,
                        "brightness": 128.3,
                        "contrast": 45.2
                    }
                },
                "message": "光谱分析完成",
                "timestamp": "2024-01-01T12:00:00"
            }
        }

class BatchSpectrumAnalysisRequest(BaseModel):
    """
    批量光谱分析请求模型
    """
    spectrum_types: List[str] = Field(..., description="光谱类型列表")
    additional_info: Optional[str] = Field(None, description="额外的上下文信息")
    
    class Config:
        schema_extra = {
            "example": {
                "spectrum_types": ["IR", "NMR", "UV"],
                "additional_info": "这些是同一化合物的不同光谱"
            }
        }

class BatchAnalysisResult(BaseModel):
    """
    单个批量分析结果
    """
    success: bool = Field(..., description="分析是否成功")
    spectrum_type: str = Field(..., description="光谱类型")
    raw_analysis: Optional[str] = Field(None, description="原始分析文本")
    parsed_result: Optional[ParsedAnalysisResult] = Field(None, description="解析后的结果")
    image_path: str = Field(..., description="图像路径")
    error: Optional[str] = Field(None, description="错误信息")

class BatchSpectrumAnalysisResponse(BaseModel):
    """
    批量光谱分析响应模型
    """
    success: bool = Field(..., description="批量分析是否成功")
    total_count: int = Field(..., description="总文件数")
    success_count: int = Field(..., description="成功分析的文件数")
    results: List[BatchAnalysisResult] = Field(..., description="各个文件的分析结果")
    message: str = Field(..., description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="分析时间")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "total_count": 3,
                "success_count": 3,
                "results": [
                    {
                        "success": True,
                        "spectrum_type": "IR",
                        "raw_analysis": "红外光谱分析结果...",
                        "parsed_result": {
                            "spectrum_type": "IR",
                            "analysis_sections": {},
                            "key_findings": [],
                            "confidence_level": "high"
                        },
                        "image_path": "/path/to/image1.jpg"
                    }
                ],
                "message": "批量光谱分析完成",
                "timestamp": "2024-01-01T12:00:00"
            }
        }

class SupportedTypesResponse(BaseModel):
    """
    支持的类型响应模型
    """
    spectrum_types: List[str] = Field(..., description="支持的光谱类型")
    image_formats: List[str] = Field(..., description="支持的图像格式")
    max_file_size_mb: int = Field(..., description="最大文件大小(MB)")
    max_batch_size: int = Field(..., description="最大批量处理数量")
    
    class Config:
        schema_extra = {
            "example": {
                "spectrum_types": ["IR", "NMR", "UV", "红外", "核磁", "紫外"],
                "image_formats": [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"],
                "max_file_size_mb": 10,
                "max_batch_size": 10
            }
        }

class SpectrumErrorResponse(BaseModel):
    """
    光谱分析错误响应模型
    """
    success: bool = Field(False, description="分析是否成功")
    error: str = Field(..., description="错误信息")
    error_code: Optional[str] = Field(None, description="错误代码")
    timestamp: datetime = Field(default_factory=datetime.now, description="错误时间")
    
    class Config:
        schema_extra = {
            "example": {
                "success": False,
                "error": "不支持的光谱类型",
                "error_code": "UNSUPPORTED_SPECTRUM_TYPE",
                "timestamp": "2024-01-01T12:00:00"
            }
        }

class SpectrumAnalysisStats(BaseModel):
    """
    光谱分析统计信息
    """
    total_analyses: int = Field(..., description="总分析次数")
    successful_analyses: int = Field(..., description="成功分析次数")
    failed_analyses: int = Field(..., description="失败分析次数")
    spectrum_type_distribution: Dict[str, int] = Field(..., description="光谱类型分布")
    average_processing_time: float = Field(..., description="平均处理时间(秒)")
    
    class Config:
        schema_extra = {
            "example": {
                "total_analyses": 150,
                "successful_analyses": 142,
                "failed_analyses": 8,
                "spectrum_type_distribution": {
                    "IR": 80,
                    "NMR": 45,
                    "UV": 25
                },
                "average_processing_time": 12.5
            }
        }
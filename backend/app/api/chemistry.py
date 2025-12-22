from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.services.chemistry_service import ChemistryService
from loguru import logger

router = APIRouter()

class PropertyRequest(BaseModel):
    molecule: str  # SMILES or name

class ImageRequest(BaseModel):
    molecule: str
    width: Optional[int] = 400
    height: Optional[int] = 400

# 依赖注入
def get_chemistry_service() -> ChemistryService:
    return ChemistryService()

@router.post("/calculate-properties")
async def calculate_properties(
    request: PropertyRequest,
    service: ChemistryService = Depends(get_chemistry_service)
):
    """计算分子属性"""
    try:
        result = await service.calculate_properties(request.molecule)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        logger.error(f"属性计算API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/structure-image")
async def generate_structure_image(
    request: ImageRequest,
    service: ChemistryService = Depends(get_chemistry_service)
):
    """生成分子结构图"""
    try:
        result = await service.generate_structure_image(
            request.molecule,
            request.width,
            request.height
        )
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        logger.error(f"结构图生成API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/structure-3d")
async def generate_3d_structure(
    request: PropertyRequest,
    service: ChemistryService = Depends(get_chemistry_service)
):
    """生成分子3D结构数据 (SDF)"""
    try:
        result = await service.generate_3d_structure(request.molecule)
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        logger.error(f"3D结构生成API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"结构图生成API错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

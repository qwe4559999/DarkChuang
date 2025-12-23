from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
from pathlib import Path
import os
import shutil
import uuid
from loguru import logger
from app.services.rag_service import RAGService
from app.core.config import settings

from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.sql_models import KnowledgeFile

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

def get_rag_service() -> RAGService:
    return RAGService()

@router.get("/files", response_model=List[Dict[str, Any]])
async def list_files(db: Session = Depends(get_db)):
    """列出知识库中的所有文件"""
    files = db.query(KnowledgeFile).order_by(KnowledgeFile.upload_time.desc()).all()
    return [
        {
            "id": f.id,
            "filename": f.filename,
            "size": f.file_size,
            "upload_time": f.upload_time,
            "status": f.status,
            "error": f.error_message
        }
        for f in files
    ]

@router.delete("/files/{file_id}")
async def delete_file(file_id: int, db: Session = Depends(get_db)):
    """删除文件"""
    file_record = db.query(KnowledgeFile).filter(KnowledgeFile.id == file_id).first()
    if not file_record:
        raise HTTPException(status_code=404, detail="File not found")
    
    # 删除物理文件
    try:
        if os.path.exists(file_record.file_path):
            os.remove(file_record.file_path)
    except Exception as e:
        logger.error(f"Failed to delete file {file_record.file_path}: {e}")

    # TODO: 从向量数据库中删除对应的向量 (需要 RAGService 支持)
    
    db.delete(file_record)
    db.commit()
    return {"success": True, "message": "File deleted"}

@router.post("/reset")
async def reset_knowledge_base(
    rag_service: RAGService = Depends(get_rag_service),
    db: Session = Depends(get_db)
):
    """重置知识库（清空向量库和文件记录）"""
    # 1. 清空向量库
    success = await rag_service.clear_database()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to clear vector database")
    
    # 2. 清空数据库记录
    db.query(KnowledgeFile).delete()
    db.commit()
    
    # 3. 清空物理文件
    upload_dir = Path(settings.UPLOAD_DIR) / "knowledge_base"
    if upload_dir.exists():
        for item in upload_dir.iterdir():
            if item.is_file():
                try:
                    item.unlink()
                except Exception as e:
                    logger.error(f"Failed to delete file {item}: {e}")

    return {"success": True, "message": "Knowledge base reset successfully"}

@router.get("/stats")
async def get_knowledge_stats(
    rag_service: RAGService = Depends(get_rag_service)
):
    """获取知识库统计信息（直接来自向量库）"""
    return await rag_service.get_database_stats()

@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    rag_service: RAGService = Depends(get_rag_service),
    db: Session = Depends(get_db)
):
    """
    上传文档到知识库

    Args:
        files: 上传的文件列表 (PDF, TXT, MD)

    Returns:
        上传结果
    """
    try:
        logger.info(f"接收到 {len(files)} 个文档上传请求")

        # 确保上传目录存在
        upload_dir = Path(settings.UPLOAD_DIR) / "knowledge_base"
        upload_dir.mkdir(parents=True, exist_ok=True)

        saved_files_info = []

        for file in files:
            # 检查文件类型
            ext = Path(file.filename).suffix.lower()
            if ext not in ['.pdf', '.txt', '.md']:
                continue

            # 保存文件
            safe_filename = f"{uuid.uuid4()}_{file.filename}"
            file_path = upload_dir / safe_filename

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # 记录到数据库
            db_file = KnowledgeFile(
                filename=file.filename,
                file_path=str(file_path),
                file_size=os.path.getsize(file_path),
                status="pending"
            )
            db.add(db_file)
            db.commit()
            db.refresh(db_file)

            saved_files_info.append({
                "path": str(file_path),
                "db_id": db_file.id
            })

        if not saved_files_info:
            raise HTTPException(status_code=400, detail="没有有效的文档被上传 (仅支持 PDF, TXT, MD)")

        # 在后台处理文档索引
        background_tasks.add_task(process_documents, rag_service, saved_files_info, db)

        return JSONResponse(content={
            "success": True,
            "message": f"成功上传 {len(saved_files_info)} 个文档，正在后台建立索引...",
            "files": [f["path"] for f in saved_files_info]
        })

    except Exception as e:
        logger.error(f"文档上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

async def process_documents(rag_service: RAGService, files_info: List[Dict], db: Session):
    """后台处理文档索引"""
    try:
        logger.info(f"开始后台处理 {len(files_info)} 个文档")

        from langchain_community.document_loaders import PyPDFLoader, TextLoader
        from langchain.schema import Document

        for info in files_info:
            file_path = info["path"]
            db_id = info["db_id"]
            
            # 获取数据库记录
            # 注意：这里需要新的 session 吗？BackgroundTasks 运行在请求结束后
            # 最好在这里重新获取 session，但为了简单，我们假设 db session 仍然有效或者我们手动处理
            # 实际上 FastAPI 的 Depends(get_db) 在后台任务中可能已经关闭
            # 正确做法是手动创建 session
            
            from app.db.base import SessionLocal
            bg_db = SessionLocal()
            file_record = bg_db.query(KnowledgeFile).filter(KnowledgeFile.id == db_id).first()

            try:
                path_obj = Path(file_path)
                ext = path_obj.suffix.lower()

                if ext == '.pdf':
                    loader = PyPDFLoader(file_path)
                else:
                    loader = TextLoader(file_path, encoding='utf-8')

                docs = loader.load()
                
                # 添加元数据
                for doc in docs:
                    doc.metadata["source"] = file_record.filename
                    doc.metadata["file_id"] = file_record.id

                await rag_service.add_documents(docs)
                
                file_record.status = "indexed"
                bg_db.commit()
                
            except Exception as e:
                logger.error(f"处理文件 {file_path} 失败: {e}")
                if file_record:
                    file_record.status = "failed"
                    file_record.error_message = str(e)
                    bg_db.commit()
            finally:
                bg_db.close()

        logger.info("后台文档处理完成")

    except Exception as e:
        logger.error(f"后台任务执行失败: {str(e)}")

@router.get("/stats")
async def get_knowledge_base_stats(rag_service: RAGService = Depends(get_rag_service)):
    """获取知识库统计信息"""
    return await rag_service.get_collection_stats()

@router.delete("/clear")
async def clear_knowledge_base(rag_service: RAGService = Depends(get_rag_service)):
    """清空知识库"""
    success = await rag_service.clear_collection()
    if success:
        return {"success": True, "message": "知识库已清空"}
    else:
        raise HTTPException(status_code=500, detail="清空知识库失败")

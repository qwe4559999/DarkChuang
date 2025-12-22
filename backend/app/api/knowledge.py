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

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

def get_rag_service() -> RAGService:
    return RAGService()

@router.post("/upload")
async def upload_documents(
    files: List[UploadFile] = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    rag_service: RAGService = Depends(get_rag_service)
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

        saved_files = []

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

            saved_files.append(str(file_path))

        if not saved_files:
            raise HTTPException(status_code=400, detail="没有有效的文档被上传 (仅支持 PDF, TXT, MD)")

        # 在后台处理文档索引
        background_tasks.add_task(process_documents, rag_service, saved_files)

        return JSONResponse(content={
            "success": True,
            "message": f"成功上传 {len(saved_files)} 个文档，正在后台建立索引...",
            "files": saved_files
        })

    except Exception as e:
        logger.error(f"文档上传失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

async def process_documents(rag_service: RAGService, file_paths: List[str]):
    """后台处理文档索引"""
    try:
        logger.info(f"开始后台处理 {len(file_paths)} 个文档")

        # 加载和索引文档
        # 注意: RAGService.load_documents_from_directory 设计为读取整个目录
        # 这里我们为了简化，可以将单个文件视为"目录"处理，或者稍微修改 RAGService
        # 但既然 RAGService 主要是基于目录的，我们可以创建一个临时目录或者直接调用底层的 loader

        # 更简单的方法: 使用 load_documents_from_directory 加载整个上传目录
        # 或者为了精确控制，我们直接使用 LangChain loaders

        from langchain_community.document_loaders import PyPDFLoader, TextLoader
        from langchain.schema import Document

        documents = []
        for file_path in file_paths:
            path_obj = Path(file_path)
            ext = path_obj.suffix.lower()

            try:
                if ext == '.pdf':
                    loader = PyPDFLoader(file_path)
                else:
                    loader = TextLoader(file_path, encoding='utf-8')

                docs = loader.load()
                # 添加元数据
                for doc in docs:
                    doc.metadata.update({
                        'source': file_path,
                        'file_name': path_obj.name
                    })
                documents.extend(docs)
            except Exception as e:
                logger.error(f"处理文件 {file_path} 失败: {str(e)}")

        if documents:
            await rag_service.add_documents(documents)
            logger.info(f"成功索引 {len(documents)} 个文档片段")

    except Exception as e:
        logger.error(f"后台文档处理失败: {str(e)}")

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

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from loguru import logger

router = APIRouter()

class ChatMessage(BaseModel):
    """聊天消息模型"""
    role: str  # "user" 或 "assistant"
    content: str
    timestamp: datetime = datetime.now()

class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    conversation_id: Optional[str] = None
    use_rag: bool = True
    max_tokens: int = 1000

class ChatResponse(BaseModel):
    """聊天响应模型"""
    message: str
    conversation_id: str
    sources: List[dict] = []
    timestamp: datetime = datetime.now()
    processing_time: float

class ConversationHistory(BaseModel):
    """对话历史模型"""
    conversation_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime

# 依赖注入
def get_rag_service() -> RAGService:
    return RAGService()

def get_llm_service() -> LLMService:
    return LLMService()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
    llm_service: LLMService = Depends(get_llm_service)
):
    """处理聊天请求"""
    start_time = datetime.now()
    
    try:
        logger.info(f"收到聊天请求: {request.message[:100]}...")
        
        # 生成对话ID
        conversation_id = request.conversation_id or f"conv_{int(datetime.now().timestamp())}"
        
        sources = []
        context = ""
        
        # 如果启用RAG，检索相关文档
        if request.use_rag:
            logger.info("开始RAG检索")
            search_results = await rag_service.search_documents(
                query=request.message,
                top_k=5
            )
            
            if search_results:
                sources = [
                    {
                        "content": result["content"][:200] + "...",
                        "source": result["metadata"].get("source", "unknown"),
                        "score": result["score"]
                    }
                    for result in search_results
                ]
                
                context = "\n\n".join([result["content"] for result in search_results])
                logger.info(f"检索到 {len(search_results)} 个相关文档")
        
        # 生成回答
        logger.info("开始生成回答")
        response_message = await llm_service.generate_response(
            query=request.message,
            context=context,
            max_tokens=request.max_tokens
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"聊天请求处理完成，耗时: {processing_time:.2f}秒")
        
        return ChatResponse(
            message=response_message,
            conversation_id=conversation_id,
            sources=sources,
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"聊天请求处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理聊天请求时发生错误: {str(e)}")

@router.get("/conversations/{conversation_id}", response_model=ConversationHistory)
async def get_conversation_history(conversation_id: str):
    """获取对话历史"""
    # TODO: 实现对话历史存储和检索
    raise HTTPException(status_code=501, detail="对话历史功能尚未实现")

@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """删除对话"""
    # TODO: 实现对话删除
    raise HTTPException(status_code=501, detail="删除对话功能尚未实现")

@router.get("/conversations")
async def list_conversations():
    """获取对话列表"""
    # TODO: 实现对话列表
    raise HTTPException(status_code=501, detail="对话列表功能尚未实现")
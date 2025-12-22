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

import json
from app.services.chemistry_service import ChemistryService

# 依赖注入
def get_rag_service() -> RAGService:
    return RAGService()

def get_llm_service() -> LLMService:
    return LLMService()

def get_chemistry_service() -> ChemistryService:
    return ChemistryService()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
    llm_service: LLMService = Depends(get_llm_service),
    chemistry_service: ChemistryService = Depends(get_chemistry_service)
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

        # 检查是否包含工具调用
        if "chemistry_tool" in response_message:
            try:
                # 尝试解析JSON
                # 提取JSON部分 (处理可能包含markdown标记的情况)
                json_str = response_message
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0].strip()
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0].strip()

                tool_call = json.loads(json_str)

                if tool_call.get("tool") == "chemistry_tool":
                    action = tool_call.get("action")
                    molecule = tool_call.get("molecule")

                    if action == "calculate_properties":
                        logger.info(f"执行化学计算工具: {molecule}")
                        props = await chemistry_service.calculate_properties(molecule)
                        if props["success"]:
                            # 将结果重新喂给LLM生成自然语言回答
                            tool_result = f"分子 {molecule} 的属性计算结果：\n{json.dumps(props['properties'], ensure_ascii=False, indent=2)}"
                            response_message = await llm_service.generate_response(
                                query=f"请根据这些属性数据回答用户关于 {molecule} 的问题：{tool_result}",
                                context=context,
                                max_tokens=request.max_tokens
                            )
                        else:
                            response_message = f"抱歉，计算 {molecule} 的属性时出错：{props.get('error')}"

                    elif action == "generate_structure_image":
                        logger.info(f"执行结构图生成工具: {molecule}")
                        img_result = await chemistry_service.generate_structure_image(molecule)
                        if img_result["success"]:
                            # 这种情况下，我们直接返回带有图片信息的回答
                            response_message = f"这是 {molecule} 的分子结构图：\n![{molecule}]({img_result['image']})\n\nSMILES: {img_result['smiles']}"
                        else:
                            response_message = f"抱歉，生成 {molecule} 的结构图时出错：{img_result.get('error')}"
            except json.JSONDecodeError:
                logger.warning("解析工具调用JSON失败，将直接返回原始回答")
            except Exception as e:
                logger.error(f"执行工具调用失败: {str(e)}")
                # 出错时保留原始回答或提供错误信息

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
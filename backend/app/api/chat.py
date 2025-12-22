from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from app.services.chemistry_service import ChemistryService
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
    image_path: Optional[str] = None

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

from sqlalchemy.orm import Session
from app.db.base import get_db
from app.models.sql_models import Conversation, Message

# 依赖注入
def get_rag_service() -> RAGService:
    return RAGService()

def get_llm_service() -> LLMService:
    return LLMService()

def get_chemistry_service() -> ChemistryService:
    return ChemistryService()

@router.get("/history", response_model=List[ConversationHistory])
async def get_chat_history(db: Session = Depends(get_db)):
    """获取所有对话历史"""
    conversations = db.query(Conversation).order_by(Conversation.updated_at.desc()).all()
    result = []
    for conv in conversations:
        msgs = [
            ChatMessage(
                role=m.role, 
                content=m.content, 
                timestamp=m.created_at
            ) for m in conv.messages
        ]
        result.append(ConversationHistory(
            conversation_id=conv.id,
            messages=msgs,
            created_at=conv.created_at,
            updated_at=conv.updated_at
        ))
    return result

@router.get("/history/{conversation_id}", response_model=ConversationHistory)
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """获取指定对话详情"""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    msgs = [
        ChatMessage(
            role=m.role, 
            content=m.content, 
            timestamp=m.created_at
        ) for m in conv.messages
    ]
    return ConversationHistory(
        conversation_id=conv.id,
        messages=msgs,
        created_at=conv.created_at,
        updated_at=conv.updated_at
    )

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
    llm_service: LLMService = Depends(get_llm_service),
    chemistry_service: ChemistryService = Depends(get_chemistry_service),
    db: Session = Depends(get_db)
):
    """处理聊天请求"""
    start_time = datetime.now()

    try:
        logger.info(f"收到聊天请求: {request.message[:100]}...")

        # 生成或获取对话ID
        conversation_id = request.conversation_id or f"conv_{int(datetime.now().timestamp())}"
        
        # 确保对话存在于数据库
        db_conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not db_conv:
            db_conv = Conversation(id=conversation_id, title=request.message[:50])
            db.add(db_conv)
            db.commit()
            db.refresh(db_conv)

        # 保存用户消息
        user_msg = Message(
            conversation_id=conversation_id,
            role="user",
            content=request.message,
            message_type="image" if request.image_path else "text",
            image_path=request.image_path
        )
        db.add(user_msg)
        db.commit()

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

        # 处理图像分析请求
        if request.image_path:
            logger.info(f"检测到图像分析请求: {request.image_path}")
            try:
                from app.tools.spectrum_tool import SpectrumAnalysisTool
                spectrum_tool = SpectrumAnalysisTool()
                analysis_result = await spectrum_tool.run(request.image_path)
                
                # 将分析结果添加到上下文中
                context += f"\n\n【光谱图像分析结果】\n{analysis_result}\n"
                logger.info("光谱分析完成")
            except Exception as e:
                logger.error(f"光谱分析失败: {str(e)}")
                context += f"\n\n【光谱图像分析失败】\n{str(e)}\n"

        # 生成回答
        logger.info("开始生成回答")
        response_message = await llm_service.generate_response(
            query=request.message,
            context=context,
            max_tokens=request.max_tokens
        )

        # 保存助手回复
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_message,
            message_type="text"
        )
        db.add(assistant_msg)
        db.commit()

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
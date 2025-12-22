from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
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
    message_type: str = "text"
    image_path: Optional[str] = None
    image_url: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

def get_image_url(image_path: str) -> Optional[str]:
    if not image_path:
        return None
    # Normalize path separators
    path = image_path.replace("\\", "/")
    if "data/uploads" in path:
        try:
            rel_path = path.split("data/uploads")[1]
            return f"/uploads{rel_path}"
        except:
            return None
    return None

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
    message_type: str = "text"
    data: Optional[Dict[str, Any]] = None

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
                timestamp=m.created_at,
                message_type=m.message_type,
                image_path=m.image_path,
                image_url=get_image_url(m.image_path),
                data=json.loads(m.data) if m.data else None
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
            timestamp=m.created_at,
            message_type=m.message_type,
            image_path=m.image_path,
            image_url=get_image_url(m.image_path),
            data=json.loads(m.data) if m.data else None
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
                # 将用户的文本消息作为提示/上下文传递给工具
                analysis_result = await spectrum_tool.run(request.image_path, user_hint=request.message)
                
                # 提取分析文本，避免直接转储字典
                if isinstance(analysis_result, dict) and "analysis" in analysis_result:
                    analysis_text = analysis_result["analysis"]
                else:
                    analysis_text = str(analysis_result)

                # 将分析结果添加到上下文中
                # 关键修改：明确告知LLM不要重复调用光谱分析工具，但必须生成结构图
                context += f"\n\n【光谱图像分析结果】\n{analysis_text}\n\n[SYSTEM NOTE: Spectrum analysis completed. 1. DO NOT call 'spectrum_tool' again. 2. If a molecule structure is identified, YOU MUST CALL 'chemistry_tool' with action 'generate_structure_image' to show the structure image.]\n"
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

        # 保存助手回复 (初始回复)
        # 注意：如果后续有工具调用，我们会更新这个回复，或者追加新的回复
        # 这里为了简化，我们先不保存，等工具链执行完再保存最终结果
        # 但为了防止工具执行失败导致没有记录，我们还是先保存，后续update
        
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content=response_message,
            message_type="text"
        )
        db.add(assistant_msg)
        db.commit()
        db.refresh(assistant_msg) # 获取ID以便后续更新
        assistant_msg_id = assistant_msg.id # 保存ID，避免对象过期问题

        # 工具调用循环 (支持多轮工具调用，例如：分析 -> 生成图片)
        max_tool_calls = 3
        current_call = 0
        
        while ("chemistry_tool" in response_message or "spectrum_tool" in response_message) and current_call < max_tool_calls:
            current_call += 1
            logger.info(f"检测到工具调用 (第 {current_call} 次)")
            
            try:
                # 尝试解析JSON
                json_str = response_message
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0].strip()
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0].strip()

                tool_call = json.loads(json_str)
                tool_result_text = ""
                
                # 1. 光谱分析工具 (文本模式)
                if tool_call.get("tool") == "spectrum_tool":
                    action = tool_call.get("action")
                    if action == "analyze_peaks":
                        peaks = tool_call.get("peaks", [])
                        hint = tool_call.get("hint", "")
                        logger.info(f"执行光谱分析工具(文本模式): {peaks}")
                        
                        from app.tools.spectrum_tool import SpectrumAnalysisTool
                        spectrum_tool = SpectrumAnalysisTool()
                        analysis_result = await spectrum_tool.analyze_peaks_from_text(peaks, hint)
                        
                        if isinstance(analysis_result, dict) and "analysis" in analysis_result:
                            tool_result_text = analysis_result["analysis"]
                        else:
                            tool_result_text = str(analysis_result)
                            
                        query_prompt = f"请根据以下光谱分析结果回答用户的问题：\n{tool_result_text}\n\n【重要指令】如果分析结果中确定了具体的分子结构（SMILES或名称），你必须接着调用 'chemistry_tool' 的 'generate_structure_image' 动作来生成该分子的结构图。请务必执行此步骤！"

                # 2. 化学工具 (属性计算 / 结构图生成)
                elif tool_call.get("tool") == "chemistry_tool":
                    action = tool_call.get("action")
                    molecule = tool_call.get("molecule")

                    if action == "calculate_properties":
                        logger.info(f"执行化学计算工具: {molecule}")
                        props = await chemistry_service.calculate_properties(molecule)
                        if props["success"]:
                            tool_result_text = f"分子 {molecule} 的属性计算结果：\n{json.dumps(props['properties'], ensure_ascii=False, indent=2)}"
                            query_prompt = f"请根据这些属性数据回答用户关于 {molecule} 的问题：{tool_result_text}"
                        else:
                            tool_result_text = f"错误：{props.get('error')}"
                            query_prompt = f"计算属性时出错：{tool_result_text}"

                    elif action == "generate_structure_image":
                        logger.info(f"执行结构图生成工具: {molecule}")
                        img_result = await chemistry_service.generate_structure_image(molecule)
                        if img_result["success"]:
                            image_markdown = f"![{molecule}]({img_result['image']})"
                            tool_result_text = f"已生成 {molecule} 的结构图: {image_markdown}\nSMILES: {img_result['smiles']}"
                            query_prompt = f"请根据上下文中的分析结果，详细解释为什么推断出是 {molecule}，并展示生成的结构图。结构图信息：{tool_result_text}"
                            
                            # 更新消息数据 (2D图)
                            msg_to_update = db.query(Message).filter(Message.id == assistant_msg_id).first()
                            if msg_to_update:
                                msg_to_update.data = json.dumps({"image": img_result['image'], "smiles": img_result['smiles']})
                                db.commit()
                        else:
                            tool_result_text = f"错误：{img_result.get('error')}"
                            query_prompt = f"生成结构图时出错：{tool_result_text}"

                    elif action == "generate_3d_structure":
                        logger.info(f"执行3D结构生成工具: {molecule}")
                        sdf_result = await chemistry_service.generate_3d_structure(molecule)
                        if sdf_result["success"]:
                            tool_result_text = f"已生成 {molecule} 的3D结构数据 (SDF格式)。"
                            query_prompt = f"请告诉用户 {molecule} 的3D结构已生成，并简要介绍该分子的立体化学特征。"
                            
                            # 更新消息数据 (3D SDF)
                            msg_to_update = db.query(Message).filter(Message.id == assistant_msg_id).first()
                            if msg_to_update:
                                msg_to_update.message_type = "molecule"
                                msg_to_update.data = json.dumps({"sdf": sdf_result['sdf'], "smiles": sdf_result['smiles']})
                                db.commit()
                        else:
                            tool_result_text = f"错误：{sdf_result.get('error')}"
                            query_prompt = f"生成3D结构时出错：{tool_result_text}"
                
                # 如果成功执行了工具，重新调用LLM
                if tool_result_text:
                    # 将工具结果追加到上下文
                    context += f"\n\n【工具执行结果】\n{tool_result_text}\n"
                    
                    response_message = await llm_service.generate_response(
                        query=query_prompt,
                        context=context,
                        max_tokens=request.max_tokens
                    )
                    
                    # 更新数据库中的消息内容
                    # 重新获取消息对象以避免 "Instance has been deleted" 错误
                    msg_to_update = db.query(Message).filter(Message.id == assistant_msg_id).first()
                    if msg_to_update:
                        msg_to_update.content = response_message
                        db.commit()
                    else:
                        logger.error(f"无法找到消息 ID {assistant_msg_id} 进行更新")
                else:
                    break # 工具执行未产生结果，跳出循环

            except json.JSONDecodeError:
                logger.warning("解析工具调用JSON失败")
                break
            except Exception as e:
                logger.error(f"执行工具调用失败: {str(e)}")
                break

        processing_time = (datetime.now() - start_time).total_seconds()

        logger.info(f"聊天请求处理完成，耗时: {processing_time:.2f}秒")

        # 获取最终的消息状态
        final_msg = db.query(Message).filter(Message.id == assistant_msg_id).first()
        
        return ChatResponse(
            message=response_message,
            conversation_id=conversation_id,
            sources=sources,
            processing_time=processing_time,
            message_type=final_msg.message_type if final_msg else "text",
            data=json.loads(final_msg.data) if final_msg and final_msg.data else None
        )

        
    except Exception as e:
        logger.error(f"聊天请求处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理聊天请求时发生错误: {str(e)}")

@router.delete("/history/{conversation_id}")
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """删除对话"""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # 手动删除关联消息
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()
    
    db.delete(conv)
    db.commit()
    return {"success": True, "message": "Conversation deleted"}
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import json
from app.services.rag_service import RAGService
from app.services.llm_service import LLMService
from app.services.chemistry_service import ChemistryService
from loguru import logger
from app.db.base import SessionLocal

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
from app.models.sql_models import Conversation, Message, User
from app.api import deps

# 依赖注入
def get_rag_service() -> RAGService:
    return RAGService()

def get_llm_service() -> LLMService:
    return LLMService()

def get_chemistry_service() -> ChemistryService:
    return ChemistryService()

async def process_chat_background(
    conversation_id: str,
    assistant_msg_id: int,
    request: ChatRequest,
    user_id: int
):
    """后台处理聊天请求"""
    logger.info(f"开始后台处理聊天请求: {conversation_id}")
    start_time = datetime.now()
    db = SessionLocal()
    
    try:
        # 实例化服务
        rag_service = RAGService()
        llm_service = LLMService()
        chemistry_service = ChemistryService()

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
                context += f"\n\n【光谱图像分析结果】\n{analysis_text}\n\n[SYSTEM NOTE: Spectrum analysis completed. 1. DO NOT call 'spectrum_tool' again. 2. If a molecule structure is identified, YOU MUST CALL 'chemistry_tool' with action 'generate_structure_image' to show the structure image.]\n"
                logger.info("光谱分析完成")
            except Exception as e:
                logger.error(f"光谱分析失败: {str(e)}")
                context += f"\n\n【光谱图像分析失败】\n{str(e)}\n"

        # 获取历史消息 (用于上下文)
        recent_msgs = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(11).all()
        
        chat_history = []
        if recent_msgs:
            # 跳过第一条（也就是刚刚插入的当前消息）
            start_index = 1 if (recent_msgs[0].role == "user" and recent_msgs[0].content == request.message) else 0
            
            for m in recent_msgs[start_index:]:
                chat_history.append({"role": m.role, "content": m.content})
            
            chat_history.reverse()

        # 生成回答
        logger.info("开始生成回答")
        response_message = await llm_service.generate_response(
            query=request.message,
            context=context,
            history=chat_history,
            max_tokens=request.max_tokens
        )

        # 更新助手回复 (初始回复)
        # 只有当回复不是工具调用时才更新数据库，避免显示JSON
        if "chemistry_tool" not in response_message and "spectrum_tool" not in response_message:
            msg_to_update = db.query(Message).filter(Message.id == assistant_msg_id).first()
            if msg_to_update:
                msg_to_update.content = response_message
                db.commit()

        # 工具调用循环
        max_tool_calls = 3
        current_call = 0
        
        while ("chemistry_tool" in response_message or "spectrum_tool" in response_message) and current_call < max_tool_calls:
            current_call += 1
            logger.info(f"检测到工具调用 (第 {current_call} 次)")
            
            # 更新状态为正在调用工具
            msg_to_update = db.query(Message).filter(Message.id == assistant_msg_id).first()
            if msg_to_update and msg_to_update.content != "正在分析请求并调用相关工具...":
                 # 如果之前已经生成了部分文本，保留它，或者替换为状态信息
                 # 这里我们选择暂时替换为状态信息，或者追加
                 pass 

            try:
                # 尝试解析JSON
                json_str = response_message
                if "```json" in json_str:
                    json_str = json_str.split("```json")[1].split("```")[0].strip()
                elif "```" in json_str:
                    json_str = json_str.split("```")[1].split("```")[0].strip()

                tool_call = json.loads(json_str)
                
                tool_calls_list = []
                if isinstance(tool_call, list):
                    tool_calls_list = tool_call
                elif isinstance(tool_call, dict):
                    tool_calls_list = [tool_call]
                else:
                    logger.warning("收到无效的工具调用格式")
                    break

                combined_tool_result_text = ""
                combined_query_prompt = ""
                
                for t_call in tool_calls_list:
                    tool_result_text = ""
                    
                    # 1. 光谱分析工具
                    if isinstance(t_call, dict) and t_call.get("tool") == "spectrum_tool":
                        action = t_call.get("action")
                        if action == "analyze_peaks":
                            peaks = t_call.get("peaks", [])
                            hint = t_call.get("hint", "")
                            logger.info(f"执行光谱分析工具(文本模式): {peaks}")
                            
                            from app.tools.spectrum_tool import SpectrumAnalysisTool
                            spectrum_tool = SpectrumAnalysisTool()
                            analysis_result = await spectrum_tool.analyze_peaks_from_text(peaks, hint)
                            
                            if isinstance(analysis_result, dict) and "analysis" in analysis_result:
                                tool_result_text = analysis_result["analysis"]
                            else:
                                tool_result_text = str(analysis_result)
                                
                            combined_query_prompt += f"请根据以下光谱分析结果回答用户的问题：\n{tool_result_text}\n\n【重要指令】如果分析结果中确定了具体的分子结构（SMILES或名称），你必须接着调用 'chemistry_tool' 的 'generate_structure_image' 动作来生成该分子的结构图。请务必执行此步骤！\n"

                    # 2. 化学工具
                    elif isinstance(t_call, dict) and t_call.get("tool") == "chemistry_tool":
                        action = t_call.get("action")
                        molecule = t_call.get("molecule")

                        if action == "calculate_properties":
                            logger.info(f"执行化学计算工具: {molecule}")
                            props = await chemistry_service.calculate_properties(molecule)
                            if props["success"]:
                                tool_result_text = f"分子 {molecule} 的属性计算结果：\n{json.dumps(props['properties'], ensure_ascii=False, indent=2)}"
                                combined_query_prompt += f"请根据这些属性数据回答用户关于 {molecule} 的问题：{tool_result_text}\n"

                                # 更新消息数据
                                msg_to_update = db.query(Message).filter(Message.id == assistant_msg_id).first()
                                if msg_to_update:
                                    current_data = json.loads(msg_to_update.data) if msg_to_update.data else {}
                                    current_data["properties"] = props["properties"]
                                    msg_to_update.message_type = "molecule"
                                    msg_to_update.data = json.dumps(current_data)
                                    db.commit()
                            else:
                                tool_result_text = f"错误：{props.get('error')}"
                                combined_query_prompt += f"计算属性时出错：{tool_result_text}\n"

                        elif action == "generate_structure_image":
                            logger.info(f"执行结构图生成工具: {molecule}")
                            img_result = await chemistry_service.generate_structure_image(molecule)
                            props_result = await chemistry_service.calculate_properties(molecule)
                            
                            if img_result["success"]:
                                image_markdown = f"![{molecule}]({img_result['image']})"
                                tool_result_text = f"已生成 {molecule} 的结构图: {image_markdown}\nSMILES: {img_result['smiles']}"
                                
                                if props_result["success"]:
                                    tool_result_text += f"\n\n同时计算了该分子的属性：\n{json.dumps(props_result['properties'], ensure_ascii=False, indent=2)}"
                                
                                combined_query_prompt += f"【系统指令】结构图已成功生成（见下文）。请直接向用户展示该图片并解释推断理由。严禁再次调用 'generate_structure_image' 工具！\n\n结构图信息：{tool_result_text}\n"
                                
                                msg_to_update = db.query(Message).filter(Message.id == assistant_msg_id).first()
                                if msg_to_update:
                                    current_data = json.loads(msg_to_update.data) if msg_to_update.data else {}
                                    current_data["image"] = img_result['image']
                                    current_data["smiles"] = img_result['smiles']
                                    if props_result["success"]:
                                        current_data["properties"] = props_result["properties"]
                                    msg_to_update.data = json.dumps(current_data)
                                    db.commit()
                            else:
                                tool_result_text = f"错误：{img_result.get('error')}"
                                combined_query_prompt += f"生成结构图时出错：{tool_result_text}\n"

                        elif action == "generate_3d_structure":
                            logger.info(f"执行3D结构生成工具: {molecule}")
                            sdf_result = await chemistry_service.generate_3d_structure(molecule)
                            props_result = await chemistry_service.calculate_properties(molecule)

                            if sdf_result["success"]:
                                tool_result_text = f"已生成 {molecule} 的3D结构数据 (SDF格式)。"
                                
                                if props_result["success"]:
                                    tool_result_text += f"\n\n同时计算了该分子的属性：\n{json.dumps(props_result['properties'], ensure_ascii=False, indent=2)}"

                                combined_query_prompt += f"【系统指令】3D结构已成功生成。请告诉用户 {molecule} 的3D结构已准备好，并简要介绍该分子的立体化学特征。严禁再次调用 'generate_3d_structure' 工具！\n"
                                
                                msg_to_update = db.query(Message).filter(Message.id == assistant_msg_id).first()
                                if msg_to_update:
                                    msg_to_update.message_type = "molecule"
                                    current_data = json.loads(msg_to_update.data) if msg_to_update.data else {}
                                    current_data["sdf"] = sdf_result['sdf']
                                    current_data["smiles"] = sdf_result['smiles']
                                    if props_result["success"]:
                                        current_data["properties"] = props_result["properties"]
                                    msg_to_update.data = json.dumps(current_data)
                                    db.commit()
                            else:
                                tool_result_text = f"错误：{sdf_result.get('error')}"
                                combined_query_prompt += f"生成3D结构时出错：{tool_result_text}\n"
                    
                    if tool_result_text:
                        combined_tool_result_text += tool_result_text + "\n"

                # 如果成功执行了工具，重新调用LLM
                if combined_tool_result_text:
                    context += f"\n\n【工具执行结果】\n{combined_tool_result_text}\n"
                    
                    response_message = await llm_service.generate_response(
                        query=combined_query_prompt,
                        context=context,
                        max_tokens=request.max_tokens
                    )
                    
                    # 只有当回复不是工具调用时才更新数据库，避免显示JSON
                    if "chemistry_tool" not in response_message and "spectrum_tool" not in response_message:
                        msg_to_update = db.query(Message).filter(Message.id == assistant_msg_id).first()
                        if msg_to_update:
                            msg_to_update.content = response_message
                            db.commit()
                else:
                    break

            except json.JSONDecodeError:
                logger.warning("解析工具调用JSON失败")
                break
            except Exception as e:
                logger.error(f"执行工具调用失败: {str(e)}")
                break

        processing_time = (datetime.now() - start_time).total_seconds()
        logger.info(f"后台处理完成，耗时: {processing_time:.2f}秒")

    except Exception as e:
        logger.error(f"后台处理失败: {str(e)}")
        # 更新消息为错误状态
        msg_to_update = db.query(Message).filter(Message.id == assistant_msg_id).first()
        if msg_to_update:
            msg_to_update.content = f"处理请求时发生错误: {str(e)}"
            db.commit()
    finally:
        db.close()

@router.get("/history", response_model=List[ConversationHistory])
async def get_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """获取所有对话历史"""
    conversations = db.query(Conversation).filter(Conversation.user_id == current_user.id).order_by(Conversation.updated_at.desc()).all()
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
async def get_conversation(
    conversation_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """获取指定对话详情"""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id).first()
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

@router.post("", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """处理聊天请求 (异步后台处理)"""
    try:
        logger.info(f"收到聊天请求: {request.message[:100]}...")

        # 生成或获取对话ID
        conversation_id = request.conversation_id or f"conv_{int(datetime.now().timestamp())}"
        
        # 确保对话存在于数据库
        db_conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not db_conv:
            db_conv = Conversation(id=conversation_id, title=request.message[:50], user_id=current_user.id)
            db.add(db_conv)
            db.commit()
            db.refresh(db_conv)
        elif db_conv.user_id != current_user.id:
             raise HTTPException(status_code=403, detail="Not authorized to access this conversation")

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

        # 创建助手消息占位符
        assistant_msg = Message(
            conversation_id=conversation_id,
            role="assistant",
            content="正在分析请求并调用相关工具...",
            message_type="text"
        )
        db.add(assistant_msg)
        db.commit()
        db.refresh(assistant_msg)

        # 添加后台任务
        background_tasks.add_task(
            process_chat_background,
            conversation_id,
            assistant_msg.id,
            request,
            current_user.id
        )

        return ChatResponse(
            message=assistant_msg.content,
            conversation_id=conversation_id,
            sources=[],
            processing_time=0.0,
            message_type="text",
            data=None
        )

    except Exception as e:
        logger.error(f"聊天请求处理失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理聊天请求时发生错误: {str(e)}")

@router.delete("/history/{conversation_id}")
async def delete_conversation(
    conversation_id: str, 
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """删除对话"""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == current_user.id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # 手动删除关联消息
    db.query(Message).filter(Message.conversation_id == conversation_id).delete()

    
    db.delete(conv)
    db.commit()
    return {"success": True, "message": "Conversation deleted"}

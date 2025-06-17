from typing import Optional, Dict, Any, List
import asyncio
from app.core.config import settings
from loguru import logger
import openai
from transformers import AutoTokenizer, AutoModel
import torch
from typing import Optional, Dict, Any
import base64
import httpx

class LLMService:
    """大语言模型服务 - 支持DeepSeek-R1和Qwen2.5-VL多模型"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.text_client = None  # DeepSeek-R1客户端
        self.vision_client = None  # Qwen2.5-VL客户端
        self._initialize()
    
    def _initialize(self):
        """初始化LLM服务"""
        try:
            logger.info("初始化多模型LLM服务...")
            
            # 初始化文本模型客户端 (DeepSeek-R1)
            if hasattr(settings, 'LLM_API_KEY') and settings.LLM_API_KEY:
                self._initialize_text_client()
            
            # 初始化视觉模型客户端 (Qwen2.5-VL)
            if hasattr(settings, 'VISION_API_KEY') and settings.VISION_API_KEY:
                self._initialize_vision_client()
            
            # 兼容旧版OpenAI配置
            if not self.text_client and settings.OPENAI_API_KEY:
                self._initialize_openai_compatible()
            
            # 如果都没有配置，使用本地模型
            if not self.text_client:
                self._initialize_local_model()
            
            logger.info("多模型LLM服务初始化完成")
            
        except Exception as e:
            logger.error(f"LLM服务初始化失败: {str(e)}")
            raise
    
    def _initialize_text_client(self):
        """初始化文本模型客户端 (DeepSeek-R1)"""
        try:
            self.text_client = openai.AsyncOpenAI(
                api_key=settings.LLM_API_KEY,
                base_url=settings.LLM_BASE_URL
            )
            logger.info(f"文本模型客户端初始化完成: {settings.LLM_MODEL}")
            
        except Exception as e:
            logger.error(f"文本模型客户端初始化失败: {str(e)}")
            raise
    
    def _initialize_vision_client(self):
        """初始化视觉模型客户端 (Qwen2.5-VL)"""
        try:
            self.vision_client = openai.AsyncOpenAI(
                api_key=settings.VISION_API_KEY,
                base_url=settings.VISION_BASE_URL
            )
            logger.info(f"视觉模型客户端初始化完成: {settings.VISION_MODEL}")
            
        except Exception as e:
            logger.error(f"视觉模型客户端初始化失败: {str(e)}")
            raise
    
    def _initialize_openai_compatible(self):
        """初始化兼容OpenAI的客户端"""
        try:
            self.text_client = openai.AsyncOpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL
            )
            logger.info("兼容OpenAI客户端初始化完成")
            
        except Exception as e:
            logger.error(f"兼容OpenAI客户端初始化失败: {str(e)}")
            raise
    
    def _initialize_local_model(self):
        """初始化本地模型"""
        try:
            # 这里可以加载本地的ChatGLM或其他模型
            # 由于模型较大，这里只是示例代码
            logger.info(f"准备加载本地模型: {settings.LLM_MODEL}")
            
            # 示例：加载ChatGLM模型
            # self.tokenizer = AutoTokenizer.from_pretrained(
            #     settings.LLM_MODEL, 
            #     trust_remote_code=True
            # )
            # self.model = AutoModel.from_pretrained(
            #     settings.LLM_MODEL, 
            #     trust_remote_code=True
            # ).half().cuda()
            
            logger.warning("本地模型加载功能尚未完全实现，请配置OpenAI API")
            
        except Exception as e:
            logger.error(f"本地模型初始化失败: {str(e)}")
            raise
    
    async def generate_response(
        self,
        query: str,
        context: str = "",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """生成回答"""
        try:
            logger.info(f"开始生成回答，查询长度: {len(query)}，上下文长度: {len(context)}")
            
            if self.text_client:
                # 使用文本模型 (DeepSeek-R1)
                return await self._generate_with_text_model(
                    query, context, max_tokens, temperature
                )
            else:
                # 使用本地模型
                return await self._generate_with_local_model(
                    query, context, max_tokens, temperature
                )
                
        except Exception as e:
            logger.error(f"生成回答失败: {str(e)}")
            return f"抱歉，生成回答时发生错误: {str(e)}"
    
    async def _generate_with_text_model(
        self,
        query: str,
        context: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """使用文本模型生成回答 (DeepSeek-R1)"""
        try:
            # 构建提示词
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(query, context)
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # 调用文本模型API
            model_name = getattr(settings, 'LLM_MODEL', 'deepseek-ai/DeepSeek-R1')
            response = await self.text_client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False
            )
            
            answer = response.choices[0].message.content
            logger.info(f"文本模型API调用成功，回答长度: {len(answer)}")
            
            return answer
            
        except Exception as e:
            logger.error(f"文本模型API调用失败: {str(e)}")
            raise
    
    async def _generate_with_local_model(
        self,
        query: str,
        context: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """使用本地模型生成回答"""
        try:
            # 这里实现本地模型推理
            # 由于模型较大，这里只是示例代码
            
            if not self.model or not self.tokenizer:
                return "本地模型未正确加载，请配置OpenAI API或检查模型路径"
            
            # 构建提示词
            prompt = self._build_user_prompt(query, context)
            
            # 示例：使用ChatGLM生成回答
            # response, history = self.model.chat(
            #     self.tokenizer,
            #     prompt,
            #     history=[],
            #     max_length=max_tokens,
            #     temperature=temperature
            # )
            
            # 临时返回
            response = f"这是一个模拟回答。查询: {query[:50]}..."
            
            logger.info(f"本地模型推理完成，回答长度: {len(response)}")
            return response
            
        except Exception as e:
            logger.error(f"本地模型推理失败: {str(e)}")
            raise
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词"""
        return """
你是一个专业的化学问答助手，具有以下特点：

1. 专业知识：精通化学各个分支，包括有机化学、无机化学、物理化学、分析化学等
2. 准确性：提供准确、可靠的化学信息和解答
3. 教育性：用清晰易懂的方式解释复杂的化学概念
4. 安全意识：在涉及化学实验或化学品时，始终强调安全注意事项
5. 结构化回答：使用清晰的格式组织答案，包括要点、步骤、公式等

回答要求：
- 基于提供的上下文信息回答问题
- 如果上下文信息不足，明确说明并提供一般性的化学知识
- 使用中文回答
- 在适当的地方使用化学公式和方程式
- 提供相关的化学原理解释
"""
    
    def _build_user_prompt(self, query: str, context: str) -> str:
        """构建用户提示词"""
        if context:
            return f"""
基于以下化学知识上下文，回答用户的问题：

上下文信息：
{context}

用户问题：
{query}

请基于上述上下文信息提供准确、详细的回答。如果上下文信息不足以完全回答问题，请说明这一点，并提供你所知道的相关化学知识。
"""
        else:
            return f"""
请回答以下化学问题：

{query}

请提供准确、详细的回答，包括相关的化学原理、公式和实例。
"""
    
    async def generate_summary(self, text: str, max_length: int = 200) -> str:
        """生成文本摘要"""
        try:
            summary_prompt = f"""
请为以下化学相关文本生成一个简洁的摘要（不超过{max_length}字）：

{text}

摘要：
"""
            
            return await self.generate_response(
                query=summary_prompt,
                context="",
                max_tokens=max_length + 50,
                temperature=0.3
            )
            
        except Exception as e:
            logger.error(f"生成摘要失败: {str(e)}")
            return f"摘要生成失败: {str(e)}"
    
    async def analyze_spectrum_image(
        self,
        image_path: str,
        spectrum_type: str = "auto",
        additional_context: str = ""
    ) -> str:
        """使用视觉模型描述光谱图像，然后用DeepSeek进行专业解析"""
        try:
            if not self.vision_client:
                return "视觉模型未配置，无法进行图谱分析"
            
            logger.info(f"开始分析光谱图像: {image_path}，类型: {spectrum_type}")
            
            # 第一步：使用Qwen2.5-VL描述谱图
            vision_description = await self._describe_spectrum_with_vision(
                image_path, spectrum_type, additional_context
            )
            
            if "失败" in vision_description:
                return vision_description
            
            # 第二步：使用DeepSeek解析描述结果
            if self.text_client:  # 如果有DeepSeek客户端
                logger.info("使用DeepSeek进行专业光谱解析")
                final_analysis = await self._analyze_spectrum_with_deepseek(
                    vision_description, spectrum_type, additional_context
                )
                return final_analysis
            else:
                # 如果没有DeepSeek，直接返回视觉描述
                logger.warning("DeepSeek未配置，仅返回视觉描述结果")
                return f"**视觉描述结果**\n\n{vision_description}\n\n**注意**: DeepSeek未配置，无法进行深度专业解析。"
            
        except Exception as e:
            logger.error(f"光谱图像分析失败: {str(e)}")
            return f"光谱分析失败: {str(e)}"
    
    async def _describe_spectrum_with_vision(
        self,
        image_path: str,
        spectrum_type: str = "auto",
        additional_context: str = ""
    ) -> str:
        """使用Qwen2.5-VL视觉模型描述光谱图像"""
        try:
            logger.info(f"使用Qwen2.5-VL描述光谱图像: {image_path}")
            
            # 读取并编码图像
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 构建简化的描述提示词
            description_prompt = self._build_vision_description_prompt(spectrum_type, additional_context)
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": description_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ]
            
            # 调用视觉模型
            model_name = getattr(settings, 'VISION_MODEL', 'Qwen/Qwen2.5-VL-72B-Instruct')
            response = await self.vision_client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=2500,  # 增加token限制以支持更详细的描述
                temperature=0.1   # 降低温度确保描述的准确性和一致性
            )
            
            description_result = response.choices[0].message.content
            logger.info(f"视觉描述完成，结果长度: {len(description_result)}")
            
            return description_result
            
        except Exception as e:
            logger.error(f"视觉模型描述失败: {str(e)}")
            return f"视觉描述失败: {str(e)}"
    
    async def _analyze_spectrum_with_deepseek(
        self,
        vision_description: str,
        spectrum_type: str = "auto",
        additional_context: str = ""
    ) -> str:
        """使用DeepSeek分析视觉模型的光谱描述结果"""
        try:
            logger.info("使用DeepSeek进行专业光谱解析")
            
            # 构建DeepSeek分析提示词
            analysis_prompt = self._build_deepseek_analysis_prompt(
                vision_description, spectrum_type, additional_context
            )
            
            response = await self.text_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位资深的化学光谱分析专家，具有丰富的光谱解析经验和深厚的化学理论基础。"
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                max_tokens=3500,    # 增加token数以支持更详细的验证分析
                temperature=0.05    # 更低温度确保最高准确性和一致性
            )
            
            analysis_result = response.choices[0].message.content
            logger.info(f"DeepSeek专业解析完成，结果长度: {len(analysis_result)}")
            
            # 组合结果
            final_result = f"""# 光谱分析报告

## 1. 视觉识别描述
{vision_description}

## 2. 专业解析结果
{analysis_result}

---
*分析流程：Qwen2.5-VL视觉识别 → DeepSeek专业解析*"""
            
            return final_result
            
        except Exception as e:
            logger.error(f"DeepSeek解析失败: {str(e)}")
            return f"**视觉描述结果**\n\n{vision_description}\n\n**DeepSeek解析失败**: {str(e)}"
    
    async def analyze_general_image(self, image_path: str) -> dict:
        """使用视觉模型进行通用图像分析"""
        try:
            if not self.vision_client:
                return {
                    'description': '视觉模型未配置，无法进行图像分析',
                    'chemical_formulas': [],
                    'chemical_structures': [],
                    'confidence': 0.0
                }
            
            logger.info(f"开始通用图像分析: {image_path}")
            
            # 读取并编码图像
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # 构建通用图像分析提示词
            general_prompt = self._build_general_image_prompt()
            
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": general_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ]
            
            # 调用视觉模型
            model_name = getattr(settings, 'VISION_MODEL', 'Qwen/Qwen2.5-VL-72B-Instruct')
            response = await self.vision_client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=2000,
                temperature=0.1
            )
            
            vision_result = response.choices[0].message.content
            logger.info(f"视觉模型分析完成，结果长度: {len(vision_result)}")
            
            # 使用DeepSeek进行结构化解析
            structured_result = await self._parse_vision_result_with_deepseek(vision_result)
            
            return structured_result
            
        except Exception as e:
            logger.error(f"通用图像分析失败: {str(e)}")
            return {
                'description': f'图像分析失败: {str(e)}',
                'chemical_formulas': [],
                'chemical_structures': [],
                'confidence': 0.0
            }
    
    def _build_spectrum_prompt(self, spectrum_type: str, additional_context: str = "") -> str:
        """构建光谱分析提示词"""
        base_prompt = f"""
你是一位专业的化学光谱分析专家。请仔细分析这张{spectrum_type}光谱图，并提供详细的分析报告。

请按以下格式分析：

1. **光谱基本信息识别**
   - 识别坐标轴标签和单位
   - 识别主要峰的位置和强度
   - 识别基线和噪声水平

2. **特征峰分析**
   - 列出所有显著的吸收峰/信号峰
   - 标注峰的位置（波数/化学位移/波长）
   - 描述峰的强度和形状特征
"""
        
        if spectrum_type.upper() == "IR" or "红外" in spectrum_type:
            specific_prompt = """
3. **红外光谱特征分析**
   - 官能团特征峰识别（如O-H, C-H, C=O, C=C等）
   - 峰位置对应的化学键振动类型
   - 强度分析（强、中、弱）
   - 可能的分子结构推断

4. **结构推断**
   - 基于特征峰推断可能的官能团
   - 分析分子骨架结构
   - 提出可能的化合物类型
"""
        elif spectrum_type.upper() == "NMR" or "核磁" in spectrum_type:
            specific_prompt = """
3. **核磁共振光谱特征分析**
   - 化学位移分析（δ值）
   - 积分比例分析
   - 偶合模式识别（单峰、双峰、三重峰等）
   - 偶合常数分析

4. **结构推断**
   - 基于化学位移推断质子环境
   - 分析偶合关系确定连接性
   - 推断分子结构和官能团
   - 计算分子式中的氢原子数目
"""
        elif spectrum_type.upper() == "UV" or "紫外" in spectrum_type:
            specific_prompt = """
3. **紫外光谱特征分析**
   - 吸收峰波长位置（λmax）
   - 摩尔吸光系数估算
   - 吸收带的精细结构
   - 溶剂效应分析

4. **结构推断**
   - 共轭体系分析
   - 发色团和助色团识别
   - 电子跃迁类型判断
   - 分子共轭程度评估
"""
    
    def _build_auto_spectrum_prompt(self, additional_context: str = "") -> str:
        """构建自动识别谱图类型的提示词"""
        base_prompt = """
你是一位专业的化学光谱分析专家。请首先识别这张光谱图的类型，然后进行详细的专业分析。

请按以下格式分析：

1. **光谱类型识别**
   - 识别光谱类型（IR红外光谱、NMR核磁共振谱、UV紫外光谱、MS质谱、Raman拉曼光谱、XRD X射线衍射等）
   - 说明识别依据（坐标轴标签、峰形特征、数据范围等）
   - 评估光谱质量和清晰度

2. **光谱基本信息识别**
   - 识别坐标轴标签和单位
   - 识别主要峰的位置和强度
   - 识别基线和噪声水平

3. **特征峰分析**
   - 列出所有显著的吸收峰/信号峰
   - 标注峰的位置（波数/化学位移/波长）
   - 描述峰的强度和形状特征

4. **专业分析**（根据识别的光谱类型进行相应分析）
   - 如果是IR：官能团特征峰识别、化学键振动类型、分子结构推断
   - 如果是NMR：化学位移分析、积分比例、偶合模式、结构推断
   - 如果是UV：吸收峰波长、共轭体系分析、发色团识别
   - 如果是MS：分子离子峰、碎片离子、分子量确定
   - 如果是Raman：振动模式、分子对称性、晶体结构
   - 如果是XRD：衍射峰位置、晶体结构、相组成

5. **结构推断与总结**
   - 基于光谱特征推断可能的分子结构
   - 分析分子骨架和官能团
   - 提出可能的化合物类型
   - 光谱质量评估和建议

请确保分析准确、专业，并使用标准的化学术语。
"""
        
        if additional_context:
            base_prompt += f"\n\n**额外信息**: {additional_context}"
        
        return base_prompt
    
    def _build_general_image_prompt(self) -> str:
        """构建通用图像分析提示词"""
        return """
请作为专业的图像分析师，详细分析这张图像。请从以下几个方面进行分析：

1. **图像内容描述**
   - 详细描述图像中的主要内容和对象
   - 识别图像的类型和用途
   - 描述图像的整体布局和结构

2. **文本内容提取**
   - 识别图像中的所有文字内容
   - 包括标题、标签、数值、单位等
   - 注意文字的位置和上下文关系

3. **化学相关内容识别**（如果适用）
   - 识别化学公式、分子式、结构式
   - 识别化学符号、元素符号
   - 识别实验数据、测量结果
   - 识别化学仪器、设备、装置

4. **图表和数据分析**（如果适用）
   - 分析图表类型（柱状图、折线图、散点图等）
   - 识别坐标轴标签和数值范围
   - 分析数据趋势和关键特征点
   - 识别图例和标注信息

5. **专业术语和概念**
   - 识别专业领域相关的术语
   - 分析图像所属的学科领域
   - 识别专业概念和理论

请提供详细、准确的分析结果，重点关注图像中的文字内容和专业信息。
"""
    
    async def _parse_vision_result_with_deepseek(self, vision_result: str) -> dict:
        """使用DeepSeek解析视觉模型的结果"""
        try:
            parse_prompt = f"""
请分析以下图像分析结果，并提取结构化信息：

{vision_result}

请从上述分析中提取以下信息，并以JSON格式返回：
{{
    "description": "图像的详细描述",
    "chemical_formulas": ["识别到的化学公式列表"],
    "chemical_structures": [
        {{
            "name": "结构名称",
            "formula": "分子式",
            "description": "结构描述"
        }}
    ],
    "confidence": 0.95
}}

注意：
1. description应该包含图像的主要内容和关键信息
2. chemical_formulas应该包含所有识别到的化学公式
3. chemical_structures应该包含识别到的化学结构信息
4. confidence应该是0-1之间的数值，表示分析的可信度
5. 如果没有相关信息，对应字段可以为空列表或空字符串
"""
            
            response = await self.text_client.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": "你是一个专业的数据解析助手，擅长从文本中提取结构化信息。"},
                    {"role": "user", "content": parse_prompt}
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            result_text = response.choices[0].message.content
            
            # 尝试解析JSON
            import json
            import re
            
            # 提取JSON部分
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', result_text, re.DOTALL)
            if json_match:
                try:
                    parsed_result = json.loads(json_match.group())
                    return parsed_result
                except json.JSONDecodeError:
                    pass
            
            # 如果JSON解析失败，返回基本结构
            return {
                'description': result_text,
                'chemical_formulas': [],
                'chemical_structures': [],
                'confidence': 0.8
            }
            
        except Exception as e:
            logger.error(f"DeepSeek解析失败: {str(e)}")
            return {
                'description': vision_result,
                'chemical_formulas': [],
                'chemical_structures': [],
                'confidence': 0.7
            }
        else:
            specific_prompt = """
3. **光谱特征分析**
   - 主要特征峰的化学意义
   - 峰形和峰位的结构信息
   - 相对强度的意义

4. **结构信息推断**
   - 基于光谱数据的结构推断
   - 可能的化合物类型
   - 结构确认的建议
"""
        
        conclusion_prompt = """
5. **总结与建议**
   - 光谱质量评估
   - 主要结构特征总结
   - 进一步确认结构的建议
   - 可能需要的补充实验

请确保分析准确、专业，并使用标准的化学术语。
"""
        
        full_prompt = base_prompt + specific_prompt + conclusion_prompt
        
        if additional_context:
            full_prompt += f"\n\n**额外信息**: {additional_context}"
        
        return full_prompt
    
    def _build_vision_description_prompt(self, spectrum_type: str = "auto", additional_context: str = "") -> str:
        """构建视觉模型的光谱描述提示词（增强版）"""
        base_prompt = """
你是一个专业的光谱图像识别助手。请仔细观察这张光谱图，并提供极其详细和精确的描述。

请按以下格式提供详尽描述：

1. **光谱类型识别**
   - 识别这是什么类型的光谱（IR红外、NMR核磁、UV紫外、MS质谱、Raman拉曼等）
   - 详细说明识别依据（坐标轴标签、单位、数据范围、图形特征、典型特征等）
   - 置信度评估（高/中/低）

2. **坐标轴详细信息**
   - X轴：完整标签、精确单位、最小值、最大值、刻度间隔、是否为对数坐标
   - Y轴：完整标签、精确单位、最小值、最大值、刻度间隔、是否为对数坐标
   - 坐标轴字体大小、清晰度评估

3. **峰的详细位置和特征**
   - 按强度排序列出所有可识别的峰
   - 每个峰的精确位置（X轴数值，尽可能精确到小数点）
   - 每个峰的相对强度（百分比或相对值）
   - 峰的半峰宽估算
   - 峰形描述（尖锐/宽阔/对称/不对称/分裂/肩峰等）
   - 峰的基线情况

4. **定量数据分析**
   - 最强峰的位置和强度
   - 峰的数量统计
   - 强峰（>70%）、中等峰（30-70%）、弱峰（<30%）的分布
   - 峰密度分析（峰/单位区间）

5. **图谱质量详细评估**
   - 基线稳定性（平直/倾斜/波动）
   - 噪声水平（信噪比估算）
   - 分辨率评估（峰的分离度）
   - 整体图谱质量评分（优秀/良好/一般/较差）
   - 可能的仪器问题或样品问题

6. **文字和标注完整信息**
   - 图中所有可见文字的完整转录
   - 所有数值标注的精确记录
   - 图例、标题、样品信息
   - 仪器参数信息（如果可见）
   - 测试条件信息（如果可见）

7. **特殊特征识别**
   - 异常峰或杂质峰
   - 基线漂移或异常
   - 饱和峰或截断峰
   - 重叠峰的识别
   - 同位素峰或精细结构

请提供极其准确、详细的描述，重点关注所有可观察的数值信息和图形特征。描述应该详细到足以让专家进行深度分析。
"""
        
        if spectrum_type.lower() != "auto":
            base_prompt += f"\n\n**注意**: 用户指定这是{spectrum_type}光谱，请重点关注该类型光谱的特征。"
        
        if additional_context:
            base_prompt += f"\n\n**额外信息**: {additional_context}"
        
        return base_prompt
    
    def _build_deepseek_analysis_prompt(
        self,
        vision_description: str,
        spectrum_type: str = "auto",
        additional_context: str = ""
    ) -> str:
        """构建DeepSeek的专业分析提示词（增强验证版）"""
        base_prompt = f"""
基于以下光谱图像的详细描述，请进行严谨的化学光谱分析和数据验证：

**光谱描述**：
{vision_description}

请作为资深光谱分析专家，提供以下专业分析和严格验证：

## 1. 数据完整性验证与光谱类型确认
- **数据质量评估**：检查描述中的数据是否完整、一致、合理
- **光谱类型验证**：基于坐标轴、数据范围、峰特征严格验证光谱类型
- **坐标轴合理性检查**：验证X轴、Y轴的单位、范围是否符合该类型光谱的标准
- **数据一致性检查**：检查峰位置、强度数据是否内部一致
- **异常数据标识**：识别可能的数据错误或异常值
- 评估光谱质量和可分析性

## 2. 特征峰的深度分析与交叉验证
- **峰位置精度验证**：检查报告的峰位置是否在合理范围内
- **峰强度逻辑验证**：验证峰强度分布是否符合化学逻辑
- **峰形状合理性**：分析峰形状是否符合理论预期
- **峰数量统计验证**：检查峰数量是否与分子复杂度匹配
"""
        
        # 根据光谱类型添加专业分析内容和严格验证
        if "IR" in vision_description.upper() or "红外" in vision_description or spectrum_type.upper() == "IR":
            base_prompt += """
- **官能团特征峰严格识别**：
  * O-H伸缩振动（3200-3600 cm⁻¹）的位置和形状验证
  * N-H伸缩振动（3300-3500 cm⁻¹）的多重性分析
  * C-H伸缩振动（2800-3100 cm⁻¹）的精确归属
  * C=O伸缩振动（1650-1750 cm⁻¹）的环境效应分析
  * 指纹区（400-1500 cm⁻¹）的详细解析
- **峰位置理论验证**：每个归属峰是否在文献报道的合理范围内
- **强度比例合理性**：相对强度是否符合分子结构预期
- **峰形状物理意义**：尖锐度、分裂是否有合理的物理化学解释

## 3. 分子结构推断与验证
- **官能团组合逻辑**：推断的官能团组合是否化学合理
- **结构一致性检查**：所有光谱特征是否支持同一分子结构
- **分子式验证**：推断结构是否与可能的分子式匹配
- **异构体可能性**：考虑可能的同分异构体并给出区分依据
- **置信度量化评估**：给出结构确认的具体置信度（百分比）
"""
        elif "NMR" in vision_description.upper() or "核磁" in vision_description or spectrum_type.upper() == "NMR":
            base_prompt += """
- **化学位移精确分析与验证**：
  * δ值范围合理性检查（0-12 ppm典型范围）
  * 芳香质子（6-8 ppm）、烯烃质子（4.5-6.5 ppm）的准确识别
  * 甲基、亚甲基、次甲基的化学位移验证
  * 杂原子邻近效应的定量分析
- **积分比例严格验证**：积分面积是否与氢原子数目匹配
- **偶合模式深度解析**：
  * J值大小的合理性验证（典型范围0-20 Hz）
  * 偶合模式与分子结构的一致性检查
  * 远程偶合和复杂偶合的识别
- **13C NMR交叉验证**：如果有碳谱数据，进行氢谱碳谱一致性检查

## 3. 分子结构推断与验证
- **质子环境逻辑验证**：每个信号的化学环境推断是否合理
- **连接性网络构建**：基于偶合关系构建分子骨架
- **分子式匹配度**：推断结构与分子式的符合程度
- **立体化学考虑**：可能的立体异构体分析
- **结构确认置信度**：基于多重证据给出量化评估
"""
        elif "UV" in vision_description.upper() or "紫外" in vision_description or spectrum_type.upper() == "UV":
            base_prompt += """
- **吸收峰波长精确验证**：
  * λmax值的合理性检查（180-800 nm典型范围）
  * 苯环吸收（250-280 nm）的准确识别
  * 共轭体系吸收的红移效应验证
  * 溶剂效应对吸收波长的影响分析
- **摩尔吸光系数逻辑验证**：ε值是否与跃迁类型匹配
- **电子跃迁类型严格归属**：
  * π→π*跃迁（高强度，ε>10000）的识别验证
  * n→π*跃迁（低强度，ε<1000）的特征确认
  * 电荷转移跃迁的可能性分析
- **共轭体系定量分析**：共轭长度与吸收波长的关系验证

## 3. 分子结构推断与验证
- **发色团逻辑验证**：识别的发色团是否与吸收特征一致
- **助色团效应分析**：取代基对吸收的影响是否合理
- **分子轨道理论验证**：电子跃迁是否符合分子轨道理论
- **结构-光谱关系**：推断结构与UV吸收的定量关系
- **化合物类型置信度**：基于UV特征给出分子类型的确定性评估
"""
        else:
            base_prompt += """
- **光谱特征严格验证**：
  * 峰位置的物理化学合理性检查
  * 峰强度分布的逻辑一致性验证
  * 光谱基线和噪声水平评估
- **数据质量定量评估**：
  * 信噪比的具体数值估算
  * 分辨率是否满足分析要求
  * 可能的仪器误差识别
- **多重验证策略**：
  * 不同区域光谱特征的相互印证
  * 理论预期与实际观测的对比
  * 文献数据的交叉验证

## 3. 分子结构推断与验证
- **证据链构建**：建立从光谱特征到结构结论的完整逻辑链
- **不确定性量化**：明确指出分析中的不确定因素
- **替代解释评估**：考虑其他可能的结构解释
- **置信度分级**：给出高、中、低置信度的具体判断标准
"""
        
        base_prompt += """

## 4. 光谱质量评估与改进建议
- **质量等级量化评估**：
  * 信噪比评分（1-10分）
  * 分辨率评分（1-10分）
  * 基线稳定性评分（1-10分）
  * 整体质量综合评分（1-10分）
- **具体问题识别**：
  * 噪声来源分析（电子噪声、振动干扰等）
  * 基线漂移的可能原因
  * 峰形失真的技术原因
  * 样品制备问题的识别
- **改进建议具体化**：
  * 仪器参数优化建议（扫描次数、分辨率设置等）
  * 样品处理改进方案
  * 测试条件优化建议
  * 数据处理方法建议
- **补充分析策略**：
  * 推荐的互补光谱技术
  * 化学分析方法建议
  * 结构确认的额外实验

## 5. 总结与结论
- **主要发现摘要**：列出3-5个最重要的分析结论
- **置信度声明**：明确说明每个结论的可信度百分比
- **局限性说明**：诚实指出分析的局限性和不确定性
- **后续工作建议**：具体的进一步研究方向和实验建议
- **风险评估**：可能的误判风险和规避策略

请确保分析准确、专业，使用标准的化学术语，并基于光谱数据提供合理的结构推断。
"""
        
        if additional_context:
            base_prompt += f"\n\n**额外背景信息**: {additional_context}"
        
        return base_prompt

    async def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """提取关键词"""
        try:
            keywords_prompt = f"""
请从以下化学文本中提取{max_keywords}个最重要的关键词，用逗号分隔：

{text}

关键词：
"""
            
            response = await self.generate_response(
                query=keywords_prompt,
                context="",
                max_tokens=100,
                temperature=0.1
            )
            
            # 解析关键词
            keywords = [kw.strip() for kw in response.split(',')]
            return keywords[:max_keywords]
            
        except Exception as e:
            logger.error(f"提取关键词失败: {str(e)}")
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """获取模型信息"""
        return {
            "model_type": "OpenAI" if self.text_client else "Local",
            "model_name": settings.LLM_MODEL,
            "api_configured": bool(settings.OPENAI_API_KEY),
            "local_model_loaded": bool(self.model and self.tokenizer)
        }
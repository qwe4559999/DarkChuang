from typing import Optional, Dict, Any, List
import asyncio
from app.core.config import settings
from loguru import logger
import openai
import base64

class LLMService:
    """大语言模型服务 - 支持GLM-4.6V单模型架构"""

    def __init__(self):
        self.client = None
        self._initialize()

    def _initialize(self):
        """初始化LLM服务"""
        try:
            logger.info("初始化GLM-4.6V单模型LLM服务...")

            # 使用SiliconFlow或其他兼容OpenAI的API
            api_key = getattr(settings, 'SILICONFLOW_API_KEY', '') or getattr(settings, 'LLM_API_KEY', '')
            base_url = getattr(settings, 'SILICONFLOW_API_BASE', '') or getattr(settings, 'LLM_BASE_URL', '')

            if api_key:
                self.client = openai.AsyncOpenAI(
                    api_key=api_key,
                    base_url=base_url
                )
                model_name = getattr(settings, 'UNIFIED_MODEL_NAME', 'zai-org/GLM-4.6V')
                logger.info(f"LLM客户端初始化完成，使用模型: {model_name}")
            else:
                logger.warning("未检测到API Key，请配置SILICONFLOW_API_KEY")

        except Exception as e:
            logger.error(f"LLM服务初始化失败: {str(e)}")
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
            if not self.client:
                return "API未配置，无法生成回答"

            # 构建提示词
            system_prompt = self._build_system_prompt()
            user_prompt = self._build_user_prompt(query, context)

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]

            # 调用API
            model_name = getattr(settings, 'UNIFIED_MODEL_NAME', 'zai-org/GLM-4.6V')
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=False
            )

            content = response.choices[0].message.content
            
            # 清理可能出现的特殊标记
            if content:
                content = content.replace("<|begin_of_box|>", "").replace("<|end_of_box|>", "")

            return content

        except Exception as e:
            logger.error(f"生成回答失败: {str(e)}")
            return f"生成回答时发生错误: {str(e)}"

    async def analyze_image(
        self,
        image_path: str,
        prompt: str
    ) -> str:
        """Generic image analysis using VLM"""
        try:
            if not self.client:
                return "API not configured."

            # Read and encode image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
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

            model_name = getattr(settings, 'UNIFIED_MODEL_NAME', 'zai-org/GLM-4.6V')
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=2000,
                temperature=0.5
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            return f"Error analyzing image: {str(e)}"

    async def analyze_spectrum_image(
        self,
        image_path: str,
        spectrum_type: str = "auto",
        additional_context: str = ""
    ) -> str:
        """使用多模态模型直接分析光谱图像"""
        try:
            if not self.client:
                return "模型API未配置，无法进行图谱分析"

            logger.info(f"开始使用多模态模型分析光谱图像: {image_path}")

            # 读取并编码图像
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')

            # 构建提示词
            prompt = self._build_spectrum_prompt(spectrum_type, additional_context)

            # 构建多模态消息
            messages = [
                {
                    "role": "system",
                    "content": "你是一位资深的化学光谱分析专家，具有丰富的光谱解析经验。请基于图像内容进行专业分析。"
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
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

            model_name = getattr(settings, 'UNIFIED_MODEL_NAME', 'zai-org/GLM-4.6V')
            response = await self.client.chat.completions.create(
                model=model_name,
                messages=messages,
                max_tokens=3000,
                temperature=0.1 # 低温度以保证准确性
            )

            analysis_result = response.choices[0].message.content
            logger.info(f"光谱分析完成，结果长度: {len(analysis_result)}")

            return analysis_result

        except Exception as e:
            logger.error(f"光谱图像分析失败: {str(e)}")
            return f"光谱分析失败: {str(e)}"

    def _build_system_prompt(self) -> str:
        return """你是一个专业的化学问答助手。
1. 精通有机、无机、物理、分析化学等领域。
2. 提供准确、安全、教育性的回答。
3. 始终使用中文回答。
4. 涉及危险化学品时必须提示安全风险。
5. 当用户询问某个分子的结构、属性或要求绘制分子结构时，请以JSON格式输出工具调用请求。
6. 当用户提供纯文本的光谱数据（如NMR峰值列表）并要求分析时，也请输出工具调用请求。格式如下：
```json
{
    "tool": "spectrum_tool",
    "action": "analyze_peaks",
    "peaks": [170.5, 23.1, ...],
    "hint": "用户提供的额外信息（如分子式）"
}
```
工具调用通用格式：
```json
{
    "tool": "chemistry_tool",
    "action": "calculate_properties",
    "molecule": "Methamphetamine"
}
```
或者
```json
{
    "tool": "chemistry_tool",
    "action": "generate_structure_image",
    "molecule": "Methamphetamine"
}
```
或者
```json
{
    "tool": "chemistry_tool",
    "action": "generate_3d_structure",
    "molecule": "Methamphetamine"
}
```
**重要提示：如果用户使用中文化学名称，请尽你所能将其翻译为标准的英文化学名称或SMILES字符串放在`molecule`字段中，以确保查询成功。**
**如果用户明确要求查看3D结构、立体结构或空间构型，请优先使用 `generate_3d_structure`。**
不要输出任何其他文本，只输出JSON。
"""

    def _build_user_prompt(self, query: str, context: str) -> str:
        if context:
            return f"基于上下文：\n{context}\n\n回答问题：\n{query}"
        else:
            return f"请回答化学问题：\n{query}"

    def _build_spectrum_prompt(self, spectrum_type: str, additional_context: str = "") -> str:
        base = f"""请仔细分析这张{spectrum_type if spectrum_type != 'auto' else ''}光谱图。
请按以下结构输出报告：
1. **类型识别**：这是什么光谱（IR/NMR/MS/UV等）？依据是什么？
2. **特征峰分析**：列出关键峰的位置、强度和可能的归属。
3. **结构推断**：基于特征峰推断可能的分子结构或官能团。
4. **总结**：综合分析结论。
"""
        if additional_context:
            base += f"\n额外信息：{additional_context}"
        return base

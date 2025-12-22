# API配置说明

## 核心模型配置 (SiliconFlow)

本项目目前统一使用 **SiliconFlow (硅基流动)** 提供的 API 服务，主要使用 **GLM-4.6V** (或 GLM-4V-Plus) 作为核心多模态模型，同时处理文本对话、化学推理和图像分析任务。

### 配置步骤

1. **复制环境变量文件**
   `ash
   cp .env.example .env
   `

2. **配置 SiliconFlow API 密钥**
   
   编辑 .env 文件，填入您的 API 密钥：
   
   `nv
   # SiliconFlow API 配置 (核心)
   SILICONFLOW_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   SILICONFLOW_API_BASE=https://api.siliconflow.cn/v1
   
   # 模型配置
   UNIFIED_MODEL_NAME=zai-org/GLM-4.6V
   SILICONFLOW_EMBEDDING_MODEL=BAAI/bge-m3
   `

3. **获取 API 密钥**
   
   - 访问 [SiliconFlow 官网](https://siliconflow.cn/) 注册并获取 API Key。
   - 确保账号有足够的余额或免费额度。

### 功能说明

- **SILICONFLOW_API_KEY**: 用于所有 AI 功能，包括：
    - **Agentic NMR 分析**: 视觉识别谱图 + 逻辑推理。
    - **RAG 问答**: 文本生成与推理。
    - **通用对话**: 处理日常化学问答。
- **SILICONFLOW_EMBEDDING_MODEL**: 用于 RAG 知识库的向量化 (Embedding)。

### 历史配置 (已弃用)

以下配置仅在旧版本中使用，v2.1+ 版本已不再强制依赖：

- VISION_API_KEY (Qwen)
- LLM_API_KEY (DeepSeek)

### 注意事项

1. **API密钥安全**: 请妥善保管您的API密钥，不要将其提交到版本控制系统。
2. **模型名称**: UNIFIED_MODEL_NAME 可以根据 SiliconFlow 的可用模型列表进行调整 (如 GLM-4V-Plus)。

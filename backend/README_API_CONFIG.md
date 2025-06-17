# API配置说明

## 光谱分析功能配置

为了使用光谱图像的自动识别和分析功能，您需要配置视觉模型的API密钥。

### 配置步骤

1. **复制环境变量文件**
   ```bash
   cp .env.example .env
   ```

2. **配置视觉模型API密钥**
   
   编辑 `.env` 文件，填入您的API密钥：
   
   ```env
   # Qwen2.5-VL视觉模型配置（光谱分析必需）
   VISION_API_KEY=your_qwen_api_key_here
   VISION_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
   VISION_MODEL=Qwen/Qwen2.5-VL-72B-Instruct
   ```

3. **获取API密钥**
   
   - **阿里云DashScope（推荐）**: 访问 [https://dashscope.console.aliyun.com/](https://dashscope.console.aliyun.com/) 获取API密钥
   - 注册账号并创建API密钥
   - 确保账号有足够的余额或免费额度

4. **可选：配置文本模型**
   
   如果您想使用DeepSeek-R1作为文本模型：
   
   ```env
   # DeepSeek-R1文本模型配置（可选）
   LLM_API_KEY=your_deepseek_api_key_here
   LLM_BASE_URL=https://api.deepseek.com/v1
   ```

### 功能说明

- **视觉模型（VISION_API_KEY）**: 用于光谱图像分析，支持自动识别谱图类型（IR、NMR、UV等）
- **文本模型（LLM_API_KEY）**: 用于文本问答和分析结果处理
- **OpenAI兼容（OPENAI_API_KEY）**: 兼容OpenAI API的模型

### 注意事项

1. **API密钥安全**: 请妥善保管您的API密钥，不要将其提交到版本控制系统
2. **费用控制**: 使用API会产生费用，请注意控制使用量
3. **网络连接**: 确保服务器能够访问相应的API端点

### 故障排除

如果遇到"视觉模型未配置"错误：

1. 检查 `.env` 文件中的 `VISION_API_KEY` 是否正确填写
2. 确认API密钥是否有效且有足够余额
3. 检查网络连接是否正常
4. 重启后端服务以加载新的配置

### 重启服务

配置完成后，重启后端服务：

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
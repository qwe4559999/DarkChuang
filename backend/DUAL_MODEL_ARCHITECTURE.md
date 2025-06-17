# 双模型光谱分析架构说明

## 概述

本系统采用双模型架构进行光谱分析，充分发挥不同模型的优势：

- **Qwen2.5-VL-72B-Instruct**: 负责图像识别和描述
- **DeepSeek-R1**: 负责专业化学分析和解释

## 架构设计

### 1. 分工明确

#### Qwen2.5-VL (视觉模型)
- **职责**: 图像识别和客观描述
- **输入**: 光谱图像文件
- **输出**: 详细的图像描述，包括：
  - 光谱类型识别
  - 坐标轴信息
  - 峰的位置和特征
  - 图谱质量评估
  - 文字和标注信息

#### DeepSeek-R1 (文本模型)
- **职责**: 专业化学分析和解释
- **输入**: Qwen2.5-VL的描述结果
- **输出**: 专业的化学分析，包括：
  - 特征峰的化学意义
  - 分子结构推断
  - 官能团识别
  - 化合物类型判断

### 2. 工作流程

```
光谱图像 → Qwen2.5-VL → 图像描述 → DeepSeek-R1 → 专业分析报告
```

#### 详细步骤：

1. **图像预处理**
   - 读取光谱图像文件
   - Base64编码
   - 构建视觉描述提示词

2. **视觉识别阶段**
   - Qwen2.5-VL分析图像
   - 识别光谱类型
   - 提取数值信息
   - 描述图形特征

3. **专业解析阶段**
   - DeepSeek-R1接收描述
   - 进行化学专业分析
   - 推断分子结构
   - 生成综合报告

## 技术实现

### 核心方法

#### `analyze_spectrum_image()`
主入口方法，协调整个分析流程：

```python
async def analyze_spectrum_image(
    self,
    image_path: str,
    spectrum_type: str = "auto",
    additional_context: str = ""
) -> str:
    # 第一步：视觉描述
    vision_description = await self._describe_spectrum_with_vision(
        image_path, spectrum_type, additional_context
    )
    
    # 第二步：专业解析
    if self.text_client:  # 如果有DeepSeek
        final_analysis = await self._analyze_spectrum_with_deepseek(
            vision_description, spectrum_type, additional_context
        )
        return final_analysis
    else:
        # 降级处理：仅返回视觉描述
        return vision_description
```

#### `_describe_spectrum_with_vision()`
视觉模型描述方法：

```python
async def _describe_spectrum_with_vision(
    self,
    image_path: str,
    spectrum_type: str = "auto",
    additional_context: str = ""
) -> str:
    # 构建简化的描述提示词
    description_prompt = self._build_vision_description_prompt(
        spectrum_type, additional_context
    )
    
    # 调用Qwen2.5-VL
    response = await self.vision_client.chat.completions.create(
        model=settings.VISION_MODEL,
        messages=messages,
        max_tokens=1500,
        temperature=0.2
    )
```

#### `_analyze_spectrum_with_deepseek()`
DeepSeek专业分析方法：

```python
async def _analyze_spectrum_with_deepseek(
    self,
    vision_description: str,
    spectrum_type: str = "auto",
    additional_context: str = ""
) -> str:
    # 构建专业分析提示词
    analysis_prompt = self._build_deepseek_analysis_prompt(
        vision_description, spectrum_type, additional_context
    )
    
    # 调用DeepSeek
    response = await self.text_client.chat.completions.create(
        model=self.model,
        messages=[
            {"role": "system", "content": "专家系统提示"},
            {"role": "user", "content": analysis_prompt}
        ],
        max_tokens=3000,
        temperature=0.1
    )
```

### 提示词设计

#### 视觉描述提示词
- 重点关注客观描述
- 避免化学解释
- 详细记录数值信息
- 识别图形特征

#### 专业分析提示词
- 基于描述进行化学分析
- 根据光谱类型定制分析内容
- 提供结构推断
- 评估分析置信度

## 配置要求

### 环境变量

```bash
# Qwen2.5-VL视觉模型配置（必需）
VISION_API_KEY=your_vision_api_key
VISION_BASE_URL=https://api.siliconflow.cn/v1
VISION_MODEL=Qwen/Qwen2.5-VL-72B-Instruct

# DeepSeek文本模型配置（推荐）
LLM_API_KEY=your_llm_api_key
LLM_BASE_URL=https://api.siliconflow.cn/v1
LLM_MODEL=deepseek-ai/DeepSeek-R1-Distill-Qwen-32B
```

### 降级策略

如果DeepSeek未配置，系统会：
1. 仅使用Qwen2.5-VL进行描述
2. 返回视觉描述结果
3. 提示用户配置DeepSeek以获得专业分析

## 优势分析

### 1. 专业化分工
- **视觉模型**: 专注图像理解，避免化学知识不足
- **文本模型**: 专注化学分析，利用专业知识库

### 2. 提高准确性
- 减少视觉模型的化学推理负担
- 利用DeepSeek的专业化学知识
- 分步验证，降低错误率

### 3. 可扩展性
- 可以独立优化各模型的提示词
- 支持不同光谱类型的定制化分析
- 便于添加新的分析步骤

### 4. 容错性
- 支持降级处理
- 模块化设计，便于调试
- 详细的日志记录

## 测试和验证

### 测试脚本
使用 `test_dual_model_spectrum.py` 进行测试：

```bash
cd backend
python test_dual_model_spectrum.py
```

### 测试模式
1. **完整双模型分析**: 测试完整流程
2. **仅视觉描述**: 测试视觉模型单独工作

### 输出文件
- `spectrum_analysis_result.md`: 完整分析结果
- `vision_description_only.md`: 仅视觉描述结果

## 性能优化

### 1. 参数调优
- **视觉模型**: `temperature=0.2`, `max_tokens=1500`
- **文本模型**: `temperature=0.1`, `max_tokens=3000`

### 2. 提示词优化
- 视觉提示词简洁明确
- 分析提示词结构化
- 根据光谱类型定制内容

### 3. 错误处理
- 完善的异常捕获
- 降级处理机制
- 详细的错误日志

## 未来扩展

### 1. 多模型支持
- 支持更多视觉模型
- 支持更多文本模型
- 模型性能对比

### 2. 结果优化
- 结构化输出格式
- 置信度评估
- 多轮对话优化

### 3. 专业化定制
- 特定领域的提示词
- 行业标准的分析流程
- 自定义分析模板

## 总结

双模型架构充分发挥了不同AI模型的优势，通过专业化分工提高了光谱分析的准确性和专业性。Qwen2.5-VL负责准确的图像识别和描述，DeepSeek-R1负责深度的化学分析和解释，两者协作提供了更可靠、更专业的光谱分析服务。
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单模型光谱分析测试脚本 (GLM-4.6V)
"""

import asyncio
import sys
import os
from pathlib import Path
import logging

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from app.services.llm_service import LLMService
from app.core.config import settings

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_single_model_analysis():
    """
    测试单模型光谱分析功能
    """
    print("=" * 60)
    print("单模型(GLM-4.6V)光谱分析测试")
    print("=" * 60)

    # 初始化服务
    print("\n1. 初始化LLM服务...")
    try:
        llm_service = LLMService()
        print("   ✅ LLM服务初始化成功")

        # 检查模型状态
        model_info = llm_service.client
        print(f"   模型客户端: {'已配置' if model_info else '未配置'}")

    except Exception as e:
        print(f"   ❌ LLM服务初始化失败: {e}")
        return

    # 测试图像路径（需要用户提供实际的光谱图像）
    test_image_path = "./test_spectrum.png"  # 用户需要提供测试图像

    if not os.path.exists(test_image_path):
        print(f"\n⚠️  测试图像不存在: {test_image_path}")
        print("   请将光谱图像文件命名为 'test_spectrum.png' 并放在当前目录")
        return

    print(f"\n2. 开始分析光谱图像: {test_image_path}")

    try:
        # 测试分析
        print("\n   📊 正在进行多模态分析...")
        result = await llm_service.analyze_spectrum_image(
            image_path=test_image_path,
            spectrum_type="auto",
            additional_context="这是一个测试样本"
        )

        print("\n   ✅ 分析完成")
        print("   结果预览:")
        print("   " + "="*50)
        # 显示结果的前500个字符
        preview = result[:500] + "..." if len(result) > 500 else result
        for line in preview.split('\n'):
            print(f"   {line}")
        print("   " + "="*50)

        # 保存完整结果
        output_file = "spectrum_analysis_result.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 光谱分析结果\n\n")
            f.write(f"**分析时间**: {asyncio.get_event_loop().time()}\n\n")
            f.write(f"**图像路径**: {test_image_path}\n\n")
            f.write(f"**模型**: {getattr(settings, 'UNIFIED_MODEL_NAME', 'unknown')}\n\n")
            f.write("## 分析结果\n\n")
            f.write(result)

        print(f"\n   📄 完整结果已保存到: {output_file}")

    except Exception as e:
        print(f"\n   ❌ 光谱分析失败: {e}")
        logger.exception("光谱分析异常")
        return

    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)

if __name__ == "__main__":
    if not os.path.exists("./test_spectrum.png"):
        print("警告: 缺少测试图片 test_spectrum.png")
    asyncio.run(test_single_model_analysis())

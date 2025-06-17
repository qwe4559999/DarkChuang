#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
双模型光谱分析测试脚本
测试 Qwen2.5-VL + DeepSeek 的光谱分析流程
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from app.services.llm_service import LLMService
from app.core.config import settings
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_dual_model_spectrum_analysis():
    """
    测试双模型光谱分析功能
    """
    print("=" * 60)
    print("双模型光谱分析测试")
    print("=" * 60)
    
    # 检查配置
    print("\n1. 检查配置:")
    print(f"   VISION_API_KEY: {'已配置' if settings.VISION_API_KEY else '未配置'}")
    print(f"   VISION_BASE_URL: {settings.VISION_BASE_URL}")
    print(f"   VISION_MODEL: {settings.VISION_MODEL}")
    print(f"   LLM_API_KEY: {'已配置' if settings.LLM_API_KEY else '未配置'}")
    print(f"   LLM_BASE_URL: {settings.LLM_BASE_URL}")
    print(f"   LLM_MODEL: {settings.LLM_MODEL}")
    
    if not settings.VISION_API_KEY:
        print("\n❌ 错误: VISION_API_KEY 未配置")
        return
    
    # 初始化服务
    print("\n2. 初始化LLM服务...")
    try:
        llm_service = LLMService()
        print("   ✅ LLM服务初始化成功")
        
        # 检查模型状态
        model_info = llm_service.get_model_info()
        print(f"   视觉模型: {'已配置' if llm_service.vision_client else '未配置'}")
        print(f"   文本模型: {'已配置' if llm_service.client else '未配置'}")
        
    except Exception as e:
        print(f"   ❌ LLM服务初始化失败: {e}")
        return
    
    # 测试图像路径（需要用户提供实际的光谱图像）
    test_image_path = "./test_spectrum.png"  # 用户需要提供测试图像
    
    if not os.path.exists(test_image_path):
        print(f"\n⚠️  测试图像不存在: {test_image_path}")
        print("   请将光谱图像文件命名为 'test_spectrum.png' 并放在当前目录")
        print("   或修改 test_image_path 变量指向实际的图像文件")
        return
    
    print(f"\n3. 开始分析光谱图像: {test_image_path}")
    
    try:
        # 测试自动识别模式
        print("\n   📊 测试自动识别模式...")
        result_auto = await llm_service.analyze_spectrum_image(
            image_path=test_image_path,
            spectrum_type="auto",
            additional_context="这是一个测试样本"
        )
        
        print("\n   ✅ 自动识别分析完成")
        print("   结果预览:")
        print("   " + "="*50)
        # 显示结果的前500个字符
        preview = result_auto[:500] + "..." if len(result_auto) > 500 else result_auto
        for line in preview.split('\n'):
            print(f"   {line}")
        print("   " + "="*50)
        
        # 保存完整结果
        output_file = "spectrum_analysis_result.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# 光谱分析结果\n\n")
            f.write(f"**分析时间**: {asyncio.get_event_loop().time()}\n\n")
            f.write(f"**图像路径**: {test_image_path}\n\n")
            f.write(f"**分析模式**: 自动识别\n\n")
            f.write("## 分析结果\n\n")
            f.write(result_auto)
        
        print(f"\n   📄 完整结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"\n   ❌ 光谱分析失败: {e}")
        logger.exception("光谱分析异常")
        return
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60)

async def test_vision_description_only():
    """
    测试仅视觉描述功能（不使用DeepSeek）
    """
    print("\n=" * 60)
    print("测试仅视觉描述功能")
    print("=" * 60)
    
    llm_service = LLMService()
    test_image_path = "./test_spectrum.png"
    
    if not os.path.exists(test_image_path):
        print(f"测试图像不存在: {test_image_path}")
        return
    
    try:
        # 直接调用视觉描述方法
        description = await llm_service._describe_spectrum_with_vision(
            image_path=test_image_path,
            spectrum_type="auto"
        )
        
        print("\n视觉描述结果:")
        print("="*50)
        print(description)
        print("="*50)
        
        # 保存描述结果
        with open("vision_description_only.md", 'w', encoding='utf-8') as f:
            f.write("# 视觉描述结果\n\n")
            f.write(description)
        
        print("\n描述结果已保存到: vision_description_only.md")
        
    except Exception as e:
        print(f"视觉描述失败: {e}")
        logger.exception("视觉描述异常")

def main():
    """
    主函数
    """
    print("双模型光谱分析测试工具")
    print("请确保:")
    print("1. 已配置 VISION_API_KEY 和 LLM_API_KEY")
    print("2. 在当前目录放置测试光谱图像 'test_spectrum.png'")
    print("3. 网络连接正常")
    
    choice = input("\n选择测试模式:\n1. 完整双模型分析\n2. 仅视觉描述\n请输入选择 (1/2): ").strip()
    
    if choice == "1":
        asyncio.run(test_dual_model_spectrum_analysis())
    elif choice == "2":
        asyncio.run(test_vision_description_only())
    else:
        print("无效选择")

if __name__ == "__main__":
    main()
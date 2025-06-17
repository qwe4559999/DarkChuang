#!/usr/bin/env python3
"""
光谱分析功能测试脚本

这个脚本用于测试新集成的DeepSeek-R1和Qwen2.5-VL-72B-Instruct模型
在光谱识别方面的功能。
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from app.services.llm_service import LLMService
from app.services.spectrum_service import SpectrumAnalysisService
from app.services.image_service import ImageService
from loguru import logger

async def test_llm_service():
    """测试LLM服务的基本功能"""
    print("\n=== 测试LLM服务 ===")
    
    try:
        llm_service = LLMService()
        
        # 测试文本生成
        response = await llm_service.generate_response(
            "请简单介绍一下红外光谱的基本原理。",
            context="化学分析"
        )
        
        print(f"✅ LLM文本生成测试成功")
        print(f"响应: {response[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM服务测试失败: {str(e)}")
        return False

async def test_spectrum_service():
    """测试光谱分析服务"""
    print("\n=== 测试光谱分析服务 ===")
    
    try:
        spectrum_service = SpectrumAnalysisService()
        
        # 检查支持的光谱类型
        supported_types = spectrum_service.get_supported_spectrum_types()
        print(f"✅ 支持的光谱类型: {supported_types}")
        
        # 检查支持的图像格式
        supported_formats = spectrum_service.get_supported_formats()
        print(f"✅ 支持的图像格式: {supported_formats}")
        
        return True
        
    except Exception as e:
        print(f"❌ 光谱分析服务测试失败: {str(e)}")
        return False

async def test_image_service():
    """测试图像服务"""
    print("\n=== 测试图像服务 ===")
    
    try:
        image_service = ImageService()
        
        # 检查支持的光谱类型
        spectrum_types = image_service.get_supported_spectrum_types()
        print(f"✅ 图像服务支持的光谱类型: {spectrum_types}")
        
        # 检查支持的图像格式
        image_formats = image_service.get_supported_image_formats()
        print(f"✅ 图像服务支持的格式: {image_formats}")
        
        return True
        
    except Exception as e:
        print(f"❌ 图像服务测试失败: {str(e)}")
        return False

async def test_spectrum_analysis_with_sample():
    """使用示例图像测试光谱分析（如果有的话）"""
    print("\n=== 测试光谱分析功能 ===")
    
    try:
        # 创建一个测试用的示例图像路径
        # 注意：这里只是演示，实际需要真实的光谱图像
        sample_image_path = "./test_spectrum_image.jpg"
        
        if not os.path.exists(sample_image_path):
            print("⚠️  没有找到测试图像文件，跳过实际分析测试")
            print("   如需完整测试，请将光谱图像文件放置在: test_spectrum_image.jpg")
            return True
        
        image_service = ImageService()
        
        # 测试光谱分析
        result = await image_service.analyze_spectrum_image(
            image_path=sample_image_path,
            spectrum_type="IR",
            additional_info="这是一个测试用的红外光谱图像"
        )
        
        if result['success']:
            print("✅ 光谱分析测试成功")
            print(f"分析结果: {result.get('parsed_result', {}).get('spectrum_type', 'N/A')}")
        else:
            print(f"❌ 光谱分析失败: {result.get('error', '未知错误')}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 光谱分析功能测试失败: {str(e)}")
        return False

async def test_configuration():
    """测试配置"""
    print("\n=== 测试配置 ===")
    
    try:
        from app.core.config import settings
        
        # 检查关键配置
        config_items = [
            ('SILICONFLOW_API_KEY', getattr(settings, 'SILICONFLOW_API_KEY', None)),
            ('SILICONFLOW_API_BASE', getattr(settings, 'SILICONFLOW_API_BASE', None)),
            ('SILICONFLOW_CHAT_MODEL', getattr(settings, 'SILICONFLOW_CHAT_MODEL', None)),
            ('SILICONFLOW_VISION_MODEL', getattr(settings, 'SILICONFLOW_VISION_MODEL', None)),
        ]
        
        all_configured = True
        for key, value in config_items:
            if value:
                print(f"✅ {key}: 已配置")
            else:
                print(f"❌ {key}: 未配置")
                all_configured = False
        
        return all_configured
        
    except Exception as e:
        print(f"❌ 配置测试失败: {str(e)}")
        return False

async def main():
    """主测试函数"""
    print("🧪 开始测试DarkChuang光谱分析功能")
    print("=" * 50)
    
    test_results = []
    
    # 运行各项测试
    test_results.append(await test_configuration())
    test_results.append(await test_llm_service())
    test_results.append(await test_spectrum_service())
    test_results.append(await test_image_service())
    test_results.append(await test_spectrum_analysis_with_sample())
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    
    passed_tests = sum(test_results)
    total_tests = len(test_results)
    
    print(f"通过测试: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！光谱分析功能已成功集成")
    else:
        print("⚠️  部分测试失败，请检查配置和依赖")
    
    print("\n📝 使用说明:")
    print("1. 确保在.env文件中配置了SILICONFLOW_API_KEY")
    print("2. 启动服务: python -m uvicorn app.main:app --reload")
    print("3. 访问API文档: http://localhost:8000/docs")
    print("4. 使用光谱分析API: POST /api/v1/spectrum/analyze")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    # 运行测试
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
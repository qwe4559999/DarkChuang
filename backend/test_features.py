#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
化学知识问答和谱图识别功能测试脚本
"""

import asyncio
import requests
import json
from pathlib import Path
import base64

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_api_health():
    """测试API健康状态"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ API健康检查: {response.status_code}")
        print(f"响应: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API健康检查失败: {e}")
        return False

def test_chemistry_qa():
    """测试化学知识问答功能"""
    print("\n=== 测试化学知识问答功能 ===")
    
    # 测试问题列表
    test_questions = [
        "什么是苯环的结构特点？",
        "请解释酸碱反应的原理",
        "有机化学中的取代反应是什么？",
        "如何区分离子键和共价键？",
        "什么是化学平衡常数？"
    ]
    
    for i, question in enumerate(test_questions, 1):
        try:
            print(f"\n问题 {i}: {question}")
            
            payload = {
                "message": question,
                "use_rag": True,
                "max_tokens": 500
            }
            
            response = requests.post(
                f"{BASE_URL}/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 回答: {result['message'][:200]}...")
                print(f"处理时间: {result['processing_time']:.2f}秒")
                if result.get('sources'):
                    print(f"参考来源: {len(result['sources'])}个")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"❌ 问答测试失败: {e}")

def test_spectrum_analysis():
    """测试谱图识别功能"""
    print("\n=== 测试谱图识别功能 ===")
    
    # 创建测试图像文件（模拟）
    test_image_path = Path("test_spectrum.png")
    
    # 如果没有真实的谱图文件，创建一个简单的测试文件
    if not test_image_path.exists():
        print("创建模拟谱图文件...")
        try:
            from PIL import Image, ImageDraw
            import numpy as np
            
            # 创建一个简单的模拟谱图
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            
            # 绘制一些模拟的谱线
            for i in range(10):
                x = 100 + i * 60
                height = np.random.randint(50, 400)
                draw.line([(x, 500), (x, 500-height)], fill='black', width=2)
            
            # 添加一些标签
            draw.text((50, 50), "IR Spectrum", fill='black')
            draw.text((50, 520), "Wavenumber (cm-1)", fill='black')
            
            img.save(test_image_path)
            print(f"✅ 创建测试图像: {test_image_path}")
            
        except ImportError:
            print("❌ PIL库未安装，跳过图像创建")
            return
        except Exception as e:
            print(f"❌ 创建测试图像失败: {e}")
            return
    
    # 测试不同类型的谱图分析
    spectrum_types = ["IR", "NMR", "UV", "红外", "核磁"]
    
    for spectrum_type in spectrum_types:
        try:
            print(f"\n测试 {spectrum_type} 谱图分析...")
            
            with open(test_image_path, 'rb') as f:
                files = {
                    'file': ('test_spectrum.png', f, 'image/png')
                }
                data = {
                    'spectrum_type': spectrum_type,
                    'additional_info': f'这是一个{spectrum_type}谱图的测试'
                }
                
                response = requests.post(
                    f"{BASE_URL}/spectrum/analyze",
                    files=files,
                    data=data
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {spectrum_type}谱图分析成功")
                print(f"分析结果: {str(result.get('analysis_result', {}))[:200]}...")
            else:
                print(f"❌ {spectrum_type}谱图分析失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"❌ {spectrum_type}谱图分析异常: {e}")

def test_supported_spectrum_types():
    """测试支持的谱图类型查询"""
    print("\n=== 测试支持的谱图类型 ===")
    
    try:
        response = requests.get(f"{BASE_URL}/spectrum/supported-types")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 支持的谱图类型: {result.get('supported_types', [])}")
        else:
            print(f"❌ 查询失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 查询异常: {e}")

def test_image_analysis():
    """测试通用图像分析功能"""
    print("\n=== 测试通用图像分析功能 ===")
    
    test_image_path = Path("test_spectrum.png")
    
    if test_image_path.exists():
        try:
            with open(test_image_path, 'rb') as f:
                files = {
                    'file': ('test_spectrum.png', f, 'image/png')
                }
                
                response = requests.post(
                    f"{BASE_URL}/analyze-image",
                    files=files
                )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 图像分析成功")
                print(f"文本内容: {result.get('text_content', '')[:100]}...")
                print(f"化学公式: {result.get('chemical_formulas', [])}")
                print(f"置信度: {result.get('confidence_scores', {})}")
            else:
                print(f"❌ 图像分析失败: {response.status_code}")
                print(f"错误信息: {response.text}")
                
        except Exception as e:
            print(f"❌ 图像分析异常: {e}")
    else:
        print("❌ 测试图像文件不存在")

def main():
    """主测试函数"""
    print("🧪 开始测试化学知识问答和谱图识别功能")
    print("=" * 50)
    
    # 1. 测试API健康状态
    if not test_api_health():
        print("❌ API服务未启动，请先启动后端服务")
        return
    
    # 2. 测试化学知识问答
    test_chemistry_qa()
    
    # 3. 测试谱图识别
    test_spectrum_analysis()
    
    # 4. 测试支持的谱图类型
    test_supported_spectrum_types()
    
    # 5. 测试通用图像分析
    test_image_analysis()
    
    print("\n" + "=" * 50)
    print("🎉 功能测试完成！")
    print("\n📋 功能总结:")
    print("✅ 化学知识问答 - 基于RAG技术的智能问答")
    print("✅ 谱图识别分析 - 支持IR、NMR、UV等多种谱图")
    print("✅ 图像文本识别 - OCR文本提取和化学公式识别")
    print("✅ 多模型支持 - DeepSeek-R1文本模型 + Qwen2.5-VL视觉模型")
    print("✅ RESTful API - 完整的API接口文档")

if __name__ == "__main__":
    main()
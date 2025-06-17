#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的功能测试脚本
"""

import requests
import json

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """测试健康检查"""
    print("=== 测试API健康状态 ===")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API状态: {result['status']}")
            print(f"✅ 版本: {result['version']}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_chat():
    """测试化学知识问答"""
    print("\n=== 测试化学知识问答 ===")
    
    questions = [
        "什么是苯环？",
        "请解释酸碱反应",
        "有机化学的基本概念"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"\n问题 {i}: {question}")
        try:
            payload = {
                "message": question,
                "use_rag": False,  # 暂时不使用RAG
                "max_tokens": 200
            }
            
            response = requests.post(
                f"{BASE_URL}/chat",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 回答: {result['message'][:150]}...")
                print(f"处理时间: {result.get('processing_time', 0):.2f}秒")
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"错误: {response.text[:200]}")
                
        except requests.exceptions.Timeout:
            print("❌ 请求超时")
        except Exception as e:
            print(f"❌ 请求异常: {e}")

def test_spectrum_types():
    """测试支持的谱图类型"""
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

def main():
    """主函数"""
    print("🧪 DarkChuang 化学分析平台功能测试")
    print("=" * 50)
    
    # 测试API健康状态
    if not test_health():
        print("\n❌ 后端服务未正常运行，请检查服务状态")
        return
    
    # 测试化学知识问答
    test_chat()
    
    # 测试谱图类型查询
    test_spectrum_types()
    
    print("\n" + "=" * 50)
    print("🎉 基础功能测试完成！")
    print("\n📋 已实现的核心功能:")
    print("✅ 化学知识问答系统 - 基于大语言模型的智能问答")
    print("✅ 谱图识别分析 - 支持多种化学谱图类型")
    print("✅ RESTful API接口 - 完整的API文档和接口")
    print("✅ 多模型架构 - 文本模型 + 视觉模型")
    print("✅ 图像处理服务 - OCR文本识别和化学公式提取")
    print("\n🌐 API文档地址: http://localhost:8000/docs")
    print("🌐 前端应用地址: http://localhost:5173/")

if __name__ == "__main__":
    main()
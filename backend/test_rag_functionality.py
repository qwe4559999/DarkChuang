#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json
import time

def test_rag_functionality():
    """测试RAG功能是否正确工作"""
    base_url = "http://localhost:8000/api/v1/chat"
    
    print("=== 测试RAG功能 ===")
    print("等待后端服务启动...")
    time.sleep(5)
    
    # 测试1: 不启用RAG
    print("\n1. 测试不启用RAG (use_rag=False):")
    try:
        response1 = requests.post(base_url, json={
            "message": "什么是苯环？",
            "use_rag": False,
            "max_tokens": 200
        }, timeout=60)
        
        if response1.status_code == 200:
            data1 = response1.json()
            print(f"状态: 成功")
            print(f"消息: {data1.get('message', '')[:100]}...")
            print(f"处理时间: {data1.get('processing_time', 'N/A')}")
            print(f"来源数量: {len(data1.get('sources', []))}")
            if data1.get('sources'):
                print("检测到来源信息 - 可能存在问题!")
            else:
                print("无来源信息 - 正常")
        else:
            print(f"错误: {response1.status_code} - {response1.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    # 测试2: 启用RAG
    print("\n2. 测试启用RAG (use_rag=True):")
    try:
        response2 = requests.post(base_url, json={
            "message": "什么是苯环？",
            "use_rag": True,
            "max_tokens": 200
        }, timeout=60)
        
        if response2.status_code == 200:
            data2 = response2.json()
            print(f"状态: 成功")
            print(f"消息: {data2.get('message', '')[:100]}...")
            print(f"处理时间: {data2.get('processing_time', 'N/A')}")
            print(f"来源数量: {len(data2.get('sources', []))}")
            if data2.get('sources'):
                print("检测到来源信息 - 正常")
                for i, source in enumerate(data2.get('sources', [])[:2]):
                    print(f"  来源{i+1}: {source.get('source', 'unknown')} (分数: {source.get('score', 'N/A')})")
            else:
                print("无来源信息 - 可能存在问题!")
        else:
            print(f"错误: {response2.status_code} - {response2.text}")
    except Exception as e:
        print(f"请求失败: {e}")
    
    print("\n=== 测试完成 ===")
    input("按回车键关闭窗口...")

if __name__ == "__main__":
    test_rag_functionality()

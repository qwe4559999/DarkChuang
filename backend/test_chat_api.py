#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

def test_chat_api():
    """测试聊天API功能"""
    url = "http://localhost:8000/api/v1/chat"
    
    # 测试数据
    data = {
        "message": "什么是苯环？",
        "use_rag": True,
        "max_tokens": 500
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("正在测试化学问答API...")
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\n=== API响应成功 ===")
            print(f"回答: {result.get('response', 'N/A')}")
            print(f"对话ID: {result.get('conversation_id', 'N/A')}")
            print(f"使用RAG: {result.get('used_rag', 'N/A')}")
            print(f"处理时间: {result.get('processing_time', 'N/A')}秒")
        else:
            print(f"\n=== API请求失败 ===")
            print(f"错误信息: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    except Exception as e:
        print(f"其他错误: {e}")

if __name__ == "__main__":
    test_chat_api()
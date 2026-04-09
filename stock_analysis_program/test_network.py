#!/usr/bin/env python3
"""
测试网络连接和基本数据获取
"""

import sys
sys.path.append('.')

import time
import requests
import akshare as ak

def test_basic_network():
    """测试基本网络连接"""
    print("=== 测试网络连接 ===")
    
    # 测试几个主要的东方财富数据接口
    test_urls = [
        "http://quote.eastmoney.com",
        "http://data.eastmoney.com",
        "https://www.akshare.xyz"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            print(f"✓ {url} 可访问，状态码: {response.status_code}")
        except Exception as e:
            print(f"✗ {url} 不可访问: {e}")
    
    print("\n=== 测试 AkShare 基本功能 ===")
    
    # 测试几个不同的 AkShare 方法
    test_methods = [
        ("stock_zh_a_hist", {"symbol": "000001", "period": "daily", "start_date": "20240401", "end_date": "20240408", "adjust": ""}),
        ("stock_zh_a_spot_em", {}),
        ("stock_szse_summary", {}),
        ("stock_sse_summary", {}),
    ]
    
    for method_name, params in test_methods:
        try:
            print(f"测试 {method_name}...")
            method = getattr(ak, method_name)
            
            # 添加延迟避免请求过快
            time.sleep(1)
            
            result = method(**params)
            if result is not None:
                print(f"✓ {method_name} 成功，返回数据形状: {result.shape if hasattr(result, 'shape') else 'N/A'}")
            else:
                print(f"✗ {method_name} 返回 None")
        except Exception as e:
            print(f"✗ {method_name} 失败: {e}")

if __name__ == "__main__":
    test_basic_network()
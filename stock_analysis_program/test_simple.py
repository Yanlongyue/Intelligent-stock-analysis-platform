#!/usr/bin/env python3
"""
简单测试数据接口
"""

import sys
sys.path.append('.')

from real_data_provider import AkShareDataProvider
import akshare as ak

def test_simple():
    """简单测试"""
    print("=== 简单测试 ===")
    
    # 直接测试 AkShare 的不同方法
    print("\n1. 测试上交所数据...")
    try:
        sh_data = ak.stock_sse_summary()
        print(f"✓ 上交所数据形状: {sh_data.shape}")
        print(f"  列名: {list(sh_data.columns)}")
        print(f"  前2行数据:")
        print(sh_data.head(2).to_string())
    except Exception as e:
        print(f"✗ 上交所数据失败: {e}")
    
    print("\n2. 测试深交所数据...")
    try:
        sz_data = ak.stock_szse_summary()
        print(f"✓ 深交所数据形状: {sz_data.shape}")
        print(f"  列名: {list(sz_data.columns)}")
        print(f"  前2行数据:")
        print(sz_data.head(2).to_string())
    except Exception as e:
        print(f"✗ 深交所数据失败: {e}")
    
    print("\n3. 测试 AkShareDataProvider...")
    provider = AkShareDataProvider()
    
    # 测试 601868.SH (中国能建)
    print("测试 601868.SH...")
    try:
        data = provider.get_daily_quotes("601868.SH", start_date="20240401", end_date="20240408")
        if data:
            print(f"✓ 获取成功，数据长度: {len(data)}")
            if len(data) > 0:
                print(f"  最新数据: 日期={data[0].get('trade_date')}, 收盘={data[0].get('close')}")
        else:
            print("✗ 获取失败，返回 None")
    except Exception as e:
        print(f"✗ 获取异常: {e}")

if __name__ == "__main__":
    test_simple()
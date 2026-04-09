#!/usr/bin/env python3
"""
测试新替换的国内可访问接口
"""

import sys
sys.path.append('.')

from real_data_provider import AkShareDataProvider

def test_new_interfaces():
    """测试新接口"""
    print("=== 测试新的国内可访问接口 ===")
    
    provider = AkShareDataProvider()
    
    # 1. 测试北向资金接口
    print("\n1. 测试北向资金接口...")
    try:
        north_data = provider.get_north_money_flow()
        if north_data:
            print(f"✓ 北向资金接口成功，数据长度：{len(north_data)}")
            if len(north_data) > 0:
                print(f"  最新数据示例：日期={north_data[0].get('trade_date')}, 净流入={north_data[0].get('net_inflow')}")
        else:
            print("✗ 北向资金接口返回空数据")
    except Exception as e:
        print(f"✗ 北向资金接口失败：{e}")
    
    # 2. 测试指数日线接口
    print("\n2. 测试指数日线接口...")
    try:
        # 测试上证指数
        index_data = provider.get_index_daily("000001.SH", start_date="2026-04-01", end_date="2026-04-08")
        if index_data:
            print(f"✓ 指数日线接口成功，数据长度：{len(index_data)}")
            if len(index_data) > 0:
                print(f"  最新数据示例：日期={index_data[0].get('trade_date')}, 收盘={index_data[0].get('close')}")
        else:
            print("✗ 指数日线接口返回空数据")
    except Exception as e:
        print(f"✗ 指数日线接口失败：{e}")
    
    # 3. 测试市场概况接口
    print("\n3. 测试市场概况接口...")
    try:
        market_data = provider.get_market_overview()
        if market_data:
            print(f"✓ 市场概况接口成功")
            print(f"  主要指数：")
            if market_data.get("major_indices"):
                for idx in market_data["major_indices"]:
                    print(f"    {idx.get('name')}: {idx.get('close')} ({idx.get('pct_chg')}%)")
            print(f"  市场情绪：{market_data.get('sentiment')}")
            print(f"  总成交额：{market_data.get('total_turnover')}")
        else:
            print("✗ 市场概况接口返回空数据")
    except Exception as e:
        print(f"✗ 市场概况接口失败：{e}")
    
    # 4. 测试日线数据接口（确保基本功能正常）
    print("\n4. 测试日线数据接口...")
    try:
        daily_data = provider.get_daily_quotes("601868.SH", start_date="2026-04-01", end_date="2026-04-08")
        if daily_data:
            print(f"✓ 日线数据接口成功，数据长度：{len(daily_data)}")
            if len(daily_data) > 0:
                print(f"  最新数据示例：日期={daily_data[0].get('trade_date')}, 收盘={daily_data[0].get('close')}")
        else:
            print("✗ 日线数据接口返回空数据")
    except Exception as e:
        print(f"✗ 日线数据接口失败：{e}")
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_new_interfaces()
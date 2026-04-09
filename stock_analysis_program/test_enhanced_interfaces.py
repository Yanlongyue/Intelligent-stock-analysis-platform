#!/usr/bin/env python3
"""
测试增强版的数据接口
"""

import sys
sys.path.append('.')

from real_data_provider import AkShareDataProvider
import time

def test_enhanced_interfaces():
    """测试增强接口"""
    print("=== 测试增强版数据接口 ===")
    
    provider = AkShareDataProvider()
    print(f"AkShare可用状态: {provider.available}")
    
    # 测试几个股票
    test_stocks = [
        "601868.SH",  # 上交所股票
        "002506.SZ",  # 深交所股票
        "000001.SH",  # 上证指数
    ]
    
    for ts_code in test_stocks:
        print(f"\n--- 测试 {ts_code} ---")
        
        # 测试日线数据
        print("获取日线数据...")
        start_time = time.time()
        try:
            daily_data = provider.get_daily_quotes(ts_code, start_date="20240401", end_date="20240408")
            elapsed = time.time() - start_time
            
            if daily_data and len(daily_data) > 0:
                print(f"✅ 成功获取 {len(daily_data)} 条日线数据 (耗时: {elapsed:.2f}s)")
                if len(daily_data) > 0:
                    latest = daily_data[-1]
                    print(f"   最新数据: 日期={latest.get('trade_date')}, 收盘={latest.get('close')}")
            else:
                print(f"⚠️ 获取日线数据失败，返回: {daily_data}")
                
        except Exception as e:
            print(f"💥 日线数据获取异常: {e}")
            import traceback
            traceback.print_exc()
        
        # 避免请求过快
        time.sleep(1)
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_enhanced_interfaces()
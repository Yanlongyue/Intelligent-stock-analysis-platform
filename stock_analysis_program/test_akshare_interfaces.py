#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 AkShare 可用接口（国内网络环境）
"""

import akshare as ak
import pandas as pd
from datetime import datetime, timedelta

def test_interface(name, func, *args, **kwargs):
    """测试单个接口"""
    try:
        print(f"🔍 测试 {name}...")
        result = func(*args, **kwargs)
        if result is not None and not (isinstance(result, pd.DataFrame) and result.empty):
            print(f"  ✅ 成功，返回数据形状: {result.shape if hasattr(result, 'shape') else len(result)}")
            return True, result
        else:
            print(f"  ⚠️ 返回空数据")
            return False, None
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        return False, None

def main():
    print("🚀 开始测试 AkShare 国内接口可用性")
    print("=" * 50)
    
    # 1. 股票日线数据（已知能用的）
    success, result = test_interface(
        "股票日线数据 (stock_zh_a_hist)",
        ak.stock_zh_a_hist,
        symbol="000001",
        period="daily",
        start_date=(datetime.now() - timedelta(days=7)).strftime("%Y%m%d"),
        end_date=datetime.now().strftime("%Y%m%d"),
        adjust=""
    )
    
    # 2. 实时行情
    success, result = test_interface(
        "实时行情 (stock_zh_a_spot)",
        ak.stock_zh_a_spot
    )
    
    # 3. 东方财富实时行情
    success, result = test_interface(
        "东方财富实时行情 (stock_zh_a_spot_em)",
        ak.stock_zh_a_spot_em
    )
    
    # 4. 北向资金（尝试不同接口）
    success, result = test_interface(
        "北向资金持股 (stock_hsgt_hold_stock_em)",
        ak.stock_hsgt_hold_stock_em,
        symbol="北向资金"
    )
    
    # 5. 指数日线
    success, result = test_interface(
        "指数日线 (index_zh_a_hist)",
        ak.index_zh_a_hist,
        symbol="000001",
        period="daily",
        start_date=(datetime.now() - timedelta(days=7)).strftime("%Y%m%d"),
        end_date=datetime.now().strftime("%Y%m%d")
    )
    
    # 6. 实时指数（用正确的接口名）
    try:
        # 先检查接口是否存在
        if hasattr(ak, 'stock_zh_index_spot'):
            success, result = test_interface(
                "实时指数 (stock_zh_index_spot)",
                ak.stock_zh_index_spot
            )
        else:
            print("  ℹ️ 接口 stock_zh_index_spot 不存在，跳过")
    except Exception as e:
        print(f"  ❌ 实时指数接口测试失败: {e}")
    
    # 7. 龙虎榜数据
    success, result = test_interface(
        "龙虎榜 (stock_sina_lhb_detail_daily)",
        ak.stock_sina_lhb_detail_daily,
        trade_date=datetime.now().strftime("%Y%m%d")
    )
    
    # 8. 个股资金流向
    success, result = test_interface(
        "个股资金流向 (stock_individual_fund_flow)",
        ak.stock_individual_fund_flow,
        stock="000001",
        market="SZ"
    )
    
    # 9. 板块资金流向
    success, result = test_interface(
        "板块资金流向 (sector_fund_flow_hist)",
        ak.sector_fund_flow_hist,
        sector="sw_l1",
        indicator="今日"
    )
    
    # 10. 新闻数据
    success, result = test_interface(
        "新闻数据 (stock_news_em)",
        ak.stock_news_em,
        symbol="沪深"
    )
    
    print("\n" + "=" * 50)
    print("📊 测试完成！")
    print("✅ 可用的接口将用于替换需要海外网络的数据源")

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试持仓配置
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

# 导入持仓配置
from config.position_config import position_config

def main():
    """主测试函数"""
    print("📊 测试持仓配置模块")
    print("="*60)
    
    # 1. 获取用户持仓股票
    user_stocks = position_config.get_user_stocks()
    print(f"✅ 用户持仓股票 ({len(user_stocks)}只):")
    for stock in user_stocks:
        print(f"  - {stock}")
    
    # 2. 获取每只股票的持仓信息
    print(f"\n📈 持仓详细信息:")
    for stock_code in user_stocks:
        info = position_config.get_position_info(stock_code)
        print(f"\n  {stock_code}:")
        print(f"    持仓数量: {info.get('quantity', 0)}股")
        print(f"    持仓类型: {info.get('position_type', 'unknown')}")
        print(f"    风险等级: {info.get('risk_tolerance', 'medium')}")
        print(f"    目标仓位: {info.get('target_ratio', 0.1)*100:.1f}%")
    
    # 3. 模拟股票价格计算持仓价值
    print(f"\n💰 模拟持仓价值计算:")
    
    # 模拟股票价格（假设当前股价）
    stock_prices = {
        "601868.SH": 2.50,   # 中国能建 假设价格
        "002506.SZ": 3.20,   # 协鑫集成 假设价格
        "600821.SH": 5.80,   # 金开新能 假设价格
    }
    
    # 计算总价值
    total_value = position_config.get_total_value(stock_prices)
    print(f"  持仓总价值: ¥{total_value:.2f}")
    
    # 计算各股票占比
    ratios = position_config.get_position_ratios(stock_prices)
    print(f"  持仓比例分布:")
    for stock_code, ratio in ratios.items():
        print(f"    {stock_code}: {ratio*100:.1f}% (¥{stock_prices[stock_code] * position_config.USER_POSITIONS[stock_code]:.2f})")
    
    # 4. 获取再平衡建议
    print(f"\n🎯 仓位再平衡建议 (假设总资金 ¥100,000):")
    total_capital = 100000.0
    suggestions = position_config.get_rebalancing_suggestions(stock_prices, total_capital)
    
    for stock_code, suggestion in suggestions.items():
        print(f"\n  {stock_code}:")
        print(f"    当前仓位: {suggestion['current_ratio']}% (目标: {suggestion['target_ratio']}%)")
        print(f"    当前价值: ¥{suggestion['current_value']:.2f} (目标: ¥{suggestion['target_value']:.2f})")
        
        if suggestion['action'] == 'buy':
            print(f"    🟢 建议操作: 买入 {suggestion['action_quantity']}股 (+¥{suggestion['difference']:.2f})")
        elif suggestion['action'] == 'sell':
            print(f"    🔴 建议操作: 卖出 {suggestion['action_quantity']}股 (-¥{suggestion['difference']:.2f})")
        else:
            print(f"    🟡 建议操作: 持有")
    
    # 5. 打印完整的持仓摘要
    print(f"\n" + "="*60)
    position_config.print_position_summary(stock_prices, total_capital)

if __name__ == "__main__":
    main()
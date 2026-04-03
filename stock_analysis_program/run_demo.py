#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓股票分析演示程序
直接运行生成持仓股票分析报告
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.position_config import get_position_stocks, calculate_position_value

def main():
    """主函数：展示持仓股票分析结果"""
    print("=" * 60)
    print("📊 持仓股票分析演示")
    print("=" * 60)
    
    # 1. 获取持仓股票信息
    print("\n🔍 获取您的持仓股票信息...")
    position_stocks = get_position_stocks()
    
    print(f"\n📈 您当前持仓 {len(position_stocks)} 只股票：")
    print("-" * 60)
    
    total_value = 0
    for stock in position_stocks:
        stock_code = stock['ts_code']
        stock_name = stock['name']
        quantity = stock['quantity']
        price = stock.get('current_price', 0)
        position_value = quantity * price
        
        print(f"股票代码: {stock_code}")
        print(f"股票名称: {stock_name}")
        print(f"持仓数量: {quantity} 股")
        print(f"当前价格: ¥{price:.2f}")
        print(f"持仓市值: ¥{position_value:.2f}")
        print("-" * 40)
        
        total_value += position_value
    
    # 2. 计算总持仓价值
    print(f"\n💰 总持仓市值: ¥{total_value:.2f}")
    
    # 3. 持仓比例分析
    print("\n📊 持仓比例分析：")
    print("-" * 60)
    for stock in position_stocks:
        stock_code = stock['ts_code']
        stock_name = stock['name']
        quantity = stock['quantity']
        price = stock.get('current_price', 0)
        position_value = quantity * price
        percentage = (position_value / total_value * 100) if total_value > 0 else 0
        
        print(f"{stock_name} ({stock_code}): {percentage:.1f}%")
    
    # 4. 投资建议
    print("\n🎯 投资建议：")
    print("-" * 60)
    print("1. 中国能建 (601868.SH) - 基建龙头，稳健投资")
    print("   - 建议：长期持有，逢低加仓")
    print("   - 目标价位：¥3.50-3.80")
    print("   - 止损价位：¥2.80")
    
    print("\n2. 协鑫集成 (002506.SZ) - 光伏概念，成长性强")
    print("   - 建议：关注短期波动，波段操作")
    print("   - 目标价位：¥2.20-2.50")
    print("   - 止损价位：¥1.80")
    
    print("\n3. 金开新能 (600821.SH) - 新能源概念，波动较大")
    print("   - 建议：谨慎操作，设置严格止损")
    print("   - 目标价位：¥4.50-5.00")
    print("   - 止损价位：¥3.50")
    
    # 5. 下一步行动建议
    print("\n🚀 下一步行动建议：")
    print("-" * 60)
    print("1. 每日监控持仓股票的技术面和基本面变化")
    print("2. 设置止盈止损价位，严格执行交易纪律")
    print("3. 关注市场整体趋势和板块轮动")
    print("4. 定期调整仓位，优化投资组合")
    print("5. 使用七步法股票分析程序进行系统化分析")
    
    # 6. 程序使用说明
    print("\n📋 程序使用说明：")
    print("-" * 60)
    print("1. 运行完整分析：python3 analyze_position_stocks.py")
    print("2. 查看持仓配置：python3 test_position_config.py")
    print("3. 生成HTML报告：python3 generate_html_report.py")
    print("4. 更新持仓信息：修改 config/position_config.py")
    
    print("\n✅ 演示完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
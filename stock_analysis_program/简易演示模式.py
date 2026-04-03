#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓股票分析 - 简易演示模式
直接运行生成持仓股票分析报告
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.position_config import PositionConfig

def main():
    """主函数：展示持仓股票分析结果"""
    print("=" * 60)
    print("📊 持仓股票分析演示 - 简易模式")
    print("=" * 60)
    
    # 1. 获取持仓股票信息
    print("\n🔍 获取您的持仓股票信息...")
    
    # 创建配置实例
    config = PositionConfig()
    
    # 假设的股票价格（实际使用时应该从API获取）
    stock_prices = {
        "601868.SH": 3.20,  # 中国能建
        "002506.SZ": 2.10,  # 协鑫集成
        "600821.SH": 4.20,  # 金开新能
    }
    
    # 2. 显示持仓详情
    print(f"\n📈 您当前持仓 {len(config.USER_POSITIONS)} 只股票：")
    print("-" * 60)
    
    total_value = 0
    for stock_code, quantity in config.USER_POSITIONS.items():
        stock_name = {
            "601868.SH": "中国能建",
            "002506.SZ": "协鑫集成", 
            "600821.SH": "金开新能"
        }.get(stock_code, stock_code)
        
        price = stock_prices.get(stock_code, 0)
        position_value = quantity * price
        total_value += position_value
        
        position_type = config.POSITION_TYPES.get(stock_code, "unknown")
        risk_level = config.RISK_TOLERANCE.get(stock_code, "medium")
        target_ratio = config.TARGET_POSITION_RATIOS.get(stock_code, 0) * 100
        
        print(f"股票名称: {stock_name} ({stock_code})")
        print(f"持仓数量: {quantity} 股")
        print(f"当前价格: ¥{price:.2f}")
        print(f"持仓市值: ¥{position_value:.2f}")
        print(f"股票类型: {position_type}")
        print(f"风险等级: {risk_level}")
        print(f"目标仓位: {target_ratio:.1f}%")
        print("-" * 40)
    
    # 3. 总持仓分析
    print(f"\n💰 总持仓分析:")
    print("-" * 60)
    print(f"持仓总市值: ¥{total_value:.2f}")
    
    # 计算持仓比例
    for stock_code, quantity in config.USER_POSITIONS.items():
        price = stock_prices.get(stock_code, 0)
        position_value = quantity * price
        percentage = (position_value / total_value * 100) if total_value > 0 else 0
        
        stock_name = {
            "601868.SH": "中国能建",
            "002506.SZ": "协鑫集成",
            "600821.SH": "金开新能"
        }.get(stock_code, stock_code)
        
        print(f"{stock_name}: {percentage:.1f}%")
    
    # 4. 投资建议（基于持仓类型和风险等级）
    print("\n🎯 投资建议：")
    print("-" * 60)
    
    advice_map = {
        "601868.SH": {
            "name": "中国能建",
            "type": "value",
            "risk": "medium",
            "advice": "基建龙头股，业绩稳定，适合长期持有。建议逢低加仓，目标价位¥3.50-3.80，止损价位¥2.80。",
            "action": "持有"
        },
        "002506.SZ": {
            "name": "协鑫集成",
            "type": "growth", 
            "risk": "high",
            "advice": "光伏概念成长股，波动较大但成长性强。建议波段操作，目标价位¥2.20-2.50，严格止损¥1.80。",
            "action": "谨慎持有"
        },
        "600821.SH": {
            "name": "金开新能",
            "type": "concept",
            "risk": "high",
            "advice": "新能源概念股，受政策和市场情绪影响大。建议设置严格止损，目标价位¥4.50-5.00，止损价位¥3.50。",
            "action": "风险监控"
        }
    }
    
    for stock_code, advice in advice_map.items():
        print(f"\n{advice['name']} ({stock_code}):")
        print(f"  类型: {advice['type']} | 风险: {advice['risk']}")
        print(f"  建议: {advice['advice']}")
        print(f"  操作: {advice['action']}")
    
    # 5. 风险提示
    print("\n⚠️ 风险提示：")
    print("-" * 60)
    print("1. 股市有风险，投资需谨慎")
    print("2. 建议仓位控制在总资金的30%-50%")
    print("3. 严格执行止损纪律（高风险股3%，中风险股5%）")
    print("4. 关注市场整体趋势和板块轮动")
    print("5. 定期复盘，优化投资策略")
    
    # 6. 下一步操作建议
    print("\n🚀 下一步操作建议：")
    print("-" * 60)
    print("1. 使用 analyze_position_stocks.py 进行七步法深度分析")
    print("2. 运行 test_position_config.py 验证持仓配置")
    print("3. 如需更新持仓信息，请修改 config/position_config.py")
    print("4. 建议每日运行分析程序，监控持仓变化")
    
    print("\n✅ 演示完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
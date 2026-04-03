#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
七步法股票分析程序 - 持仓配置模块
管理用户的具体持仓信息
"""

from typing import Dict, List
from datetime import datetime

class PositionConfig:
    """持仓配置管理"""
    
    # 用户持仓信息（股票代码: 持仓数量）
    USER_POSITIONS: Dict[str, int] = {
        "601868.SH": 400,  # 中国能建 400股
        "002506.SZ": 400,  # 协鑫集成 400股
        "600821.SH": 600,  # 金开新能 600股
    }
    
    # 持仓成本价（可选，如果不知道可以留空）
    COST_PRICES: Dict[str, float] = {
        # "601868.SH": 2.50,   # 中国能建成本价（示例）
        # "002506.SZ": 3.20,   # 协鑫集成成本价（示例）
        # "600821.SH": 5.80,   # 金开新能成本价（示例）
    }
    
    # 持仓时间（可选，如果不知道可以留空）
    POSITION_DATES: Dict[str, datetime] = {
        # "601868.SH": datetime(2025, 12, 15),  # 中国能建持仓日期（示例）
        # "002506.SZ": datetime(2025, 11, 20),  # 协鑫集成持仓日期（示例）
        # "600821.SH": datetime(2025, 10, 10),  # 金开新能持仓日期（示例）
    }
    
    # 持仓类型配置
    POSITION_TYPES: Dict[str, str] = {
        "601868.SH": "value",      # 价值股
        "002506.SZ": "growth",     # 成长股
        "600821.SH": "concept",    # 概念股
    }
    
    # 风险承受等级配置
    RISK_TOLERANCE: Dict[str, str] = {
        "601868.SH": "medium",     # 中等风险
        "002506.SZ": "high",       # 高风险
        "600821.SH": "high",       # 高风险
    }
    
    # 持仓目标（百分比）
    TARGET_POSITION_RATIOS: Dict[str, float] = {
        "601868.SH": 0.15,  # 目标仓位15%
        "002506.SZ": 0.12,  # 目标仓位12%
        "600821.SH": 0.18,  # 目标仓位18%
    }
    
    @classmethod
    def get_user_stocks(cls) -> List[str]:
        """获取用户持仓的股票代码列表"""
        return list(cls.USER_POSITIONS.keys())
    
    @classmethod
    def get_position_info(cls, stock_code: str) -> Dict[str, any]:
        """获取某只股票的详细持仓信息"""
        if stock_code not in cls.USER_POSITIONS:
            return {}
        
        return {
            "quantity": cls.USER_POSITIONS.get(stock_code, 0),
            "cost_price": cls.COST_PRICES.get(stock_code, 0.0),
            "position_date": cls.POSITION_DATES.get(stock_code, None),
            "position_type": cls.POSITION_TYPES.get(stock_code, "unknown"),
            "risk_tolerance": cls.RISK_TOLERANCE.get(stock_code, "medium"),
            "target_ratio": cls.TARGET_POSITION_RATIOS.get(stock_code, 0.1),
        }
    
    @classmethod
    def get_total_value(cls, stock_prices: Dict[str, float]) -> float:
        """根据股票价格计算持仓总价值"""
        total_value = 0.0
        for stock_code, quantity in cls.USER_POSITIONS.items():
            price = stock_prices.get(stock_code, 0.0)
            total_value += price * quantity
        return total_value
    
    @classmethod
    def get_position_ratios(cls, stock_prices: Dict[str, float]) -> Dict[str, float]:
        """计算各股票在持仓中的占比"""
        total_value = cls.get_total_value(stock_prices)
        if total_value == 0:
            return {}
        
        ratios = {}
        for stock_code, quantity in cls.USER_POSITIONS.items():
            price = stock_prices.get(stock_code, 0.0)
            value = price * quantity
            ratios[stock_code] = value / total_value if total_value > 0 else 0.0
        
        return ratios
    
    @classmethod
    def get_rebalancing_suggestions(cls, stock_prices: Dict[str, float], total_capital: float) -> Dict[str, Dict[str, any]]:
        """获取仓位再平衡建议"""
        if not total_capital:
            return {}
        
        suggestions = {}
        for stock_code, quantity in cls.USER_POSITIONS.items():
            price = stock_prices.get(stock_code, 0.0)
            current_value = price * quantity
            current_ratio = current_value / total_capital if total_capital > 0 else 0.0
            target_ratio = cls.TARGET_POSITION_RATIOS.get(stock_code, 0.1)
            
            target_value = total_capital * target_ratio
            difference = target_value - current_value
            
            action = "hold"
            if difference > 0:
                action = "buy"
            elif difference < 0:
                action = "sell"
            
            suggestions[stock_code] = {
                "current_ratio": round(current_ratio * 100, 2),
                "target_ratio": round(target_ratio * 100, 2),
                "current_value": round(current_value, 2),
                "target_value": round(target_value, 2),
                "difference": round(abs(difference), 2),
                "action": action,
                "action_quantity": int(abs(difference) / price) if price > 0 else 0,
            }
        
        return suggestions
    
    @classmethod
    def print_position_summary(cls, stock_prices: Dict[str, float] = None, total_capital: float = 100000.0):
        """打印持仓摘要"""
        print("\n" + "="*60)
        print("📊 用户持仓配置摘要")
        print("="*60)
        
        print(f"\n📈 持仓股票 ({len(cls.USER_POSITIONS)}只):")
        for stock_code, quantity in cls.USER_POSITIONS.items():
            position_type = cls.POSITION_TYPES.get(stock_code, "unknown")
            risk_tolerance = cls.RISK_TOLERANCE.get(stock_code, "medium")
            print(f"  {stock_code}: {quantity}股 | 类型: {position_type} | 风险等级: {risk_tolerance}")
        
        if stock_prices:
            print(f"\n💰 持仓价值分析 (假设总资金: ¥{total_capital:,.2f}):")
            total_value = cls.get_total_value(stock_prices)
            print(f"  持仓总价值: ¥{total_value:,.2f}")
            print(f"  仓位占比: {(total_value/total_capital*100):.1f}%")
            
            ratios = cls.get_position_ratios(stock_prices)
            for stock_code, ratio in ratios.items():
                print(f"  {stock_code}: {ratio*100:.1f}%")
        
        print(f"\n🎯 目标仓位配置:")
        for stock_code, target_ratio in cls.TARGET_POSITION_RATIOS.items():
            print(f"  {stock_code}: {target_ratio*100:.1f}%")
        
        print("\n" + "="*60)

# 创建配置实例
position_config = PositionConfig()

if __name__ == "__main__":
    # 测试配置
    position_config.print_position_summary()
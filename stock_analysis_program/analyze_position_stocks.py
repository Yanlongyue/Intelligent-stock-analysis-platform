#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
持仓股票分析程序
使用用户的持仓信息进行完整七步法分析
"""

import sys
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

# 导入配置
from config.position_config import position_config
from config.settings import config

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class PositionStockAnalysis:
    """持仓股票分析器"""
    
    def __init__(self):
        self.user_stocks = position_config.get_user_stocks()
        logger.info(f"初始化持仓分析器，共 {len(self.user_stocks)} 只持仓股票")
    
    def generate_analysis_report(self, date_str=None):
        """生成持仓分析报告"""
        
        if date_str is None:
            date_str = datetime.now().strftime("%Y%m%d")
        
        print("\n" + "="*80)
        print("📊 持仓股票七步法分析报告")
        print(f"📅 分析日期: {date_str}")
        print("="*80)
        
        # 步骤1: 持仓概述
        self._step1_position_summary()
        
        # 步骤2: 股票基本信息
        self._step2_stock_info()
        
        # 步骤3: 风险分析
        self._step3_risk_analysis()
        
        # 步骤4: 投资建议
        self._step4_investment_suggestions()
        
        # 步骤5: 仓位管理
        self._step5_position_management()
        
        # 步骤6: 操作计划
        self._step6_operation_plan()
        
        # 步骤7: 监控策略
        self._step7_monitoring_strategy()
        
        print("\n" + "="*80)
        print("✅ 持仓分析报告生成完成")
        print("="*80)
    
    def _step1_position_summary(self):
        """步骤1: 持仓概述"""
        print(f"\n📋 步骤1: 持仓概述")
        print("-" * 40)
        
        print(f"  持仓股票数量: {len(self.user_stocks)} 只")
        print(f"  总持仓数量: {sum(position_config.USER_POSITIONS.values())} 股")
        
        # 计算持仓价值（假设价格）
        stock_prices = {
            "601868.SH": 2.50,   # 中国能建
            "002506.SZ": 3.20,   # 协鑫集成
            "600821.SH": 5.80,   # 金开新能
        }
        
        total_value = position_config.get_total_value(stock_prices)
        print(f"  持仓总价值: ¥{total_value:.2f}")
        
        # 持仓分布
        ratios = position_config.get_position_ratios(stock_prices)
        print(f"  持仓分布:")
        for stock_code, ratio in ratios.items():
            stock_name = self._get_stock_name(stock_code)
            print(f"    {stock_name}({stock_code}): {ratio*100:.1f}%")
    
    def _step2_stock_info(self):
        """步骤2: 股票基本信息"""
        print(f"\n📈 步骤2: 股票基本信息")
        print("-" * 40)
        
        for stock_code in self.user_stocks:
            stock_name = self._get_stock_name(stock_code)
            info = position_config.get_position_info(stock_code)
            
            print(f"\n  🏢 {stock_name}({stock_code}):")
            print(f"    持仓数量: {info.get('quantity', 0)} 股")
            print(f"    持仓类型: {self._get_position_type_name(info.get('position_type', 'unknown'))}")
            print(f"    风险等级: {self._get_risk_level_name(info.get('risk_tolerance', 'medium'))}")
            print(f"    目标仓位: {info.get('target_ratio', 0.1)*100:.1f}%")
    
    def _step3_risk_analysis(self):
        """步骤3: 风险分析"""
        print(f"\n⚠️  步骤3: 风险分析")
        print("-" * 40)
        
        total_risk_score = 0
        risk_count = 0
        
        for stock_code in self.user_stocks:
            stock_name = self._get_stock_name(stock_code)
            info = position_config.get_position_info(stock_code)
            risk_level = info.get('risk_tolerance', 'medium')
            
            print(f"  {stock_name}({stock_code}):")
            
            if risk_level == 'high':
                print(f"    🔴 高风险股票 (概念股/成长股)")
                print(f"      特点: 波动大，收益潜力高，风险也高")
                print(f"      建议: 密切关注，设置3%止损")
                total_risk_score += 3
            elif risk_level == 'medium':
                print(f"    🟡 中风险股票 (价值股)")
                print(f"      特点: 相对稳定，适合中长期持有")
                print(f"      建议: 设置5%止损，分批操作")
                total_risk_score += 2
            else:
                print(f"    🟢 低风险股票")
                print(f"      建议: 设置7%止损，稳健持有")
                total_risk_score += 1
            
            risk_count += 1
        
        if risk_count > 0:
            avg_risk = total_risk_score / risk_count
            print(f"\n  📊 整体风险评分: {avg_risk:.1f}/3.0")
            if avg_risk >= 2.5:
                print(f"  ⚠️ 警告: 整体风险偏高，建议适当减仓或增加对冲")
            elif avg_risk >= 1.5:
                print(f"  📈 提示: 风险适中，保持当前仓位")
            else:
                print(f"  ✅ 良好: 风险较低，可适当增加仓位")
    
    def _step4_investment_suggestions(self):
        """步骤4: 投资建议"""
        print(f"\n💡 步骤4: 投资建议")
        print("-" * 40)
        
        # 模拟股票价格
        stock_prices = {
            "601868.SH": 2.50,   # 中国能建
            "002506.SZ": 3.20,   # 协鑫集成
            "600821.SH": 5.80,   # 金开新能
        }
        
        total_capital = 100000.0  # 假设总资金10万元
        suggestions = position_config.get_rebalancing_suggestions(stock_prices, total_capital)
        
        print(f"  基于总资金 ¥{total_capital:,.2f} 的仓位再平衡建议:")
        
        for stock_code, suggestion in suggestions.items():
            stock_name = self._get_stock_name(stock_code)
            
            if suggestion['action'] == 'buy':
                print(f"\n  🟢 {stock_name}: 建议买入")
                print(f"    当前仓位: {suggestion['current_ratio']}% (目标: {suggestion['target_ratio']}%)")
                print(f"    建议买入数量: {suggestion['action_quantity']} 股")
                print(f"    建议买入金额: ¥{suggestion['difference']:.2f}")
            elif suggestion['action'] == 'sell':
                print(f"\n  🔴 {stock_name}: 建议卖出")
                print(f"    当前仓位: {suggestion['current_ratio']}% (目标: {suggestion['target_ratio']}%)")
                print(f"    建议卖出数量: {suggestion['action_quantity']} 股")
                print(f"    建议卖出金额: ¥{suggestion['difference']:.2f}")
            else:
                print(f"\n  🟡 {stock_name}: 建议持有")
                print(f"    当前仓位: {suggestion['current_ratio']}% (目标: {suggestion['target_ratio']}%)")
    
    def _step5_position_management(self):
        """步骤5: 仓位管理"""
        print(f"\n📊 步骤5: 仓位管理")
        print("-" * 40)
        
        print(f"  总仓位建议:")
        print(f"    ⏳ 当前仓位: 建议控制在 30-50%")
        print(f"    🎯 目标仓位: 逐步调整到目标比例")
        print(f"    ⚠️  单股上限: 不超过总资金的 15%")
        
        print(f"\n  持仓股票目标仓位:")
        for stock_code in self.user_stocks:
            stock_name = self._get_stock_name(stock_code)
            info = position_config.get_position_info(stock_code)
            target_ratio = info.get('target_ratio', 0.1) * 100
            
            print(f"    {stock_name}: {target_ratio:.1f}%")
    
    def _step6_operation_plan(self):
        """步骤6: 操作计划"""
        print(f"\n📝 步骤6: 操作计划")
        print("-" * 40)
        
        print(f"  明日操作建议:")
        
        for stock_code in self.user_stocks:
            stock_name = self._get_stock_name(stock_code)
            info = position_config.get_position_info(stock_code)
            position_type = info.get('position_type', 'unknown')
            
            print(f"\n  {stock_name}:")
            
            if position_type == 'concept':
                print(f"    🚀 概念股操作策略:")
                print(f"      1. 设置3%止损线")
                print(f"      2. 快进快出，不恋战")
                print(f"      3. 关注市场情绪和游资动向")
                print(f"      4. 获利5-10%考虑减仓")
            elif position_type == 'growth':
                print(f"    📈 成长股操作策略:")
                print(f"      1. 设置5%止损线")
                print(f"      2. 关注公司业绩和行业趋势")
                print(f"      3. 逢低分批买入")
                print(f"      4. 长期持有为主")
            elif position_type == 'value':
                print(f"    🏢 价值股操作策略:")
                print(f"      1. 设置7%止损线")
                print(f"      2. 关注股息率和估值")
                print(f"      3. 以时间换空间")
                print(f"      4. 适合长线持有")
    
    def _step7_monitoring_strategy(self):
        """步骤7: 监控策略"""
        print(f"\n🔍 步骤7: 监控策略")
        print("-" * 40)
        
        print(f"  风险监控要点:")
        print(f"    1. 📊 每日检查仓位比例")
        print(f"    2. ⚠️  严格执行止损纪律")
        print(f"    3. 📰 关注公司公告和行业新闻")
        print(f"    4. 💰 监控资金流向和市场情绪")
        print(f"    5. 🌍 关注国际局势和宏观政策")
        
        print(f"\n  关键监控指标:")
        for stock_code in self.user_stocks:
            stock_name = self._get_stock_name(stock_code)
            info = position_config.get_position_info(stock_code)
            
            print(f"    {stock_name}:")
            if info.get('risk_tolerance') == 'high':
                print(f"      - 每日波动率 > 5% 需警惕")
                print(f"      - 关注龙虎榜和游资动向")
            else:
                print(f"      - 关注基本面变化")
                print(f"      - 监控行业政策影响")
    
    def _get_stock_name(self, stock_code: str) -> str:
        """获取股票名称"""
        stock_names = {
            "601868.SH": "中国能建",
            "002506.SZ": "协鑫集成",
            "600821.SH": "金开新能",
        }
        return stock_names.get(stock_code, stock_code)
    
    def _get_position_type_name(self, position_type: str) -> str:
        """获取持仓类型名称"""
        type_names = {
            "value": "价值股",
            "growth": "成长股",
            "concept": "概念股",
            "unknown": "未知类型",
        }
        return type_names.get(position_type, position_type)
    
    def _get_risk_level_name(self, risk_level: str) -> str:
        """获取风险等级名称"""
        risk_names = {
            "high": "高风险",
            "medium": "中风险",
            "low": "低风险",
        }
        return risk_names.get(risk_level, risk_level)

def main():
    """主函数"""
    
    print("🔄 开始持仓股票分析...")
    
    # 创建分析器
    analyzer = PositionStockAnalysis()
    
    # 生成分析报告
    analyzer.generate_analysis_report()
    
    print(f"\n🎉 分析完成！")
    print(f"📈 持仓股票: {len(analyzer.user_stocks)} 只")
    print(f"💼 总持仓: {sum(position_config.USER_POSITIONS.values())} 股")
    print(f"📋 详细建议请查看上方报告")

if __name__ == "__main__":
    main()
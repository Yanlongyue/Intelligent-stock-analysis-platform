#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成HTML持仓分析报告
"""

import sys
import os
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

# 导入配置
from config.position_config import position_config

def generate_html_report():
    """生成HTML持仓分析报告"""
    
    # 获取当前日期
    today = datetime.now().strftime("%Y年%m月%d日")
    
    # HTML模板
    html_template = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>持仓股票七步法分析报告</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f7fa;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
            padding: 30px;
        }
        
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #3498db;
        }
        
        .header h1 {
            color: #2c3e50;
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .header .date {
            color: #7f8c8d;
            font-size: 18px;
        }
        
        .summary-box {
            background-color: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #3498db;
        }
        
        .summary-box h2 {
            color: #2c3e50;
            margin-bottom: 15px;
        }
        
        .stock-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stock-card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border: 1px solid #e0e0e0;
            transition: transform 0.2s;
        }
        
        .stock-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .stock-name {
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        .stock-code {
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 15px;
        }
        
        .stock-info {
            margin-bottom: 15px;
        }
        
        .info-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 8px;
            padding: 5px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .info-label {
            color: #666;
        }
        
        .info-value {
            font-weight: bold;
        }
        
        .risk-high {
            color: #e74c3c;
        }
        
        .risk-medium {
            color: #f39c12;
        }
        
        .risk-low {
            color: #27ae60;
        }
        
        .step-section {
            margin-bottom: 40px;
            padding: 20px;
            background-color: #fff;
            border-radius: 8px;
            border-left: 4px solid;
        }
        
        .step-1 { border-left-color: #3498db; }
        .step-2 { border-left-color: #9b59b6; }
        .step-3 { border-left-color: #e74c3c; }
        .step-4 { border-left-color: #2ecc71; }
        .step-5 { border-left-color: #f39c12; }
        .step-6 { border-left-color: #1abc9c; }
        .step-7 { border-left-color: #34495e; }
        
        .step-title {
            font-size: 24px;
            color: #2c3e50;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }
        
        .step-number {
            background-color: #3498db;
            color: white;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-weight: bold;
        }
        
        .suggestion-box {
            background-color: #f9f9f9;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
            border-left: 3px solid;
        }
        
        .buy-suggestion { border-left-color: #2ecc71; }
        .sell-suggestion { border-left-color: #e74c3c; }
        .hold-suggestion { border-left-color: #f39c12; }
        
        .warning-box {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
            color: #856404;
        }
        
        .success-box {
            background-color: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 6px;
            padding: 15px;
            margin: 15px 0;
            color: #155724;
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #7f8c8d;
            font-size: 14px;
        }
        
        .download-btn {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            margin-top: 20px;
            transition: background-color 0.3s;
        }
        
        .download-btn:hover {
            background-color: #2980b9;
        }
        
        @media (max-width: 768px) {
            .stock-grid {
                grid-template-columns: 1fr;
            }
            
            .container {
                padding: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 头部 -->
        <div class="header">
            <h1>📊 持仓股票七步法分析报告</h1>
            <div class="date">📅 分析日期: {today}</div>
        </div>
        
        <!-- 持仓概要 -->
        <div class="summary-box">
            <h2>📋 持仓概要</h2>
            <div class="info-row">
                <span class="info-label">持仓股票数量:</span>
                <span class="info-value">{total_stocks} 只</span>
            </div>
            <div class="info-row">
                <span class="info-label">总持仓数量:</span>
                <span class="info-value">{total_quantity} 股</span>
            </div>
            <div class="info-row">
                <span class="info-label">持仓总价值:</span>
                <span class="info-value">¥{total_value:,.2f}</span>
            </div>
        </div>
        
        <!-- 股票卡片 -->
        <h2 style="color: #2c3e50; margin-bottom: 20px;">📈 持仓股票详情</h2>
        <div class="stock-grid">
            {stock_cards}
        </div>
        
        <!-- 七步法分析 -->
        <h2 style="color: #2c3e50; margin-bottom: 20px;">🎯 七步法深度分析</h2>
        
        <!-- 步骤1: 持仓概述 -->
        <div class="step-section step-1">
            <div class="step-title">
                <div class="step-number">1</div>
                持仓概述
            </div>
            <p>您的持仓包含以下三只股票，总持仓1400股，总价值约¥5,760.00。</p>
            <p>当前持仓分布：中国能建(17.4%)、协鑫集成(22.2%)、金开新能(60.4%)。</p>
        </div>
        
        <!-- 步骤2: 股票基本信息 -->
        <div class="step-section step-2">
            <div class="step-title">
                <div class="step-number">2</div>
                股票基本信息
            </div>
            {stock_info}
        </div>
        
        <!-- 步骤3: 风险分析 -->
        <div class="step-section step-3">
            <div class="step-title">
                <div class="step-number">3</div>
                风险分析
            </div>
            {risk_analysis}
            <div class="warning-box">
                ⚠️ <strong>风险提示:</strong> 整体风险评分 2.7/3.0，整体风险偏高，建议适当减仓或增加对冲措施。
            </div>
        </div>
        
        <!-- 步骤4: 投资建议 -->
        <div class="step-section step-4">
            <div class="step-title">
                <div class="step-number">4</div>
                投资建议
            </div>
            {investment_suggestions}
        </div>
        
        <!-- 步骤5: 仓位管理 -->
        <div class="step-section step-5">
            <div class="step-title">
                <div class="step-number">5</div>
                仓位管理
            </div>
            <p><strong>总仓位建议:</strong></p>
            <ul style="margin-left: 20px; margin-bottom: 15px;">
                <li>⏳ 当前仓位：建议控制在 30-50%</li>
                <li>🎯 目标仓位：逐步调整到目标比例</li>
                <li>⚠️ 单股上限：不超过总资金的 15%</li>
            </ul>
            <p><strong>持仓股票目标仓位:</strong></p>
            <ul style="margin-left: 20px;">
                <li>中国能建：15.0%</li>
                <li>协鑫集成：12.0%</li>
                <li>金开新能：18.0%</li>
            </ul>
        </div>
        
        <!-- 步骤6: 操作计划 -->
        <div class="step-section step-6">
            <div class="step-title">
                <div class="step-number">6</div>
                操作计划
            </div>
            {operation_plan}
        </div>
        
        <!-- 步骤7: 监控策略 -->
        <div class="step-section step-7">
            <div class="step-title">
                <div class="step-number">7</div>
                监控策略
            </div>
            <p><strong>风险监控要点:</strong></p>
            <ul style="margin-left: 20px; margin-bottom: 15px;">
                <li>📊 每日检查仓位比例</li>
                <li>⚠️ 严格执行止损纪律</li>
                <li>📰 关注公司公告和行业新闻</li>
                <li>💰 监控资金流向和市场情绪</li>
                <li>🌍 关注国际局势和宏观政策</li>
            </ul>
            <p><strong>关键监控指标:</strong></p>
            <ul style="margin-left: 20px;">
                <li>中国能建：关注基本面变化，监控行业政策影响</li>
                <li>协鑫集成：每日波动率 > 5%需警惕，关注龙虎榜和游资动向</li>
                <li>金开新能：每日波动率 > 5%需警惕，关注龙虎榜和游资动向</li>
            </ul>
        </div>
        
        <!-- 下载按钮 -->
        <div style="text-align: center; margin-top: 40px;">
            <a href="#" class="download-btn" onclick="window.print()">🖨️ 打印报告</a>
            <button class="download-btn" onclick="saveAsPDF()" style="margin-left: 10px;">📥 保存为PDF</button>
        </div>
        
        <!-- 页脚 -->
        <div class="footer">
            <p>🧠 七步法股票分析程序 | 📅 生成时间: {current_time}</p>
            <p>⚠️ 免责声明: 本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。</p>
        </div>
    </div>
    
    <script>
        function saveAsPDF() {
            alert("PDF保存功能需要浏览器支持。建议使用打印功能（Ctrl+P），然后选择'保存为PDF'。");
            window.print();
        }
        
        // 页面加载完成后执行
        document.addEventListener('DOMContentLoaded', function() {
            console.log('持仓分析报告加载完成');
        });
    </script>
</body>
</html>"""
    
    # 获取持仓数据
    user_stocks = position_config.get_user_stocks()
    total_stocks = len(user_stocks)
    total_quantity = sum(position_config.USER_POSITIONS.values())
    
    # 模拟股票价格计算总价值
    stock_prices = {
        "601868.SH": 2.50,   # 中国能建
        "002506.SZ": 3.20,   # 协鑫集成
        "600821.SH": 5.80,   # 金开新能
    }
    total_value = position_config.get_total_value(stock_prices)
    
    # 生成股票卡片
    stock_cards = ""
    for stock_code in user_stocks:
        stock_name = get_stock_name(stock_code)
        info = position_config.get_position_info(stock_code)
        position_type = get_position_type_name(info.get('position_type', 'unknown'))
        risk_level = info.get('risk_tolerance', 'medium')
        
        # 风险等级颜色
        risk_class = f"risk-{risk_level}"
        
        stock_cards += f"""
            <div class="stock-card">
                <div class="stock-name">{stock_name}</div>
                <div class="stock-code">{stock_code}</div>
                <div class="stock-info">
                    <div class="info-row">
                        <span class="info-label">持仓数量:</span>
                        <span class="info-value">{info.get('quantity', 0)} 股</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">持仓类型:</span>
                        <span class="info-value">{position_type}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">风险等级:</span>
                        <span class="info-value {risk_class}">{get_risk_level_name(risk_level)}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">目标仓位:</span>
                        <span class="info-value">{info.get('target_ratio', 0.1)*100:.1f}%</span>
                    </div>
                </div>
            </div>
        """
    
    # 股票详细信息
    stock_info = ""
    for stock_code in user_stocks:
        stock_name = get_stock_name(stock_code)
        info = position_config.get_position_info(stock_code)
        position_type = get_position_type_name(info.get('position_type', 'unknown'))
        risk_level = get_risk_level_name(info.get('risk_tolerance', 'medium'))
        
        stock_info += f"""
            <p><strong>{stock_name}({stock_code}):</strong></p>
            <ul style="margin-left: 20px; margin-bottom: 15px;">
                <li>持仓数量: {info.get('quantity', 0)} 股</li>
                <li>持仓类型: {position_type}</li>
                <li>风险等级: {risk_level}</li>
                <li>目标仓位: {info.get('target_ratio', 0.1)*100:.1f}%</li>
            </ul>
        """
    
    # 风险分析
    risk_analysis = ""
    for stock_code in user_stocks:
        stock_name = get_stock_name(stock_code)
        info = position_config.get_position_info(stock_code)
        risk_level = info.get('risk_tolerance', 'medium')
        
        if risk_level == 'high':
            risk_text = "🔴 高风险股票 (概念股/成长股)"
            risk_desc = "波动大，收益潜力高，风险也高。建议密切关注，设置3%止损。"
        elif risk_level == 'medium':
            risk_text = "🟡 中风险股票 (价值股)"
            risk_desc = "相对稳定，适合中长期持有。建议设置5%止损，分批操作。"
        else:
            risk_text = "🟢 低风险股票"
            risk_desc = "建议设置7%止损，稳健持有。"
        
        risk_analysis += f"""
            <p><strong>{stock_name}:</strong> {risk_text}</p>
            <p style="margin-left: 20px; margin-bottom: 15px;">{risk_desc}</p>
        """
    
    # 投资建议
    investment_suggestions = ""
    total_capital = 100000.0
    suggestions = position_config.get_rebalancing_suggestions(stock_prices, total_capital)
    
    for stock_code, suggestion in suggestions.items():
        stock_name = get_stock_name(stock_code)
        
        if suggestion['action'] == 'buy':
            suggestion_class = "buy-suggestion"
            action_icon = "🟢"
            action_text = "建议买入"
        elif suggestion['action'] == 'sell':
            suggestion_class = "sell-suggestion"
            action_icon = "🔴"
            action_text = "建议卖出"
        else:
            suggestion_class = "hold-suggestion"
            action_icon = "🟡"
            action_text = "建议持有"
        
        investment_suggestions += f"""
            <div class="suggestion-box {suggestion_class}">
                <p><strong>{action_icon} {stock_name}: {action_text}</strong></p>
                <div class="info-row">
                    <span class="info-label">当前仓位:</span>
                    <span class="info-value">{suggestion['current_ratio']}% (目标: {suggestion['target_ratio']}%)</span>
                </div>
                <div class="info-row">
                    <span class="info-label">建议操作:</span>
                    <span class="info-value">{suggestion['action_quantity']} 股</span>
                </div>
                <div class="info-row">
                    <span class="info-label">操作金额:</span>
                    <span class="info-value">¥{suggestion['difference']:.2f}</span>
                </div>
            </div>
        """
    
    # 操作计划
    operation_plan = ""
    for stock_code in user_stocks:
        stock_name = get_stock_name(stock_code)
        info = position_config.get_position_info(stock_code)
        position_type = info.get('position_type', 'unknown')
        
        if position_type == 'concept':
            strategy = """
                <li>设置3%止损线</li>
                <li>快进快出，不恋战</li>
                <li>关注市场情绪和游资动向</li>
                <li>获利5-10%考虑减仓</li>
            """
        elif position_type == 'growth':
            strategy = """
                <li>设置5%止损线</li>
                <li>关注公司业绩和行业趋势</li>
                <li>逢低分批买入</li>
                <li>长期持有为主</li>
            """
        elif position_type == 'value':
            strategy = """
                <li>设置7%止损线</li>
                <li>关注股息率和估值</li>
                <li>以时间换空间</li>
                <li>适合长线持有</li>
            """
        else:
            strategy = "<li>根据市场情况灵活操作</li>"
        
        operation_plan += f"""
            <p><strong>{stock_name}:</strong></p>
            <ul style="margin-left: 20px; margin-bottom: 15px;">
                {strategy}
            </ul>
        """
    
    # 当前时间
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 填充模板
    html_content = html_template.format(
        today=today,
        total_stocks=total_stocks,
        total_quantity=total_quantity,
        total_value=total_value,
        stock_cards=stock_cards,
        stock_info=stock_info,
        risk_analysis=risk_analysis,
        investment_suggestions=investment_suggestions,
        operation_plan=operation_plan,
        current_time=current_time
    )
    
    # 保存HTML文件
    reports_dir = Path(__file__).parent / "reports" / "html"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = reports_dir / f"持仓股票分析报告_{datetime.now().strftime('%Y%m%d')}.html"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML报告已生成: {output_file}")
    return output_file

def get_stock_name(stock_code: str) -> str:
    """获取股票名称"""
    stock_names = {
        "601868.SH": "中国能建",
        "002506.SZ": "协鑫集成",
        "600821.SH": "金开新能",
    }
    return stock_names.get(stock_code, stock_code)

def get_position_type_name(position_type: str) -> str:
    """获取持仓类型名称"""
    type_names = {
        "value": "价值股",
        "growth": "成长股",
        "concept": "概念股",
        "unknown": "未知类型",
    }
    return type_names.get(position_type, position_type)

def get_risk_level_name(risk_level: str) -> str:
    """获取风险等级名称"""
    risk_names = {
        "high": "高风险",
        "medium": "中风险",
        "low": "低风险",
    }
    return risk_names.get(risk_level, risk_level)

def main():
    """主函数"""
    print("🔄 开始生成HTML持仓分析报告...")
    
    try:
        output_file = generate_html_report()
        print(f"\n🎉 HTML报告生成成功！")
        print(f"📂 文件位置: {output_file}")
        print(f"🌐 访问地址: http://localhost:8899/stock_analysis_program/reports/html/持仓股票分析报告_{datetime.now().strftime('%Y%m%d')}.html")
        print(f"\n📋 报告内容:")
        print(f"  1. 持仓概要")
        print(f"  2. 股票详情卡片")
        print(f"  3. 七步法深度分析")
        print(f"  4. 风险分析")
        print(f"  5. 投资建议")
        print(f"  6. 操作计划")
        print(f"  7. 监控策略")
        
    except Exception as e:
        print(f"❌ 生成HTML报告时出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
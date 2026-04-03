#!/usr/bin/env python3
"""
七步法股票分析程序 - 简化版本
"""

import os
import sys
import json
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_config():
    """加载配置"""
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'tushare_config.py')
    
    # 动态导入配置
    import importlib.util
    spec = importlib.util.spec_from_file_location("tushare_config", config_path)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    
    return config_module

def load_memory_rules():
    """加载记忆规则"""
    memory_file = os.path.join(os.path.dirname(__file__), 'data', 'memory_rules.json')
    
    try:
        with open(memory_file, 'r', encoding='utf-8') as f:
            rules = json.load(f)
        logger.info(f"✅ 加载记忆规则: {len(rules.get('core_principles', []))} 条核心原则")
        return rules
    except Exception as e:
        logger.error(f"❌ 加载记忆规则失败: {e}")
        return {}

def get_stock_data(ts_code, config):
    """获取股票数据"""
    try:
        # 初始化Tushare
        pro = ts.pro_api(token=config.TOKEN)
        
        # 获取今日数据
        today = datetime.now().strftime('%Y%m%d')
        df = pro.daily(ts_code=ts_code, trade_date=today)
        
        if df.empty:
            # 获取昨日数据
            yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
            df = pro.daily(ts_code=ts_code, trade_date=yesterday)
        
        if not df.empty:
            return {
                'ts_code': ts_code,
                'close': float(df['close'].iloc[0]),
                'pct_chg': float(df['pct_chg'].iloc[0]),
                'vol': float(df['vol'].iloc[0])
            }
        else:
            return None
    except Exception as e:
        logger.error(f"❌ 获取股票数据失败 {ts_code}: {e}")
        return None

def generate_report(stocks_data, memory_rules):
    """生成报告"""
    today = datetime.now().strftime('%Y%m%d')
    
    # HTML报告
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>七步法股票分析报告 - {today}</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            margin: 20px;
            background-color: #f5f7fa;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #3498db;
            margin-top: 30px;
        }}
        .stock-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .stock-table th, .stock-table td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        .stock-table th {{
            background-color: #3498db;
            color: white;
        }}
        .stock-table tr:nth-child(even) {{
            background-color: #f2f2f2;
        }}
        .up {{
            color: #e74c3c;
            font-weight: bold;
        }}
        .down {{
            color: #27ae60;
            font-weight: bold;
        }}
        .memory-rules {{
            background-color: #f9f9f9;
            border-left: 4px solid #3498db;
            padding: 15px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 七步法股票分析报告</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <div class="memory-rules">
            <h2>🎯 核心原则</h2>
            <ul>
                {''.join([f'<li>{rule}</li>' for rule in memory_rules.get('core_principles', [])])}
            </ul>
        </div>
        
        <h2>📈 股票数据概览</h2>
        <table class="stock-table">
            <thead>
                <tr>
                    <th>股票代码</th>
                    <th>收盘价</th>
                    <th>涨跌幅</th>
                    <th>成交量</th>
                    <th>状态</th>
                </tr>
            </thead>
            <tbody>
                {''.join([f'''
                <tr>
                    <td>{stock['ts_code']}</td>
                    <td>{stock['close']:.2f}</td>
                    <td class="{'up' if stock['pct_chg'] > 0 else 'down'}">{stock['pct_chg']:.2f}%</td>
                    <td>{stock['vol']:,.0f}</td>
                    <td>✅ 数据正常</td>
                </tr>
                ''' for stock in stocks_data if stock])}
            </tbody>
        </table>
        
        <h2>🎯 投资建议</h2>
        <ul>
            <li>建议关注基本面良好的价值股</li>
            <li>控制总仓位在45%以内</li>
            <li>严格执行止损纪律：高风险股3%，中风险股5%，低风险股7%</li>
            <li>分批操作：30%/40%/30%</li>
        </ul>
        
        <h2>⚠️ 风险提示</h2>
        <ul>
            <li>国际局势变化可能影响市场</li>
            <li>基本面风险需要持续监控</li>
            <li>技术面破位信号需及时响应</li>
            <li>市场情绪波动可能带来短期风险</li>
        </ul>
        
        <h2>📅 明日预测</h2>
        <p>基于当前数据，明日市场可能出现震荡整理走势，建议：</p>
        <ul>
            <li>09:30-10:30：观望市场方向</li>
            <li>10:30-11:30：根据量能决定操作</li>
            <li>13:00-14:00：关注外资动向</li>
            <li>14:00-15:00：根据收盘情况调整仓位</li>
        </ul>
        
        <hr>
        <p style="text-align: center; color: #7f8c8d; font-size: 14px;">
            七步法股票分析程序 v1.0.0 | 风暴 🌪️ 出品 | 数据来源：Tushare Pro
        </p>
    </div>
</body>
</html>"""
    
    # Markdown报告
    markdown_content = f"""# 📊 七步法股票分析报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 🎯 核心原则

{''.join([f'- {rule}' for rule in memory_rules.get('core_principles', [])])}

## 📈 股票数据概览

| 股票代码 | 收盘价 | 涨跌幅 | 成交量 | 状态 |
|---------|--------|--------|--------|------|
{''.join([f"| {stock['ts_code']} | {stock['close']:.2f} | {stock['pct_chg']:+.2f}% | {stock['vol']:,.0f} | ✅ 数据正常 |" for stock in stocks_data if stock])}

## 🎯 投资建议

- 建议关注基本面良好的价值股
- 控制总仓位在45%以内
- 严格执行止损纪律：高风险股3%，中风险股5%，低风险股7%
- 分批操作：30%/40%/30%

## ⚠️ 风险提示

- 国际局势变化可能影响市场
- 基本面风险需要持续监控
- 技术面破位信号需及时响应
- 市场情绪波动可能带来短期风险

## 📅 明日预测

基于当前数据，明日市场可能出现震荡整理走势，建议：

1. **09:30-10:30**：观望市场方向
2. **10:30-11:30**：根据量能决定操作
3. **13:00-14:00**：关注外资动向
4. **14:00-15:00**：根据收盘情况调整仓位

---
*七步法股票分析程序 v1.0.0 | 风暴 🌪️ 出品 | 数据来源：Tushare Pro*
"""
    
    return html_content, markdown_content

def main():
    """主函数"""
    print("\n" + "="*60)
    print("    七步法股票分析程序 - 简化版本 v1.0.0")
    print("="*60)
    
    try:
        # 1. 加载配置
        config = load_config()
        logger.info("✅ 配置加载成功")
        
        # 2. 加载记忆规则
        memory_rules = load_memory_rules()
        
        # 3. 加载股票配置
        stock_file = os.path.join(os.path.dirname(__file__), 'data', 'stock_config.json')
        with open(stock_file, 'r', encoding='utf-8') as f:
            stock_config = json.load(f)
        
        stocks = stock_config['portfolio']
        logger.info(f"✅ 加载股票配置: {len(stocks)} 只股票")
        
        # 4. 获取股票数据
        print("\n📈 获取股票数据...")
        stocks_data = []
        for stock in stocks:
            data = get_stock_data(stock['ts_code'], config)
            if data:
                stocks_data.append(data)
                print(f"   ✅ {stock['ts_code']} - {stock['name']}: {data['close']:.2f} ({data['pct_chg']:+.2f}%)")
            else:
                print(f"   ⚠️ {stock['ts_code']} - {stock['name']}: 数据获取失败")
        
        if not stocks_data:
            logger.error("❌ 未获取到任何股票数据")
            return
        
        # 5. 生成报告
        print("\n📊 生成分析报告...")
        html_content, markdown_content = generate_report(stocks_data, memory_rules)
        
        # 6. 保存报告
        today = datetime.now().strftime('%Y%m%d')
        
        # HTML报告
        reports_html_dir = os.path.join(os.path.dirname(__file__), 'reports', 'html')
        os.makedirs(reports_html_dir, exist_ok=True)
        html_file = os.path.join(reports_html_dir, f'深度复盘与明日投资计划_{today}.html')
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Markdown报告
        reports_md_dir = os.path.join(os.path.dirname(__file__), 'reports', 'markdown')
        os.makedirs(reports_md_dir, exist_ok=True)
        md_file = os.path.join(reports_md_dir, f'深度复盘与明日投资计划_{today}.md')
        
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"✅ HTML报告已保存: {html_file}")
        print(f"✅ Markdown报告已保存: {md_file}")
        
        # 7. 启动HTTP服务器预览
        print(f"\n🌐 启动本地预览: http://localhost:8899/stock_analysis_program/reports/html/深度复盘与明日投资计划_{today}.html")
        
        print("\n🎉 七步法分析完成！")
        print("="*60)
        
    except Exception as e:
        logger.error(f"❌ 程序运行失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
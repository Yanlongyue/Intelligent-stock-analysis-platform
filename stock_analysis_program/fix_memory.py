#!/usr/bin/env python3
"""
修复记忆管理器问题的脚本
"""

import json
import os
import sys

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def fix_memory_issue():
    """修复记忆加载问题"""
    print("🔧 修复记忆管理器问题...")
    
    # 1. 确保数据目录存在
    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✅ 创建数据目录: {data_dir}")
    
    # 2. 创建记忆规则文件
    memory_file = os.path.join(data_dir, 'memory_rules.json')
    
    memory_rules = {
        "core_principles": [
            "数据是分析的基石，数据错了，分析再多都是错的",
            "必须使用真实API数据",
            "对比方法必须正确：用昨天预测的股价来对比今天的实际股价",
            "样式布局必须一致：保持与模板完全相同的结构和排版",
            "强制记忆检索必须执行：每次分析前必须读取长期记忆",
            "自动化程序已创建：七步法流程已完全自动化，确保质量和一致性"
        ],
        "analysis_rules": [
            "国际风险权重: 55%（国际局势缓解，从60%下调）",
            "基本面权重: 65%（维持不变）",
            "技术面权重: 40%（维持不变）",
            "总仓位上限: ≤45%（国际风险缓解，从30%上调）"
        ]
    }
    
    with open(memory_file, 'w', encoding='utf-8') as f:
        json.dump(memory_rules, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 创建记忆规则文件: {memory_file}")
    print(f"✅ 包含 {len(memory_rules['core_principles'])} 条核心原则")
    print(f"✅ 包含 {len(memory_rules['analysis_rules'])} 条分析规则")
    
    # 3. 创建一个简单的股票配置
    stock_config_file = os.path.join(data_dir, 'stock_config.json')
    
    stock_config = {
        "portfolio": [
            {
                "ts_code": "000001.SZ",
                "name": "平安银行",
                "category": "价值股",
                "risk_level": "中等"
            },
            {
                "ts_code": "600519.SH",
                "name": "贵州茅台",
                "category": "价值股",
                "risk_level": "低"
            },
            {
                "ts_code": "300750.SZ",
                "name": "宁德时代",
                "category": "成长股",
                "risk_level": "中等"
            }
        ],
        "analysis_date": "2026-04-02"
    }
    
    with open(stock_config_file, 'w', encoding='utf-8') as f:
        json.dump(stock_config, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 创建股票配置文件: {stock_config_file}")
    print(f"✅ 包含 {len(stock_config['portfolio'])} 只股票")
    
    # 4. 创建一个简单的模板文件
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    if not os.path.exists(templates_dir):
        os.makedirs(templates_dir)
    
    template_file = os.path.join(templates_dir, 'report_template.md')
    
    template_content = """# 七步法股票分析报告

## 第一部分：深度复盘

### 昨日预测准确性统计

## 第二部分：误差分析

### 系统性误差原因分析

## 第三部分：明日小时级预测

### 总体市场环境

## 第四部分：投资计划与仓位管理

### 总体仓位建议

## 第五部分：风险控制与操作纪律

### 国际局势监控

## 第六部分：其他潜力股票推荐

### 推荐股票分析
"""
    
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✅ 创建模板文件: {template_file}")
    
    print("\n🎉 所有修复完成！")
    print("现在可以运行: python3 src/main.py --simple")
    
    return True

if __name__ == "__main__":
    fix_memory_issue()
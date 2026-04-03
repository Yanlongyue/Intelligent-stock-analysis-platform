#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
终端界面GUI应用程序
基于文本的股票分析界面
作者：风暴 🌪️
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path

class TerminalStockAnalyzer:
    """终端股票分析界面"""
    
    def __init__(self):
        self.running = True
        self.selection = 0
        self.options = [
            "📊 仪表盘 - 查看持仓股票",
            "🔍 运行分析 - 执行股票分析",
            "📈 持仓管理 - 管理持仓股票",
            "📑 报告查看 - 查看历史报告",
            "⚙️  设置 - 系统配置",
            "❌ 退出程序"
        ]
        
    def clear_screen(self):
        """清屏"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
    def print_header(self):
        """打印头部"""
        print("=" * 60)
        print("股票分析专业版 - 终端界面")
        print("=" * 60)
        print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
    def print_menu(self):
        """打印菜单"""
        print("\n📱 主菜单:")
        for i, option in enumerate(self.options):
            if i == self.selection:
                print(f"  ▶ [{i+1}] {option}  ◀")
            else:
                print(f"   [{i+1}] {option}")
                
    def print_dashboard(self):
        """打印仪表盘"""
        self.clear_screen()
        self.print_header()
        
        print("\n📊 持仓股票监控:")
        print("-" * 60)
        
        stocks = [
            {"code": "601868.SH", "name": "中国能建", "price": "2.45", "change": "+1.24%", "quantity": "400"},
            {"code": "002506.SZ", "name": "协鑫集成", "price": "3.15", "change": "-0.63%", "quantity": "400"},
            {"code": "600821.SH", "name": "金开新能", "price": "5.75", "change": "+2.68%", "quantity": "600"},
        ]
        
        for stock in stocks:
            change_color = "\033[92m" if "+" in stock['change'] else "\033[91m"  # 绿色或红色
            reset_color = "\033[0m"
            
            print(f"  {stock['name']} ({stock['code']})")
            print(f"    当前价: ¥{stock['price']}")
            print(f"    涨跌幅: {change_color}{stock['change']}{reset_color}")
            print(f"    持仓量: {stock['quantity']}股")
            print()
            
        # 统计信息
        print("📈 持仓统计:")
        print("-" * 60)
        print("  总市值: ¥25,680.00")
        print("  总盈亏: +¥1,245.60 (+5.1%)")
        print("  风险等级: 中等")
        print()
        
        input("按回车键返回主菜单...")
        
    def run_analysis(self):
        """运行分析"""
        self.clear_screen()
        self.print_header()
        
        print("\n🔍 运行股票分析")
        print("-" * 60)
        
        print("请选择分析类型:")
        print("  1. 完整分析")
        print("  2. 快速分析")
        print("  3. 持仓分析")
        
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == "1":
            analysis_type = "完整分析"
        elif choice == "2":
            analysis_type = "快速分析"
        elif choice == "3":
            analysis_type = "持仓分析"
        else:
            print("无效选择，返回主菜单")
            time.sleep(2)
            return
            
        print(f"\n开始{analysis_type}...")
        
        # 模拟分析过程
        steps = [
            "1. 获取股票数据...",
            "2. 计算技术指标...", 
            "3. 分析基本面...",
            "4. 评估风险...",
            "5. 生成报告..."
        ]
        
        for step in steps:
            print(f"  {step}")
            time.sleep(0.5)
            
        print(f"\n✅ {analysis_type}完成！")
        print("报告已生成到 reports/html/ 目录")
        
        input("\n按回车键返回主菜单...")
        
    def manage_portfolio(self):
        """管理持仓"""
        self.clear_screen()
        self.print_header()
        
        print("\n📈 持仓管理")
        print("-" * 60)
        
        print("当前持仓股票:")
        print("-" * 30)
        
        portfolio = [
            ("601868.SH", "中国能建", "400", "2.40", "2.45", "980.00", "+20.00"),
            ("002506.SZ", "协鑫集成", "400", "3.20", "3.15", "1260.00", "-20.00"),
            ("600821.SH", "金开新能", "600", "5.50", "5.75", "3450.00", "+150.00"),
        ]
        
        print("代码       名称       数量   成本价  当前价   市值      盈亏")
        print("-" * 60)
        for item in portfolio:
            print(f"{item[0]:<10} {item[1]:<8} {item[2]:<6} {item[3]:<7} {item[4]:<7} {item[5]:<8} {item[6]:<8}")
            
        print()
        print("操作选项:")
        print("  1. 添加股票")
        print("  2. 编辑股票")
        print("  3. 删除股票")
        print("  4. 刷新数据")
        print("  5. 返回主菜单")
        
        choice = input("\n请选择 (1-5): ").strip()
        
        if choice == "1":
            print("\n添加股票功能开发中...")
        elif choice == "2":
            print("\n编辑股票功能开发中...")
        elif choice == "3":
            print("\n删除股票功能开发中...")
        elif choice == "4":
            print("\n正在刷新数据...")
            time.sleep(1)
            print("数据刷新完成")
        elif choice == "5":
            return
            
        time.sleep(2)
        
    def view_reports(self):
        """查看报告"""
        self.clear_screen()
        self.print_header()
        
        print("\n📑 报告查看")
        print("-" * 60)
        
        # 检查报告目录
        reports_dir = Path(__file__).parent / "reports"
        
        if reports_dir.exists():
            print("可用报告:")
            print("-" * 30)
            
            # HTML报告
            html_dir = reports_dir / "html"
            if html_dir.exists():
                html_files = list(html_dir.glob("*.html"))
                if html_files:
                    print("HTML报告:")
                    for file in sorted(html_files, reverse=True)[:5]:  # 最近5个
                        print(f"  📄 {file.name}")
                    print()
                    
            # Markdown报告
            md_dir = reports_dir / "markdown"
            if md_dir.exists():
                md_files = list(md_dir.glob("*.md"))
                if md_files:
                    print("Markdown报告:")
                    for file in sorted(md_files, reverse=True)[:5]:  # 最近5个
                        print(f"  📋 {file.name}")
                    print()
                    
            if not (html_files or md_files):
                print("未找到报告文件")
        else:
            print("报告目录不存在")
            
        print()
        print("操作选项:")
        print("  1. 查看最新HTML报告")
        print("  2. 查看最新Markdown报告")
        print("  3. 返回主菜单")
        
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == "1":
            print("\n正在打开最新HTML报告...")
            time.sleep(1)
            print("请在浏览器中查看 reports/html/ 目录下的最新文件")
        elif choice == "2":
            print("\n正在打开最新Markdown报告...")
            time.sleep(1)
            print("请在终端中查看 reports/markdown/ 目录下的最新文件")
        elif choice == "3":
            return
            
        input("\n按回车键继续...")
        
    def show_settings(self):
        """显示设置"""
        self.clear_screen()
        self.print_header()
        
        print("\n⚙️  系统设置")
        print("-" * 60)
        
        print("当前配置:")
        print("-" * 30)
        print("  1. 自动刷新: 开启")
        print("  2. 更新频率: 5分钟")
        print("  3. 默认分析类型: 完整分析")
        print("  4. 通知设置: 关闭")
        
        print()
        print("操作选项:")
        print("  1. 修改设置")
        print("  2. 保存配置")
        print("  3. 返回主菜单")
        
        choice = input("\n请选择 (1-3): ").strip()
        
        if choice == "1":
            print("\n设置修改功能开发中...")
        elif choice == "2":
            print("\n配置已保存")
        elif choice == "3":
            return
            
        time.sleep(2)
        
    def main_loop(self):
        """主循环"""
        while self.running:
            self.clear_screen()
            self.print_header()
            self.print_menu()
            
            print("\n使用方向键↑↓选择，回车键确认，或直接输入选项编号")
            print("-" * 60)
            
            # 获取用户输入
            try:
                user_input = input("\n请选择: ").strip()
                
                if user_input == "":
                    # 回车键确认当前选择
                    self.handle_selection()
                elif user_input.isdigit():
                    # 直接输入数字
                    option_num = int(user_input) - 1
                    if 0 <= option_num < len(self.options):
                        self.selection = option_num
                        self.handle_selection()
                    else:
                        print("无效选项，请重新选择")
                        time.sleep(1)
                elif user_input in ["q", "Q", "quit", "exit"]:
                    self.running = False
                else:
                    print("无效输入，请重新选择")
                    time.sleep(1)
                    
            except KeyboardInterrupt:
                print("\n\n程序被中断")
                self.running = False
            except Exception as e:
                print(f"错误: {e}")
                time.sleep(2)
                
    def handle_selection(self):
        """处理选择"""
        option = self.options[self.selection]
        
        if "仪表盘" in option:
            self.print_dashboard()
        elif "运行分析" in option:
            self.run_analysis()
        elif "持仓管理" in option:
            self.manage_portfolio()
        elif "报告查看" in option:
            self.view_reports()
        elif "设置" in option:
            self.show_settings()
        elif "退出程序" in option:
            print("\n感谢使用股票分析专业版！")
            self.running = False
            time.sleep(1)
            
    def run(self):
        """运行程序"""
        print("启动股票分析专业版终端界面...")
        time.sleep(1)
        self.main_loop()

def main():
    """主函数"""
    app = TerminalStockAnalyzer()
    app.run()

if __name__ == "__main__":
    main()
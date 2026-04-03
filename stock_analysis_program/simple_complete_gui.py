#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的完整GUI应用程序
解决macOS版本兼容性问题
作者：风暴 🌪️
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
import json
import os
import sys
from pathlib import Path

class SimpleStockAnalyzerGUI:
    """简化的股票分析GUI应用程序"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("股票分析专业版 - 简化GUI")
        self.root.geometry("1000x700")
        
        # 设置窗口图标和背景
        try:
            self.root.configure(bg='#f5f7fa')
        except:
            pass
        
        # 初始化变量
        self.is_analyzing = False
        self.portfolio_data = []
        
        # 创建界面
        self.create_menu()
        self.create_main_content()
        self.create_statusbar()
        
        # 加载模拟数据
        self.load_mock_data()
        
    def create_menu(self):
        """创建简化菜单"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 分析菜单
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="分析", menu=analysis_menu)
        analysis_menu.add_command(label="运行分析", command=self.run_analysis)
        analysis_menu.add_command(label="查看报告", command=self.view_reports)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
        
    def create_main_content(self):
        """创建主要内容区域"""
        # 创建标签页控件
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建各个标签页
        self.create_dashboard_tab()
        self.create_analysis_tab()
        self.create_portfolio_tab()
        
    def create_dashboard_tab(self):
        """创建仪表盘标签页"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="📊 仪表盘")
        
        # 标题
        title_label = ttk.Label(dashboard_frame, text="股票分析仪表盘", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # 股票卡片区域
        cards_frame = ttk.Frame(dashboard_frame)
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=20)
        
        # 创建股票卡片
        self.stock_cards = []
        
        stock_data = [
            {"code": "601868.SH", "name": "中国能建", "price": "2.45", "change": "+1.24%"},
            {"code": "002506.SZ", "name": "协鑫集成", "price": "3.15", "change": "-0.63%"},
            {"code": "600821.SH", "name": "金开新能", "price": "5.75", "change": "+2.68%"},
        ]
        
        for stock in stock_data:
            card = self.create_stock_card(cards_frame, stock)
            self.stock_cards.append(card)
            
        # 统计信息
        stats_frame = ttk.LabelFrame(dashboard_frame, text="持仓统计", padding=15)
        stats_frame.pack(fill=tk.X, padx=20, pady=20)
        
        ttk.Label(stats_frame, text="总市值：¥25,680.00").pack(anchor=tk.W, pady=5)
        ttk.Label(stats_frame, text="总盈亏：+¥1,245.60 (+5.1%)").pack(anchor=tk.W, pady=5)
        ttk.Label(stats_frame, text="风险等级：中等").pack(anchor=tk.W, pady=5)
        
        # 操作按钮
        btn_frame = ttk.Frame(dashboard_frame)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(btn_frame, text="刷新数据", command=self.refresh_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="运行分析", command=self.run_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="查看报告", command=self.view_reports).pack(side=tk.RIGHT, padx=5)
        
    def create_stock_card(self, parent, stock):
        """创建股票卡片"""
        card_frame = ttk.LabelFrame(parent, text=f"{stock['name']} ({stock['code']})", padding=10)
        card_frame.pack(fill=tk.X, pady=10)
        
        # 价格信息
        price_frame = ttk.Frame(card_frame)
        price_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(price_frame, text="当前价格：", font=("Arial", 10)).pack(side=tk.LEFT)
        price_label = ttk.Label(price_frame, text=f"¥{stock['price']}", font=("Arial", 12, "bold"), foreground="#27ae60")
        price_label.pack(side=tk.LEFT, padx=10)
        
        # 涨跌幅
        change_color = "#e74c3c" if "-" in stock['change'] else "#27ae60"
        change_label = ttk.Label(price_frame, text=stock['change'], font=("Arial", 10, "bold"), foreground=change_color)
        change_label.pack(side=tk.RIGHT)
        
        # 操作按钮
        btn_frame = ttk.Frame(card_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="详细分析", width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="查看图表", width=10).pack(side=tk.LEFT, padx=2)
        
        return {
            "frame": card_frame,
            "price": price_label,
            "change": change_label
        }
        
    def create_analysis_tab(self):
        """创建分析标签页"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="🔍 分析")
        
        # 标题
        title_label = ttk.Label(analysis_frame, text="股票分析控制面板", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # 分析选项
        options_frame = ttk.LabelFrame(analysis_frame, text="分析选项", padding=15)
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 分析类型
        type_frame = ttk.Frame(options_frame)
        type_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(type_frame, text="分析类型：", width=10).pack(side=tk.LEFT)
        self.analysis_type = tk.StringVar(value="full")
        
        ttk.Radiobutton(type_frame, text="完整分析", variable=self.analysis_type, value="full").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="快速分析", variable=self.analysis_type, value="quick").pack(side=tk.LEFT, padx=10)
        
        # 分析按钮
        btn_frame = ttk.Frame(options_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.run_btn = ttk.Button(btn_frame, text="开始分析", command=self.start_analysis, width=15)
        self.run_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="停止分析", command=self.stop_analysis, width=15, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 进度显示
        progress_frame = ttk.LabelFrame(analysis_frame, text="分析进度", padding=15)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 进度条
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate', length=400)
        self.progress_bar.pack(pady=10)
        
        # 状态标签
        self.status_label = ttk.Label(progress_frame, text="等待开始分析...")
        self.status_label.pack(pady=5)
        
        # 日志输出
        log_frame = ttk.LabelFrame(progress_frame, text="分析日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def create_portfolio_tab(self):
        """创建持仓标签页"""
        portfolio_frame = ttk.Frame(self.notebook)
        self.notebook.add(portfolio_frame, text="📈 持仓")
        
        # 标题
        title_label = ttk.Label(portfolio_frame, text="持仓管理", font=("Arial", 16, "bold"))
        title_label.pack(pady=20)
        
        # 持仓表格
        table_frame = ttk.LabelFrame(portfolio_frame, text="持仓股票列表", padding=15)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 创建表格
        columns = ('代码', '名称', '数量', '成本价', '当前价', '市值', '盈亏')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=8)
        
        # 设置列标题
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor=tk.CENTER)
            
        # 添加示例数据
        sample_data = [
            ('601868.SH', '中国能建', '400', '2.40', '2.45', '980.00', '+20.00'),
            ('002506.SZ', '协鑫集成', '400', '3.20', '3.15', '1260.00', '-20.00'),
            ('600821.SH', '金开新能', '600', '5.50', '5.75', '3450.00', '+150.00'),
        ]
        
        for data in sample_data:
            self.tree.insert('', tk.END, values=data)
            
        # 添加滚动条
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 操作按钮
        btn_frame = ttk.Frame(portfolio_frame)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Button(btn_frame, text="添加股票", width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="编辑选中", width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除选中", width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="刷新数据", command=self.refresh_data, width=12).pack(side=tk.RIGHT, padx=5)
        
    def create_statusbar(self):
        """创建状态栏"""
        self.statusbar = ttk.Frame(self.root)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_text = ttk.Label(self.statusbar, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 时间显示
        self.update_time()
        
    def update_time(self):
        """更新时间显示"""
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 如果时间标签不存在，创建它
        if not hasattr(self, 'time_label'):
            self.time_label = ttk.Label(self.statusbar, text=current_time, relief=tk.SUNKEN, anchor=tk.E, width=20)
            self.time_label.pack(side=tk.RIGHT)
        else:
            self.time_label.config(text=current_time)
            
        # 每秒更新一次
        self.root.after(1000, self.update_time)
        
    def load_mock_data(self):
        """加载模拟数据"""
        self.log_message("加载模拟数据...")
        
    def run_analysis(self):
        """运行分析"""
        if not self.is_analyzing:
            self.start_analysis()
            
    def start_analysis(self):
        """开始分析"""
        if self.is_analyzing:
            return
            
        self.is_analyzing = True
        self.run_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_bar.start()
        
        analysis_type = self.analysis_type.get()
        self.log_message(f"开始{analysis_type}分析...")
        self.update_status(f"正在运行{analysis_type}分析...")
        
        # 在新线程中模拟分析过程
        self.analysis_thread = threading.Thread(target=self._simulate_analysis, args=(analysis_type,))
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        
    def _simulate_analysis(self, analysis_type):
        """模拟分析过程"""
        try:
            # 模拟分析步骤
            steps = [
                "获取股票数据...",
                "计算技术指标...",
                "分析基本面...",
                "评估风险...",
                "生成报告..."
            ]
            
            for i, step in enumerate(steps):
                if not self.is_analyzing:
                    break
                    
                time.sleep(1)  # 模拟耗时操作
                progress = (i + 1) * 20
                
                # 在主线程中更新UI
                self.root.after(0, self._update_analysis_progress, step, progress)
                
            if self.is_analyzing:
                self.root.after(0, self._analysis_completed, True, analysis_type)
            else:
                self.root.after(0, self._analysis_completed, False, analysis_type)
                
        except Exception as e:
            self.root.after(0, self._analysis_completed, False, analysis_type, str(e))
            
    def _update_analysis_progress(self, step, progress):
        """更新分析进度"""
        self.log_message(step)
        
    def _analysis_completed(self, success, analysis_type, error_msg=None):
        """分析完成回调"""
        self.is_analyzing = False
        self.run_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        
        if success:
            self.log_message(f"{analysis_type}分析完成！")
            self.update_status("分析完成")
            messagebox.showinfo("成功", f"{analysis_type}分析完成！")
        else:
            if error_msg:
                self.log_message(f"分析失败: {error_msg}", level="error")
                self.update_status("分析失败")
                messagebox.showerror("错误", f"分析失败: {error_msg}")
            else:
                self.log_message("分析已停止", level="warning")
                self.update_status("分析已停止")
                
    def stop_analysis(self):
        """停止分析"""
        if self.is_analyzing:
            self.is_analyzing = False
            self.log_message("正在停止分析...", level="warning")
            
    def log_message(self, message, level="info"):
        """记录日志消息"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
    def update_status(self, message):
        """更新状态栏"""
        self.status_text.config(text=message)
        
    def refresh_data(self):
        """刷新数据"""
        self.log_message("刷新股票数据...")
        self.update_status("正在刷新数据...")
        
        # 模拟刷新过程
        self.root.after(1000, lambda: self._refresh_completed())
        
    def _refresh_completed(self):
        """刷新完成"""
        self.log_message("数据刷新完成")
        self.update_status("数据已刷新")
        
    def view_reports(self):
        """查看报告"""
        messagebox.showinfo("报告", "报告查看功能开发中...\n\n您可以查看以下位置：\nreports/html/\nreports/markdown/")
        
    def show_about(self):
        """显示关于信息"""
        about_text = """股票分析专业版 - 简化GUI
版本：1.0.0
作者：风暴 🌪️

功能：
- 股票监控仪表盘
- 分析控制面板
- 持仓管理
- 实时数据显示

技术支持：使用Python Tkinter开发
"""
        messagebox.showinfo("关于", about_text)

def main():
    """主函数"""
    root = tk.Tk()
    app = SimpleStockAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
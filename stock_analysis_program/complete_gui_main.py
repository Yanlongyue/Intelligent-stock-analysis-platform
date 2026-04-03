#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析完整GUI应用程序
功能：专业的股票分析桌面应用程序，支持可视化操作、实时监控、持仓管理、报告查看等
作者：风暴 🌪️
版本：1.0.0
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import time
import json
import os
import sys
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from pathlib import Path

# 添加项目路径，确保可以导入其他模块
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 尝试导入分析程序模块
try:
    from config.position_config import position_config
    from analyze_position_stocks import main as run_analysis
    from config.tushare_config import TUSHARE_TOKEN
    
    # 从position_config中提取数据
    POSITION_STOCKS = {}
    POSITION_WEIGHTS = {}
    
    # 从position_config中获取持仓股票
    for stock_code in position_config.get_user_stocks():
        POSITION_STOCKS[stock_code] = stock_code  # 暂时用代码作为名称
        POSITION_WEIGHTS[stock_code] = position_config.TARGET_POSITION_RATIOS.get(stock_code, 0.1) * 100
    
    POSITION_CONFIG = {
        "total_stocks": len(POSITION_STOCKS),
        "total_weight": sum(POSITION_WEIGHTS.values())
    }
    
    HAS_ANALYSIS_MODULE = True
except ImportError as e:
    print(f"分析模块导入失败: {e}")
    HAS_ANALYSIS_MODULE = False

class StockAnalyzerGUI:
    """完整的股票分析GUI应用程序"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("股票分析专业版 - 完整GUI（兼容模式）")
        self.root.geometry("1200x800")
        
        # 设置窗口图标
        try:
            self.root.iconbitmap(default="")  # 可以添加图标文件路径
        except:
            pass
        
        # 初始化变量
        self.is_analyzing = False
        self.analysis_thread = None
        self.portfolio_data = []
        self.report_files = []
        
        # 创建数据库连接
        self.db_path = project_root / "data" / "stock_gui.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_database()
        
        # 加载配置
        self.config = self.load_config()
        
        # 设置主题
        self.setup_theme()
        
        # 创建界面组件
        self.create_menu()
        self.create_toolbar()
        self.create_statusbar()
        self.create_main_content()
        
        # 加载初始数据
        self.load_initial_data()
        
        # 设置定时器
        self.setup_timers()
        
        # 绑定窗口事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_theme(self):
        """设置界面主题"""
        style = ttk.Style()
        style.theme_use('clam')  # 使用clam主题
        
        # 自定义颜色
        self.bg_color = "#f5f7fa"
        self.sidebar_color = "#2c3e50"
        self.header_color = "#3498db"
        self.success_color = "#27ae60"
        self.warning_color = "#f39c12"
        self.danger_color = "#e74c3c"
        
        # 设置主窗口背景色
        self.root.configure(bg=self.bg_color)
        
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="新建分析", command=self.new_analysis, accelerator="Ctrl+N")
        file_menu.add_command(label="打开报告", command=self.open_report, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="保存配置", command=self.save_config)
        file_menu.add_command(label="导出数据", command=self.export_data)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing, accelerator="Ctrl+Q")
        
        # 编辑菜单
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="持仓管理", command=self.open_portfolio_editor)
        edit_menu.add_command(label="偏好设置", command=self.open_settings)
        
        # 分析菜单
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="分析", menu=analysis_menu)
        analysis_menu.add_command(label="运行完整分析", command=self.run_full_analysis, accelerator="F5")
        analysis_menu.add_command(label="快速分析", command=self.run_quick_analysis, accelerator="Ctrl+F5")
        analysis_menu.add_command(label="持仓分析", command=self.run_portfolio_analysis)
        analysis_menu.add_separator()
        analysis_menu.add_command(label="查看历史分析", command=self.view_history)
        
        # 查看菜单
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="查看", menu=view_menu)
        view_menu.add_command(label="仪表盘", command=lambda: self.notebook.select(0))
        view_menu.add_command(label="分析面板", command=lambda: self.notebook.select(1))
        view_menu.add_command(label="持仓管理", command=lambda: self.notebook.select(2))
        view_menu.add_command(label="报告查看", command=lambda: self.notebook.select(3))
        view_menu.add_separator()
        view_menu.add_command(label="刷新", command=self.refresh_all, accelerator="F5")
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="数据更新", command=self.update_data)
        tools_menu.add_command(label="数据库管理", command=self.manage_database)
        tools_menu.add_command(label="清理缓存", command=self.clean_cache)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用手册", command=self.show_manual)
        help_menu.add_command(label="关于", command=self.show_about)
        
        # 绑定快捷键
        self.root.bind("<Control-n>", lambda e: self.new_analysis())
        self.root.bind("<Control-o>", lambda e: self.open_report())
        self.root.bind("<Control-q>", lambda e: self.on_closing())
        self.root.bind("<F5>", lambda e: self.run_full_analysis())
        self.root.bind("<Control-F5>", lambda e: self.run_quick_analysis())
        
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = ttk.Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        # 工具栏按钮
        buttons = [
            ("🏠 仪表盘", lambda: self.notebook.select(0), "切换到仪表盘"),
            ("📊 运行分析", self.run_full_analysis, "运行完整分析"),
            ("📈 持仓管理", self.open_portfolio_editor, "管理持仓股票"),
            ("📑 查看报告", lambda: self.notebook.select(3), "查看分析报告"),
            ("⚙️ 设置", self.open_settings, "打开设置面板"),
            ("🔄 刷新", self.refresh_all, "刷新所有数据"),
        ]
        
        for text, command, tooltip in buttons:
            btn = ttk.Button(toolbar, text=text, command=command, width=12)
            btn.pack(side=tk.LEFT, padx=2, pady=2)
            
    def create_statusbar(self):
        """创建状态栏"""
        self.statusbar = ttk.Frame(self.root)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 状态标签
        self.status_label = ttk.Label(self.statusbar, text="就绪", relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # 时间标签
        self.time_label = ttk.Label(self.statusbar, text="", relief=tk.SUNKEN, anchor=tk.E, width=20)
        self.time_label.pack(side=tk.RIGHT)
        
        # 更新状态栏时间
        self.update_time()
        
    def create_main_content(self):
        """创建主要内容区域"""
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建标签页控件
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建各个标签页
        self.create_dashboard_tab()
        self.create_analysis_tab()
        self.create_portfolio_tab()
        self.create_reports_tab()
        
    def create_dashboard_tab(self):
        """创建仪表盘标签页"""
        dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(dashboard_frame, text="仪表盘")
        
        # 创建左右布局
        left_panel = ttk.Frame(dashboard_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        right_panel = ttk.Frame(dashboard_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0), pady=5)
        
        # 左侧：股票卡片区域
        ttk.Label(left_panel, text="持仓股票监控", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # 创建滚动区域
        canvas = tk.Canvas(left_panel, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(left_panel, orient="vertical", command=canvas.yview)
        self.stock_cards_frame = ttk.Frame(canvas)
        
        self.stock_cards_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.stock_cards_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 右侧：统计信息
        ttk.Label(right_panel, text="统计分析", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        # 统计信息框架
        stats_frame = ttk.LabelFrame(right_panel, text="持仓统计", padding=10)
        stats_frame.pack(fill=tk.BOTH, expand=True)
        
        # 统计项
        self.total_value_label = ttk.Label(stats_frame, text="总市值：--")
        self.total_value_label.pack(anchor=tk.W, pady=5)
        
        self.total_profit_label = ttk.Label(stats_frame, text="总盈亏：--")
        self.total_profit_label.pack(anchor=tk.W, pady=5)
        
        self.risk_level_label = ttk.Label(stats_frame, text="风险等级：--")
        self.risk_level_label.pack(anchor=tk.W, pady=5)
        
        self.update_time_label = ttk.Label(stats_frame, text="更新时间：--")
        self.update_time_label.pack(anchor=tk.W, pady=5)
        
        # 操作按钮
        btn_frame = ttk.Frame(stats_frame)
        btn_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(btn_frame, text="刷新数据", command=self.update_stock_data).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="导出统计", command=self.export_stats).pack(side=tk.LEFT, padx=2)
        
    def create_stock_card(self, stock_code, stock_name):
        """创建单个股票卡片"""
        card_frame = ttk.LabelFrame(self.stock_cards_frame, text=f"{stock_name} ({stock_code})", padding=10)
        card_frame.pack(fill=tk.X, pady=5, padx=5)
        
        # 股票信息
        info_frame = ttk.Frame(card_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        # 价格信息
        price_frame = ttk.Frame(info_frame)
        price_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(price_frame, text="当前价：", font=("Arial", 9)).pack(anchor=tk.W)
        self.current_price_label = ttk.Label(price_frame, text="--", font=("Arial", 10, "bold"))
        self.current_price_label.pack(anchor=tk.W)
        
        # 涨跌幅信息
        change_frame = ttk.Frame(info_frame)
        change_frame.pack(side=tk.RIGHT, padx=(10, 0))
        
        ttk.Label(change_frame, text="涨跌幅：", font=("Arial", 9)).pack(anchor=tk.W)
        self.change_label = ttk.Label(change_frame, text="--", font=("Arial", 10))
        self.change_label.pack(anchor=tk.W)
        
        # 操作按钮
        btn_frame = ttk.Frame(card_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(btn_frame, text="详细分析", command=lambda: self.analyze_stock(stock_code), width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="查看图表", command=lambda: self.show_chart(stock_code), width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="删除", command=lambda: self.remove_stock(stock_code), width=8).pack(side=tk.RIGHT, padx=2)
        
        return {
            'frame': card_frame,
            'current_price': self.current_price_label,
            'change': self.change_label
        }
        
    def create_analysis_tab(self):
        """创建分析标签页"""
        analysis_frame = ttk.Frame(self.notebook)
        self.notebook.add(analysis_frame, text="分析")
        
        # 分析控制面板
        control_frame = ttk.LabelFrame(analysis_frame, text="分析控制", padding=15)
        control_frame.pack(fill=tk.X, pady=10, padx=10)
        
        # 分析类型选择
        type_frame = ttk.Frame(control_frame)
        type_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(type_frame, text="分析类型：", width=10).pack(side=tk.LEFT)
        self.analysis_type = tk.StringVar(value="full")
        
        ttk.Radiobutton(type_frame, text="完整分析", variable=self.analysis_type, value="full").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="快速分析", variable=self.analysis_type, value="quick").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(type_frame, text="持仓分析", variable=self.analysis_type, value="portfolio").pack(side=tk.LEFT, padx=10)
        
        # 分析选项
        options_frame = ttk.Frame(control_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(options_frame, text="分析选项：", width=10).pack(side=tk.LEFT)
        
        self.include_history = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="包含历史数据", variable=self.include_history).pack(side=tk.LEFT, padx=10)
        
        self.generate_report = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="生成报告", variable=self.generate_report).pack(side=tk.LEFT, padx=10)
        
        self.send_notification = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="发送通知", variable=self.send_notification).pack(side=tk.LEFT, padx=10)
        
        # 分析按钮
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.run_btn = ttk.Button(btn_frame, text="开始分析", command=self.start_analysis, width=15)
        self.run_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(btn_frame, text="停止分析", command=self.stop_analysis, width=15, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="查看历史", command=self.view_history, width=15).pack(side=tk.RIGHT, padx=5)
        
        # 分析进度
        progress_frame = ttk.LabelFrame(analysis_frame, text="分析进度", padding=15)
        progress_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10), padx=10)
        
        # 进度条
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # 状态标签
        self.analysis_status = ttk.Label(progress_frame, text="等待开始分析...")
        self.analysis_status.pack(anchor=tk.W)
        
        # 日志输出
        log_frame = ttk.LabelFrame(progress_frame, text="分析日志", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def create_portfolio_tab(self):
        """创建持仓管理标签页"""
        portfolio_frame = ttk.Frame(self.notebook)
        self.notebook.add(portfolio_frame, text="持仓")
        
        # 持仓列表
        list_frame = ttk.LabelFrame(portfolio_frame, text="持仓股票列表", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=10, padx=10)
        
        # 创建表格
        columns = ('代码', '名称', '数量', '成本价', '当前价', '市值', '盈亏', '盈亏率', '操作')
        self.portfolio_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题
        for col in columns:
            self.portfolio_tree.heading(col, text=col)
            if col == '操作':
                self.portfolio_tree.column(col, width=80, anchor=tk.CENTER)
            else:
                self.portfolio_tree.column(col, width=100, anchor=tk.CENTER)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.portfolio_tree.yview)
        self.portfolio_tree.configure(yscrollcommand=scrollbar.set)
        
        self.portfolio_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 操作按钮
        btn_frame = ttk.Frame(portfolio_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        ttk.Button(btn_frame, text="添加股票", command=self.add_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="编辑选中", command=self.edit_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="删除选中", command=self.delete_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="刷新数据", command=self.refresh_portfolio).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="导出持仓", command=self.export_portfolio).pack(side=tk.RIGHT, padx=5)
        
    def create_reports_tab(self):
        """创建报告查看标签页"""
        reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(reports_frame, text="报告")
        
        # 报告列表和预览区域
        paned_window = ttk.PanedWindow(reports_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧：报告列表
        list_frame = ttk.LabelFrame(paned_window, text="报告列表", padding=10)
        
        # 搜索框
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(search_frame, text="搜索：").pack(side=tk.LEFT)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(search_frame, text="搜索", command=self.search_reports, width=8).pack(side=tk.RIGHT)
        
        # 报告列表
        self.report_listbox = tk.Listbox(list_frame, height=20)
        self.report_listbox.pack(fill=tk.BOTH, expand=True)
        
        # 列表滚动条
        list_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.report_listbox.yview)
        self.report_listbox.configure(yscrollcommand=list_scrollbar.set)
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 列表操作按钮
        list_btn_frame = ttk.Frame(list_frame)
        list_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(list_btn_frame, text="刷新列表", command=self.refresh_report_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(list_btn_frame, text="打开选中", command=self.open_selected_report).pack(side=tk.LEFT, padx=2)
        ttk.Button(list_btn_frame, text="删除选中", command=self.delete_selected_report).pack(side=tk.RIGHT, padx=2)
        
        paned_window.add(list_frame, weight=1)
        
        # 右侧：报告预览
        preview_frame = ttk.LabelFrame(paned_window, text="报告预览", padding=10)
        
        # 预览标签
        self.preview_label = ttk.Label(preview_frame, text="选择左侧报告进行预览")
        self.preview_label.pack(anchor=tk.W, pady=(0, 10))
        
        # 预览文本区域
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=20, wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
        # 预览操作按钮
        preview_btn_frame = ttk.Frame(preview_frame)
        preview_btn_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(preview_btn_frame, text="导出报告", command=self.export_report).pack(side=tk.LEFT, padx=2)
        ttk.Button(preview_btn_frame, text="打印报告", command=self.print_report).pack(side=tk.LEFT, padx=2)
        ttk.Button(preview_btn_frame, text="清空预览", command=self.clear_preview).pack(side=tk.RIGHT, padx=2)
        
        paned_window.add(preview_frame, weight=2)
        
        # 绑定列表选择事件
        self.report_listbox.bind('<<ListboxSelect>>', self.on_report_selected)
        
    def init_database(self):
        """初始化数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建用户表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    theme TEXT DEFAULT 'light',
                    update_interval INTEGER DEFAULT 5,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建持仓表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT UNIQUE,
                    stock_name TEXT,
                    quantity INTEGER DEFAULT 0,
                    cost_price REAL DEFAULT 0.0,
                    target_price REAL DEFAULT 0.0,
                    stop_loss REAL DEFAULT 0.0,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建分析历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS analysis_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    analysis_date DATE,
                    analysis_type TEXT,
                    duration REAL,
                    success BOOLEAN,
                    result_file TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建报告表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_date DATE,
                    report_type TEXT,
                    file_path TEXT UNIQUE,
                    file_size INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            print("数据库初始化成功")
            
        except Exception as e:
            print(f"数据库初始化失败: {e}")
            
    def load_config(self):
        """加载配置"""
        config_path = project_root / "config" / "gui_config.json"
        default_config = {
            'theme': 'light',
            'update_interval': 5,
            'auto_refresh': True,
            'notifications': False,
            'default_analysis_type': 'full',
            'recent_files': []
        }
        
        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载配置失败: {e}")
            
        return default_config
        
    def save_config(self):
        """保存配置"""
        config_path = project_root / "config" / "gui_config.json"
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            self.log_message("配置已保存")
        except Exception as e:
            self.log_message(f"保存配置失败: {e}", level="error")
            
    def load_initial_data(self):
        """加载初始数据"""
        try:
            # 加载持仓数据
            if HAS_ANALYSIS_MODULE:
                for stock_code, stock_name in POSITION_STOCKS.items():
                    if stock_code in POSITION_WEIGHTS:
                        self.add_stock_to_gui(stock_code, stock_name, POSITION_WEIGHTS[stock_code])
            
            # 加载报告列表
            self.refresh_report_list()
            
            self.log_message("初始数据加载完成")
        except Exception as e:
            self.log_message(f"加载初始数据失败: {e}", level="error")
            
    def setup_timers(self):
        """设置定时器"""
        # 更新时间显示
        self.root.after(1000, self.update_time)
        
        # 自动刷新数据
        if self.config.get('auto_refresh', True):
            interval = self.config.get('update_interval', 5) * 1000  # 转换为毫秒
            self.root.after(interval, self.auto_refresh)
            
    def update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)
        
    def auto_refresh(self):
        """自动刷新数据"""
        if self.config.get('auto_refresh', True):
            self.refresh_stock_data()
            interval = self.config.get('update_interval', 5) * 1000
            self.root.after(interval, self.auto_refresh)
            
    def log_message(self, message, level="info"):
        """记录日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if level == "error":
            tag = "error"
            color = "red"
        elif level == "warning":
            tag = "warning"
            color = "orange"
        else:
            tag = "info"
            color = "blue"
            
        log_entry = f"[{timestamp}] {message}\n"
        
        # 更新日志文本框
        self.log_text.insert(tk.END, log_entry)
        self.log_text.tag_add(tag, f"end-{len(log_entry)}c", "end-1c")
        self.log_text.tag_config(tag, foreground=color)
        self.log_text.see(tk.END)
        
        # 更新状态栏
        self.status_label.config(text=message)
        
    def update_status(self, message):
        """更新状态栏"""
        self.status_label.config(text=message)
        
    # ========== 业务方法 ==========
    
    def run_full_analysis(self):
        """运行完整分析"""
        if self.is_analyzing:
            messagebox.showwarning("警告", "分析正在进行中，请等待完成")
            return
            
        self.start_analysis()
        
    def run_quick_analysis(self):
        """运行快速分析"""
        self.analysis_type.set("quick")
        self.start_analysis()
        
    def run_portfolio_analysis(self):
        """运行持仓分析"""
        self.analysis_type.set("portfolio")
        self.start_analysis()
        
    def start_analysis(self):
        """开始分析"""
        if self.is_analyzing:
            return
            
        if not HAS_ANALYSIS_MODULE:
            messagebox.showerror("错误", "分析模块未正确导入，请检查配置文件")
            return
            
        self.is_analyzing = True
        self.run_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress_bar.start()
        
        analysis_type = self.analysis_type.get()
        self.log_message(f"开始{analysis_type}分析...")
        
        # 在新线程中运行分析
        self.analysis_thread = threading.Thread(target=self._run_analysis_thread, args=(analysis_type,))
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
        
    def _run_analysis_thread(self, analysis_type):
        """运行分析的线程函数"""
        try:
            start_time = time.time()
            
            # 运行分析程序
            if HAS_ANALYSIS_MODULE:
                run_analysis()
                
            # 记录分析历史
            duration = time.time() - start_time
            
            # 在主线程中更新UI
            self.root.after(0, self._analysis_completed, True, duration, analysis_type)
            
        except Exception as e:
            self.root.after(0, self._analysis_completed, False, 0, analysis_type, str(e))
            
    def _analysis_completed(self, success, duration, analysis_type, error_msg=None):
        """分析完成回调"""
        self.is_analyzing = False
        self.run_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress_bar.stop()
        
        if success:
            self.log_message(f"{analysis_type}分析完成，耗时{duration:.2f}秒", level="info")
            messagebox.showinfo("成功", f"分析完成！耗时{duration:.2f}秒")
        else:
            self.log_message(f"分析失败: {error_msg}", level="error")
            messagebox.showerror("错误", f"分析失败: {error_msg}")
            
    def stop_analysis(self):
        """停止分析"""
        if self.is_analyzing and self.analysis_thread:
            self.is_analyzing = False
            self.log_message("分析已停止", level="warning")
            
    def add_stock_to_gui(self, stock_code, stock_name, weight):
        """添加股票到GUI"""
        # 创建股票卡片
        card = self.create_stock_card(stock_code, stock_name)
        
        # 添加到持仓列表
        self.portfolio_data.append({
            'code': stock_code,
            'name': stock_name,
            'weight': weight,
            'card': card
        })
        
        # 更新持仓表格
        self.update_portfolio_table()
        
    def update_portfolio_table(self):
        """更新持仓表格"""
        # 清空现有数据
        for item in self.portfolio_tree.get_children():
            self.portfolio_tree.delete(item)
            
        # 添加新数据
        for stock in self.portfolio_data:
            self.portfolio_tree.insert('', tk.END, values=(
                stock['code'],
                stock['name'],
                '1000',  # 默认数量
                '10.00',  # 默认成本价
                '--',     # 当前价
                '--',     # 市值
                '--',     # 盈亏
                '--',     # 盈亏率
                '📊'      # 操作图标
            ))
            
    def refresh_portfolio(self):
        """刷新持仓数据"""
        self.log_message("刷新持仓数据...")
        # 这里可以添加获取实时价格的逻辑
        self.log_message("持仓数据已刷新")
        
    def refresh_report_list(self):
        """刷新报告列表"""
        self.report_listbox.delete(0, tk.END)
        
        # 查找报告文件
        reports_dir = project_root / "reports"
        
        if reports_dir.exists():
            for report_type in ['html', 'markdown']:
                type_dir = reports_dir / report_type
                if type_dir.exists():
                    for file in type_dir.glob("*.html" if report_type == 'html' else "*.md"):
                        self.report_listbox.insert(tk.END, f"{file.name}")
                        
        if self.report_listbox.size() == 0:
            self.report_listbox.insert(tk.END, "未找到报告文件")
            
    def on_report_selected(self, event):
        """报告选择事件"""
        selection = self.report_listbox.curselection()
        if selection:
            report_name = self.report_listbox.get(selection[0])
            self.preview_report(report_name)
            
    def preview_report(self, report_name):
        """预览报告"""
        try:
            reports_dir = project_root / "reports"
            
            # 尝试查找文件
            for report_type in ['html', 'markdown']:
                file_path = reports_dir / report_type / report_name
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    self.preview_text.delete(1.0, tk.END)
                    self.preview_text.insert(1.0, content)
                    self.preview_label.config(text=f"预览: {report_name}")
                    return
                    
            self.preview_label.config(text="文件未找到")
        except Exception as e:
            self.preview_label.config(text=f"预览失败: {str(e)}")
            
    # ========== 事件处理方法 ==========
    
    def new_analysis(self):
        """新建分析"""
        self.log_message("准备新建分析...")
        # 这里可以添加新建分析的逻辑
        
    def open_report(self):
        """打开报告"""
        file_path = filedialog.askopenfilename(
            title="选择报告文件",
            filetypes=[("HTML文件", "*.html"), ("Markdown文件", "*.md"), ("所有文件", "*.*")]
        )
        
        if file_path:
            self.preview_report(Path(file_path).name)
            
    def open_portfolio_editor(self):
        """打开持仓编辑器"""
        self.notebook.select(2)  # 切换到持仓标签页
        
    def open_settings(self):
        """打开设置面板"""
        # 这里可以添加设置对话框
        messagebox.showinfo("设置", "设置功能开发中...")
        
    def view_history(self):
        """查看历史"""
        self.log_message("查看分析历史...")
        # 这里可以添加历史查看逻辑
        
    def refresh_all(self):
        """刷新所有数据"""
        self.log_message("刷新所有数据...")
        self.refresh_portfolio()
        self.refresh_report_list()
        self.refresh_stock_data()
        self.log_message("数据刷新完成")
        
    def update_data(self):
        """更新数据"""
        self.log_message("更新数据...")
        # 这里可以添加数据更新逻辑
        
    def manage_database(self):
        """数据库管理"""
        messagebox.showinfo("数据库管理", "数据库管理功能开发中...")
        
    def clean_cache(self):
        """清理缓存"""
        if messagebox.askyesno("确认", "确定要清理缓存吗？"):
            self.log_message("清理缓存...")
            # 这里可以添加缓存清理逻辑
            self.log_message("缓存清理完成")
            
    def show_manual(self):
        """显示使用手册"""
        manual_text = """股票分析专业版 GUI 使用手册（兼容模式）

⚠️ 本桌面 GUI 仅为兼容保留入口，推荐优先使用：
- ./start_real_data_system.sh
- ./start_enhanced_system.sh

说明：部分桌面按钮目前仍处于维护/占位状态。

1. 仪表盘
   - 查看持仓股票实时价格
   - 监控涨跌幅变化
   - 查看统计信息

2. 分析功能
   - 完整分析：运行完整的七步法分析
   - 快速分析：快速生成分析结果
   - 持仓分析：分析当前持仓情况

3. 持仓管理
   - 添加/删除持仓股票
   - 编辑持仓信息
   - 查看持仓详情

4. 报告查看
   - 查看历史分析报告
   - 预览HTML和Markdown报告
   - 导出和打印报告

快捷键：
- Ctrl+N: 新建分析
- Ctrl+O: 打开报告
- F5: 运行完整分析
- Ctrl+F5: 运行快速分析
- Ctrl+Q: 退出程序
"""
        messagebox.showinfo("使用手册", manual_text)
        
    def show_about(self):
        """显示关于信息"""
        about_text = """股票分析专业版（桌面 GUI 兼容模式）
版本：1.0.0
作者：风暴 🌪️
创建时间：2026年4月2日

当前状态：
- 桌面 GUI 为兼容保留入口
- 默认主入口已切换到 Web 界面
- 部分桌面功能仍处于维护/占位状态

推荐入口：
- ./start_real_data_system.sh
- ./start_enhanced_system.sh

技术支持：使用 Python Tkinter 开发
"""
        messagebox.showinfo("关于", about_text)
        
    def on_closing(self):
        """窗口关闭事件"""
        if self.is_analyzing:
            if not messagebox.askyesno("确认", "分析正在进行中，确定要退出吗？"):
                return
                
        # 保存配置
        self.save_config()
        
        # 关闭数据库连接等资源
        # ...
        
        self.root.destroy()
        
    # ========== 占位方法（需要后续实现） ==========
    
    def update_stock_data(self):
        """更新股票数据"""
        self.log_message("股票数据更新功能开发中...")
        
    def export_stats(self):
        """导出统计"""
        self.log_message("导出统计功能开发中...")
        
    def analyze_stock(self, stock_code):
        """分析单个股票"""
        self.log_message(f"分析股票 {stock_code} 功能开发中...")
        
    def show_chart(self, stock_code):
        """显示图表"""
        self.log_message(f"显示 {stock_code} 图表功能开发中...")
        
    def remove_stock(self, stock_code):
        """删除股票"""
        if messagebox.askyesno("确认", f"确定要删除股票 {stock_code} 吗？"):
            self.log_message(f"删除股票 {stock_code} 功能开发中...")
            
    def add_stock(self):
        """添加股票"""
        self.log_message("添加股票功能开发中...")
        
    def edit_stock(self):
        """编辑股票"""
        self.log_message("编辑股票功能开发中...")
        
    def delete_stock(self):
        """删除股票"""
        self.log_message("删除选中股票功能开发中...")
        
    def export_portfolio(self):
        """导出持仓"""
        self.log_message("导出持仓功能开发中...")
        
    def search_reports(self):
        """搜索报告"""
        self.log_message("搜索报告功能开发中...")
        
    def open_selected_report(self):
        """打开选中的报告"""
        self.log_message("打开选中报告功能开发中...")
        
    def delete_selected_report(self):
        """删除选中的报告"""
        self.log_message("删除选中报告功能开发中...")
        
    def export_report(self):
        """导出报告"""
        self.log_message("导出报告功能开发中...")
        
    def print_report(self):
        """打印报告"""
        self.log_message("打印报告功能开发中...")
        
    def clear_preview(self):
        """清空预览"""
        self.preview_text.delete(1.0, tk.END)
        self.preview_label.config(text="选择左侧报告进行预览")
        
    def refresh_stock_data(self):
        """刷新股票数据"""
        # 这里可以添加获取实时数据的逻辑
        pass
        
    def export_data(self):
        """导出数据"""
        self.log_message("导出数据功能开发中...")

def main():
    """主函数"""
    root = tk.Tk()
    app = StockAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
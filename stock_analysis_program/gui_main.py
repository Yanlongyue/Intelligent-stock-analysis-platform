#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析可视化界面 - 主程序
作者: 风暴 🌪️
创建时间: 2026年4月2日
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import os
import sys
import threading
import subprocess
import json
import sqlite3
from datetime import datetime
import webbrowser
import psutil
import platform

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class StockAnalysisGUI:
    """股票分析可视化界面主类"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("七步法股票分析系统 🚀")
        self.root.geometry("1200x800")
        
        # 设置图标
        self.set_icon()
        
        # 设置主题样式
        self.setup_styles()
        
        # 创建菜单栏
        self.create_menu()
        
        # 创建主界面
        self.create_main_interface()
        
        # 创建状态栏
        self.create_statusbar()
        
        # 初始化数据库
        self.init_database()
        
        # 加载配置
        self.load_config()
        
        # 启动时显示欢迎信息
        self.show_welcome_message()
    
    def set_icon(self):
        """设置窗口图标"""
        try:
            # 尝试设置图标文件
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
    
    def setup_styles(self):
        """设置界面样式"""
        # 定义颜色
        self.colors = {
            'primary': '#2c3e50',      # 深蓝
            'secondary': '#3498db',    # 科技蓝
            'success': '#27ae60',      # 绿色
            'warning': '#e67e22',      # 橙色
            'danger': '#e74c3c',       # 红色
            'light': '#f5f7fa',        # 浅灰
            'dark': '#2c3e50',         # 深色
            'white': '#ffffff',        # 白色
        }
        
        # 创建样式
        style = ttk.Style()
        
        # 配置主题
        style.theme_use('clam')
        
        # 配置按钮样式
        style.configure('Primary.TButton', 
                       background=self.colors['secondary'],
                       foreground='white',
                       font=('Microsoft YaHei', 11, 'bold'),
                       padding=10)
        
        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground='white',
                       font=('Microsoft YaHei', 11, 'bold'),
                       padding=10)
        
        style.configure('Danger.TButton',
                       background=self.colors['danger'],
                       foreground='white',
                       font=('Microsoft YaHei', 11, 'bold'),
                       padding=10)
        
        style.configure('Warning.TButton',
                       background=self.colors['warning'],
                       foreground='white',
                       font=('Microsoft YaHei', 11, 'bold'),
                       padding=10)
        
        # 配置标签样式
        style.configure('Title.TLabel',
                       font=('Microsoft YaHei', 16, 'bold'),
                       foreground=self.colors['primary'])
        
        style.configure('Subtitle.TLabel',
                       font=('Microsoft YaHei', 12),
                       foreground=self.colors['dark'])
        
        # 配置框架样式
        style.configure('Card.TFrame',
                       background=self.colors['white'],
                       relief='raised',
                       borderwidth=2)
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开报告", command=self.open_report)
        file_menu.add_command(label="保存配置", command=self.save_config)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.quit_app)
        
        # 分析菜单
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="分析", menu=analysis_menu)
        analysis_menu.add_command(label="一键完整分析", command=self.run_full_analysis)
        analysis_menu.add_command(label="快速持仓分析", command=self.run_quick_analysis)
        analysis_menu.add_command(label="生成今日报告", command=self.generate_today_report)
        analysis_menu.add_separator()
        analysis_menu.add_command(label="查看历史报告", command=self.show_history_reports)
        
        # 持仓菜单
        position_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="持仓", menu=position_menu)
        position_menu.add_command(label="持仓管理", command=self.show_position_management)
        position_menu.add_command(label="添加持仓", command=self.add_position)
        position_menu.add_command(label="导入持仓", command=self.import_positions)
        position_menu.add_command(label="导出持仓", command=self.export_positions)
        
        # 工具菜单
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="工具", menu=tools_menu)
        tools_menu.add_command(label="系统状态", command=self.show_system_status)
        tools_menu.add_command(label="清理缓存", command=self.clear_cache)
        tools_menu.add_command(label="检查更新", command=self.check_updates)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用教程", command=self.show_tutorial)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_main_interface(self):
        """创建主界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧控制面板
        left_frame = ttk.Frame(main_frame, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        # 右侧主内容区
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 创建选项卡
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建各个标签页
        self.create_dashboard_tab()
        self.create_position_tab()
        self.create_report_tab()
        self.create_chart_tab()
        self.create_settings_tab()
        
        # 创建左侧控制面板内容
        self.create_control_panel(left_frame)
    
    def create_control_panel(self, parent):
        """创建控制面板"""
        # 标题
        title_label = ttk.Label(parent, text="🎯 控制中心", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # 快速操作按钮
        operations_frame = ttk.LabelFrame(parent, text="快速操作", padding=10)
        operations_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 一键完整分析按钮
        full_analysis_btn = ttk.Button(operations_frame, text="🚀 一键完整分析", 
                                      style='Primary.TButton',
                                      command=self.run_full_analysis)
        full_analysis_btn.pack(fill=tk.X, pady=5)
        
        # 快速持仓分析按钮
        quick_analysis_btn = ttk.Button(operations_frame, text="📊 快速持仓分析",
                                       style='Success.TButton',
                                       command=self.run_quick_analysis)
        quick_analysis_btn.pack(fill=tk.X, pady=5)
        
        # 生成今日报告按钮
        report_btn = ttk.Button(operations_frame, text="📄 生成今日报告",
                               style='Warning.TButton',
                               command=self.generate_today_report)
        report_btn.pack(fill=tk.X, pady=5)
        
        # 查看持仓按钮
        position_btn = ttk.Button(operations_frame, text="📈 查看持仓",
                                 command=self.show_position_management)
        position_btn.pack(fill=tk.X, pady=5)
        
        # 系统状态信息
        status_frame = ttk.LabelFrame(parent, text="系统状态", padding=10)
        status_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 创建状态标签
        self.status_labels = {}
        
        # CPU使用率
        cpu_label = ttk.Label(status_frame, text="CPU: 加载中...")
        cpu_label.pack(anchor=tk.W, pady=2)
        self.status_labels['cpu'] = cpu_label
        
        # 内存使用率
        memory_label = ttk.Label(status_frame, text="内存: 加载中...")
        memory_label.pack(anchor=tk.W, pady=2)
        self.status_labels['memory'] = memory_label
        
        # 磁盘空间
        disk_label = ttk.Label(status_frame, text="磁盘: 加载中...")
        disk_label.pack(anchor=tk.W, pady=2)
        self.status_labels['disk'] = disk_label
        
        # 程序状态
        program_label = ttk.Label(status_frame, text="程序: 就绪")
        program_label.pack(anchor=tk.W, pady=2)
        self.status_labels['program'] = program_label
        
        # 快捷链接
        links_frame = ttk.LabelFrame(parent, text="快捷链接", padding=10)
        links_frame.pack(fill=tk.X)
        
        # 打开报告目录按钮
        open_reports_btn = ttk.Button(links_frame, text="📂 打开报告目录",
                                     command=self.open_reports_folder)
        open_reports_btn.pack(fill=tk.X, pady=2)
        
        # 查看配置按钮
        config_btn = ttk.Button(links_frame, text="⚙️ 查看配置",
                               command=self.open_config_folder)
        config_btn.pack(fill=tk.X, pady=2)
        
        # 打开使用指南按钮
        guide_btn = ttk.Button(links_frame, text="📖 打开使用指南",
                              command=self.open_guide)
        guide_btn.pack(fill=tk.X, pady=2)
        
        # 开始更新状态
        self.update_system_status()
    
    def create_dashboard_tab(self):
        """创建仪表板标签页"""
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_tab, text="🏠 首页")
        
        # 欢迎标题
        welcome_frame = ttk.Frame(self.dashboard_tab)
        welcome_frame.pack(fill=tk.X, padx=20, pady=20)
        
        welcome_label = ttk.Label(welcome_frame, 
                                 text="欢迎使用七步法股票分析系统 🚀",
                                 style='Title.TLabel')
        welcome_label.pack()
        
        date_label = ttk.Label(welcome_frame,
                              text=f"当前时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}",
                              style='Subtitle.TLabel')
        date_label.pack(pady=5)
        
        # KPI指标卡片
        kpi_frame = ttk.Frame(self.dashboard_tab)
        kpi_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        # 创建4个KPI卡片
        kpis = [
            {"title": "持仓股票数", "value": "3", "unit": "只", "color": "primary"},
            {"title": "总持仓市值", "value": "¥4,640", "unit": "", "color": "success"},
            {"title": "风险等级", "value": "中高", "unit": "风险", "color": "warning"},
            {"title": "今日报告", "value": "0", "unit": "个", "color": "secondary"}
        ]
        
        for i, kpi in enumerate(kpis):
            card = self.create_kpi_card(kpi_frame, kpi)
            card.grid(row=0, column=i, padx=10, pady=10, sticky='nsew')
            kpi_frame.columnconfigure(i, weight=1)
        
        # 最近报告区域
        recent_frame = ttk.LabelFrame(self.dashboard_tab, text="📋 最近报告", padding=20)
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # 创建报告列表
        self.report_tree = ttk.Treeview(recent_frame, columns=('date', 'type', 'summary'), 
                                       show='headings', height=8)
        self.report_tree.heading('date', text='报告日期')
        self.report_tree.heading('type', text='报告类型')
        self.report_tree.heading('summary', text='报告摘要')
        
        self.report_tree.column('date', width=120)
        self.report_tree.column('type', width=100)
        self.report_tree.column('summary', width=300)
        
        self.report_tree.pack(fill=tk.BOTH, expand=True)
        
        # 添加示例数据
        reports = [
            ("2026-04-01", "完整分析", "金开新能跌停分析，模型优化完成"),
            ("2026-03-31", "持仓分析", "持仓结构调整建议"),
            ("2026-03-30", "深度复盘", "国际风险权重调整至60%")
        ]
        
        for report in reports:
            self.report_tree.insert('', 'end', values=report)
        
        # 操作按钮
        button_frame = ttk.Frame(recent_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        view_btn = ttk.Button(button_frame, text="查看报告", 
                             command=self.view_selected_report)
        view_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_btn = ttk.Button(button_frame, text="刷新列表",
                                command=self.refresh_reports)
        refresh_btn.pack(side=tk.LEFT)
    
    def create_kpi_card(self, parent, kpi):
        """创建KPI指标卡片"""
        card = ttk.Frame(parent, style='Card.TFrame', padding=20)
        
        # 标题
        title_label = ttk.Label(card, text=kpi['title'], 
                               font=('Microsoft YaHei', 11))
        title_label.pack()
        
        # 数值
        value_label = ttk.Label(card, text=kpi['value'], 
                               font=('Microsoft YaHei', 24, 'bold'),
                               foreground=self.colors.get(kpi['color'], '#000000'))
        value_label.pack(pady=5)
        
        # 单位
        if kpi['unit']:
            unit_label = ttk.Label(card, text=kpi['unit'],
                                  font=('Microsoft YaHei', 10))
            unit_label.pack()
        
        return card
    
    def create_position_tab(self):
        """创建持仓管理标签页"""
        self.position_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.position_tab, text="📈 持仓管理")
        
        # 工具栏
        toolbar = ttk.Frame(self.position_tab)
        toolbar.pack(fill=tk.X, padx=20, pady=10)
        
        add_btn = ttk.Button(toolbar, text="➕ 添加持仓", 
                           command=self.add_position_dialog)
        add_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        edit_btn = ttk.Button(toolbar, text="✏️ 编辑持仓",
                            command=self.edit_position_dialog)
        edit_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_btn = ttk.Button(toolbar, text="🗑️ 删除持仓",
                              command=self.delete_position)
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_btn = ttk.Button(toolbar, text="🔄 刷新",
                               command=self.load_positions)
        refresh_btn.pack(side=tk.LEFT)
        
        # 持仓列表
        list_frame = ttk.Frame(self.position_tab)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # 创建Treeview
        columns = ('code', 'name', 'quantity', 'price', 'value', 'type', 'risk', 'target')
        self.position_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)
        
        # 设置列标题
        headers = [
            ('code', '股票代码', 100),
            ('name', '股票名称', 150),
            ('quantity', '持仓数量', 100),
            ('price', '当前价格', 100),
            ('value', '持仓市值', 120),
            ('type', '股票类型', 100),
            ('risk', '风险等级', 100),
            ('target', '目标仓位', 100)
        ]
        
        for col_id, col_text, col_width in headers:
            self.position_tree.heading(col_id, text=col_text)
            self.position_tree.column(col_id, width=col_width)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.position_tree.yview)
        self.position_tree.configure(yscrollcommand=scrollbar.set)
        
        self.position_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加示例数据
        self.load_positions()
        
        # 统计信息
        stats_frame = ttk.LabelFrame(self.position_tab, text="📊 持仓统计", padding=15)
        stats_frame.pack(fill=tk.X, padx=20, pady=(0, 20))
        
        stats_text = """总持仓股票: 3只
总持仓市值: ¥4,640.00
平均风险等级: 中高
建议操作: 降低金开新能仓位至20%以下"""
        
        stats_label = ttk.Label(stats_frame, text=stats_text, justify=tk.LEFT)
        stats_label.pack()
    
    def create_report_tab(self):
        """创建报告查看标签页"""
        self.report_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.report_tab, text="📄 分析报告")
        
        # 左右分割布局
        paned = ttk.PanedWindow(self.report_tab, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 左侧报告列表
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        # 报告列表标题
        list_title = ttk.Label(left_frame, text="📋 报告列表", style='Subtitle.TLabel')
        list_title.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # 报告列表
        report_list_frame = ttk.Frame(left_frame)
        report_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.report_listbox = tk.Listbox(report_list_frame, font=('Microsoft YaHei', 11))
        report_scrollbar = ttk.Scrollbar(report_list_frame, orient=tk.VERTICAL, 
                                        command=self.report_listbox.yview)
        self.report_listbox.configure(yscrollcommand=report_scrollbar.set)
        
        self.report_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        report_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加示例报告
        reports = [
            "深度复盘与明日投资计划_20260331.html",
            "持仓股票分析报告_20260402.md",
            "金开新能跌停板分析_20260330.html",
            "股票分析报告_20260327_自动化分析.html"
        ]
        
        for report in reports:
            self.report_listbox.insert(tk.END, report)
        
        # 报告操作按钮
        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        view_btn = ttk.Button(button_frame, text="查看报告", 
                             command=self.view_report)
        view_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_btn = ttk.Button(button_frame, text="删除报告",
                              command=self.delete_report)
        delete_btn.pack(side=tk.LEFT)
        
        # 右侧报告预览
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=2)
        
        # 预览标题
        preview_title = ttk.Label(right_frame, text="📄 报告预览", style='Subtitle.TLabel')
        preview_title.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # 报告预览区域
        preview_frame = ttk.Frame(right_frame)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # 使用文本框显示报告内容
        self.report_preview = scrolledtext.ScrolledText(preview_frame, 
                                                       font=('Consolas', 10),
                                                       wrap=tk.WORD)
        self.report_preview.pack(fill=tk.BOTH, expand=True)
        
        # 添加示例内容
        self.report_preview.insert(tk.END, "选择左侧的报告进行预览...\n\n")
        self.report_preview.insert(tk.END, "📊 七步法股票分析报告\n")
        self.report_preview.insert(tk.END, "=" * 50 + "\n\n")
        self.report_preview.insert(tk.END, "1. 深度复盘与预测误差分析\n")
        self.report_preview.insert(tk.END, "2. 误差分析与经验总结\n")
        self.report_preview.insert(tk.END, "3. 明日小时级预测\n")
        self.report_preview.insert(tk.END, "4. 投资计划与仓位管理\n")
        self.report_preview.insert(tk.END, "5. 风险控制与操作纪律\n")
        self.report_preview.insert(tk.END, "6. 其他潜力股票推荐\n")
        
        self.report_preview.config(state=tk.DISABLED)
    
    def create_chart_tab(self):
        """创建图表展示标签页"""
        self.chart_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.chart_tab, text="📊 图表展示")
        
        # 图表区域占位
        chart_placeholder = ttk.Label(self.chart_tab, 
                                     text="📊 图表展示功能开发中...\n\n" +
                                          "这里将显示持仓分布图、收益趋势图等可视化图表",
                                     font=('Microsoft YaHei', 14),
                                     justify=tk.CENTER)
        chart_placeholder.pack(expand=True)
    
    def create_settings_tab(self):
        """创建系统设置标签页"""
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="⚙️ 系统设置")
        
        # 设置框架
        settings_frame = ttk.Frame(self.settings_tab)
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Tushare配置
        tushare_frame = ttk.LabelFrame(settings_frame, text="Tushare Pro配置", padding=15)
        tushare_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(tushare_frame, text="API Token:").grid(row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W)
        self.token_var = tk.StringVar(value="您的Tushare Token")
        token_entry = ttk.Entry(tushare_frame, textvariable=self.token_var, width=40)
        token_entry.grid(row=0, column=1, pady=5, sticky=tk.W)
        
        test_token_btn = ttk.Button(tushare_frame, text="测试连接", 
                                   command=self.test_tushare_token)
        test_token_btn.grid(row=0, column=2, padx=(10, 0), pady=5)
        
        # 界面设置
        ui_frame = ttk.LabelFrame(settings_frame, text="界面设置", padding=15)
        ui_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 主题选择
        ttk.Label(ui_frame, text="界面主题:").grid(row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W)
        self.theme_var = tk.StringVar(value="默认主题")
        theme_combo = ttk.Combobox(ui_frame, textvariable=self.theme_var, 
                                  values=["默认主题", "深色主题", "蓝色主题", "绿色主题"],
                                  state="readonly", width=20)
        theme_combo.grid(row=0, column=1, pady=5, sticky=tk.W)
        
        # 字体大小
        ttk.Label(ui_frame, text="字体大小:").grid(row=1, column=0, padx=(0, 10), pady=5, sticky=tk.W)
        self.font_size_var = tk.StringVar(value="中等")
        font_combo = ttk.Combobox(ui_frame, textvariable=self.font_size_var,
                                 values=["小", "中等", "大", "特大"],
                                 state="readonly", width=20)
        font_combo.grid(row=1, column=1, pady=5, sticky=tk.W)
        
        # 分析设置
        analysis_frame = ttk.LabelFrame(settings_frame, text="分析设置", padding=15)
        analysis_frame.pack(fill=tk.X, pady=(0, 20))
        
        # 自动运行
        self.auto_run_var = tk.BooleanVar(value=False)
        auto_run_check = ttk.Checkbutton(analysis_frame, text="启动时自动运行分析",
                                        variable=self.auto_run_var)
        auto_run_check.grid(row=0, column=0, padx=(0, 20), pady=5, sticky=tk.W)
        
        # 风险偏好
        ttk.Label(analysis_frame, text="风险偏好:").grid(row=0, column=1, padx=(0, 10), pady=5, sticky=tk.W)
        self.risk_var = tk.StringVar(value="平衡型")
        risk_combo = ttk.Combobox(analysis_frame, textvariable=self.risk_var,
                                 values=["保守型", "平衡型", "进取型"],
                                 state="readonly", width=15)
        risk_combo.grid(row=0, column=2, pady=5, sticky=tk.W)
        
        # 保存按钮
        save_btn = ttk.Button(settings_frame, text="💾 保存设置", 
                             style='Success.TButton',
                             command=self.save_settings)
        save_btn.pack(pady=20)
    
    def create_statusbar(self):
        """创建状态栏"""
        self.statusbar = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 左侧状态信息
        self.status_label = ttk.Label(self.statusbar, text="就绪")
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # 右侧系统信息
        sys_info = f"Python {platform.python_version()} | 内存使用: -- | 时间: --"
        self.sys_label = ttk.Label(self.statusbar, text=sys_info)
        self.sys_label.pack(side=tk.RIGHT, padx=10)
    
    def init_database(self):
        """初始化数据库"""
        self.db_path = os.path.join(os.path.dirname(__file__), "data", "stock_analysis.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建持仓表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    stock_code TEXT NOT NULL,
                    stock_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    entry_price REAL,
                    current_price REAL,
                    stock_type TEXT,
                    risk_level TEXT,
                    target_position REAL,
                    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建报告表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_date TEXT NOT NULL,
                    report_type TEXT NOT NULL,
                    html_path TEXT,
                    md_path TEXT,
                    summary TEXT,
                    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建设置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT UNIQUE NOT NULL,
                    setting_value TEXT,
                    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"数据库初始化失败: {e}")
    
    def load_config(self):
        """加载配置文件"""
        self.config_path = os.path.join(os.path.dirname(__file__), "config", "gui_settings.json")
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        default_config = {
            "window_size": "1200x800",
            "theme": "默认主题",
            "font_size": "中等",
            "auto_run": False,
            "risk_preference": "平衡型",
            "last_report_path": ""
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except:
                self.config = default_config
        else:
            self.config = default_config
            self.save_config()
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            self.update_status("配置已保存")
        except Exception as e:
            messagebox.showerror("保存失败", f"无法保存配置: {e}")
    
    def show_welcome_message(self):
        """显示欢迎信息"""
        self.update_status("欢迎使用七步法股票分析系统！")
    
    def update_system_status(self):
        """更新系统状态信息"""
        try:
            # CPU使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            self.status_labels['cpu'].config(text=f"CPU: {cpu_percent:.1f}%")
            
            # 内存使用率
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            self.status_labels['memory'].config(text=f"内存: {memory_percent:.1f}%")
            
            # 磁盘空间
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            self.status_labels['disk'].config(text=f"磁盘: {disk_percent:.1f}%")
            
            # 更新状态栏
            current_time = datetime.now().strftime("%H:%M:%S")
            sys_info = f"Python {platform.python_version()} | 内存: {memory_percent:.1f}% | 时间: {current_time}"
            self.sys_label.config(text=sys_info)
            
        except Exception as e:
            print(f"更新系统状态失败: {e}")
        
        # 每秒更新一次
        self.root.after(1000, self.update_system_status)
    
    def update_status(self, message):
        """更新状态栏信息"""
        self.status_label.config(text=message)
    
    # ========== 功能方法 ==========
    
    def run_full_analysis(self):
        """运行完整分析"""
        self.update_status("正在运行完整分析...")
        
        # 在新线程中运行分析
        def run_analysis():
            try:
                # 切换到工作目录
                os.chdir(os.path.dirname(__file__))
                
                # 运行分析程序
                result = subprocess.run(['python3', 'analyze_position_stocks.py'], 
                                      capture_output=True, text=True, encoding='utf-8')
                
                if result.returncode == 0:
                    self.root.after(0, lambda: self.update_status("分析完成！"))
                    self.root.after(0, lambda: messagebox.showinfo("分析完成", "完整分析已成功运行！"))
                else:
                    error_msg = result.stderr if result.stderr else "未知错误"
                    self.root.after(0, lambda: self.update_status("分析失败"))
                    self.root.after(0, lambda: messagebox.showerror("分析失败", f"错误信息:\n{error_msg}"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.update_status("分析异常"))
                self.root.after(0, lambda: messagebox.showerror("分析异常", f"异常信息:\n{str(e)}"))
        
        # 启动分析线程
        analysis_thread = threading.Thread(target=run_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def run_quick_analysis(self):
        """运行快速分析"""
        self.update_status("正在运行快速分析...")
        
        def run_quick():
            try:
                os.chdir(os.path.dirname(__file__))
                result = subprocess.run(['python3', '简易演示模式.py'], 
                                      capture_output=True, text=True, encoding='utf-8')
                
                if result.returncode == 0:
                    # 显示结果
                    output = result.stdout
                    self.show_analysis_result(output)
                else:
                    error_msg = result.stderr if result.stderr else "未知错误"
                    self.root.after(0, lambda: messagebox.showerror("快速分析失败", f"错误信息:\n{error_msg}"))
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("快速分析异常", f"异常信息:\n{str(e)}"))
        
        quick_thread = threading.Thread(target=run_quick)
        quick_thread.daemon = True
        quick_thread.start()
    
    def show_analysis_result(self, output):
        """显示分析结果"""
        # 创建结果显示窗口
        result_window = tk.Toplevel(self.root)
        result_window.title("📊 快速分析结果")
        result_window.geometry("800x600")
        
        # 创建文本框显示结果
        text_widget = scrolledtext.ScrolledText(result_window, font=('Consolas', 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 插入结果
        text_widget.insert(tk.END, output)
        text_widget.config(state=tk.DISABLED)
        
        # 添加关闭按钮
        close_btn = ttk.Button(result_window, text="关闭", 
                              command=result_window.destroy)
        close_btn.pack(pady=(0, 10))
    
    def generate_today_report(self):
        """生成今日报告"""
        self.update_status("正在生成今日报告...")
        messagebox.showinfo("报告生成", "今日报告生成功能开发中...")
        self.update_status("就绪")
    
    def show_position_management(self):
        """显示持仓管理界面"""
        self.notebook.select(self.position_tab)
    
    def add_position_dialog(self):
        """添加持仓对话框"""
        messagebox.showinfo("添加持仓", "添加持仓功能开发中...")
    
    def edit_position_dialog(self):
        """编辑持仓对话框"""
        selection = self.position_tree.selection()
        if not selection:
            messagebox.showwarning("编辑持仓", "请先选择要编辑的持仓")
            return
        
        messagebox.showinfo("编辑持仓", "编辑持仓功能开发中...")
    
    def delete_position(self):
        """删除持仓"""
        selection = self.position_tree.selection()
        if not selection:
            messagebox.showwarning("删除持仓", "请先选择要删除的持仓")
            return
        
        if messagebox.askyesno("确认删除", "确定要删除选中的持仓吗？"):
            for item in selection:
                self.position_tree.delete(item)
            self.update_status("持仓已删除")
    
    def load_positions(self):
        """加载持仓数据"""
        # 清空现有数据
        for item in self.position_tree.get_children():
            self.position_tree.delete(item)
        
        # 添加示例数据
        positions = [
            ('601868.SH', '中国能建', 400, 3.20, 1280.00, '价值股', '中等', '15%'),
            ('002506.SZ', '协鑫集成', 400, 2.10, 840.00, '成长股', '高风险', '12%'),
            ('600821.SH', '金开新能', 600, 4.20, 2520.00, '概念股', '高风险', '18%')
        ]
        
        for pos in positions:
            self.position_tree.insert('', 'end', values=pos)
    
    def view_report(self):
        """查看报告"""
        selection = self.report_listbox.curselection()
        if not selection:
            messagebox.showwarning("查看报告", "请先选择一个报告")
            return
        
        report_name = self.report_listbox.get(selection[0])
        self.report_preview.config(state=tk.NORMAL)
        self.report_preview.delete(1.0, tk.END)
        self.report_preview.insert(tk.END, f"📄 报告内容: {report_name}\n")
        self.report_preview.insert(tk.END, "=" * 50 + "\n\n")
        self.report_preview.insert(tk.END, "这是报告的预览内容...\n")
        self.report_preview.insert(tk.END, "完整报告请查看对应的HTML文件。\n")
        self.report_preview.config(state=tk.DISABLED)
    
    def delete_report(self):
        """删除报告"""
        selection = self.report_listbox.curselection()
        if not selection:
            messagebox.showwarning("删除报告", "请先选择一个报告")
            return
        
        if messagebox.askyesno("确认删除", "确定要删除选中的报告吗？"):
            self.report_listbox.delete(selection[0])
            self.update_status("报告已删除")
    
    def test_tushare_token(self):
        """测试Tushare Token"""
        token = self.token_var.get()
        if token == "您的Tushare Token" or not token.strip():
            messagebox.showwarning("Token测试", "请输入有效的Tushare Token")
            return
        
        self.update_status("正在测试Token...")
        messagebox.showinfo("Token测试", f"Token测试功能开发中...\n您输入的Token: {token}")
        self.update_status("就绪")
    
    def save_settings(self):
        """保存设置"""
        self.config['theme'] = self.theme_var.get()
        self.config['font_size'] = self.font_size_var.get()
        self.config['auto_run'] = self.auto_run_var.get()
        self.config['risk_preference'] = self.risk_var.get()
        
        self.save_config()
        messagebox.showinfo("保存成功", "系统设置已保存！")
    
    def open_report(self):
        """打开报告"""
        file_path = filedialog.askopenfilename(
            title="选择报告文件",
            filetypes=[("HTML文件", "*.html"), ("Markdown文件", "*.md"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                webbrowser.open(f"file://{file_path}")
                self.update_status(f"已打开报告: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("打开失败", f"无法打开报告:\n{str(e)}")
    
    def open_reports_folder(self):
        """打开报告目录"""
        reports_dir = os.path.join(os.path.dirname(__file__), "reports")
        if os.path.exists(reports_dir):
            os.system(f'open "{reports_dir}"' if platform.system() == 'Darwin' else f'explorer "{reports_dir}"')
        else:
            messagebox.showinfo("报告目录", "报告目录不存在，请先运行分析生成报告。")
    
    def open_config_folder(self):
        """打开配置目录"""
        config_dir = os.path.join(os.path.dirname(__file__), "config")
        if os.path.exists(config_dir):
            os.system(f'open "{config_dir}"' if platform.system() == 'Darwin' else f'explorer "{config_dir}"')
        else:
            os.makedirs(config_dir, exist_ok=True)
            os.system(f'open "{config_dir}"' if platform.system() == 'Darwin' else f'explorer "{config_dir}"')
    
    def open_guide(self):
        """打开使用指南"""
        guide_path = os.path.join(os.path.dirname(__file__), "快速使用指南.md")
        if os.path.exists(guide_path):
            webbrowser.open(f"file://{guide_path}")
        else:
            messagebox.showinfo("使用指南", "使用指南文件不存在。")
    
    def show_system_status(self):
        """显示系统状态"""
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status_text = f"""系统状态信息：
        
CPU使用率: {cpu:.1f}%
内存使用: {memory.percent:.1f}% ({memory.used/1024/1024/1024:.1f}GB / {memory.total/1024/1024/1024:.1f}GB)
磁盘使用: {disk.percent:.1f}% ({disk.used/1024/1024/1024:.1f}GB / {disk.total/1024/1024/1024:.1f}GB)

Python版本: {platform.python_version()}
操作系统: {platform.system()} {platform.release()}
程序路径: {os.path.dirname(__file__)}
        """
        
        messagebox.showinfo("系统状态", status_text)
    
    def clear_cache(self):
        """清理缓存"""
        if messagebox.askyesno("清理缓存", "确定要清理程序缓存吗？"):
            try:
                # 清理临时文件
                temp_dirs = ['__pycache__', '.cache', 'temp']
                for temp_dir in temp_dirs:
                    temp_path = os.path.join(os.path.dirname(__file__), temp_dir)
                    if os.path.exists(temp_path):
                        import shutil
                        shutil.rmtree(temp_path)
                
                self.update_status("缓存已清理")
                messagebox.showinfo("清理完成", "程序缓存已清理完成！")
            except Exception as e:
                messagebox.showerror("清理失败", f"清理缓存时出错:\n{str(e)}")
    
    def check_updates(self):
        """检查更新"""
        messagebox.showinfo("检查更新", "检查更新功能开发中...")
    
    def show_tutorial(self):
        """显示使用教程"""
        tutorial_text = """七步法股票分析系统 - 使用教程

1. 快速开始
   - 点击左侧控制面板的"一键完整分析"运行完整分析
   - 点击"快速持仓分析"查看当前持仓情况
   - 点击"生成今日报告"创建当天的分析报告

2. 持仓管理
   - 切换到"持仓管理"标签页管理您的持仓
   - 可以添加、编辑、删除持仓股票
   - 系统会自动计算持仓比例和风险等级

3. 查看报告
   - 切换到"分析报告"标签页查看历史报告
   - 左侧选择报告，右侧预览内容
   - 支持HTML和Markdown格式报告

4. 系统设置
   - 在"系统设置"标签页配置程序参数
   - 设置Tushare Token、界面主题等
   - 保存设置后立即生效

5. 快捷操作
   - 使用菜单栏快速访问常用功能
   - 右键点击系统托盘图标进行快速操作
   - 使用快捷键提高操作效率

更多帮助请查看"快速使用指南.md"文件。
        """
        
        messagebox.showinfo("使用教程", tutorial_text)
    
    def show_about(self):
        """显示关于信息"""
        about_text = f"""七步法股票分析系统 🚀

版本: v1.0.0
创建时间: 2026年4月2日
开发者: 风暴 🌪️

功能特点：
- 完整的七步法股票分析流程
- 可视化操作界面，一键运行
- 持仓管理和风险监控
- 自动化报告生成
- 图表可视化展示

技术栈：
- Python 3.x + Tkinter GUI
- Tushare Pro API 数据源
- SQLite 数据存储
- HTML/Markdown 报告生成

感谢使用！如有问题请联系开发者。
        """
        
        messagebox.showinfo("关于", about_text)
    
    def view_selected_report(self):
        """查看选中的报告"""
        selection = self.report_tree.selection()
        if not selection:
            messagebox.showwarning("查看报告", "请先选择一个报告")
            return
        
        item = self.report_tree.item(selection[0])
        report_date = item['values'][0]
        messagebox.showinfo("查看报告", f"查看报告功能开发中...\n报告日期: {report_date}")
    
    def refresh_reports(self):
        """刷新报告列表"""
        self.update_status("正在刷新报告列表...")
        # 这里可以添加实际刷新逻辑
        self.root.after(1000, lambda: self.update_status("报告列表已刷新"))
    
    def add_position(self):
        """添加持仓"""
        messagebox.showinfo("添加持仓", "添加持仓功能开发中...")
    
    def import_positions(self):
        """导入持仓"""
        messagebox.showinfo("导入持仓", "导入持仓功能开发中...")
    
    def export_positions(self):
        """导出持仓"""
        messagebox.showinfo("导出持仓", "导出持仓功能开发中...")
    
    def show_history_reports(self):
        """显示历史报告"""
        self.notebook.select(self.report_tab)
    
    def quit_app(self):
        """退出程序"""
        if messagebox.askyesno("退出", "确定要退出程序吗？"):
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """运行主程序"""
        self.root.mainloop()

def main():
    """主函数"""
    # 检查Python版本
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        return
    
    # 检查依赖
    try:
        import psutil
        import sqlite3
    except ImportError as e:
        print(f"缺少依赖包: {e}")
        print("请运行: pip install psutil")
        return
    
    # 创建并运行GUI
    app = StockAnalysisGUI()
    app.run()

if __name__ == "__main__":
    main()
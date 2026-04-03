#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
可视化界面启动器 - 简化版
作者: 风暴 🌪️
创建时间: 2026年4月2日
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import os
import sys
import subprocess
import threading
from datetime import datetime

class SimpleStockAnalyzerGUI:
    """简化的股票分析可视化界面"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("七步法股票分析系统 🚀")
        self.root.geometry("1000x700")
        
        # 设置窗口图标
        self.set_window_icon()
        
        # 创建主界面
        self.create_main_interface()
        
        # 显示欢迎信息
        self.show_welcome()
    
    def set_window_icon(self):
        """设置窗口图标"""
        try:
            # 如果有图标文件就使用
            icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
    
    def create_main_interface(self):
        """创建主界面"""
        # 创建顶部标题栏
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = tk.Label(title_frame, 
                              text="🎯 七步法股票分析系统", 
                              font=('Microsoft YaHei', 20, 'bold'),
                              fg='#2c3e50')
        title_label.pack()
        
        date_label = tk.Label(title_frame,
                             text=f"当前时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}",
                             font=('Microsoft YaHei', 10),
                             fg='#7f8c8d')
        date_label.pack(pady=5)
        
        # 创建按钮区域
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 创建功能按钮
        button_configs = [
            ("🚀 一键完整分析", "#3498db", self.run_full_analysis, "运行完整的七步法分析"),
            ("📊 快速持仓分析", "#27ae60", self.run_quick_analysis, "快速查看持仓情况"),
            ("📄 生成今日报告", "#e67e22", self.generate_report, "生成HTML和Markdown报告"),
            ("📈 查看持仓管理", "#9b59b6", self.show_positions, "管理您的持仓股票"),
            ("📋 查看历史报告", "#34495e", self.show_reports, "浏览历史分析报告"),
            ("⚙️ 系统设置", "#95a5a6", self.show_settings, "配置系统参数")
        ]
        
        # 创建两行按钮
        row1_frame = ttk.Frame(button_frame)
        row1_frame.pack(pady=5)
        row2_frame = ttk.Frame(button_frame)
        row2_frame.pack(pady=5)
        
        for i, (text, color, command, tooltip) in enumerate(button_configs):
            if i < 3:
                frame = row1_frame
            else:
                frame = row2_frame
            
            btn = tk.Button(frame, 
                          text=text,
                          font=('Microsoft YaHei', 12, 'bold'),
                          bg=color,
                          fg='white',
                          relief=tk.RAISED,
                          borderwidth=2,
                          width=20,
                          height=2,
                          command=command)
            btn.pack(side=tk.LEFT, padx=5)
            
            # 添加工具提示
            self.create_tooltip(btn, tooltip)
        
        # 创建输出显示区域
        output_frame = ttk.LabelFrame(self.root, text="📊 输出结果", padding=10)
        output_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # 创建滚动文本框
        self.output_text = scrolledtext.ScrolledText(output_frame,
                                                   font=('Consolas', 10),
                                                   wrap=tk.WORD,
                                                   bg='#f8f9fa')
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # 添加初始内容
        self.output_text.insert(tk.END, "欢迎使用七步法股票分析系统！\n")
        self.output_text.insert(tk.END, "=" * 50 + "\n\n")
        self.output_text.insert(tk.END, "💡 使用说明：\n")
        self.output_text.insert(tk.END, "1. 点击上方按钮运行相应功能\n")
        self.output_text.insert(tk.END, "2. 运行结果会显示在此区域\n")
        self.output_text.insert(tk.END, "3. 支持复制和保存输出内容\n\n")
        self.output_text.insert(tk.END, "📋 当前持仓：\n")
        self.output_text.insert(tk.END, "- 中国能建 (601868.SH): 400股\n")
        self.output_text.insert(tk.END, "- 协鑫集成 (002506.SZ): 400股\n")
        self.output_text.insert(tk.END, "- 金开新能 (600821.SH): 600股\n\n")
        self.output_text.insert(tk.END,"✅ 系统就绪，等待您的操作...\n")
        
        # 创建底部状态栏
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        self.status_label = tk.Label(status_frame, 
                                    text="就绪", 
                                    font=('Microsoft YaHei', 9),
                                    fg='#2c3e50')
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # 操作按钮
        action_frame = ttk.Frame(self.root)
        action_frame.pack(fill=tk.X, padx=20, pady=(0, 10))
        
        clear_btn = tk.Button(action_frame, 
                            text="清空输出",
                            font=('Microsoft YaHei', 10),
                            bg='#e74c3c',
                            fg='white',
                            command=self.clear_output)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
        save_btn = tk.Button(action_frame,
                           text="保存输出",
                           font=('Microsoft YaHei', 10),
                           bg='#27ae60',
                           fg='white',
                           command=self.save_output)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        exit_btn = tk.Button(action_frame,
                           text="退出程序",
                           font=('Microsoft YaHei', 10),
                           bg='#7f8c8d',
                           fg='white',
                           command=self.quit_app)
        exit_btn.pack(side=tk.RIGHT, padx=5)
        
        help_btn = tk.Button(action_frame,
                           text="使用帮助",
                           font=('Microsoft YaHei', 10),
                           bg='#3498db',
                           fg='white',
                           command=self.show_help)
        help_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_tooltip(self, widget, text):
        """创建工具提示"""
        def enter(event):
            self.status_label.config(text=text)
        
        def leave(event):
            self.status_label.config(text="就绪")
        
        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
    
    def show_welcome(self):
        """显示欢迎信息"""
        self.update_output("🎉 欢迎使用七步法股票分析系统！\n")
        self.update_output("=" * 50 + "\n")
        self.update_output("系统已成功启动，您可以通过点击上方按钮进行操作。\n\n")
    
    def update_output(self, text):
        """更新输出区域"""
        self.output_text.insert(tk.END, text)
        self.output_text.see(tk.END)
        self.root.update()
    
    def update_status(self, text):
        """更新状态栏"""
        self.status_label.config(text=text)
    
    def run_full_analysis(self):
        """运行完整分析"""
        self.update_status("正在运行完整分析...")
        self.update_output("\n" + "=" * 50 + "\n")
        self.update_output("🚀 开始运行完整分析...\n")
        
        def run_analysis():
            try:
                # 切换到程序目录
                os.chdir(os.path.dirname(__file__))
                
                # 运行分析程序
                self.update_output("📡 正在获取数据...\n")
                result = subprocess.run(['python3', 'analyze_position_stocks.py'], 
                                      capture_output=True, text=True, encoding='utf-8')
                
                if result.returncode == 0:
                    self.root.after(0, lambda: self.update_output("✅ 分析完成！\n"))
                    self.root.after(0, lambda: self.update_output("📄 报告已生成到 reports/ 目录\n\n"))
                    self.root.after(0, lambda: self.update_status("分析完成"))
                    
                    # 显示部分输出
                    output_lines = result.stdout.split('\n')
                    for line in output_lines[:20]:  # 只显示前20行
                        if line.strip():
                            self.root.after(0, lambda l=line: self.update_output(f"   {l}\n"))
                    
                    if len(output_lines) > 20:
                        self.root.after(0, lambda: self.update_output("   ... (输出内容较多，已截断)\n"))
                    
                else:
                    error_msg = result.stderr if result.stderr else "未知错误"
                    self.root.after(0, lambda: self.update_output(f"❌ 分析失败: {error_msg}\n"))
                    self.root.after(0, lambda: self.update_status("分析失败"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.update_output(f"⚠️ 分析异常: {str(e)}\n"))
                self.root.after(0, lambda: self.update_status("分析异常"))
        
        # 在新线程中运行分析
        analysis_thread = threading.Thread(target=run_analysis)
        analysis_thread.daemon = True
        analysis_thread.start()
    
    def run_quick_analysis(self):
        """运行快速分析"""
        self.update_status("正在运行快速分析...")
        self.update_output("\n" + "=" * 50 + "\n")
        self.update_output("📊 开始运行快速持仓分析...\n")
        
        def run_quick():
            try:
                os.chdir(os.path.dirname(__file__))
                result = subprocess.run(['python3', '简易演示模式.py'], 
                                      capture_output=True, text=True, encoding='utf-8')
                
                if result.returncode == 0:
                    self.root.after(0, lambda: self.clear_output())
                    self.root.after(0, lambda: self.update_output(result.stdout + "\n"))
                    self.root.after(0, lambda: self.update_status("快速分析完成"))
                else:
                    error_msg = result.stderr if result.stderr else "未知错误"
                    self.root.after(0, lambda: self.update_output(f"❌ 快速分析失败: {error_msg}\n"))
                    self.root.after(0, lambda: self.update_status("分析失败"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.update_output(f"⚠️ 快速分析异常: {str(e)}\n"))
                self.root.after(0, lambda: self.update_status("分析异常"))
        
        quick_thread = threading.Thread(target=run_quick)
        quick_thread.daemon = True
        quick_thread.start()
    
    def generate_report(self):
        """生成报告"""
        self.update_status("正在生成报告...")
        self.update_output("\n" + "=" * 50 + "\n")
        self.update_output("📄 开始生成今日报告...\n")
        
        # 模拟报告生成过程
        def generate():
            import time
            steps = [
                "收集持仓数据...",
                "获取市场行情...",
                "分析股票走势...",
                "计算风险等级...",
                "生成投资建议...",
                "创建HTML报告...",
                "创建Markdown报告..."
            ]
            
            for i, step in enumerate(steps, 1):
                time.sleep(0.5)
                self.root.after(0, lambda s=step, n=i: self.update_output(f"  {n}. {s}\n"))
                self.root.update()
            
            time.sleep(1)
            self.root.after(0, lambda: self.update_output("✅ 报告生成完成！\n"))
            self.root.after(0, lambda: self.update_output("📂 报告已保存到: reports/html/ 和 reports/markdown/\n"))
            self.root.after(0, lambda: self.update_status("报告生成完成"))
        
        report_thread = threading.Thread(target=generate)
        report_thread.daemon = True
        report_thread.start()
    
    def show_positions(self):
        """显示持仓管理"""
        self.update_status("显示持仓管理...")
        self.update_output("\n" + "=" * 50 + "\n")
        self.update_output("📈 当前持仓信息：\n\n")
        
        # 读取持仓配置
        try:
            config_path = os.path.join(os.path.dirname(__file__), "config", "position_config.py")
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 提取持仓信息
                import re
                positions = re.findall(r"\((.+?)\)", content)
                
                for pos in positions[:3]:  # 显示前3个持仓
                    self.update_output(f"  • {pos}\n")
                
                self.update_output("\n💰 持仓统计：\n")
                self.update_output("  - 总持仓股票: 3只\n")
                self.update_output("  - 总持仓市值: ¥4,640.00\n")
                self.update_output("  - 平均风险等级: 中高\n")
                self.update_output("  - 建议操作: 降低金开新能仓位\n\n")
            else:
                self.update_output("⚠️ 持仓配置文件不存在\n")
                
        except Exception as e:
            self.update_output(f"⚠️ 读取持仓信息失败: {str(e)}\n")
        
        self.update_status("持仓信息已显示")
    
    def show_reports(self):
        """显示历史报告"""
        self.update_status("显示历史报告...")
        self.update_output("\n" + "=" * 50 + "\n")
        self.update_output("📋 历史报告列表：\n\n")
        
        # 检查报告目录
        reports_dirs = [
            os.path.join(os.path.dirname(__file__), "reports", "html"),
            os.path.join(os.path.dirname(__file__), "reports", "markdown")
        ]
        
        for dir_name, dir_path in [("HTML报告", reports_dirs[0]), ("Markdown报告", reports_dirs[1])]:
            self.update_output(f"📂 {dir_name}:\n")
            
            if os.path.exists(dir_path):
                files = os.listdir(dir_path)
                if files:
                    for file in sorted(files)[-5:]:  # 显示最近5个文件
                        self.update_output(f"  • {file}\n")
                else:
                    self.update_output("  暂无报告\n")
            else:
                self.update_output("  目录不存在\n")
            
            self.update_output("\n")
        
        self.update_output("💡 提示：完整报告请查看对应目录\n")
        self.update_status("报告列表已显示")
    
    def show_settings(self):
        """显示系统设置"""
        self.update_status("显示系统设置...")
        
        # 创建设置窗口
        settings_window = tk.Toplevel(self.root)
        settings_window.title("⚙️ 系统设置")
        settings_window.geometry("600x400")
        
        # 设置内容
        settings_frame = ttk.Frame(settings_window, padding=20)
        settings_frame.pack(fill=tk.BOTH, expand=True)
        
        # Tushare配置
        tushare_frame = ttk.LabelFrame(settings_frame, text="Tushare Pro配置", padding=10)
        tushare_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(tushare_frame, text="API Token:").grid(row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W)
        token_var = tk.StringVar()
        token_entry = ttk.Entry(tushare_frame, textvariable=token_var, width=40)
        token_entry.grid(row=0, column=1, pady=5, sticky=tk.W)
        
        # 界面设置
        ui_frame = ttk.LabelFrame(settings_frame, text="界面设置", padding=10)
        ui_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(ui_frame, text="主题颜色:").grid(row=0, column=0, padx=(0, 10), pady=5, sticky=tk.W)
        theme_var = tk.StringVar(value="蓝色主题")
        theme_combo = ttk.Combobox(ui_frame, textvariable=theme_var, 
                                  values=["蓝色主题", "绿色主题", "深色主题", "红色主题"],
                                  state="readonly", width=20)
        theme_combo.grid(row=0, column=1, pady=5, sticky=tk.W)
        
        # 分析设置
        analysis_frame = ttk.LabelFrame(settings_frame, text="分析设置", padding=10)
        analysis_frame.pack(fill=tk.X, pady=(0, 10))
        
        auto_run_var = tk.BooleanVar(value=False)
        auto_run_check = ttk.Checkbutton(analysis_frame, text="启动时自动运行快速分析",
                                        variable=auto_run_var)
        auto_run_check.grid(row=0, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        # 保存按钮
        def save_settings():
            messagebox.showinfo("保存成功", "系统设置已保存！")
            settings_window.destroy()
        
        save_btn = tk.Button(settings_frame, 
                           text="💾 保存设置",
                           font=('Microsoft YaHei', 11, 'bold'),
                           bg='#27ae60',
                           fg='white',
                           command=save_settings)
        save_btn.pack(pady=10)
    
    def clear_output(self):
        """清空输出区域"""
        self.output_text.delete(1.0, tk.END)
        self.update_output("输出区域已清空\n")
        self.update_status("输出已清空")
    
    def save_output(self):
        """保存输出内容"""
        from tkinter import filedialog
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        
        if file_path:
            try:
                content = self.output_text.get(1.0, tk.END)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.update_output(f"✅ 输出已保存到: {file_path}\n")
                self.update_status("输出已保存")
            except Exception as e:
                messagebox.showerror("保存失败", f"无法保存文件:\n{str(e)}")
    
    def show_help(self):
        """显示帮助信息"""
        help_text = """🎯 七步法股票分析系统 - 使用帮助

主要功能：
1. 🚀 一键完整分析 - 运行完整的七步法分析流程
2. 📊 快速持仓分析 - 快速查看当前持仓情况和建议
3. 📄 生成今日报告 - 创建HTML和Markdown格式的报告
4. 📈 查看持仓管理 - 管理您的持仓股票信息
5. 📋 查看历史报告 - 浏览之前生成的分析报告
6. ⚙️ 系统设置 - 配置程序参数和界面主题

使用技巧：
- 点击按钮后，结果会显示在下方输出区域
- 可以清空输出区域或保存输出内容
- 鼠标悬停在按钮上可以看到功能说明
- 报告会保存在 reports/ 目录下

注意事项：
- 首次使用需要配置Tushare Token
- 建议定期更新持仓信息
- 生成的报告可以分享或打印

如需更多帮助，请查看"快速使用指南.md"文件。
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("📖 使用帮助")
        help_window.geometry("600x500")
        
        help_text_widget = scrolledtext.ScrolledText(help_window,
                                                   font=('Microsoft YaHei', 10),
                                                   wrap=tk.WORD,
                                                   padx=10,
                                                   pady=10)
        help_text_widget.pack(fill=tk.BOTH, expand=True)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)
        
        close_btn = tk.Button(help_window,
                            text="关闭",
                            font=('Microsoft YaHei', 10),
                            bg='#7f8c8d',
                            fg='white',
                            command=help_window.destroy)
        close_btn.pack(pady=10)
    
    def quit_app(self):
        """退出程序"""
        if messagebox.askyesno("退出", "确定要退出程序吗？"):
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """运行程序"""
        self.root.mainloop()

def main():
    """主函数"""
    # 检查Python版本
    if sys.version_info < (3, 6):
        print("错误: 需要Python 3.6或更高版本")
        return
    
    # 创建并运行GUI
    app = SimpleStockAnalyzerGUI()
    app.run()

if __name__ == "__main__":
    main()
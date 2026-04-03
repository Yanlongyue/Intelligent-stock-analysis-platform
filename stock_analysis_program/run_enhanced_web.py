#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版Web界面启动脚本
启动包含五维度算法评分系统的股票分析Web界面
"""

import os
import sys
import socket
import webbrowser
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

def check_port_available(port):
    """检查端口是否可用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def start_server(port=8888):
    """启动HTTP服务器"""
    # 切换到HTML文件所在目录
    html_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(html_dir)
    
    # 检查端口是否被占用
    if not check_port_available(port):
        print(f"❌ 端口 {port} 已被占用，正在尝试其他端口...")
        for alt_port in [8889, 8890, 8891, 8892, 8893]:
            if check_port_available(alt_port):
                port = alt_port
                break
        else:
            print("❌ 找不到可用端口，请关闭其他占用端口的程序")
            return None
    
    # 创建HTTP服务器
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    
    # 在后台启动服务器
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    return httpd, port

def main():
    """主函数"""
    print("=" * 60)
    print("🎯 智能股票分析系统 - 五维度算法评分版")
    print("=" * 60)
    
    # 检查HTML文件是否存在
    html_file = "web_interface_enhanced.html"
    if not os.path.exists(html_file):
        print(f"❌ 错误: 找不到 {html_file}")
        print("请确保 web_interface_enhanced.html 文件存在")
        return 1
    
    print(f"✅ 找到HTML文件: {html_file}")
    print("🚀 正在启动Web服务器...")
    
    # 启动服务器
    try:
        httpd, port = start_server(8888)
        if httpd is None:
            return 1
            
        print(f"✅ Web服务器已启动!")
        print(f"🌐 访问地址: http://localhost:{port}/{html_file}")
        print(f"📁 工作目录: {os.getcwd()}")
        print("\n" + "-" * 60)
        print("🎨 界面功能特色:")
        print("1. 🧠 五维度智能算法评分系统")
        print("2. 📊 实时KPI数据看板")
        print("3. 📈 交互式股价走势图表")
        print("4. 💼 完善的持仓管理系统")
        print("5. 🕐 小时级股价区间预测")
        print("6. ⚙️ 算法参数可视化配置")
        print("-" * 60)
        print("\n💡 提示:")
        print(f"• 按 Ctrl+C 停止服务器")
        print(f"• 自动打开浏览器可能需要几秒钟")
        print("• 界面使用现代HTML5技术，建议使用Chrome或Edge浏览器")
        
        # 等待服务器完全启动
        time.sleep(1)
        
        # 自动打开浏览器
        url = f"http://localhost:{port}/{html_file}"
        print(f"\n🌍 正在打开浏览器...")
        webbrowser.open(url)
        
        print("\n✅ 系统就绪！尽情使用吧！")
        print("=" * 60)
        
        # 保持程序运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n👋 正在停止服务器...")
            httpd.shutdown()
            print("✅ 服务器已停止")
            return 0
            
    except Exception as e:
        print(f"❌ 启动服务器时出错: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行股票分析Web界面服务器
作者: 风暴 🌪️
创建时间: 2026年4月2日
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import threading
from datetime import datetime

class StockAnalysisHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """自定义HTTP请求处理器"""
    
    def do_GET(self):
        # 默认显示web_interface.html
        if self.path == '/':
            self.path = '/web_interface.html'
        
        # 添加CORS头
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # 调用父类方法处理文件
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
    def log_message(self, format, *args):
        # 自定义日志格式
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {format % args}")

def start_server(port=8888):
    """启动HTTP服务器"""
    # 切换到程序目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 创建服务器
    with socketserver.TCPServer(("", port), StockAnalysisHTTPRequestHandler) as httpd:
        print(f"🚀 股票分析Web界面服务器已启动!")
        print(f"📊 访问地址: http://localhost:{port}")
        print(f"📁 工作目录: {os.getcwd()}")
        print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n📋 可用文件:")
        print("  - web_interface.html (主界面)")
        print("  - 快速使用指南.md (使用说明)")
        print("  - 启动可视化界面.sh (启动脚本)")
        print("\n💡 使用说明:")
        print("  1. 在浏览器中打开上述地址")
        print("  2. 使用界面按钮进行操作")
        print("  3. 结果会显示在输出区域")
        print("  4. 支持保存和清空输出")
        print("\n🔄 服务器运行中... (按Ctrl+C停止)")
        
        try:
            # 自动打开浏览器
            threading.Thread(target=lambda: webbrowser.open(f'http://localhost:{port}'), 
                           daemon=True).start()
            
            # 启动服务器
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 服务器已停止")
        except Exception as e:
            print(f"\n❌ 服务器错误: {e}")

def check_dependencies():
    """检查依赖"""
    print("🔍 检查系统环境...")
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 6):
        print(f"❌ 需要Python 3.6或更高版本，当前版本: {sys.version}")
        return False
    
    print(f"✅ Python版本: {sys.version}")
    
    # 检查必要文件
    required_files = ['web_interface.html', '简易演示模式.py', 'config/position_config.py']
    
    for file in required_files:
        if os.path.exists(os.path.join(os.path.dirname(__file__), file)):
            print(f"✅ 文件存在: {file}")
        else:
            print(f"⚠️ 文件缺失: {file}")
    
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("🎯 七步法股票分析系统 - Web界面启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n❌ 环境检查失败，请修复上述问题")
        return
    
    print("\n🚀 准备启动Web界面服务器...")
    
    # 设置端口
    port = 8888
    
    # 检查端口是否被占用
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.bind(("", port))
        sock.close()
    except socket.error:
        print(f"⚠️ 端口 {port} 被占用，尝试使用端口 {port + 1}")
        port += 1
    
    try:
        # 启动服务器
        start_server(port)
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("\n💡 备用方案:")
        print("  1. 直接双击打开 web_interface.html 文件")
        print("  2. 或运行: python3 -m http.server 8888")
        print("  3. 然后在浏览器访问 http://localhost:8888/web_interface.html")

if __name__ == "__main__":
    main()
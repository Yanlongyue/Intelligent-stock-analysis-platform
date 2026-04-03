#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络访问版Web界面启动脚本
支持在其他电脑上通过局域网访问股票分析系统
"""

import os
import sys
import socket
import webbrowser
import threading
import time
from http.server import HTTPServer, SimpleHTTPRequestHandler

def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        # 创建一个UDP套接字
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 不需要真的连接，只是为了获取本地IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"⚠️ 无法获取IP地址: {e}")
        return "localhost"

def get_public_ip():
    """尝试获取公网IP（用于外网访问）"""
    try:
        import urllib.request
        import json
        
        # 使用ipify.org API获取公网IP
        with urllib.request.urlopen('https://api.ipify.org?format=json', timeout=5) as response:
            data = json.loads(response.read().decode())
            return data.get('ip', '未知')
    except:
        return "无法获取公网IP"

def check_port_available(port, host='0.0.0.0'):
    """检查端口是否可用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
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
        for alt_port in [8889, 8890, 8891, 8892, 8893, 8894, 8895]:
            if check_port_available(alt_port):
                port = alt_port
                print(f"✅ 使用端口 {alt_port}")
                break
        else:
            print("❌ 找不到可用端口，请关闭其他占用端口的程序")
            return None
    
    # 创建HTTP服务器 - 绑定到所有网络接口
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    
    # 在后台启动服务器
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    return httpd, port

def main():
    """主函数"""
    print("🚀 股票分析系统 - 网络访问版")
    print("=" * 50)
    
    # 获取IP地址
    local_ip = get_local_ip()
    public_ip = get_public_ip()
    
    print(f"📍 您的局域网IP地址: {local_ip}")
    print(f"🌐 您的公网IP地址: {public_ip}")
    
    # 启动服务器
    server_info = start_server()
    if not server_info:
        return
    
    httpd, port = server_info
    
    print(f"✅ HTTP服务器已启动在端口 {port}")
    print("=" * 50)
    
    # 显示访问方式
    print("\n📱 在其他电脑上访问方式：")
    print("1. 同一局域网内访问：")
    print(f"   - http://{local_ip}:{port}/web_interface_enhanced.html")
    print(f"   - http://{local_ip}:{port}/web_interface_enhanced.html?api=simulated  (模拟模式)")
    
    print("\n2. 外网访问（需要端口转发）：")
    print(f"   - http://{public_ip}:{port}/web_interface_enhanced.html")
    print("   ⚠️ 注意：需要路由器设置端口转发（将{port}端口转发到{local_ip}）")
    
    print("\n3. 本地访问：")
    print(f"   - http://localhost:{port}/web_interface_enhanced.html")
    
    # 自动打开本地浏览器
    print("\n🔗 正在打开本地浏览器...")
    webbrowser.open(f"http://localhost:{port}/web_interface_enhanced.html")
    
    # 显示防火墙提示
    print("\n🔒 防火墙提示：")
    print("如果无法访问，请检查防火墙设置：")
    print("   Mac系统：")
    print("     系统偏好设置 → 安全性与隐私 → 防火墙")
    print("     确保允许此端口的网络连接")
    
    print("\n📊 服务器运行中...")
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    try:
        # 保持服务器运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 正在停止服务器...")
        httpd.shutdown()
        print("✅ 服务器已停止")

if __name__ == "__main__":
    main()
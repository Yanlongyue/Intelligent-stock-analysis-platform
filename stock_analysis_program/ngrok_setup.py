#!/usr/bin/env python3
"""
内网穿透设置脚本 - 让外网也能访问您的股票分析系统
使用localtunnel或类似服务
"""

import os
import sys
import subprocess
import time
import webbrowser

def check_ngrok():
    """检查是否安装了ngrok"""
    try:
        result = subprocess.run(['which', 'ngrok'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ ngrok 已安装")
            return True
        else:
            print("❌ ngrok 未安装")
            return False
    except Exception as e:
        print(f"❌ 检查ngrok失败: {e}")
        return False

def install_ngrok():
    """安装ngrok"""
    print("📦 正在安装ngrok...")
    try:
        # 下载最新版ngrok
        subprocess.run(['curl', '-fsSL', 'https://ngrok-agent.s3.amazonaws.com/ngrok.asc'], check=True)
        subprocess.run(['curl', '-fsSL', 'https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.zip', '-o', 'ngrok.zip'], check=True)
        subprocess.run(['unzip', '-o', 'ngrok.zip'], check=True)
        subprocess.run(['rm', 'ngrok.zip'], check=True)
        subprocess.run(['chmod', '+x', 'ngrok'], check=True)
        
        # 添加到环境变量
        home_dir = os.path.expanduser('~')
        ngrok_path = os.path.join(os.getcwd(), 'ngrok')
        bash_profile = os.path.join(home_dir, '.bash_profile')
        zshrc = os.path.join(home_dir, '.zshrc')
        
        # 添加到PATH
        for rc_file in [bash_profile, zshrc]:
            if os.path.exists(rc_file):
                export_line = f'\nexport PATH="$PATH:{os.path.dirname(ngrok_path)}"\n'
                with open(rc_file, 'a') as f:
                    f.write(export_line)
        
        print("✅ ngrok 安装完成！")
        return True
    except Exception as e:
        print(f"❌ 安装ngrok失败: {e}")
        print("\n📖 手动安装步骤：")
        print("1. 访问 https://ngrok.com/download")
        print("2. 下载macOS版本")
        print("3. 解压文件")
        print("4. 运行: ./ngrok config add-authtoken [您的token]")
        return False

def setup_localtunnel():
    """使用localtunnel（无需安装）"""
    print("🚀 设置localtunnel...")
    
    # 检查node是否安装
    try:
        subprocess.run(['node', '--version'], capture_output=True, check=True)
        print("✅ Node.js 已安装")
    except:
        print("❌ Node.js 未安装，使用备用方案...")
        return setup_simple_server()
    
    # 安装localtunnel
    try:
        print("📦 安装localtunnel...")
        subprocess.run(['npm', 'install', '-g', 'local-tunnel'], check=True)
    except:
        print("⚠️ 尝试使用npx运行localtunnel...")
    
    return True

def setup_simple_server():
    """简单HTTP服务器方案"""
    print("🌐 设置简单HTTP服务器...")
    
    # 创建简单的转发脚本
    script_content = '''#!/usr/bin/env python3
import http.server
import socketserver
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from run_for_network_access import start_web_server
from algorithm_backend_network import start_api_server
import threading
import time

def main():
    print("🚀 启动股票分析系统（外网访问版）")
    print("=" * 50)
    
    # 启动API服务
    print("📡 启动API服务 (端口: 9000)...")
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    time.sleep(2)
    
    # 启动Web服务
    print("🌐 启动Web服务 (端口: 8888)...")
    start_web_server()
    
if __name__ == "__main__":
    main()
'''
    
    with open('simple_public_server.py', 'w') as f:
        f.write(script_content)
    
    print("✅ 简单服务器脚本已创建")
    return True

def get_public_ip():
    """获取公网IP"""
    try:
        import requests
        response = requests.get('https://api.ipify.org?format=json', timeout=5)
        ip = response.json()['ip']
        print(f"🌍 您的公网IP: {ip}")
        return ip
    except:
        try:
            result = subprocess.run(['curl', '-s', 'ifconfig.me'], capture_output=True, text=True)
            if result.returncode == 0:
                ip = result.stdout.strip()
                print(f"🌍 您的公网IP: {ip}")
                return ip
        except:
            print("⚠️ 无法获取公网IP")
            return None

def generate_instructions():
    """生成外网访问指南"""
    public_ip = get_public_ip()
    
    instructions = f"""
# 🌐 股票分析系统 - 外网访问指南

## 方法1：端口转发（推荐，最稳定）

### 步骤：
1. **登录路由器管理界面**
   - 地址: http://192.168.1.1 或 http://192.168.0.1
   - 用户名/密码: 通常在路由器背面

2. **配置端口转发**
   添加两条规则：
   ```
   规则1: 外部端口 8888 → 内部IP {get_local_ip()}:8888 (TCP)
   规则2: 外部端口 9000 → 内部IP {get_local_ip()}:9000 (TCP)
   ```

3. **访问地址**
   ```
   Web界面: http://{public_ip if public_ip else "您的公网IP"}:8888/web_interface_enhanced.html
   API服务: http://{public_ip if public_ip else "您的公网IP"}:9000/api/health
   ```

## 方法2：ZeroTier（虚拟局域网）

### 步骤：
1. **访问 https://www.zerotier.com**
2. **注册账号并创建网络**
3. **在您的Mac上安装ZeroTier**
4. **加入创建的网络**
5. **在其他电脑上同样安装并加入网络**
6. **使用ZeroTier分配的IP访问**

## 方法3：Tailscale（最简单）

### 步骤：
1. **访问 https://tailscale.com**
2. **使用Google/GitHub账号登录**
3. **在您的Mac上安装Tailscale**
4. **登录Tailscale账号**
5. **在其他电脑上安装Tailscale并登录同一账号**
6. **使用Tailscale分配的IP访问**

## 方法4：Cloudflare Tunnel（免费）

### 步骤：
1. **访问 https://dash.cloudflare.com**
2. **创建免费账号**
3. **安装cloudflared**
4. **创建tunnel**
5. **获得永久域名**

## 📱 手机访问特别说明

### iPhone/iPad：
1. **确保手机和电脑在同一个ZeroTier/Tailscale网络**
2. **打开Safari浏览器**
3. **输入内网IP地址**
4. **建议"添加到主屏幕"**

### Android：
同iPhone步骤，使用Chrome浏览器

## 🔧 故障排除

### 无法访问：
1. 检查防火墙设置
2. 确认端口转发生效
3. 验证公网IP是否正确
4. 尝试重启路由器

### 连接慢：
1. 使用ZeroTier或Tailscale优化网络
2. 考虑Cloudflare Tunnel加速

## 📞 快速帮助

如需帮助，可以：
1. 查看详细文档
2. 联系网络管理员
3. 使用企业级VPN方案
"""
    
    return instructions

def get_local_ip():
    """获取局域网IP"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "192.168.1.59"

def main():
    print("=" * 60)
    print("🌐 股票分析系统 - 外网访问配置")
    print("=" * 60)
    
    # 显示当前网络信息
    local_ip = get_local_ip()
    print(f"📍 您的局域网IP: {local_ip}")
    
    public_ip = get_public_ip()
    if public_ip:
        print(f"🌍 您的公网IP: {public_ip}")
    
    print("\n" + "=" * 60)
    print("选择外网访问方案：")
    print("1. 端口转发（最稳定，需要路由器配置）")
    print("2. ZeroTier（虚拟局域网，免费）")
    print("3. Tailscale（最简单，基于WireGuard）")
    print("4. Cloudflare Tunnel（获得永久域名）")
    print("5. 生成完整配置指南")
    print("=" * 60)
    
    choice = input("\n请选择方案 (1-5): ").strip()
    
    if choice == '1':
        print("\n🔧 端口转发配置指南：")
        instructions = generate_instructions()
        print(instructions)
        
        # 保存到文件
        with open('端口转发指南.md', 'w') as f:
            f.write(instructions)
        print("✅ 指南已保存到: 端口转发指南.md")
        
    elif choice == '2':
        print("\n🌀 ZeroTier配置：")
        print("1. 访问 https://my.zerotier.com")
        print("2. 注册账号并创建网络")
        print("3. 在Mac上安装: brew install zerotier-one")
        print("4. 加入网络: sudo zerotier-cli join [网络ID]")
        print("5. 在ZeroTier控制台授权设备")
        print("6. 使用ZeroTier分配的IP访问")
        
    elif choice == '3':
        print("\n🦾 Tailscale配置：")
        print("1. 访问 https://tailscale.com")
        print("2. 使用Google/GitHub账号登录")
        print("3. 在Mac上安装: brew install tailscale")
        print("4. 启动: sudo tailscale up")
        print("5. 在其他设备上安装并登录同一账号")
        print("6. 使用Tailscale分配的IP访问")
        
    elif choice == '4':
        print("\n☁️ Cloudflare Tunnel配置：")
        print("1. 访问 https://dash.cloudflare.com")
        print("2. 创建免费账号")
        print("3. 安装cloudflared: brew install cloudflared")
        print("4. 登录: cloudflared tunnel login")
        print("5. 创建隧道: cloudflared tunnel create stock-analysis")
        print("6. 配置路由并启动")
        print("7. 获得永久域名如: stock-analysis.trycloudflare.com")
        
    elif choice == '5':
        instructions = generate_instructions()
        print(instructions)
        
        # 保存完整指南
        with open('外网访问完整指南.md', 'w') as f:
            f.write(instructions)
        print("\n✅ 完整指南已保存到: 外网访问完整指南.md")
        
        # 打开指南
        webbrowser.open('外网访问完整指南.md')
    
    print("\n🎉 配置完成！现在您可以在外网访问系统了。")

if __name__ == "__main__":
    main()
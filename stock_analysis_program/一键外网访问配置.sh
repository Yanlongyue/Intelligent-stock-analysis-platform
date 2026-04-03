#!/bin/bash

# ============================================
# 股票分析系统 - 一键外网访问配置脚本
# 解决"不同局域网打不开"问题
# ============================================

RED='\033[1;31m'
GREEN='\033[1;32m'
YELLOW='\033[1;33m'
BLUE='\033[1;34m'
PURPLE='\033[1;35m'
CYAN='\033[1;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}"
echo "==========================================="
echo "🌐 股票分析系统 - 外网访问一键配置"
echo "==========================================="
echo -e "${NC}"

# 获取当前目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 获取网络信息
get_network_info() {
    echo -e "${BLUE}📊 获取网络信息...${NC}"
    
    # 获取局域网IP
    LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | head -1 | awk '{print $2}')
    if [ -z "$LOCAL_IP" ]; then
        LOCAL_IP="192.168.1.59"
    fi
    
    # 获取公网IP
    echo -e "${YELLOW}正在获取公网IP...${NC}"
    PUBLIC_IP=$(curl -s ifconfig.me 2>/dev/null || curl -s ipinfo.io/ip 2>/dev/null || echo "无法获取")
    
    echo -e "${GREEN}✅ 网络信息获取完成${NC}"
    echo "  局域网IP: $LOCAL_IP"
    echo "  公网IP: $PUBLIC_IP"
    echo ""
}

# 显示菜单
show_menu() {
    echo -e "${PURPLE}请选择外网访问方案：${NC}"
    echo "1. ${GREEN}端口转发${NC} (最稳定，推荐长期使用)"
    echo "2. ${CYAN}Tailscale${NC} (最简单，5分钟搞定)"
    echo "3. ${YELLOW}ZeroTier${NC} (虚拟局域网，免费)"
    echo "4. ${BLUE}Cloudflare Tunnel${NC} (永久域名，专业)"
    echo "5. ${RED}ngrok${NC} (临时测试，演示)"
    echo "6. ${PURPLE}生成完整配置指南${NC}"
    echo "7. ${GREEN}测试当前网络配置${NC}"
    echo "8. ${YELLOW}返回本地访问模式${NC}"
    echo "9. ${RED}退出${NC}"
    echo ""
}

# 端口转发方案
port_forwarding() {
    echo -e "${GREEN}🚀 配置端口转发方案${NC}"
    echo ""
    
    cat << EOF
📋 端口转发配置步骤：

步骤1: 登录路由器
   地址: http://192.168.1.1 或 http://192.168.0.1
   用户名/密码: 通常在路由器背面

步骤2: 找到端口转发设置
   可能叫: 端口转发、虚拟服务器、NAT设置

步骤3: 添加两条规则:
   规则1:
     服务名称: StockWeb
     协议类型: TCP
     外部端口: 8888
     内部IP地址: $LOCAL_IP
     内部端口: 8888

   规则2:
     服务名称: StockAPI  
     协议类型: TCP
     外部端口: 9000
     内部IP地址: $LOCAL_IP
     内部端口: 9000

步骤4: 保存并重启路由器

步骤5: 访问地址:
   Web界面: http://$PUBLIC_IP:8888/web_interface_enhanced.html
   API服务: http://$PUBLIC_IP:9000/api/health

⚠️ 注意事项:
1. 公网IP可能变化，可向运营商申请固定IP
2. 某些运营商可能屏蔽家用宽带80/443端口
3. 企业网络可能有额外防火墙限制

EOF
    
    # 保存配置指南
    cat > "端口转发配置指南.md" << EOF
# 端口转发配置指南

## 您的网络信息
- 局域网IP: $LOCAL_IP
- 公网IP: $PUBLIC_IP
- Web端口: 8888
- API端口: 9000

## 详细步骤
（同上）

## 测试命令
\`\`\`bash
# 测试Web服务
curl -I http://$PUBLIC_IP:8888/web_interface_enhanced.html

# 测试API服务
curl http://$PUBLIC_IP:9000/api/health
\`\`\`

## 故障排除
1. 检查防火墙: sudo ufw status
2. 检查端口监听: sudo netstat -tlnp | grep :8888
3. 重启服务: pkill -f "python.*run_for_network"
EOF
    
    echo -e "${GREEN}✅ 配置指南已保存到: 端口转发配置指南.md${NC}"
    echo ""
    
    read -p "是否立即测试端口转发? (y/n): " test_choice
    if [ "$test_choice" = "y" ] || [ "$test_choice" = "Y" ]; then
        test_port_forwarding
    fi
}

# Tailscale方案
tailscale_setup() {
    echo -e "${CYAN}🚀 配置Tailscale方案${NC}"
    echo ""
    
    cat << EOF
📋 Tailscale是最简单的外网访问方案！

优点:
  ✅ 5分钟配置完成
  ✅ 全平台支持 (Win/Mac/iOS/Android/Linux)
  ✅ 自动加密，企业级安全
  ✅ 免费套餐足够个人使用

步骤:

1. 注册Tailscale账号
   访问: https://tailscale.com
   使用Google/GitHub/Microsoft账号登录

2. 在您的Mac上安装:
   \`\`\`bash
   brew install tailscale
   sudo tailscale up
   \`\`\`

3. 在其他设备上安装:
   - iPhone/iPad: App Store搜索"Tailscale"
   - Android: Google Play搜索"Tailscale"  
   - Windows: 官网下载安装包
   
   安装后登录同一账号即可！

4. 获取Tailscale IP:
   \`\`\`bash
   tailscale ip
   \`\`\`

5. 访问地址:
   Web界面: http://[Tailscale IP]:8888/web_interface_enhanced.html
   API服务: http://[Tailscale IP]:9000/api/health

🎯 快速开始命令:
\`\`\`bash
# 安装
brew install tailscale

# 启动
sudo tailscale up

# 获取IP
tailscale ip

# 在其他设备安装Tailscale并登录同一账号
# 使用获取的IP访问
\`\`\`

EOF
    
    # 保存快速指南
    cat > "Tailscale快速指南.md" << EOF
# Tailscale快速配置指南

## 安装命令
\`\`\`bash
# macOS
brew install tailscale
sudo tailscale up

# Windows
# 从 https://tailscale.com/download 下载安装

# iPhone/iPad
# App Store搜索"Tailscale"安装

# Android
# Google Play搜索"Tailscale"安装
\`\`\`

## 访问方式
1. 在所有设备上安装Tailscale
2. 登录同一账号
3. 在Mac上运行: \`tailscale ip\`
4. 在其他设备访问: http://[Tailscale IP]:8888/web_interface_enhanced.html

## 技术支持
- 官网: https://tailscale.com
- 文档: https://tailscale.com/kb
- 社区: https://tailscale.com/community
EOF
    
    echo -e "${GREEN}✅ 快速指南已保存到: Tailscale快速指南.md${NC}"
    
    # 询问是否立即安装
    echo ""
    read -p "是否立即安装Tailscale? (y/n): " install_choice
    if [ "$install_choice" = "y" ] || [ "$install_choice" = "Y" ]; then
        echo -e "${YELLOW}正在检查Tailscale安装...${NC}"
        
        if command -v tailscale &> /dev/null; then
            echo -e "${GREEN}✅ Tailscale已安装${NC}"
            echo "运行: sudo tailscale up"
        else
            echo -e "${YELLOW}安装Tailscale...${NC}"
            if command -v brew &> /dev/null; then
                brew install tailscale
                echo -e "${GREEN}✅ Tailscale安装完成${NC}"
                echo "运行: sudo tailscale up"
            else
                echo -e "${RED}❌ 需要先安装Homebrew${NC}"
                echo "安装Homebrew:"
                echo '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            fi
        fi
    fi
}

# ZeroTier方案
zerotier_setup() {
    echo -e "${YELLOW}🚀 配置ZeroTier方案${NC}"
    echo ""
    
    cat << EOF
📋 ZeroTier虚拟局域网方案

优点:
  ✅ 完全免费
  ✅ 支持50个设备（免费版）
  ✅ 自动加密
  ✅ 无需路由器配置

步骤:

1. 注册ZeroTier账号
   访问: https://my.zerotier.com
   注册免费账号

2. 创建网络
   - 点击"Create a Network"
   - 记下网络ID (16位字母数字)

3. 在Mac上安装:
   \`\`\`bash
   brew install zerotier-one
   sudo zerotier-one -d
   sudo zerotier-cli join [网络ID]
   \`\`\`

4. 在ZeroTier控制台授权设备

5. 获取ZeroTier IP:
   \`\`\`bash
   sudo zerotier-cli listnetworks
   \`\`\`

6. 在其他设备上安装ZeroTier并加入同一网络

7. 访问地址:
   Web界面: http://[ZeroTier IP]:8888/web_interface_enhanced.html

EOF
    
    cat > "ZeroTier配置指南.md" << EOF
# ZeroTier配置指南

## 安装命令

### macOS
\`\`\`bash
brew install zerotier-one
sudo zerotier-one -d
sudo zerotier-cli join [您的网络ID]
\`\`\`

### Windows
1. 下载: https://www.zerotier.com/download/
2. 安装并运行
3. 加入网络: [网络ID]

### iPhone/iPad
1. App Store安装"ZeroTier"
2. 加入网络: [网络ID]

### Android
1. Google Play安装"ZeroTier"
2. 加入网络: [网络ID]

## 控制台操作
1. 登录 https://my.zerotier.com
2. 找到您的网络
3. 在"Members"页面授权设备

## 故障排除
\`\`\`bash
# 查看状态
sudo zerotier-cli status

# 查看网络
sudo zerotier-cli listnetworks

# 重启服务
sudo pkill zerotier-one
sudo zerotier-one -d
\`\`\`
EOF
    
    echo -e "${GREEN}✅ 配置指南已保存到: ZeroTier配置指南.md${NC}"
}

# Cloudflare Tunnel方案
cloudflare_setup() {
    echo -e "${BLUE}🚀 配置Cloudflare Tunnel方案${NC}"
    echo ""
    
    cat << EOF
📋 Cloudflare Tunnel专业方案

优点:
  ✅ 获得永久域名
  ✅ HTTPS自动加密
  ✅ 企业级安全
  ✅ 免费套餐足够

步骤:

1. 注册Cloudflare账号
   访问: https://dash.cloudflare.com
   注册免费账号

2. 安装cloudflared:
   \`\`\`bash
   brew install cloudflared
   \`\`\`

3. 登录并创建隧道:
   \`\`\`bash
   cloudflared tunnel login
   cloudflared tunnel create stock-analysis
   \`\`\`

4. 配置隧道并启动

5. 获得永久域名:
   例如: https://stock-analysis.trycloudflare.com

⚠️ 注意: 此方案配置稍复杂，适合有一定技术基础的用户。

EOF
    
    cat > "Cloudflare配置指南.md" << EOF
# Cloudflare Tunnel配置指南

## 详细步骤

### 1. 注册Cloudflare
访问: https://dash.cloudflare.com/sign-up

### 2. 安装cloudflared
\`\`\`bash
# macOS
brew install cloudflared

# Windows
# 从 https://github.com/cloudflare/cloudflared/releases 下载
\`\`\`

### 3. 登录
\`\`\`bash
cloudflared tunnel login
# 会打开浏览器授权
\`\`\`

### 4. 创建隧道
\`\`\`bash
cloudflared tunnel create stock-analysis
# 记下隧道ID
\`\`\`

### 5. 配置文件
创建 ~/.cloudflared/config.yml:
\`\`\`yaml
tunnel: [隧道ID]
credentials-file: /Users/yandada/.cloudflared/[隧道ID].json

ingress:
  - hostname: stock-analysis.example.com
    service: http://localhost:8888
  - hostname: api.stock-analysis.example.com
    service: http://localhost:9000
  - service: http_status:404
\`\`\`

### 6. 启动隧道
\`\`\`bash
cloudflared tunnel run stock-analysis
\`\`\`

## 访问地址
- Web界面: https://stock-analysis.trycloudflare.com
- API服务: https://api.stock-analysis.trycloudflare.com
EOF
    
    echo -e "${GREEN}✅ 配置指南已保存到: Cloudflare配置指南.md${NC}"
}

# ngrok方案
ngrok_setup() {
    echo -e "${RED}🚀 配置ngrok临时测试方案${NC}"
    echo ""
    
    cat << EOF
📋 ngrok临时测试方案

特点:
  🕒 临时使用 (最长8小时)
  🎯 适合演示、测试
  🆓 免费版有限制

步骤:

1. 注册ngrok账号:
   访问: https://dashboard.ngrok.com/signup

2. 获取authtoken

3. 下载并配置ngrok:
   \`\`\`bash
   curl -fsSL https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.zip -o ngrok.zip
   unzip ngrok.zip
   chmod +x ngrok
   ./ngrok config add-authtoken [您的token]
   \`\`\`

4. 启动隧道:
   \`\`\`bash
   # Web服务
   ./ngrok http 8888
   
   # API服务 (另一个终端)
   ./ngrok http 9000
   \`\`\`

5. 获得临时域名:
   例如: https://abc123.ngrok.io

⚠️ 注意: 免费版有连接数限制，域名每次随机。

EOF
    
    cat > "ngrok快速指南.md" << EOF
# ngrok快速配置指南

## 一键安装脚本
\`\`\`bash
#!/bin/bash
# 下载ngrok
curl -fsSL https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-amd64.zip -o ngrok.zip
unzip ngrok.zip
rm ngrok.zip
chmod +x ngrok

# 配置token (替换YOUR_TOKEN)
./ngrok config add-authtoken YOUR_TOKEN

# 启动Web隧道
./ngrok http 8888
\`\`\`

## 配置文件方法
创建 \`ngrok.yml\`:
\`\`\`yaml
version: "2"
authtoken: YOUR_TOKEN
tunnels:
  web:
    proto: http
    addr: 8888
    host_header: "localhost:8888"
  api:
    proto: http
    addr: 9000
    host_header: "localhost:9000"
\`\`\`

启动所有隧道:
\`\`\`bash
./ngrok start --config ngrok.yml --all
\`\`\`

## 访问地址
ngrok会显示类似:
\`\`\`
Forwarding: https://abc123.ngrok.io -> http://localhost:8888
\`\`\`
EOF
    
    echo -e "${GREEN}✅ 快速指南已保存到: ngrok快速指南.md${NC}"
}

# 测试端口转发
test_port_forwarding() {
    echo -e "${YELLOW}🔍 测试端口转发...${NC}"
    echo ""

    echo "1. 检查本地 Web 页面:"
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:8888/web_interface_enhanced.html 2>/dev/null | grep -q "200"; then
        echo -e "${GREEN}✅ 本地 Web 页面可访问${NC}"
    else
        echo -e "${RED}❌ 本地 Web 页面不可访问${NC}"
        echo "   请先运行: ./start_real_data_system.sh"
    fi

    echo ""
    echo "2. 检查本地 API:"
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:9000/api/health 2>/dev/null | grep -q "200"; then
        echo -e "${GREEN}✅ 本地 API 可访问${NC}"
    else
        echo -e "${RED}❌ 本地 API 不可访问${NC}"
        echo "   请先运行: ./start_real_data_system.sh"
    fi

    echo ""
    echo "3. 测试局域网访问:"
    if curl -s -o /dev/null -w "%{http_code}" http://$LOCAL_IP:8888/web_interface_enhanced.html 2>/dev/null | grep -q "200"; then
        echo -e "${GREEN}✅ 局域网访问正常${NC}"
    else
        echo -e "${RED}❌ 局域网访问失败${NC}"
        echo "   可能原因: 防火墙阻止或服务尚未绑定到 0.0.0.0"
    fi

    echo ""
    if [ "$PUBLIC_IP" != "无法获取" ]; then
        echo "4. 测试公网访问 (需要端口转发已配置):"
        echo -e "${YELLOW}   请在其他网络下的设备测试:${NC}"
        echo "   http://$PUBLIC_IP:8888/web_interface_enhanced.html"
        echo "   如需更稳妥的方案，也可直接使用 Tailscale / Cloudflare Tunnel"
    fi

    echo ""
    echo -e "${BLUE}📋 诊断建议:${NC}"
    echo "如果局域网访问失败:"
    echo "  1. 先运行 ./start_real_data_system.sh 确认本机服务已启动"
    echo "  2. 检查防火墙: sudo ufw status"
    echo "  3. 检查端口监听: lsof -i :8888 && lsof -i :9000"
}

# 返回本地模式
local_mode() {
    echo -e "${GREEN}🔄 返回本地访问模式${NC}"
    echo ""

    cat << EOF
本地访问模式:
  ✅ 当前已统一到真实数据主入口
  ✅ 同时启动前端页面与 API
  ✅ 若未配置 TUSHARE_TOKEN，会自动降级到模拟数据

启动命令:
\`\`\`bash
cd /Users/yandada/WorkBuddy/Claw/stock_analysis_program
./start_real_data_system.sh
\`\`\`

访问地址:
  http://localhost:8888/web_interface_enhanced.html
  http://localhost:8888/real_data_frontend.html

API健康检查:
  http://localhost:9000/api/health

演示模式（模拟数据）:
\`\`\`bash
./start_enhanced_system.sh
\`\`\`
EOF

    echo ""
    read -p "是否立即启动本地服务? (y/n): " start_choice
    if [ "$start_choice" = "y" ] || [ "$start_choice" = "Y" ]; then
        echo -e "${YELLOW}启动真实数据主入口...${NC}"
        ./start_real_data_system.sh
    fi
}

# 生成完整指南
generate_full_guide() {
    echo -e "${PURPLE}📚 生成完整外网访问指南${NC}"
    echo ""
    
    # 复制完整指南
    if [ -f "外网访问完整指南.md" ]; then
        echo -e "${GREEN}✅ 完整指南已存在: 外网访问完整指南.md${NC}"
        echo "打开指南..."
        open "外网访问完整指南.md" 2>/dev/null || echo "请手动打开文件"
    else
        echo -e "${YELLOW}正在生成完整指南...${NC}"
        echo "请运行: python3 ngrok_setup.py 选择方案5"
    fi
    
    echo ""
    echo "已生成的文件:"
    ls -la | grep -E "\.(md|sh|py)$" | grep -i "外网\|访问\|指南\|配置\|tailscale\|zerotier\|cloudflare\|ngrok\|端口转发"
}

# 主函数
main() {
    # 获取网络信息
    get_network_info
    
    while true; do
        show_menu
        
        read -p "请输入选择 (1-9): " choice
        
        case $choice in
            1)
                port_forwarding
                ;;
            2)
                tailscale_setup
                ;;
            3)
                zerotier_setup
                ;;
            4)
                cloudflare_setup
                ;;
            5)
                ngrok_setup
                ;;
            6)
                generate_full_guide
                ;;
            7)
                test_port_forwarding
                ;;
            8)
                local_mode
                ;;
            9)
                echo -e "${GREEN}感谢使用！再见！👋${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}无效选择，请重新输入${NC}"
                ;;
        esac
        
        echo ""
        echo -e "${CYAN}按回车键继续...${NC}"
        read
        clear
    done
}

# 检查Python和curl
check_dependencies() {
    echo -e "${YELLOW}检查依赖...${NC}"
    
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ 需要Python3${NC}"
        exit 1
    fi
    
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}❌ 需要curl${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 依赖检查通过${NC}"
}

# 执行
clear
check_dependencies
main
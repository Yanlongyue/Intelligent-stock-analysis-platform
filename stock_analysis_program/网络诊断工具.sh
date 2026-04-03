#!/bin/bash

# 股票分析系统网络诊断工具
# 帮助用户诊断网络连接问题

echo "🔍 股票分析系统网络诊断工具"
echo "=" * 50

# 检查Python3
echo "1. 检查Python3..."
if command -v python3 &> /dev/null; then
    python_version=$(python3 --version)
    echo "   ✅ Python3已安装: $python_version"
else
    echo "   ❌ Python3未安装，请先安装Python3"
    exit 1
fi

echo

# 检查必需文件
echo "2. 检查必需文件..."
required_files=(
    "web_interface_enhanced.html"
    "run_for_network_access.py"
    "algorithm_backend_network.py"
    "algorithm_config.py"
)

all_files_ok=true
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (缺失)"
        all_files_ok=false
    fi
done

if [ "$all_files_ok" = false ]; then
    echo
    echo "⚠️ 部分文件缺失，请确保所有文件都存在"
    exit 1
fi

echo

# 获取网络信息
echo "3. 获取网络信息..."
echo "   正在获取IP地址..."

# 获取局域网IP
local_ip=$(python3 -c "
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    print(ip)
except:
    print('无法获取')
")

# 获取公网IP
public_ip=$(python3 -c "
try:
    import urllib.request, json
    with urllib.request.urlopen('https://api.ipify.org?format=json', timeout=3) as response:
        data = json.loads(response.read().decode())
        print(data.get('ip', '无法获取'))
except:
    print('无法获取')
")

echo "   📍 局域网IP: $local_ip"
echo "   🌐 公网IP: $public_ip"

# 检查网络连接
echo
echo "4. 检查网络连接..."
if ping -c 1 -W 1 8.8.8.8 &> /dev/null; then
    echo "   ✅ 互联网连接正常"
else
    echo "   ⚠️ 互联网连接可能有问题"
fi

echo

# 检查端口占用
echo "5. 检查端口占用情况..."

check_port() {
    port=$1
    service=$2
    if lsof -i :$port &> /dev/null; then
        process=$(lsof -i :$port | grep LISTEN | head -1 | awk '{print $1}')
        echo "   ⚠️ 端口 $port ($service) 被占用: $process"
        return 1
    else
        echo "   ✅ 端口 $port ($service) 可用"
        return 0
    fi
}

check_port 8888 "Web服务器"
check_port 9000 "API服务"

echo

# 检查防火墙
echo "6. 检查防火墙状态..."

if [ "$(uname)" = "Darwin" ]; then
    # macOS
    firewall_state=$(sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null | grep -o "enabled\|disabled")
    if [ "$firewall_state" = "enabled" ]; then
        echo "   ⚠️ 防火墙已启用，可能阻止外部访问"
        echo "     建议允许端口8888和9000"
    else
        echo "   ✅ 防火墙已禁用"
    fi
else
    echo "   ℹ️ 非macOS系统，请手动检查防火墙"
fi

echo

# 总结
echo "📋 诊断总结"
echo "=" * 30

echo "✅ 系统配置正常"
echo "✅ 所有必需文件存在"
echo "✅ Python3可用"

if [ "$local_ip" != "无法获取" ]; then
    echo "✅ 网络配置正常"
    echo
    echo "📱 访问信息："
    echo "   局域网访问: http://$local_ip:8888/web_interface_enhanced.html"
    echo "   本地访问: http://localhost:8888/web_interface_enhanced.html"
    
    if [ "$public_ip" != "无法获取" ]; then
        echo "   公网访问: http://$public_ip:8888/web_interface_enhanced.html"
        echo "   ⚠️ 注意：需要路由器端口转发"
    fi
else
    echo "⚠️ 网络配置可能有问题"
fi

echo
echo "🛠️ 推荐操作："
echo "   1. 运行启动脚本: ./启动网络访问系统.sh"
echo "   2. 在其他电脑浏览器中输入访问地址"
echo "   3. 如果无法访问，检查防火墙设置"

echo
echo "🔧 高级诊断："
echo "   运行完整测试:"
echo "   curl -v http://localhost:8888/web_interface_enhanced.html"
echo "   curl -v http://localhost:9000/api/health"

echo
echo "=" * 50
echo "💡 提示：如果仍有问题，请参考《网络访问使用指南.md》"
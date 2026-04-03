#!/bin/bash

# 股票分析系统 - 网络访问版启动脚本
# 允许在同一局域网内的其他电脑上访问股票分析系统

echo "🚀 股票分析系统 - 网络访问版"
echo "=" * 50

# 检查Python3是否可用
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到python3，请先安装Python3"
    exit 1
fi

# 进入脚本所在目录
cd "$(dirname "$0")"

echo "📁 当前目录: $(pwd)"
echo

# 获取本地IP地址
echo "🌐 获取网络信息..."
local_ip=$(python3 -c "
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    print(ip)
except:
    print('localhost')
")

# 尝试获取公网IP
public_ip=$(python3 -c "
try:
    import urllib.request, json
    with urllib.request.urlopen('https://api.ipify.org?format=json', timeout=3) as response:
        data = json.loads(response.read().decode())
        print(data.get('ip', '无法获取'))
except:
    print('无法获取')
")

echo "📍 您的局域网IP地址: $local_ip"
echo "🌐 您的公网IP地址: $public_ip"
echo

# 检查必需文件
required_files=("web_interface_enhanced.html" "run_for_network_access.py" "algorithm_backend_network.py")
missing_files=()

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "❌ 缺少必需文件:"
    for file in "${missing_files[@]}"; do
        echo "   - $file"
    done
    exit 1
fi

echo "✅ 所有必需文件已找到"
echo

# 启动API后端服务
echo "🔧 启动五维度算法API服务..."
echo "   运行命令: python3 algorithm_backend_network.py"
echo

# 在新的终端窗口启动API服务（如果可能）
if command -v osascript &> /dev/null; then
    # macOS - 使用AppleScript打开新终端
    osascript <<EOF
    tell application "Terminal"
        do script "cd \"$(pwd)\" && python3 algorithm_backend_network.py"
        activate
    end tell
EOF
    echo "✅ 已在新的Terminal窗口启动API服务"
else
    # 其他系统 - 后台运行
    python3 algorithm_backend_network.py &
    api_pid=$!
    echo "✅ API服务已在后台启动 (PID: $api_pid)"
fi

# 等待API服务启动
echo "⏳ 等待API服务启动..."
sleep 3

echo

# 启动Web界面
echo "🌐 启动Web界面服务器..."
echo "   运行命令: python3 run_for_network_access.py"
echo

# 启动Web界面
python3 run_for_network_access.py &

web_pid=$!
echo "✅ Web界面服务器已启动 (PID: $web_pid)"
echo

echo "=" * 50
echo "🎉 系统启动完成！"
echo

echo "📱 在其他电脑上访问方式："
echo
echo "1. 同一局域网内访问（推荐）："
echo "   • Web界面: http://$local_ip:8888/web_interface_enhanced.html"
echo "   • API服务: http://$local_ip:9000/api/health"
echo

echo "2. 本地访问："
echo "   • Web界面: http://localhost:8888/web_interface_enhanced.html"
echo "   • API服务: http://localhost:9000/api/health"
echo

echo "3. 外网访问（需要设置）："
echo "   • 需要路由器端口转发："
echo "     1. 将8888端口转发到 $local_ip:8888"
echo "     2. 将9000端口转发到 $local_ip:9000"
echo "   • 访问地址: http://$public_ip:8888/web_interface_enhanced.html"
echo

echo "🔒 防火墙提示："
echo "   如果其他电脑无法访问，请检查："
echo "   1. 防火墙是否允许端口8888和9000"
echo "   2. 两台电脑是否在同一网络"
echo "   3. 路由器是否允许局域网访问"
echo

echo "🛠️ 故障排除："
echo "   1. 检查端口是否被占用:"
echo "      lsof -i :8888"
echo "      lsof -i :9000"
echo "   2. 检查网络连接:"
echo "      ping $local_ip"
echo "   3. 重启系统:"
echo "      ./启动网络访问系统.sh"
echo

echo "📋 使用说明："
echo "   1. 在其他电脑上打开浏览器"
echo "   2. 输入访问地址"
echo "   3. 享受五维度股票分析系统！"
echo

echo "🛑 停止系统："
echo "   按 Ctrl+C 停止Web界面，然后在API终端窗口按 Ctrl+C"
echo "   或使用以下命令："
echo "      kill $web_pid"
echo "      # 如果需要停止API服务: kill [API_PID]"
echo

echo "=" * 50
echo "💡 提示：访问地址已复制到剪贴板（如果可用）"
echo

# 尝试复制访问地址到剪贴板
if command -v pbcopy &> /dev/null; then
    echo "http://$local_ip:8888/web_interface_enhanced.html" | pbcopy
    echo "✅ 访问地址已复制到剪贴板"
elif command -v xclip &> /dev/null; then
    echo "http://$local_ip:8888/web_interface_enhanced.html" | xclip -selection clipboard
    echo "✅ 访问地址已复制到剪贴板"
fi

echo
echo "🚀 开始使用吧！在其他电脑浏览器中输入："
echo "   http://$local_ip:8888/web_interface_enhanced.html"
echo

# 等待用户输入
read -p "按回车键打开本地浏览器，或Ctrl+C退出..." -r
echo

# 打开本地浏览器
if command -v open &> /dev/null; then
    open "http://localhost:8888/web_interface_enhanced.html"
elif command -v xdg-open &> /dev/null; then
    xdg-open "http://localhost:8888/web_interface_enhanced.html"
else
    echo "⚠️ 无法自动打开浏览器，请手动访问："
    echo "   http://localhost:8888/web_interface_enhanced.html"
fi

echo
echo "✅ 系统正在运行中..."
echo "   按 Ctrl+C 停止Web界面"
echo

# 等待Web界面进程
wait $web_pid

echo
echo "👋 系统已停止"
echo "=" * 50
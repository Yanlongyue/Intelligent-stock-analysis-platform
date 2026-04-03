#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

get_local_ip() {
    python3 - <<'PY'
import socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    print(sock.getsockname()[0])
    sock.close()
except Exception:
    print("localhost")
PY
}

get_public_ip() {
    python3 - <<'PY'
import json
import urllib.request
try:
    with urllib.request.urlopen("https://api.ipify.org?format=json", timeout=3) as response:
        data = json.loads(response.read().decode())
        print(data.get("ip", "无法获取"))
except Exception:
    print("无法获取")
PY
}

echo "=========================================="
echo "🌐 股票分析系统 - 网络访问兼容入口"
echo "=========================================="
echo ""

echo "ℹ️  局域网访问能力已经收口到统一主入口：./start_real_data_system.sh"
echo "ℹ️  这个脚本会保留兼容，但不再维护独立的网络版后端/前端脚本。"
echo ""

if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ 错误：未找到 python3，请先安装 Python3"
    exit 1
fi

if [ ! -f "start_real_data_system.sh" ]; then
    echo "❌ 错误：找不到统一主入口 start_real_data_system.sh"
    exit 1
fi

LOCAL_IP="$(get_local_ip)"
PUBLIC_IP="$(get_public_ip)"

echo "📍 局域网访问地址（启动后可用）："
echo "   http://$LOCAL_IP:8888/web_interface_enhanced.html"
echo "   http://$LOCAL_IP:8888/real_data_frontend.html"
echo ""
echo "🌐 公网访问提示："
if [ "$PUBLIC_IP" != "无法获取" ]; then
    echo "   当前公网 IP: $PUBLIC_IP"
    echo "   若要跨网络访问，请运行：./一键外网访问配置.sh"
else
    echo "   当前未获取到公网 IP；如需跨网络访问，请运行：./一键外网访问配置.sh"
fi

echo ""
echo "🚀 正在切换到统一主入口 ./start_real_data_system.sh ..."
echo ""

exec ./start_real_data_system.sh

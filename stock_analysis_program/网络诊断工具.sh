#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "🔍 股票分析系统网络诊断工具"
echo "=========================================="
echo ""

probe_url() {
    curl -s -o /dev/null -w "%{http_code}" "$1" 2>/dev/null || true
}

get_local_ip() {
    python3 - <<'PY'
import socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    print(sock.getsockname()[0])
    sock.close()
except Exception:
    print("无法获取")
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

check_port() {
    local port="$1"
    local service="$2"
    if lsof -i :"$port" >/dev/null 2>&1; then
        local process
        process="$(lsof -i :"$port" | grep LISTEN | head -1 | awk '{print $1}')"
        echo "   ⚠️ 端口 $port ($service) 已被占用: ${process:-未知进程}"
    else
        echo "   ✅ 端口 $port ($service) 当前可用"
    fi
}

if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ 未找到 Python3，请先安装。"
    exit 1
fi

echo "1. 检查关键文件..."
required_files=(
    "start_real_data_system.sh"
    "web_interface_enhanced.html"
    "real_data_frontend.html"
    "real_data_backend.py"
    "config.js"
)

missing=false
for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (缺失)"
        missing=true
    fi
done

if [ "$missing" = true ]; then
    echo ""
    echo "⚠️ 关键文件不完整，建议先修复文件缺失问题。"
    exit 1
fi

echo ""
echo "2. 获取网络信息..."
LOCAL_IP="$(get_local_ip)"
PUBLIC_IP="$(get_public_ip)"
echo "   📍 局域网 IP: $LOCAL_IP"
echo "   🌐 公网 IP: $PUBLIC_IP"

echo ""
echo "3. 检查互联网连接..."
if ping -c 1 -W 1 8.8.8.8 >/dev/null 2>&1; then
    echo "   ✅ 互联网连接正常"
else
    echo "   ⚠️ 互联网连接可能异常"
fi

echo ""
echo "4. 检查端口状态..."
check_port 8888 "Web 页面"
check_port 9000 "API 服务"

echo ""
echo "5. 检查本地服务可访问性..."
WEB_STATUS="$(probe_url "http://localhost:8888/web_interface_enhanced.html")"
API_STATUS="$(probe_url "http://localhost:9000/api/health")"

if [ "$WEB_STATUS" = "200" ]; then
    echo "   ✅ 本地 Web 页面可访问: http://localhost:8888/web_interface_enhanced.html"
else
    echo "   ⚠️ 本地 Web 页面当前不可访问（HTTP $WEB_STATUS）"
fi

if [ "$API_STATUS" = "200" ]; then
    echo "   ✅ 本地 API 可访问: http://localhost:9000/api/health"
else
    echo "   ⚠️ 本地 API 当前不可访问（HTTP $API_STATUS）"
fi

echo ""
echo "6. 检查防火墙状态..."
if [ "$(uname)" = "Darwin" ]; then
    firewall_state="$(/usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate 2>/dev/null | grep -o "enabled\|disabled" || true)"
    if [ "$firewall_state" = "enabled" ]; then
        echo "   ⚠️ macOS 防火墙已启用，请确认 8888 / 9000 端口已放行"
    else
        echo "   ✅ macOS 防火墙未启用，或未检测到阻断信息"
    fi
else
    echo "   ℹ️ 非 macOS 系统，请手动检查防火墙规则"
fi

echo ""
echo "📋 诊断结论"
echo "------------------------------------------"
echo "- 推荐本地 / 局域网主入口：./start_real_data_system.sh"
echo "- 如需跨网络访问：./一键外网访问配置.sh"
echo "- 诊断文档：网络访问使用指南.md"

echo ""
echo "🛠️ 下一步建议"
echo "1. 如果本地页面或 API 不通，先运行：./start_real_data_system.sh"
echo "2. 如果局域网设备打不开，检查防火墙与路由器是否允许 8888 / 9000"
echo "3. 如果要真正跨网络访问，优先用 Tailscale，或继续走 Cloudflare / 端口转发方案"

echo ""
echo "📱 参考访问地址"
echo "   本地页面:   http://localhost:8888/web_interface_enhanced.html"
echo "   局域网页面: http://$LOCAL_IP:8888/web_interface_enhanced.html"
echo "   本地 API:    http://localhost:9000/api/health"
if [ "$PUBLIC_IP" != "无法获取" ]; then
    echo "   公网参考:   http://$PUBLIC_IP:8888/web_interface_enhanced.html"
fi

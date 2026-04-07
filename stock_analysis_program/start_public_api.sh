#!/bin/bash
# ============================================================
#  🌐 公网 API 一键启动脚本
#  功能：启动后端 + 内网穿透 → 输出公网访问地址
# ============================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "🌐 智能股票分析系统 - 公网 API 启动工具"
echo "============================================"
echo ""

# ---- 1. 检查后端是否在运行 ----
BACKEND_PORT=9000
if lsof -ti:$BACKEND_PORT >/dev/null 2>&1; then
    echo "✅ 后端服务已在端口 $BACKEND_PORT 运行"
else
    echo "🔧 正在启动后端服务 (端口 $BACKEND_PORT) ..."
    # 检查 Tushare Token
    if [ -z "$TUSHARE_TOKEN" ]; then
        if [ -f ".env" ]; then
            export $(grep -v '^#' .env | xargs) 2>/dev/null || true
        fi
    fi
    if [ -n "$TUSHARE_TOKEN" ]; then
        echo "   ✅ Tushare Token: 已配置 (长度 ${#TUSHARE_TOKEN})"
    else
        echo "   ⚠️  Tushare Token: 未配置，后端将使用模拟数据"
        echo "   💡 设置方式: export TUSHARE_TOKEN=你的token"
    fi
    python3 real_data_backend.py &
    BACKEND_PID=$!
    sleep 2
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "   ✅ 后端已启动 (PID: $BACKEND_PID)"
    else
        echo "   ❌ 后端启动失败，请检查 Python 环境和依赖"
        exit 1
    fi
fi
echo ""

# ---- 2. 选择内网穿透方案 ----
TUNNEL_OPTIONS=("cloudflare" "cloudflare_named" "ngrok" "localtunnel")
TUNNEL_NAMES=("Cloudflare Quick Tunnel（临时地址，推荐快速验证）" "Cloudflare Named Tunnel（固定域名，更稳）" "ngrok (需要账号)" "localtunnel (无需注册)")

echo "📡 可用的内网穿透方案："
for i in "${!TUNNEL_OPTIONS[@]}"; do
    printf "   %d) %s\n" $((i+1)) "${TUNNEL_NAMES[$i]}"
done
echo ""
read -p "请选择方案 [1-4, 默认=1 Quick Tunnel]: " CHOICE
CHOICE=${CHOICE:-1}

case $CHOICE in
    1)
        TOOL="cloudflare"
        ;;
    2)
        TOOL="cloudflare_named"
        ;;
    3)
        TOOL="ngrok"
        ;;
    4)
        TOOL="localtunnel"
        ;;
    *)
        echo "❌ 无效选择，使用默认: cloudflare"
        TOOL="cloudflare"
        ;;
esac
echo ""

# ---- 3. 执行穿透 ----
PUBLIC_URL=""

case $TOOL in
    cloudflare)
        echo "☁️  启动 Cloudflare Quick Tunnel..."
        echo "   (首次运行会自动下载 cloudflared；此模式地址是临时的)"
        
        # 使用临时 URL 模式
        nohup npx -y cloudflared tunnel --url http://localhost:$BACKEND_PORT >/tmp/stock_cloudflared_quick.log 2>&1 &
        CF_PID=$!
        
        echo ""
        echo "⏳ 等待隧道建立 (约 5-10 秒)... "
        sleep 8
        
        # 从日志中提取 URL
        PUBLIC_URL=$(python3 - <<'PY'
import re, pathlib
path = pathlib.Path('/tmp/stock_cloudflared_quick.log')
text = path.read_text(errors='ignore') if path.exists() else ''
m = re.search(r'https://[-a-z0-9]+\.trycloudflare\.com', text)
print(m.group(0) if m else '')
PY
)
        
        if [ -z "$PUBLIC_URL" ]; then
            echo ""
            echo "📍 未自动解析到 Quick Tunnel 地址，请查看 /tmp/stock_cloudflared_quick.log"
            echo "   其中会有类似这样的地址："
            echo "   https://xxxx-xxx-xxx.trycloudflare.com"
            echo ""
            read -p "👆 手动粘贴该地址: " PUBLIC_URL
        fi
        ;;

    cloudflare_named)
        echo "☁️  启动 Cloudflare Named Tunnel（固定域名模式）..."
        CF_BIN="cloudflared"
        if ! command -v cloudflared &>/dev/null; then
            echo "   ℹ️  本机未安装 cloudflared，改用 npx 临时执行"
            CF_BIN="npx -y cloudflared"
        fi

        CF_CONFIG="${HOME}/.cloudflared/config.yml"
        if [ ! -f "$CF_CONFIG" ] && [ -f "${HOME}/.cloudflared/config.yaml" ]; then
            CF_CONFIG="${HOME}/.cloudflared/config.yaml"
        fi

        TUNNEL_NAME="${STOCK_CLOUDFLARE_TUNNEL_NAME:-stock-analysis}"
        API_HOSTNAME="${STOCK_API_HOSTNAME:-}"

        if [ -z "$API_HOSTNAME" ] && [ -f "$CF_CONFIG" ]; then
            API_HOSTNAME=$(python3 - "$CF_CONFIG" "$BACKEND_PORT" <<'PY'
import re, sys, pathlib
config_path = pathlib.Path(sys.argv[1])
port = sys.argv[2]
text = config_path.read_text(errors='ignore')
pattern = re.compile(r'-\s*hostname:\s*([^\n#]+)\s*\n\s*service:\s*http://(?:127\.0\.0\.1|localhost):' + re.escape(port))
m = pattern.search(text)
print(m.group(1).strip() if m else '')
PY
)
        fi

        if [ ! -f "$CF_CONFIG" ]; then
            echo "❌ 未找到 ~/.cloudflared/config.yml"
            echo "   固定域名模式需要先完成一次 Cloudflare 登录和命名隧道配置。"
            echo "   可先执行: cloudflared tunnel login"
            echo "   然后创建隧道并写好 config.yml 后再重试。"
            exit 1
        fi

        if [ -z "$API_HOSTNAME" ]; then
            echo "❌ 未在 $CF_CONFIG 中找到指向 localhost:$BACKEND_PORT 的 hostname"
            echo "   可通过环境变量指定，例如:"
            echo "   export STOCK_API_HOSTNAME=api.stock.example.com"
            exit 1
        fi

        echo "   ✅ 使用隧道名: $TUNNEL_NAME"
        echo "   ✅ 固定域名: https://$API_HOSTNAME"

        nohup bash -lc "$CF_BIN tunnel run '$TUNNEL_NAME'" >/tmp/stock_cloudflared_named.log 2>&1 &
        CF_NAMED_PID=$!
        sleep 5

        if kill -0 $CF_NAMED_PID 2>/dev/null; then
            PUBLIC_URL="https://$API_HOSTNAME"
        else
            echo "❌ Named Tunnel 启动失败，请查看 /tmp/stock_cloudflared_named.log"
            exit 1
        fi
        ;;
    
    ngrok)
        # 检查 ngrok 是否可用
        if ! command -v ngrok &>/dev/null; then
            echo "❌ ngrok 未安装。请先执行:"
            echo "   brew install ngrok/ngrok/ngrok"
            echo "   ngrok config add-authtoken YOUR_TOKEN"
            exit 1
        fi
        
        # 检查是否认证
        if ! ngrok config check 2>/dev/null; then
            echo "❌ ngrok 未配置 authtoken。请先:"
            echo "   1. 访问 https://dashboard.ngrok.com/signup 注册"
            echo "   2. 获取 authtoken: https://dashboard.ngrok.com/get-started/your-authtoken"
            echo "   3. 运行: ngrok config add-authtoken YOUR_TOKEN"
            exit 1
        fi
        
        echo "🚀 启动 ngrok..."
        ngrok http $BACKEND_PORT --log=stdout > /tmp/stock_ngrok.log 2>&1 &
        NGROK_PID=$!
        
        sleep 3
        
        # 从 API 获取公网 URL
        PUBLIC_URL=$(curl -s http://127.0.0.1:4040/api/tunnels 2>/dev/null | \
            python3 -c "import sys,json; print(json.load(sys.stdin)['tunnels'][0]['public_url'])" 2>/dev/null || true)
        
        if [ -z "$PUBLIC_URL" ]; then
            echo "⚠️  无法自动获取 ngrok 地址，请查看 /tmp/stock_ngrok.log"
        fi
        ;;
    
    localtunnel)
        echo "🚀 启动 localtunnel..."
        npx -y localtunnel --port $BACKEND_PORT 2>&1 &
        LT_PID=$!
        
        echo "⏳ 等待隧道建立..."
        sleep 6
        
        echo ""
        echo "📍 请在上方输出中找到 your url is: 后面的地址"
        read -p "👆 手动粘贴该地址: " PUBLIC_URL
        ;;
esac

# ---- 4. 输出结果 ----
echo ""
echo "============================================"
if [ -n "$PUBLIC_URL" ]; then
    echo "✅ 公网 API 地址:"
    echo "   🌐 $PUBLIC_URL"
    echo ""
    echo "📋 接下来的步骤："
    echo ""
    echo "   方式 A — URL 参数（快速验证）："
    echo "   在浏览器打开 GitHub Pages 地址时加上："
    echo "   ?api=$PUBLIC_URL"
    echo ""
    echo "   方式 B — 写入 config.js（永久生效）："
    echo "   编辑 config.js 的 production 字段："
    echo "   production: '$PUBLIC_URL',"
    echo ""
    echo "   方式 C — 直接访问线上前端："
    PAGES_URL="https://yanlongyue.github.io/Intelligent-stock-analysis-platform/stock_analysis_program/real_data_frontend.html"
    echo "   $PAGES_URL?api=$PUBLIC_URL"
    echo ""
    echo "============================================"
    echo ""
    echo "💡 提示: 按 Ctrl+C 停止隧道服务"
    
    # 保持脚本运行以维持隧道
    wait
else
    echo "⚠️  未能自动获取公网地址"
    echo "   请手动查看上方输出的隧道信息"
fi

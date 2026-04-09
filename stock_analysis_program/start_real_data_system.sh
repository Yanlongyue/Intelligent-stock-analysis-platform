#!/bin/bash

echo "🚀 启动真实数据股票分析系统"
echo "================================"
echo ""

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📊 Python版本: $python_version"

# 检查依赖包
echo "🔍 检查依赖包..."
pip list | grep -E "requests|pandas" || {
    echo "📦 安装依赖包..."
    pip install requests pandas --quiet
}

# MySQL 数据库配置（优先使用外部环境变量，否则使用默认值）
export MYSQL_HOST="${MYSQL_HOST:-127.0.0.1}"
export MYSQL_PORT="${MYSQL_PORT:-3306}"
export MYSQL_USER="${MYSQL_USER:-stock_user}"
export MYSQL_PASSWORD="${MYSQL_PASSWORD:-201411}"
export MYSQL_DATABASE="${MYSQL_DATABASE:-stock_analysis}"
echo "🗄️  MySQL 配置: ${MYSQL_USER}@${MYSQL_HOST}:${MYSQL_PORT}/${MYSQL_DATABASE}"

# 检查Tushare Token
if [ -z "$TUSHARE_TOKEN" ]; then
    echo "⚠️  警告: 未设置Tushare Pro API Token"
    echo "💡 提示: 设置环境变量 TUSHARE_TOKEN 以使用真实数据"
    echo "🔗 获取Token: https://tushare.pro/"
    echo "📝 当前使用模拟数据模式"
    echo ""
    echo "📌 临时设置Token方法:"
    echo "   export TUSHARE_TOKEN=你的token"
    echo ""
else
    echo "✅ Tushare Token已配置"
fi

# 创建启动目录
cd "$(dirname "$0")"

resolve_github_pages_url() {
    local remote_url slug owner repo
    remote_url="$(git config --get remote.github.url 2>/dev/null || true)"

    if [ -z "$remote_url" ]; then
        return 1
    fi

    slug="$(printf '%s' "$remote_url" | sed -E 's#^git@github\.com:##; s#^https?://([^@/]+@)?github\.com/##; s#\.git$##')"
    owner="$(printf '%s' "$slug" | cut -d'/' -f1 | tr '[:upper:]' '[:lower:]')"
    repo="$(printf '%s' "$slug" | cut -d'/' -f2)"

    if [ -n "$owner" ] && [ -n "$repo" ]; then
        printf 'https://%s.github.io/%s' "$owner" "$repo"
        return 0
    fi

    return 1
}

GITHUB_PAGES_URL="$(resolve_github_pages_url || true)"

echo ""
echo "📡 启动服务..."
echo ""

# 启动真实数据后端服务
echo "🎯 启动真实数据后端服务 (端口: 9000)"
python3 real_data_backend.py &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动Web服务器
echo "🌐 启动Web界面服务器 (端口: 8888)"
python3 -m http.server 8888 --bind 0.0.0.0 &
WEB_PID=$!

# 显示状态
echo ""
echo "✅ 系统启动完成!"
echo ""
echo "📌 服务状态:"
echo "   🔹 真实数据后端: http://localhost:9000/api/health"
echo "   🔹 真实数据页面: http://localhost:8888/real_data_frontend.html"
echo "   🔹 增强版页面: http://localhost:8888/web_interface_enhanced.html"
echo ""
if [ -n "$GITHUB_PAGES_URL" ]; then
    echo "📌 GitHub Pages在线版本:"
    echo "   🔹 ${GITHUB_PAGES_URL}/web_interface_enhanced.html"
    echo "   🔹 ${GITHUB_PAGES_URL}/real_data_frontend.html"
    echo ""
fi
echo "📌 可用API端点:"
echo "   🔸 GET /api/health          - 健康检查"
echo "   🔸 GET /api/positions       - 获取持仓数据"
echo "   🔸 GET /api/analyze/<code>  - 分析指定股票"
echo "   🔸 GET /api/analyze_all     - 分析所有持仓"
echo "   🔸 GET /api/price_history/<code> - 获取价格历史"
echo "   🔸 GET /api/update_prices   - 更新价格缓存"
echo "   🔸 GET /api/market_overview - 获取市场概况"
echo "   🔸 GET /api/data_status     - 获取数据状态"
echo "   🔸 GET /api/db_stats        - 查看数据库存储统计"
echo ""
echo "🔄 按 Ctrl+C 停止所有服务"

# 捕获Ctrl+C信号
trap 'echo ""; echo "🛑 停止服务..."; kill $BACKEND_PID $WEB_PID 2>/dev/null; exit 0' INT

# 等待
wait $BACKEND_PID $WEB_PID
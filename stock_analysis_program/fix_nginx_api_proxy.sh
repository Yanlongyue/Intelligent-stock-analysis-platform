#!/bin/bash
# ============================================================
# 一键修复：为宝塔站点添加 /api 反向代理到后端 9000 端口
# 用途：为宝塔站点添加 /api 反向代理到后端 9000 端口
# 让浏览器通过 Nginx 同源端口(80)访问 API，无需暴露后端端口
# ============================================================

set -e

echo "============================================="
echo "🔧 开始配置 Nginx /api 反向代理..."
echo "============================================="

# 1. 找到当前站点的 Nginx 配置文件
NGINX_CONF_DIR="/www/server/panel/vhost/nginx"
CONF_FILE=""

# 搜索包含 stock_analysis 或 Intelligent-stock 或 80 端口的配置
for f in "$NGINX_CONF_DIR"/*.conf; do
    if grep -q "stock_analysis\|Intelligent-stock\|101.133.150.164" "$f" 2>/dev/null; then
        CONF_FILE="$f"
        echo "✅ 找到站点配置: $f"
        break
    fi
done

if [ -z "$CONF_FILE" ]; then
    # 备选：找宝塔默认站点的配置
    CONF_FILE=$(grep -rl "stock_analysis\|Intelligent-stock\|101.133.150.164" "$NGINX_CONF_DIR/" 2>/dev/null | head -1)
    if [ -n "$CONF_FILE" ]; then
        echo "✅ 通过端口搜索找到配置: $CONF_FILE"
    fi
fi

if [ -z "$CONF_FILE" ]; then
    echo "❌ 未找到股票分析站点的 Nginx 配置文件"
    echo "请手动检查: ls $NGINX_CONF_DIR/"
    exit 1
fi

# 显示当前配置文件名和路径
echo ""
echo "📋 配置文件内容摘要:"
grep -n "listen\|server_name\|root\|location" "$CONF_FILE" | head -20

# 2. 检查是否已有 /api/ 代理配置
if grep -q "location /api/" "$CONF_FILE"; then
    echo ""
    echo "⚠️ 已存在 /api/ 代理配置，检查是否正确..."
    grep -A5 "location /api/" "$CONF_FILE"
    echo ""
    read -p "是否重新覆盖？(y/N): " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
        echo "跳过修改。请手动确认 proxy_pass 指向 127.0.0.1:9000"
        exit 0
    fi
fi

# 3. 备份原配置
BACKUP="${CONF_FILE}.bak.$(date +%Y%m%d%H%M%S)"
cp "$CONF_FILE" "$BACKUP"
echo ""
echo "📦 已备份原配置到: $BACKUP"

# 4. 在配置文件的最后一个 } 之前插入 /api/ 反代规则
# 使用 sed 在 server 块的结束大括号前插入

PYTHON_SCRIPT=$(cat << 'PYEOF'
import sys

conf_file = sys.argv[1]

with open(conf_file, 'r') as f:
    content = f.read()

api_block = """

    # ============ API 反向代理（股票分析后端）============
    location = /api {
        return 301 /api/;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:9000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;
        proxy_buffering off;
    }
    # ============ API 反向代理结束 =====================
"""

# 找到最后一个 server 块的结尾 } 并在它前面插入
import re
# 匹配 server 块的最后一个关闭括号（通常是文件末尾的独立行或缩进行）
last_brace = content.rfind('}')
if last_brace != -1:
    # 检查这个 } 是否是 server 块的一部分（简单判断：后面没有太多内容）
    new_content = content[:last_brace] + api_block + content[last_brace:]
    
    with open(conf_file, 'w') as f:
        f.write(new_content)
    print("✅ 已添加 /api/ 反向代理配置")
else:
    print("❌ 无法找到配置文件结构，请手动编辑")
    sys.exit(1)
PYEOF
)

python3 -c "$PYTHON_SCRIPT" "$CONF_FILE"

# 5. 测试 Nginx 配置语法
echo ""
echo "🔍 测试 Nginx 配置语法..."
if nginx -t 2>&1; then
    echo "✅ Nginx 配置语法正确"
else
    echo "❌ Nginx 配置有误！已自动恢复备份..."
    cp "$BACKUP" "$CONF_FILE"
    exit 1
fi

# 6. 重载 Nginx
echo ""
echo "🔄 重载 Nginx..."
nginx -s reload 2>&1 && echo "✅ Nginx 重载成功"

# 7. 验证反代是否生效
echo ""
echo "🧪 验证反向代理..."
sleep 1

# 通过 80 端口（Nginx）测试 /api/health
if curl -s --connect-timeout 5 "http://127.0.0.1/api/health" | grep -q "healthy"; then
    echo "✅ 反向代理验证通过！(localhost/api/health → 后端)"
else
    echo "⚠️ localhost 验证未通过，尝试公网验证..."
fi

# 通过公网 IP 测试（Nginx 80端口）
echo ""
echo "📡 公网验证（通过 Nginx 80 端口）:"
curl -s --connect-timeout 10 "http://101.133.150.164/api/health" || echo "❌ 公网访问失败（可能安全组未放行 80 入站或 Nginx 未配置）"

echo ""
echo "============================================="
echo "🎉 修复完成！"
echo "============================================="
echo ""
echo "下一步操作："
echo "1. 打开浏览器访问: http://101.133.150.164/"
echo "2. 按 Ctrl+Shift+R 强制刷新"
echo "3. 查看「操作建议」列是否有内容"
echo ""
echo "如需回滚: cp $BACKUP $CONF_FILE && nginx -s reload"
echo "============================================="

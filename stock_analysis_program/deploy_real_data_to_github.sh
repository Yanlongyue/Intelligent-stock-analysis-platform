#!/bin/bash
set -e

echo "🚀 准备 GitHub Pages 部署文件"
echo "================================"
echo ""

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEPLOY_DIR="$REPO_ROOT/deploy_real_data"

cd "$SCRIPT_DIR"

if [ ! -f "$SCRIPT_DIR/real_data_frontend.html" ]; then
    echo "❌ 错误: 请在 stock_analysis_program 目录中运行此脚本"
    exit 1
fi

if ! git -C "$REPO_ROOT" status &> /dev/null; then
    echo "❌ 错误: 当前项目不是 Git 仓库"
    exit 1
fi

resolve_github_slug() {
    local remote_url slug

    remote_url="$(git -C "$REPO_ROOT" config --get remote.github.url 2>/dev/null || true)"
    if [ -z "$remote_url" ]; then
        remote_url="$(git -C "$REPO_ROOT" remote -v 2>/dev/null | grep 'github.com' | awk 'NR==1 {print $2}')"
    fi

    if [ -z "$remote_url" ]; then
        return 1
    fi

    slug="$(printf '%s' "$remote_url" | sed -E 's#^git@github\.com:##; s#^https?://([^@/]+@)?github\.com/##; s#\.git$##')"
    printf '%s' "$slug"
}

GITHUB_SLUG="$(resolve_github_slug || true)"
if [ -n "$GITHUB_SLUG" ]; then
    GITHUB_OWNER="$(printf '%s' "$GITHUB_SLUG" | cut -d'/' -f1 | tr '[:upper:]' '[:lower:]')"
    GITHUB_REPO="$(printf '%s' "$GITHUB_SLUG" | cut -d'/' -f2)"
    GITHUB_WEB_URL="https://github.com/${GITHUB_SLUG}"
    GITHUB_REPO_URL="https://github.com/${GITHUB_SLUG}.git"
    PAGES_BASE="https://${GITHUB_OWNER}.github.io/${GITHUB_REPO}"
    ONLINE_HINT="已自动识别 GitHub Pages 地址：${PAGES_BASE}"
else
    GITHUB_WEB_URL="https://github.com/<your-account>/<your-repo>"
    GITHUB_REPO_URL="https://github.com/<your-account>/<your-repo>.git"
    PAGES_BASE=""
    ONLINE_HINT="未检测到 GitHub 远程；请先添加 github remote，再重新运行脚本生成准确链接。"
fi

if [ -n "$PAGES_BASE" ]; then
    REAL_DATA_URL="${PAGES_BASE}/real_data_frontend.html"
    ENHANCED_URL="${PAGES_BASE}/web_interface_enhanced.html"
    ROOT_URL="${PAGES_BASE}/"
else
    REAL_DATA_URL=""
    ENHANCED_URL=""
    ROOT_URL=""
fi

echo "📁 重建部署目录: $DEPLOY_DIR"
rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

echo "📋 复制部署文件..."
cp "$SCRIPT_DIR/real_data_frontend.html" "$DEPLOY_DIR/"
cp "$SCRIPT_DIR/web_interface_enhanced.html" "$DEPLOY_DIR/"
cp "$SCRIPT_DIR/config.js" "$DEPLOY_DIR/"
cp "$SCRIPT_DIR/TUSHARE_TOKEN配置指南.md" "$DEPLOY_DIR/"

if [ -f "$SCRIPT_DIR/index.html" ]; then
    cp "$SCRIPT_DIR/index.html" "$DEPLOY_DIR/"
fi

echo "📝 生成部署说明..."
cat > "$DEPLOY_DIR/README.md" <<EOF
# 🎯 智能股票分析系统 - Pages 部署包

基于真实金融数据的五维度算法评分平台，前端可部署到 GitHub Pages，后端通过独立 API 提供真实数据。

## 🌐 在线访问

- 增强版页面：${ENHANCED_URL:-请先配置 GitHub Pages 地址}
- 真实数据页：${REAL_DATA_URL:-请先配置 GitHub Pages 地址}
- 站点首页：${ROOT_URL:-请先配置 GitHub Pages 地址}

> ${ONLINE_HINT}

## 📦 本次部署包含

- \\`web_interface_enhanced.html\\`：增强版主界面
- \\`real_data_frontend.html\\`：真实数据专用页面
- \\`config.js\\`：统一 API 配置入口
- \\`TUSHARE_TOKEN配置指南.md\\`：Token 配置说明

## 🔧 真实数据配置

1. 后端机器设置环境变量：\\`export TUSHARE_TOKEN=你的token\\`
2. 启动后端 API 服务：\\`python3 real_data_backend.py\\`
3. 在 \\`config.js\\` 中填写公网可访问的 \\`production\\` 地址
4. 或通过页面参数临时指定：\\`?api=https://你的后端地址\\`

## 🧪 本地预览

### 启动后端

\\`\\`\\`bash
cd stock_analysis_program
python3 real_data_backend.py
\\`\\`\\`

### 启动静态页面

\\`\\`\\`bash
cd stock_analysis_program
python3 -m http.server 8888 --bind 0.0.0.0
\\`\\`\\`

### 访问地址

- 增强版页面：http://localhost:8888/web_interface_enhanced.html
- 真实数据页：http://localhost:8888/real_data_frontend.html
- API 健康检查：http://localhost:9000/api/health

## 🚀 推送步骤

将部署目录内容推送到你的 GitHub Pages 仓库：

\\`\\`\\`bash
cd "$DEPLOY_DIR"
git init
git add .
git commit -m "准备 Pages 部署文件"
git remote add origin ${GITHUB_REPO_URL}
git branch -M main
git push -u origin main
\\`\\`\\`

## ⚠️ 注意事项

- GitHub Pages 只负责托管静态前端，**不会**运行 Python 后端。
- 未配置公网 API 时，页面会自动退回模拟数据模式。
- 不要把 Tushare Token 写进代码或提交到 Git 仓库。
EOF

echo "🔗 生成跳转页面..."
cat > "$DEPLOY_DIR/real_data_index.html" <<EOF
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>智能股票分析系统 - 真实数据版</title>
    <meta http-equiv="refresh" content="0; url=real_data_frontend.html">
    <style>
        body {
            font-family: 'Microsoft YaHei', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            text-align: center;
        }
        .container {
            max-width: 640px;
            padding: 40px;
            background: rgba(255,255,255,0.12);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        .spinner {
            border: 4px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top: 4px solid white;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        a {
            color: white;
            text-decoration: underline;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="spinner"></div>
        <h1>🎯 智能股票分析系统</h1>
        <p>正在跳转到真实数据页面...</p>
        <p>如果未自动跳转，请<a href="real_data_frontend.html">点击这里</a></p>
        <p style="margin-top: 24px; opacity: 0.85;">增强版页面：<a href="web_interface_enhanced.html">web_interface_enhanced.html</a></p>
    </div>
</body>
</html>
EOF

echo "📚 生成项目结构说明..."
cat > "$DEPLOY_DIR/project_structure.md" <<EOF
# 📁 部署目录结构

\\`\\`\\`
deploy_real_data/
├── config.js
├── real_data_frontend.html
├── real_data_index.html
├── web_interface_enhanced.html
├── README.md
├── TUSHARE_TOKEN配置指南.md
└── project_structure.md
\\`\\`\\`

## 文件说明

- \\`config.js\\`：统一管理本地/公网 API 地址
- \\`real_data_frontend.html\\`：简化版真实数据页面
- \\`web_interface_enhanced.html\\`：增强版主界面
- \\`README.md\\`：部署与配置说明
- \\`TUSHARE_TOKEN配置指南.md\\`：Token 配置教程

## 相关链接

- GitHub 仓库：${GITHUB_WEB_URL}
- GitHub Pages：${ROOT_URL:-请先配置 GitHub Pages 地址}
EOF

echo ""
echo "✅ 部署文件准备完成！"
echo "📦 输出目录: $DEPLOY_DIR"
if [ -n "$PAGES_BASE" ]; then
    echo "🌐 预期在线地址: $ENHANCED_URL"
else
    echo "⚠️  尚未检测到 GitHub 远程，README 中已保留占位说明。"
fi

echo ""
echo "📋 下一步建议："
echo "1. 检查 deploy_real_data/ 中的 config.js 和两个 HTML 页面"
echo "2. 将该目录内容推送到 GitHub Pages 对应仓库"
echo "3. 配置公网后端 API 后，再访问线上页面验证真实数据"

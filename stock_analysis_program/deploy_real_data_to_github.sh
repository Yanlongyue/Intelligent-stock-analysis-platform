#!/bin/bash

echo "🚀 部署真实数据股票分析系统到GitHub Pages"
echo "=========================================="
echo ""

# 检查是否在项目目录
if [ ! -f "real_data_frontend.html" ]; then
    echo "❌ 错误: 请在 stock_analysis_program 目录中运行此脚本"
    exit 1
fi

# 检查Git状态
if ! git status &> /dev/null; then
    echo "❌ 错误: 当前目录不是Git仓库"
    exit 1
fi

# 创建部署目录
DEPLOY_DIR="../deploy_real_data"
echo "📁 创建部署目录: $DEPLOY_DIR"
rm -rf "$DEPLOY_DIR"
mkdir -p "$DEPLOY_DIR"

# 复制必要文件
echo "📋 复制文件..."
cp real_data_frontend.html "$DEPLOY_DIR/"
cp index.html "$DEPLOY_DIR/"
cp "TUSHARE_TOKEN配置指南.md" "$DEPLOY_DIR/"

# 创建GitHub Pages配置
echo "📝 创建GitHub Pages配置..."
cat > "$DEPLOY_DIR/README.md" << 'EOF'
# 🎯 智能股票分析系统 - 真实数据版

基于真实金融数据的五维度算法评分平台。

## 🌐 在线访问

访问地址：https://yanlongyue.github.io/Intelligent-stock-analysis-platform/real_data_frontend.html

## 📊 系统功能

- **真实数据接入**：通过Tushare Pro API获取实时金融数据
- **五维度算法**：国际局势、国内政策、企业发展、技术分析、市场情绪
- **持仓管理**：实时监控持仓盈亏
- **市场概况**：主要指数、市场情绪、资金流向
- **风险预警**：基于算法评分的风险等级评估

## 🔧 数据配置

要使用真实数据，需要配置Tushare Pro API Token。

详细配置指南：[TUSHARE_TOKEN配置指南.md](TUSHARE_TOKEN配置指南.md)

## 📱 使用说明

1. **访问在线版本**：直接通过浏览器访问
2. **配置API Token**：设置Tushare Token以获取真实数据
3. **启动本地服务**：如需完整功能，可启动本地后端服务

## 🚀 本地开发

### 启动后端服务
```bash
cd stock_analysis_program
python3 real_data_backend.py
```

### 启动Web界面
```bash
python3 -m http.server 8888 --bind localhost
```

### 访问地址
- Web界面: http://localhost:8888/real_data_frontend.html
- API服务: http://localhost:9000/api/health

## 📞 技术支持

如有问题，请参考项目文档或联系开发者。

---

**注意**：GitHub Pages版本为前端静态页面，真实数据需要配置Tushare Token并启动本地后端服务。
EOF

# 创建访问重定向
echo "🔗 创建访问重定向..."
cat > "$DEPLOY_DIR/real_data_index.html" << 'EOF'
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
            max-width: 600px;
            padding: 40px;
            background: rgba(255,255,255,0.1);
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        h1 {
            font-size: 2.5rem;
            margin-bottom: 20px;
        }
        p {
            font-size: 1.2rem;
            margin-bottom: 30px;
            opacity: 0.9;
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
        <p>正在跳转到真实数据版本...</p>
        <p>如果未自动跳转，请<a href="real_data_frontend.html">点击这里</a></p>
        <p style="margin-top: 30px; font-size: 0.9rem; opacity: 0.7;">
            数据模式：真实数据接入 | 版本：v2.0
        </p>
    </div>
</body>
</html>
EOF

# 创建项目结构说明
cat > "$DEPLOY_DIR/project_structure.md" << 'EOF'
# 📁 项目结构

```
deploy_real_data/
├── real_data_frontend.html     # 真实数据前端界面
├── real_data_index.html        # 重定向页面
├── index.html                  # 主页面重定向
├── README.md                   # 项目说明
├── TUSHARE_TOKEN配置指南.md    # API配置指南
└── project_structure.md        # 本文档
```

## 📄 文件说明

### real_data_frontend.html
- 真实数据版前端界面
- 连接到本地后端API服务 (http://localhost:9000)
- 支持真实数据/模拟数据切换

### TUSHARE_TOKEN配置指南.md
- Tushare Pro API Token配置说明
- API接口列表和使用方法
- 常见问题解答

## 🔗 相关链接

- **GitHub仓库**: https://github.com/Yanlongyue/Intelligent-stock-analysis-platform
- **在线访问**: https://yanlongyue.github.io/Intelligent-stock-analysis-platform/
- **真实数据版**: https://yanlongyue.github.io/Intelligent-stock-analysis-platform/real_data_frontend.html
EOF

echo ""
echo "✅ 部署文件准备完成！"
echo ""

# 显示下一步操作
echo "📋 下一步操作："
echo "1. 将部署目录推送到GitHub:"
echo ""
echo "   cd $DEPLOY_DIR"
echo "   git init"
echo "   git add ."
echo "   git commit -m \"部署真实数据版本\""
echo "   git remote add origin https://github.com/Yanlongyue/Intelligent-stock-analysis-platform.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "2. 或复制文件到现有仓库:"
echo ""
echo "   cp -r $DEPLOY_DIR/* /Users/yandada/WorkBuddy/Claw/"
echo "   cd /Users/yandada/WorkBuddy/Claw"
echo "   git add ."
echo "   git commit -m \"添加真实数据版本\""
echo "   git push"
echo ""
echo "3. GitHub Pages会自动构建，访问地址："
echo "   https://yanlongyue.github.io/Intelligent-stock-analysis-platform/real_data_frontend.html"
echo ""

# 可选：直接复制到项目根目录
read -p "是否直接复制到项目根目录并推送到GitHub? (y/N): " choice
if [[ $choice =~ ^[Yy]$ ]]; then
    echo "📤 复制文件到项目根目录..."
    cp -r "$DEPLOY_DIR"/* /Users/yandada/WorkBuddy/Claw/
    
    echo "🔗 推送到GitHub..."
    cd /Users/yandada/WorkBuddy/Claw
    git add real_data_frontend.html real_data_index.html "TUSHARE_TOKEN配置指南.md" README.md project_structure.md
    
    if git commit -m "添加真实数据版本股票分析系统"; then
        git push
        echo ""
        echo "🎉 部署成功！"
        echo "🌐 访问地址: https://yanlongyue.github.io/Intelligent-stock-analysis-platform/real_data_frontend.html"
    else
        echo "⚠️  没有文件变更，跳过提交"
    fi
fi

echo ""
echo "📝 部署完成！"
echo "💡 提示: 真实数据需要配置Tushare Token并启动本地后端服务"
#!/bin/bash
# 启动股票分析可视化界面脚本
# 作者: 风暴 🌪️
# 创建时间: 2026年4月2日

echo "================================================"
echo "🚀 启动七步法股票分析可视化界面"
echo "================================================"

# 检查Python版本
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📊 Python版本: $python_version"

# 检查是否在正确的目录
if [ ! -f "gui_launcher.py" ]; then
    echo "❌ 错误: 请在 stock_analysis_program 目录下运行此脚本"
    echo "当前目录: $(pwd)"
    exit 1
fi

# 检查依赖
echo "🔍 检查依赖..."
if ! python3 -c "import tkinter" 2>/dev/null; then
    echo "⚠️ 警告: tkinter未安装，界面可能无法正常工作"
fi

if ! python3 -c "import psutil" 2>/dev/null; then
    echo "📦 安装psutil..."
    pip install psutil
fi

# 创建必要的目录
echo "📁 创建目录结构..."
mkdir -p reports/html
mkdir -p reports/markdown
mkdir -p config
mkdir -p logs
mkdir -p data

# 检查配置文件
if [ ! -f "config/position_config.py" ]; then
    echo "⚠️ 警告: 持仓配置文件不存在，使用默认配置"
fi

# 启动可视化界面
echo "🎨 启动可视化界面..."
echo "💡 提示: 界面加载可能需要几秒钟"

# 运行主程序
python3 gui_launcher.py

echo "================================================"
echo "👋 程序已退出"
echo "================================================"
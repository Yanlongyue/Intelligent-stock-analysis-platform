#!/bin/bash
# 启动增强版股票分析系统 - 简化版

echo "========================================"
echo "🎯 智能股票分析系统 - 五维度算法版"
echo "========================================"
echo ""

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 需要Python3，但未找到"
    exit 1
fi

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 显示系统信息
echo "📊 系统配置:"
echo "  • Python版本: $(python3 --version | cut -d' ' -f2)"
echo "  • 工作目录: $(pwd)"
echo "  • HTML界面: web_interface_enhanced.html"
echo "  • 算法引擎: algorithm_backend.py"
echo ""

# 同时启动Web界面和API服务
echo "🚀 同时启动Web界面和API服务..."
echo ""

# 启动API服务（后台）
echo "启动算法API服务 (端口: 9000)..."
python3 algorithm_backend.py &
API_PID=$!
echo "API服务PID: $API_PID"
echo ""

# 等待API服务启动
echo "等待API服务启动..."
sleep 3

# 检查API服务状态
if curl -s http://localhost:9000/api/health > /dev/null; then
    echo "✅ API服务启动成功"
else
    echo "⚠️ API服务启动异常，但继续启动Web界面"
fi

echo ""

# 启动Web界面
echo "启动Web界面 (端口: 8888)..."
echo ""
python3 run_enhanced_web.py

# 如果Web界面退出，也停止API服务
echo ""
echo "正在停止API服务..."
kill $API_PID 2>/dev/null
wait $API_PID 2>/dev/null

echo ""
echo "========================================"
echo "👋 系统已停止，感谢使用！"
echo "========================================"
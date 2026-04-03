#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================"
echo "🎯 智能股票分析系统 - 演示模式（兼容入口）"
echo "========================================"
echo ""
echo "ℹ️  旧的增强版启动脚本已经收口到统一演示入口。"
echo "ℹ️  推荐使用：./start_enhanced_system.sh"
echo "ℹ️  如需真实数据，请运行：./start_real_data_system.sh"
echo ""
echo "🚀 现在转到统一演示入口 ./start_enhanced_system.sh ..."
echo ""

exec ./start_enhanced_system.sh

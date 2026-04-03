#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "================================================"
echo "🎨 七步法股票分析可视化界面（兼容入口）"
echo "================================================"
echo ""
echo "ℹ️  旧的可视化入口已经收口到统一 Web 主入口。"
echo "ℹ️  推荐使用：./start_real_data_system.sh"
echo "ℹ️  如果只想看演示模式，请运行：./start_enhanced_system.sh"
echo "ℹ️  如果仍要打开旧版桌面 GUI，请运行：./启动完整GUI.sh 并选择兼容模式"
echo ""
echo "🚀 现在转到统一主入口 ./start_real_data_system.sh ..."
echo ""

exec ./start_real_data_system.sh

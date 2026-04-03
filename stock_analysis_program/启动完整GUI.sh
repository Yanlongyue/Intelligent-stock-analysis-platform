#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "=========================================="
echo "股票分析入口导航（兼容启动器）"
echo "=========================================="
echo ""
echo "请选择启动方式："
echo ""
echo "1. 🌐 真实数据 Web 主入口（推荐）"
echo "2. 🖥️  命令行七步法分析"
echo "3. 🎨 兼容旧版桌面 GUI（维护模式）"
echo "4. 📖 查看使用指南"
echo "5. ❌ 退出"
echo ""
echo "=========================================="

read -p "请选择 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🌐 启动真实数据 Web 主入口..."
        echo ""
        ./start_real_data_system.sh
        ;;
    2)
        echo ""
        echo "🖥️ 启动命令行七步法分析..."
        echo ""
        ./start.sh analyze
        ;;
    3)
        echo ""
        echo "🎨 启动兼容旧版桌面 GUI..."
        echo "⚠️  该模式仅为兼容保留，不再作为默认入口"
        echo ""
        python3 run_complete_gui.py
        ;;
    4)
        echo ""
        echo "📖 打开使用指南..."
        echo ""
        if command -v open >/dev/null 2>&1; then
            open 完整GUI使用指南.md
        elif command -v xdg-open >/dev/null 2>&1; then
            xdg-open 完整GUI使用指南.md
        else
            echo "无法自动打开指南，请手动查看：完整GUI使用指南.md"
        fi
        ;;
    5)
        echo ""
        echo "感谢使用！再见！"
        echo ""
        exit 0
        ;;
    *)
        echo ""
        echo "无效选择，程序退出"
        echo ""
        exit 1
        ;;
esac

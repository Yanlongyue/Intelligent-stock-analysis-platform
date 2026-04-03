#!/bin/bash
# 股票分析完整GUI启动脚本
# 作者：风暴 🌪️

cd "$(dirname "$0")"

echo "=========================================="
echo "股票分析专业版 GUI 启动器"
echo "=========================================="
echo ""
echo "请选择GUI模式："
echo ""
echo "1. 🌐 Web界面 (推荐) - 在浏览器中运行"
echo "2. 🖥️  终端界面 - 在终端中运行"
echo "3. 🎨 完整GUI (macOS可能需要特殊配置)"
echo "4. 📖 查看使用指南"
echo "5. ❌ 退出"
echo ""
echo "=========================================="

read -p "请选择 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🌐 启动Web界面..."
        echo "将在浏览器中打开 http://localhost:8888"
        echo ""
        python3 run_web_interface.py
        ;;
    2)
        echo ""
        echo "🖥️  启动终端界面..."
        echo ""
        python3 terminal_gui.py
        ;;
    3)
        echo ""
        echo "🎨 启动完整GUI..."
        echo "注意：macOS版本可能需要特殊配置"
        echo ""
        python3 run_complete_gui.py
        ;;
    4)
        echo ""
        echo "📖 打开使用指南..."
        echo ""
        if command -v open &> /dev/null; then
            open 完整GUI使用指南.md
        elif command -v xdg-open &> /dev/null; then
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
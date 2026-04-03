#!/bin/bash
# 启动增强版股票分析系统
# 包含五维度算法评分系统和完善的管理功能

echo "=========================================="
echo "🎯 智能股票分析系统 - 五维度算法版"
echo "=========================================="
echo ""

# 检查Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 需要Python3，但未找到"
    exit 1
fi

# 检查必要文件
REQUIRED_FILES=(
    "web_interface_enhanced.html"
    "run_enhanced_web.py"
    "algorithm_backend.py"
    "algorithm_config.py"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 错误: 找不到文件 $file"
        exit 1
    fi
done

echo "✅ 所有必要文件已找到"
echo ""

# 显示系统信息
echo "📊 系统配置:"
echo "  • Python版本: $(python3 --version | cut -d' ' -f2)"
echo "  • 工作目录: $(pwd)"
echo "  • HTML界面: web_interface_enhanced.html"
echo "  • 算法引擎: algorithm_backend.py"
echo ""

# 选择启动模式
echo "🚀 请选择启动模式:"
echo "  1) 只启动Web界面 (推荐)"
echo "  2) 只启动算法API服务"
echo "  3) 同时启动Web界面和API服务"
echo "  4) 查看使用说明"
echo ""

read -p "请输入选项 (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🌐 启动Web界面..."
        python3 run_enhanced_web.py
        ;;
    2)
        echo ""
        echo "🧠 启动算法API服务..."
        echo "API服务将在端口 9000 启动（模拟数据）"
        echo "如需打开界面，请另一个终端运行: python3 run_enhanced_web.py"
        echo "界面地址: http://localhost:8888/web_interface_enhanced.html"
        python3 algorithm_backend.py
        ;;
    3)
        echo ""
        echo "🚀 同时启动Web界面和API服务..."
        
        # 启动API服务（后台）
        echo "启动算法API服务 (端口: 9000)..."
        python3 algorithm_backend.py &
        API_PID=$!
        echo "API服务PID: $API_PID"
        
        # 等待API服务启动
        sleep 2
        
        # 启动Web界面
        echo "启动Web界面 (端口: 8888)..."
        python3 run_enhanced_web.py
        
        # 如果Web界面退出，也停止API服务
        kill $API_PID 2>/dev/null
        ;;
    4)
        echo ""
        echo "📖 使用说明:"
        echo "=========================================="
        echo "🎯 智能股票分析系统 - 五维度算法版"
        echo "=========================================="
        echo ""
        echo "🌟 核心功能:"
        echo "  1. 五维度智能算法评分系统"
        echo "     • 国际局势算法 (权重: 20%)"
        echo "     • 国内政策算法 (权重: 20%)"
        echo "     • 企业发展异动算法 (权重: 25%)"
        echo "     • 技术侧分析算法 (权重: 20%)"
        echo "     • 股民情绪算法 (权重: 15%)"
        echo ""
        echo "  2. 可视化界面功能"
        echo "     • 实时KPI数据看板"
        echo "     • 交互式股价走势图表"
        echo "     • 完善的持仓管理系统"
        echo "     • 小时级股价区间预测"
        echo "     • 算法参数可视化配置"
        echo ""
        echo "  3. 管理功能"
        echo "     • 添加/删除持仓股票"
        echo "     • 修改持仓数量"
        echo "     • 仓位再平衡建议"
        echo "     • 风险等级评估"
        echo "     • 投资报告生成"
        echo ""
        echo "🌐 访问方式:"
        echo "  • Web界面: http://localhost:8888/web_interface_enhanced.html"
        echo "  • API服务: http://localhost:9000/api/health"
        echo ""
        echo "⚙️ 配置文件:"
        echo "  • algorithm_config.py - 算法参数配置"
        echo "  • algorithm_backend.py - 算法引擎"
        echo "  • web_interface_enhanced.html - Web界面"
        echo ""
        echo "💡 使用技巧:"
        echo "  1. 首次使用建议选择选项3（同时启动）"
        echo "  2. 界面支持响应式设计，适配各种设备"
        echo "  3. 所有数据都可以导出为HTML报告"
        echo "  4. 算法评分会随市场变化动态更新"
        echo ""
        echo "⚠️ 注意事项:"
        echo "  • 这是本地演示系统，数据为模拟数据"
        echo "  • 实际投资需要结合更多信息"
        echo "  • 算法结果仅供参考"
        echo ""
        echo "📞 支持:"
        echo "  • 按Ctrl+C停止所有服务"
        echo "  • 查看日志文件了解运行状态"
        echo "  • 配置参数可在algorithm_config.py中修改"
        echo ""
        ;;
    *)
        echo "❌ 无效选项，请重新运行脚本"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "👋 感谢使用智能股票分析系统！"
echo "=========================================="
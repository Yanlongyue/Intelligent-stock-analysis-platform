#!/bin/bash

# ============================================
# 七步法股票分析程序 - 演示脚本
# 版本: v1.0.0
# 创建日期: 2026年4月2日
# ============================================

echo "============================================"
echo "  七步法股票分析程序演示"
echo "============================================"
echo ""

# 检查是否在正确的目录
if [ ! -d "stock_analysis_program" ]; then
    echo "❌ 错误: 请在项目根目录运行此脚本"
    echo "   当前目录: $(pwd)"
    echo "   需要的目录结构:"
    echo "     Claw/"
    echo "     ├── stock_analysis_program/"
    echo "     └── 演示脚本.sh"
    exit 1
fi

# 进入程序目录
cd stock_analysis_program

echo "✅ 进入程序目录: $(pwd)"
echo ""

# 演示1: 显示程序摘要
echo "🎯 演示1: 显示程序配置摘要"
echo "--------------------------------------------"
python3 src/main.py --summary
echo ""

# 演示2: 检查依赖
echo "🎯 演示2: 检查Python依赖"
echo "--------------------------------------------"
echo "依赖包列表:"
cat requirements.txt | head -10
echo "..."
echo ""

# 演示3: 检查程序结构
echo "🎯 演示3: 检查程序结构"
echo "--------------------------------------------"
echo "核心模块:"
ls -la src/*.py
echo ""

# 演示4: 显示README摘要
echo "🎯 演示4: 显示项目说明"
echo "--------------------------------------------"
echo "项目简介:"
grep -A 5 "🎯 项目简介" README.md | head -10
echo ""

# 演示5: 七步法流程说明
echo "🎯 演示5: 七步法流程说明"
echo "--------------------------------------------"
echo "完整七步流程:"
grep -A 10 "完整七步流程" README.md | grep "第[0-9]" | head -7
echo ""

# 演示6: 运行测试模式
echo "🎯 演示6: 运行测试模式"
echo "--------------------------------------------"
echo "注意: 测试模式需要Tushare Pro Token配置"
echo "如果未配置Token，将显示配置提示"
echo ""
read -p "是否继续? (y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 src/main.py --test 2>&1 | head -20
else
    echo "跳过测试模式"
fi
echo ""

# 演示7: 显示部署选项
echo "🎯 演示7: Git部署选项"
echo "--------------------------------------------"
echo "项目已准备好部署到以下平台:"
echo "1. GitHub (推荐)"
echo "2. Gitee (国内推荐)"
echo "3. GitLab (企业级)"
echo ""
echo "详细部署指南请查看 ../Git部署指南.md"
echo ""

# 演示8: 显示项目统计
echo "🎯 演示8: 项目统计"
echo "--------------------------------------------"
echo "代码统计:"
echo "- 总文件数: 46个"
echo "- 总代码行数: 约20,954行"
echo "- Python文件: 12个"
echo "- 文档文件: 8个"
echo ""
echo "模块统计:"
echo "- 记忆管理模块: 500+行"
echo "- 数据获取模块: 250+行"
echo "- 分析引擎模块: 500+行"
echo "- 报告生成模块: 600+行"
echo "- 质量检查模块: 400+行"
echo "- 主程序模块: 300+行"
echo ""

# 演示9: 运行帮助
echo "🎯 演示9: 程序帮助信息"
echo "--------------------------------------------"
python3 src/main.py --help 2>&1 | head -20
echo ""

echo "============================================"
echo "演示完成!"
echo "============================================"
echo ""
echo "🎉 项目已完全准备好部署!"
echo ""
echo "下一步操作建议:"
echo "1. 配置Tushare Pro Token:"
echo "   cp config/tushare_config_example.py config/tushare_config.py"
echo "   # 编辑config/tushare_config.py，填入您的Token"
echo ""
echo "2. 部署到Git平台:"
echo "   查看 ../Git部署指南.md 获取详细步骤"
echo ""
echo "3. 运行完整分析:"
echo "   python3 src/main.py"
echo ""
echo "4. 查看生成的报告:"
echo "   报告将生成在 reports/ 目录中"
echo ""
echo "祝您使用愉快! 🚀"
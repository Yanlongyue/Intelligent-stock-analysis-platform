#!/bin/bash
# ============================================
# 股票分析软件 - 一键部署脚本
# 执行方式：bash 部署命令_一键执行.sh
# ============================================

echo "🚀 开始部署股票分析软件..."
echo ""

# 1. 进入项目目录
cd /www/wwwroot/stock_analysis_program || {
    echo "❌ 项目目录不存在，请检查路径"
    exit 1
}

# 2. 拉取最新代码
echo "📥 拉取最新代码..."
git pull origin master
if [ $? -ne 0 ]; then
    echo "❌ 代码拉取失败，请检查网络或仓库配置"
    exit 1
fi
echo "✅ 代码拉取成功"
echo ""

# 3. 停止旧服务
echo "🛑 停止旧服务..."
pkill -f "python3 real_data_backend.py" 2>/dev/null
sleep 2
echo "✅ 旧服务已停止"
echo ""

# 4. 清理日志
echo "🧹 清理旧日志..."
> backend.log 2>/dev/null
echo "✅ 日志已清理"
echo ""

# 5. 测试后端模块
echo "🧪 测试后端模块导入..."
python3 -c "from real_data_provider import get_data_provider; from real_data_backend import RealDataBackendHandler; from technical_advisor import TechnicalAdvisor; print('✅ 所有模块导入成功')"
if [ $? -ne 0 ]; then
    echo "❌ 模块导入失败，请检查依赖"
    exit 1
fi
echo ""

# 6. 启动新服务
echo "▶️ 启动后端服务..."
nohup python3 real_data_backend.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "📌 后端服务 PID: $BACKEND_PID"
sleep 5
echo ""

# 7. 健康检查
echo "🔍 服务健康检查..."
HEALTH=$(curl -s http://localhost:9000/api/health 2>/dev/null)
if [ -n "$HEALTH" ]; then
    echo "✅ 后端服务运行正常"
    echo "📊 健康状态: $HEALTH"
else
    echo "⚠️ 健康检查失败，查看日志..."
    tail -20 backend.log
fi
echo ""

# 8. 测试持仓接口
echo "📈 测试持仓接口..."
POSITIONS=$(curl -s http://localhost:9000/api/positions 2>/dev/null | head -c 500)
if [ -n "$POSITIONS" ]; then
    echo "✅ 持仓接口正常"
    echo "📝 返回数据预览:"
    echo "$POSITIONS"
else
    echo "⚠️ 持仓接口测试失败"
fi
echo ""

echo "=========================================="
echo "🎉 部署完成！"
echo "📍 后端地址: http://101.133.150.164:9000"
echo "📋 实时日志: tail -f /www/wwwroot/stock_analysis_program/backend.log"
echo "=========================================="

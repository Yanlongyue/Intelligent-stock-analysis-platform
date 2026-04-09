#!/bin/bash
# 宝塔防火墙快速放行脚本

echo "=== 查看当前宝塔防火墙规则 ==="
cat /www/server/panel/data/port.pl 2>/dev/null || echo "端口配置文件不存在"

echo ""
echo "=== 放行 8889 端口 ==="
/www/server/panel/pyenv/bin/python3 /www/server/panel/class/panelPlugin.py addPort 8889 tcp 股票分析平台前端

echo ""
echo "=== 放行 9000 端口 ==="
/www/server/panel/pyenv/bin/python3 /www/server/panel/class/panelPlugin.py addPort 9000 tcp 股票分析平台API

echo ""
echo "=== 查看已放行端口 ==="
/www/server/panel/pyenv/bin/python3 /www/server/panel/class/panelPlugin.py getPortList

echo ""
echo "完成！请测试访问：http://101.133.150.164:8889/"

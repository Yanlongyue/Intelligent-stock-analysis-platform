#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

print("🧪 快速测试七步法股票分析程序")

# 测试1: 检查目录结构
print("\n1. 检查目录结构...")
from config.settings import config
config.ensure_directories()
print("✅ 目录结构检查完成")

# 测试2: 检查配置文件
print("\n2. 检查配置文件...")
config.print_config_summary()

# 测试3: 检查记忆文件
print("\n3. 检查记忆文件...")
if config.EXTERNAL_MEMORY_PATH.exists():
    print(f"✅ 记忆文件存在: {config.EXTERNAL_MEMORY_PATH}")
else:
    print(f"❌ 记忆文件不存在: {config.EXTERNAL_MEMORY_PATH}")

if config.EXTERNAL_TEMPLATE_PATH.exists():
    print(f"✅ 模板文件存在: {config.EXTERNAL_TEMPLATE_PATH}")
else:
    print(f"❌ 模板文件不存在: {config.EXTERNAL_TEMPLATE_PATH}")

# 测试4: 检查核心原则
print("\n4. 检查核心原则...")
print("核心原则:")
for i, principle in enumerate(config.CORE_PRINCIPLES, 1):
    print(f"  {i}. {principle}")

print("\n✅ 快速测试完成!")
print("\n下一步:")
print("1. 配置Tushare Token: 编辑 config/tushare_config.py")
print("2. 运行完整测试: python3 test_basic.py")
print("3. 运行主程序: python3 src/main.py --summary")
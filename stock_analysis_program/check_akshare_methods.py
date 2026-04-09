#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查 AkShare 所有方法，找出北向资金、指数相关的国内接口
"""

import akshare as ak
import re

def find_methods(pattern):
    """查找匹配模式的方法"""
    methods = []
    for attr_name in dir(ak):
        if re.search(pattern, attr_name, re.IGNORECASE):
            methods.append(attr_name)
    return methods

print("🔍 查找 AkShare 中与北向资金相关的方法...")
north_methods = find_methods(r'hsgt|north|south|外资|沪股通|深股通')
print(f"找到 {len(north_methods)} 个方法:")
for m in sorted(north_methods):
    print(f"  - {m}")

print("\n🔍 查找 AkShare 中与指数相关的方法...")
index_methods = find_methods(r'index|指数')
print(f"找到 {len(index_methods)} 个方法:")
for m in sorted(index_methods):
    print(f"  - {m}")

print("\n🔍 查找 AkShare 中与市场概况相关的方法...")
market_methods = find_methods(r'market|overview|大盘|市场|概况')
print(f"找到 {len(market_methods)} 个方法:")
for m in sorted(market_methods):
    print(f"  - {m}")

print("\n🔍 查找 AkShare 中与资金流向相关的方法...")
moneyflow_methods = find_methods(r'money|flow|资金|流入|流出')
print(f"找到 {len(moneyflow_methods)} 个方法:")
for m in sorted(moneyflow_methods):
    print(f"  - {m}")
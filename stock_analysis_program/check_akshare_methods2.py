#!/usr/bin/env python3
"""
检查 AkShare 中可用的股票历史数据方法
"""

import akshare as ak
import inspect

# 获取所有包含 "stock" 和 "hist" 的方法
all_methods = dir(ak)
stock_hist_methods = []

print("=== 检查 AkShare 股票历史数据方法 ===")

for method_name in all_methods:
    if 'stock' in method_name.lower() and 'hist' in method_name.lower():
        try:
            method = getattr(ak, method_name)
            if callable(method):
                stock_hist_methods.append(method_name)
        except:
            pass

print(f"找到 {len(stock_hist_methods)} 个股票历史数据方法:")
for i, method in enumerate(sorted(stock_hist_methods), 1):
    print(f"  {i:2d}. {method}")

# 特别检查新浪财经接口
print("\n=== 检查新浪财经相关方法 ===")
sina_methods = [m for m in stock_hist_methods if 'sina' in m.lower()]
if sina_methods:
    print("新浪财经方法:")
    for method in sina_methods:
        print(f"  - {method}")
else:
    print("未找到新浪财经方法")
    
    # 查看所有包含 sina 的方法
    all_sina_methods = [m for m in all_methods if 'sina' in m.lower()]
    print(f"所有包含 'sina' 的方法 ({len(all_sina_methods)} 个):")
    for method in sorted(all_sina_methods):
        print(f"  - {method}")
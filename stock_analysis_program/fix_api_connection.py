#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API连接诊断脚本
用于检查网络、环境变量与本地后端状态。
"""

import os
import sys
from pathlib import Path

import requests

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_network_connection():
    """检查基础网络连通性"""
    print("🔍 检查网络连接状态...")

    test_urls = [
        ("百度", "https://www.baidu.com"),
        ("Tushare API", "https://api.tushare.pro"),
    ]

    all_good = True
    for name, url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"  ✅ {name}: 可访问")
            else:
                print(f"  ⚠️ {name}: 状态码 {response.status_code}")
                all_good = False
        except Exception as exc:
            print(f"  ❌ {name}: 连接失败 - {exc}")
            all_good = False

    return all_good


def check_tushare_token():
    """检查 Tushare Token 环境变量"""
    print("\n🔍 检查 Tushare Token 配置...")

    token = (os.getenv("TUSHARE_TOKEN") or "").strip()
    if not token:
        print("  ❌ 未检测到环境变量 TUSHARE_TOKEN")
        print("  ℹ️ 请先执行: export TUSHARE_TOKEN=您的Token")
        print("  ℹ️ 出于安全原因，不再支持把 Token 写入代码文件")
        return False

    print(f"  ✅ Token 已配置: {token[:6]}...{token[-4:]}")
    return True


def check_local_backend():
    """检查本地后端接口是否可访问"""
    print("\n🔍 检查本地后端服务...")

    try:
        response = requests.get("http://localhost:9000/api/health", timeout=5)
        if response.ok:
            print("  ✅ 本地后端服务可访问: http://localhost:9000/api/health")
            return True

        print(f"  ⚠️ 本地后端返回异常状态码: {response.status_code}")
        return False
    except Exception as exc:
        print(f"  ❌ 本地后端不可访问: {exc}")
        print("  ℹ️ 如需本地调试，请先运行 ./start_real_data_system.sh")
        return False


def main():
    print("=" * 60)
    print("智能股票分析系统 - API连接诊断")
    print("=" * 60)

    network_ok = check_network_connection()
    token_ok = check_tushare_token()
    backend_ok = check_local_backend()

    print("\n📋 诊断结论")
    print("- 网络状态:", "正常" if network_ok else "存在问题")
    print("- Token状态:", "已配置" if token_ok else "未配置")
    print("- 本地后端:", "可访问" if backend_ok else "不可访问")

    print("\n🛠️ 建议操作")
    if not token_ok:
        print("1. 在当前终端执行 export TUSHARE_TOKEN=您的Token")
    if not backend_ok:
        print("2. 启动本地真实数据系统：./start_real_data_system.sh")
    if token_ok and backend_ok:
        print("1. 本地真实数据链路已具备，接下来可检查前端 config.js 中的 production 地址配置")
        print("2. 公网部署可通过 ?api=https://您的后端地址 临时指定接口")

    print("\n完成。")


if __name__ == "__main__":
    main()

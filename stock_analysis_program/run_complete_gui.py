#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旧版桌面 GUI 兼容启动器
作者：风暴 🌪️
"""

import subprocess
import sys
from pathlib import Path


def main():
    script_dir = Path(__file__).resolve().parent
    legacy_gui = script_dir / "complete_gui_main.py"

    print("=" * 60)
    print("股票分析桌面 GUI 兼容启动器")
    print("=" * 60)
    print("⚠️  桌面 GUI 已降级为兼容模式，不再作为默认主入口。")
    print("ℹ️  日常使用请优先运行：")
    print("   1. ./start_real_data_system.sh   真实数据 Web 主入口")
    print("   2. ./start_enhanced_system.sh    演示模式入口")
    print("ℹ️  当前将继续启动旧版桌面 GUI ...")
    print("")

    if not legacy_gui.exists():
        print(f"❌ 未找到旧版桌面 GUI 主程序：{legacy_gui.name}")
        sys.exit(1)

    result = subprocess.run([sys.executable, str(legacy_gui)], cwd=str(script_dir))
    if result.returncode != 0:
        print("")
        print("❌ 旧版桌面 GUI 启动失败。")
        print("ℹ️  如只需要日常使用，建议改用 Web 主入口：./start_real_data_system.sh")

    sys.exit(result.returncode)


if __name__ == "__main__":
    main()

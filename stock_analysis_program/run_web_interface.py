#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
兼容入口：旧版基础 Web 启动脚本
"""

from pathlib import Path
import runpy
import sys


def main():
    base_dir = Path(__file__).resolve().parent
    target = base_dir / "run_enhanced_web.py"

    print("=" * 60)
    print("📦 run_web_interface.py 已收口为兼容入口")
    print("ℹ️ 推荐主入口：./start_enhanced_system.sh")
    print("ℹ️ 当前将自动转到增强版 Web 启动器 run_enhanced_web.py")
    print("ℹ️ 如需真实数据，请运行：./start_real_data_system.sh")
    print("=" * 60)
    print()

    if not target.exists():
        print(f"❌ 找不到目标脚本: {target.name}")
        return 1

    runpy.run_path(str(target), run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())

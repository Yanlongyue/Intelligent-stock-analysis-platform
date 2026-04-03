#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
兼容入口：旧版持仓演示脚本
"""

from pathlib import Path
import runpy
import sys


def main():
    base_dir = Path(__file__).resolve().parent
    target = base_dir / "简易演示模式.py"

    print("=" * 60)
    print("📦 run_demo.py 已收口为兼容入口")
    print("ℹ️ 推荐直接运行：python3 简易演示模式.py")
    print("ℹ️ 如需完整七步法分析，请运行：./start.sh analyze")
    print("=" * 60)
    print()

    if not target.exists():
        print(f"❌ 找不到目标脚本: {target.name}")
        return 1

    runpy.run_path(str(target), run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())

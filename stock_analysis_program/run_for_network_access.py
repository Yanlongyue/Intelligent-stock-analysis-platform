#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
兼容入口：旧版网络访问启动脚本
"""

from pathlib import Path
import subprocess
import sys


def main():
    base_dir = Path(__file__).resolve().parent
    target = base_dir / "启动网络访问系统.sh"

    print("=" * 60)
    print("📦 run_for_network_access.py 已收口为兼容入口")
    print("ℹ️ 推荐主入口：./start_real_data_system.sh")
    print("ℹ️ 当前将自动转到网络访问兼容脚本，继续提供局域网/外网访问提示")
    print("=" * 60)
    print()

    if not target.exists():
        print(f"❌ 找不到目标脚本: {target.name}")
        return 1

    return subprocess.call(["bash", str(target)], cwd=str(base_dir))


if __name__ == "__main__":
    sys.exit(main())

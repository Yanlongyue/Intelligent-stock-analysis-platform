#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
运行完整GUI应用程序
作者：风暴 🌪️
"""

import sys
import os
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import tkinter
        import pandas
        import numpy
        import matplotlib
        import requests
        import tushare
        import sqlite3
        
        print("✅ 所有核心依赖已安装")
        return True
        
    except ImportError as e:
        print(f"❌ 依赖检查失败: {e}")
        return False

def install_dependencies():
    """安装依赖"""
    print("正在安装依赖...")
    
    # 读取requirements文件
    req_file = Path(__file__).parent / "requirements_gui.txt"
    if req_file.exists():
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(req_file)])
            print("✅ 依赖安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖安装失败: {e}")
            return False
    else:
        print("❌ 未找到requirements_gui.txt文件")
        return False

def check_config_files():
    """检查配置文件"""
    config_dir = Path(__file__).parent / "config"
    
    # 检查配置文件
    config_files = {
        "position_config.py": "持仓配置文件",
        "tushare_config.py": "Tushare Token配置文件",
        "gui_config.json": "GUI配置文件"
    }
    
    missing_files = []
    for file_name, description in config_files.items():
        file_path = config_dir / file_name
        if not file_path.exists():
            missing_files.append(f"{description} ({file_name})")
    
    if missing_files:
        print("⚠️  缺少以下配置文件:")
        for file_desc in missing_files:
            print(f"   - {file_desc}")
        return False
    else:
        print("✅ 所有配置文件检查通过")
        return True

def create_missing_config_files():
    """创建缺失的配置文件"""
    config_dir = Path(__file__).parent / "config"
    config_dir.mkdir(exist_ok=True)
    
    # 创建默认的position_config.py
    position_config = '''"""
持仓配置文件
包含持仓股票信息和权重配置
"""

# 持仓股票代码和名称映射
POSITION_STOCKS = {
    "300033.SZ": "同花顺",
    "600031.SH": "三一重工",
    "000001.SZ": "平安银行",
    "002415.SZ": "海康威视",
    "300059.SZ": "东方财富"
}

# 持仓权重配置（0-100%）
POSITION_WEIGHTS = {
    "300033.SZ": 25,    # 同花顺 25%
    "600031.SH": 20,    # 三一重工 20%
    "000001.SZ": 20,    # 平安银行 20%
    "002415.SZ": 20,    # 海康威视 20%
    "300059.SZ": 15     # 东方财富 15%
}

# 持仓配置摘要
POSITION_CONFIG = {
    "total_stocks": len(POSITION_STOCKS),
    "total_weight": sum(POSITION_WEIGHTS.values()),
    "high_risk_stocks": ["300033.SZ", "300059.SZ"],  # 高风险股票
    "medium_risk_stocks": ["600031.SH", "002415.SZ"], # 中风险股票
    "low_risk_stocks": ["000001.SZ"]  # 低风险股票
}
'''
    
    # 创建默认的tushare_config.py
    tushare_config = '''"""
Tushare Pro API Token 配置文件
请在此处填写您的Tushare Pro Token
"""

# Tushare Pro Token
TUSHARE_TOKEN = "您的Tushare Pro Token请填写在这里"

# API配置
TUSHARE_URL = "http://api.tushare.pro"
'''
    
    # 写入文件
    with open(config_dir / "position_config.py", "w", encoding="utf-8") as f:
        f.write(position_config)
    
    with open(config_dir / "tushare_config.py", "w", encoding="utf-8") as f:
        f.write(tushare_config)
    
    print("✅ 已创建默认配置文件")
    print("⚠️  请编辑 config/tushare_config.py 填写您的Tushare Pro Token")

def run_gui():
    """运行GUI应用程序"""
    try:
        from complete_gui_main import main
        print("🚀 启动股票分析专业版GUI...")
        main()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

def main():
    """主函数"""
    print("=" * 60)
    print("股票分析专业版GUI - 启动器")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        print("\n是否安装依赖？ (y/n): ", end="")
        choice = input().strip().lower()
        if choice == 'y':
            if not install_dependencies():
                sys.exit(1)
        else:
            sys.exit(1)
    
    # 检查配置文件
    if not check_config_files():
        print("\n是否创建默认配置文件？ (y/n): ", end="")
        choice = input().strip().lower()
        if choice == 'y':
            create_missing_config_files()
            print("\n⚠️  请先配置Tushare Token，然后重新启动程序")
            sys.exit(0)
        else:
            sys.exit(1)
    
    print("\n" + "=" * 60)
    
    # 运行GUI
    run_gui()

if __name__ == "__main__":
    main()
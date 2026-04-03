#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tushare Pro API 配置示例
仅演示通过环境变量 TUSHARE_TOKEN 注入，不在代码中保存真实 Token。
"""

import os
import tushare as ts


class TushareConfig:
    """Tushare API 配置示例类"""

    ENV_VAR_NAME = "TUSHARE_TOKEN"
    BASE_URL = "https://api.tushare.pro"

    @classmethod
    def get_token(cls):
        return (os.getenv(cls.ENV_VAR_NAME) or "").strip()

    @classmethod
    def has_token(cls):
        return bool(cls.get_token())

    @classmethod
    def init_tushare(cls):
        token = cls.get_token()
        if not token:
            raise ValueError("未检测到环境变量 TUSHARE_TOKEN，请先设置后再启动")

        ts.set_token(token)
        return ts.pro_api()

    @classmethod
    def print_config(cls):
        print("Tushare Pro API 配置示例")
        if cls.has_token():
            token = cls.get_token()
            print(f"✅ Token 已配置: {token[:6]}...{token[-4:]}")
        else:
            print("❌ Token 未配置，请先执行 export TUSHARE_TOKEN=您的Token")


TUSHARE_TOKEN = TushareConfig.get_token()
TOKEN = TUSHARE_TOKEN

tushare_config = TushareConfig()

if __name__ == "__main__":
    tushare_config.print_config()

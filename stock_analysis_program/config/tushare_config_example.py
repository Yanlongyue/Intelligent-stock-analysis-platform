#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tushare Pro API示例配置文件
请复制此文件为tushare_config.py并填入您的Token
"""

import tushare as ts
from config.settings import config

class TushareConfig:
    """Tushare API配置类"""
    
    # Tushare Pro Token（需要用户配置）
    # 请从 https://tushare.pro 获取您的Token
    TOKEN = "your_tushare_token_here"  # 替换为您的实际Token
    
    # API配置
    BASE_URL = "https://api.tushare.pro"
    TIMEOUT = config.data_source.TUSHARE_TIMEOUT
    RETRY_COUNT = config.data_source.TUSHARE_RETRY_COUNT
    
    # 数据接口配置
    API_CONFIG = {
        "daily": {
            "name": "历史日线",
            "params": ["ts_code", "trade_date", "start_date", "end_date"],
            "fields": ["ts_code", "trade_date", "open", "high", "low", "close", "pre_close", "change", "pct_chg", "vol", "amount"],
            "description": "获取股票日线数据"
        },
        "pro_bar": {
            "name": "专业行情",
            "params": ["ts_code", "asset", "start_date", "end_date", "freq"],
            "fields": ["ts_code", "trade_date", "open", "high", "low", "close", "pre_close", "change", "pct_chg", "vol", "amount"],
            "description": "获取专业行情数据"
        },
        "income": {
            "name": "利润表",
            "params": ["ts_code", "period", "start_date", "end_date"],
            "fields": ["ts_code", "ann_date", "end_date", "revenue", "operate_profit", "net_profit"],
            "description": "获取公司利润表数据"
        },
        "balancesheet": {
            "name": "资产负债表",
            "params": ["ts_code", "period", "start_date", "end_date"],
            "fields": ["ts_code", "ann_date", "end_date", "total_assets", "total_liab", "total_equity"],
            "description": "获取公司资产负债表数据"
        },
        "cashflow": {
            "name": "现金流量表",
            "params": ["ts_code", "period", "start_date", "end_date"],
            "fields": ["ts_code", "ann_date", "end_date", "n_cashflow_act", "n_cash_flow"],
            "description": "获取公司现金流量表数据"
        },
        "moneyflow_hsgt": {
            "name": "沪深港通资金流向",
            "params": ["trade_date", "start_date", "end_date"],
            "fields": ["trade_date", "buy_amount", "sell_amount", "net_amount"],
            "description": "获取北向资金流向数据"
        },
        "index_weight": {
            "name": "指数成分股权重",
            "params": ["index_code", "trade_date"],
            "fields": ["index_code", "con_code", "trade_date", "weight"],
            "description": "获取指数成分股权重数据"
        },
        "cn_gdp": {
            "name": "中国GDP数据",
            "params": ["period", "start_date", "end_date"],
            "fields": ["period", "gdp", "gdp_yoy"],
            "description": "获取中国GDP数据"
        },
        "cn_cpi": {
            "name": "中国CPI数据",
            "params": ["period", "start_date", "end_date"],
            "fields": ["period", "cpi", "cpi_yoy"],
            "description": "获取中国CPI数据"
        },
    }
    
    @classmethod
    def init_tushare(cls):
        """初始化Tushare Pro"""
        if cls.TOKEN == "your_tushare_token_here":
            raise ValueError("请先在config/tushare_config.py中配置您的Tushare Pro Token")
        
        try:
            ts.set_token(cls.TOKEN)
            pro = ts.pro_api()
            print(f"✅ Tushare Pro API初始化成功")
            return pro
        except Exception as e:
            print(f"❌ Tushare Pro API初始化失败: {str(e)}")
            raise
    
    @classmethod
    def get_api(cls, api_name):
        """获取API配置"""
        if api_name not in cls.API_CONFIG:
            raise ValueError(f"API '{api_name}' 不存在，请检查配置")
        
        return cls.API_CONFIG[api_name]
    
    @classmethod
    def validate_token(cls):
        """验证Token是否有效"""
        if cls.TOKEN == "your_tushare_token_here":
            return False
        
        try:
            ts.set_token(cls.TOKEN)
            pro = ts.pro_api()
            # 尝试获取一个简单的数据来验证Token
            data = pro.query('daily', ts_code='000001.SZ', trade_date='20240101')
            if data.empty:
                print("⚠️ Token验证：API返回空数据，但Token可能有效")
            else:
                print("✅ Token验证成功")
            return True
        except Exception as e:
            print(f"❌ Token验证失败: {str(e)}")
            return False
    
    @classmethod
    def print_config(cls):
        """打印配置信息"""
        print("\n" + "="*60)
        print("Tushare Pro API配置")
        print("="*60)
        
        print(f"\n🔑 Token状态:")
        if cls.TOKEN == "your_tushare_token_here":
            print("  ❌ Token未配置，请从 https://tushare.pro 获取您的Token")
        else:
            print(f"  ✅ Token已配置: {cls.TOKEN[:10]}...")
        
        print(f"\n📊 支持的API接口:")
        for api_name, config in cls.API_CONFIG.items():
            print(f"  {api_name}: {config['description']}")
        
        print(f"\n⚙️ 连接配置:")
        print(f"  基础URL: {cls.BASE_URL}")
        print(f"  超时时间: {cls.TIMEOUT}秒")
        print(f"  重试次数: {cls.RETRY_COUNT}")
        
        print("\n" + "="*60)

# 导出配置实例
tushare_config = TushareConfig()

if __name__ == "__main__":
    # 测试配置
    tushare_config.print_config()
    
    # 验证Token
    if tushare_config.validate_token():
        print("✅ Token验证成功，API可用")
    else:
        print("❌ Token验证失败，请配置正确的Token")
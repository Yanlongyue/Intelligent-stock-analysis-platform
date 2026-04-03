#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实数据提供者模块
从Tushare Pro API获取实时金融数据
"""

import json
import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import os

class RealDataProvider:
    """真实数据提供者基类"""
    
    def __init__(self, tushare_token=None):
        """
        初始化数据提供者
        
        Args:
            tushare_token: Tushare Pro API token，如果为None则尝试从环境变量读取
        """
        self.tushare_token = tushare_token or os.getenv('TUSHARE_TOKEN')
        self.api_url = "https://api.tushare.pro"
        
        # 缓存机制
        self.cache = {}
        self.cache_ttl = 300  # 5分钟缓存
        
        # 默认股票列表（持仓股）
        self.default_stocks = [
            {"code": "601868.SH", "name": "中国能建"},
            {"code": "002506.SZ", "name": "协鑫集成"}, 
            {"code": "600821.SH", "name": "金开新能"}
        ]
    
    def call_tushare_api(self, api_name, params=None, fields=None):
        """
        调用Tushare Pro API
        
        Args:
            api_name: API接口名称
            params: 请求参数
            fields: 返回字段，默认返回全部
            
        Returns:
            API响应数据
        """
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        payload = {
            "api_name": api_name,
            "token": self.tushare_token,
            "params": params or {},
            "fields": fields or ""
        }
        
        try:
            response = requests.post(
                self.api_url, 
                headers=headers, 
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") == 0:
                return result["data"]
            else:
                print(f"Tushare API错误: {result.get('msg', '未知错误')}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            return None
    
    def get_stock_basic_info(self, ts_code):
        """
        获取股票基本信息
        
        Args:
            ts_code: 股票代码（带交易所后缀）
            
        Returns:
            股票基本信息字典
        """
        cache_key = f"basic_{ts_code}"
        if self._get_from_cache(cache_key):
            return self._get_from_cache(cache_key)
        
        data = self.call_tushare_api(
            "stock_basic",
            params={"ts_code": ts_code},
            fields="ts_code,symbol,name,area,industry,list_date,market,is_hs"
        )
        
        if data and data.get("items"):
            result = self._format_basic_data(data["items"][0], data["fields"])
            self._save_to_cache(cache_key, result)
            return result
        
        return None
    
    def get_daily_quotes(self, ts_code, start_date=None, end_date=None):
        """
        获取日线行情数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期，格式YYYYMMDD
            end_date: 结束日期，格式YYYYMMDD
            
        Returns:
            日线行情数据列表
        """
        # 默认获取最近30天数据
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
        
        cache_key = f"daily_{ts_code}_{start_date}_{end_date}"
        if self._get_from_cache(cache_key):
            return self._get_from_cache(cache_key)
        
        data = self.call_tushare_api(
            "daily",
            params={
                "ts_code": ts_code,
                "start_date": start_date,
                "end_date": end_date
            },
            fields="trade_date,open,high,low,close,pre_close,change,pct_chg,vol,amount"
        )
        
        if data and data.get("items"):
            result = self._format_daily_data(data["items"], data["fields"])
            self._save_to_cache(cache_key, result)
            return result
        
        return []
    
    def get_financial_indicators(self, ts_code):
        """
        获取财务指标数据
        
        Args:
            ts_code: 股票代码
            
        Returns:
            财务指标数据
        """
        cache_key = f"fina_{ts_code}"
        if self._get_from_cache(cache_key):
            return self._get_from_cache(cache_key)
        
        # 获取最新的财务指标
        data = self.call_tushare_api(
            "fina_indicator",
            params={
                "ts_code": ts_code,
                "period": "20231231",  # 最新年报
                "type": "P"
            },
            fields="roe,gpr,npr,dt_ratio,total_revenue_ps,profit_dedt,eps_basic,or_yoy,q_profit_yoy"
        )
        
        if data and data.get("items"):
            result = self._format_financial_data(data["items"][0], data["fields"])
            self._save_to_cache(cache_key, result)
            return result
        
        return None
    
    def get_moneyflow_data(self, ts_code):
        """
        获取资金流向数据
        
        Args:
            ts_code: 股票代码
            
        Returns:
            资金流向数据
        """
        cache_key = f"moneyflow_{ts_code}"
        if self._get_from_cache(cache_key):
            return self._get_from_cache(cache_key)
        
        # 获取最近一天的资金流向
        today = datetime.now().strftime("%Y%m%d")
        data = self.call_tushare_api(
            "moneyflow",
            params={
                "ts_code": ts_code,
                "start_date": today,
                "end_date": today
            },
            fields="buy_sm_vol,buy_sm_amount,sell_sm_vol,sell_sm_amount,buy_md_vol,buy_md_amount,sell_md_vol,sell_md_amount,buy_lg_vol,buy_lg_amount,sell_lg_vol,sell_lg_amount,buy_elg_vol,buy_elg_amount,sell_elg_vol,sell_elg_amount,net_mf_vol,net_mf_amount"
        )
        
        if data and data.get("items"):
            result = self._format_moneyflow_data(data["items"][0], data["fields"])
            self._save_to_cache(cache_key, result)
            return result
        
        return None
    
    def get_top_list_data(self, trade_date=None):
        """
        获取龙虎榜数据
        
        Args:
            trade_date: 交易日期，格式YYYYMMDD
            
        Returns:
            龙虎榜数据
        """
        if not trade_date:
            trade_date = datetime.now().strftime("%Y%m%d")
        
        cache_key = f"toplist_{trade_date}"
        if self._get_from_cache(cache_key):
            return self._get_from_cache(cache_key)
        
        data = self.call_tushare_api(
            "top_list",
            params={"trade_date": trade_date},
            fields="ts_code,name,p_change,amount,buy,sell,reason"
        )
        
        if data and data.get("items"):
            result = self._format_toplist_data(data["items"], data["fields"])
            self._save_to_cache(cache_key, result)
            return result
        
        return []
    
    # 辅助方法
    def _format_basic_data(self, item, fields):
        """格式化基本信息"""
        result = {}
        for i, field in enumerate(fields):
            result[field] = item[i] if i < len(item) else None
        return result
    
    def _format_daily_data(self, items, fields):
        """格式化日线数据"""
        formatted = []
        for item in items:
            data_point = {}
            for i, field in enumerate(fields):
                if i < len(item):
                    value = item[i]
                    # 特殊处理数值字段
                    if field in ["open", "high", "low", "close", "pre_close", "change"]:
                        value = float(value) if value else 0.0
                    elif field in ["pct_chg"]:
                        value = float(value) if value else 0.0
                    elif field in ["vol", "amount"]:
                        value = float(value) if value else 0.0
                    data_point[field] = value
            formatted.append(data_point)
        return formatted
    
    def _format_financial_data(self, item, fields):
        """格式化财务数据"""
        result = {}
        for i, field in enumerate(fields):
            if i < len(item):
                value = item[i]
                # 转换数值类型
                if value and value != "":
                    try:
                        value = float(value)
                    except:
                        pass
                result[field] = value
        return result
    
    def _format_moneyflow_data(self, item, fields):
        """格式化资金流向数据"""
        result = {}
        for i, field in enumerate(fields):
            if i < len(item):
                value = item[i]
                if value:
                    try:
                        value = float(value)
                    except:
                        pass
                result[field] = value
        return result
    
    def _format_toplist_data(self, items, fields):
        """格式化龙虎榜数据"""
        formatted = []
        for item in items:
            data_point = {}
            for i, field in enumerate(fields):
                if i < len(item):
                    data_point[field] = item[i]
            formatted.append(data_point)
        return formatted
    
    def _save_to_cache(self, key, data):
        """保存数据到缓存"""
        self.cache[key] = {
            "data": data,
            "timestamp": time.time()
        }
    
    def _get_from_cache(self, key):
        """从缓存获取数据"""
        if key in self.cache:
            cache_entry = self.cache[key]
            if time.time() - cache_entry["timestamp"] < self.cache_ttl:
                return cache_entry["data"]
            else:
                # 缓存过期，删除
                del self.cache[key]
        return None
    
    def get_stock_realtime_price(self, ts_code):
        """
        获取股票实时价格（最新收盘价）
        
        Args:
            ts_code: 股票代码
            
        Returns:
            实时价格，如果失败返回None
        """
        daily_data = self.get_daily_quotes(ts_code, start_date=None, end_date=None)
        if daily_data and len(daily_data) > 0:
            # 返回最新的收盘价
            latest = daily_data[-1]
            return latest.get("close")
        
        return None
    
    def get_all_holdings_data(self):
        """
        获取所有持仓股的实时数据
        
        Returns:
            持仓股数据列表
        """
        holdings = []
        
        for stock in self.default_stocks:
            try:
                # 获取基础信息
                basic_info = self.get_stock_basic_info(stock["code"])
                
                # 获取实时价格
                current_price = self.get_stock_realtime_price(stock["code"])
                
                # 获取财务指标
                financials = self.get_financial_indicators(stock["code"])
                
                # 获取资金流向
                moneyflow = self.get_moneyflow_data(stock["code"])
                
                # 获取最近30天价格历史
                price_history = self.get_daily_quotes(stock["code"])
                
                # 组合数据
                stock_data = {
                    "code": stock["code"],
                    "name": stock["name"],
                    "basic_info": basic_info or {},
                    "current_price": current_price or 0.0,
                    "financials": financials or {},
                    "moneyflow": moneyflow or {},
                    "price_history": price_history or [],
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                holdings.append(stock_data)
                
                # 避免API限流
                time.sleep(0.5)
                
            except Exception as e:
                print(f"获取 {stock['name']}({stock['code']}) 数据失败: {e}")
                continue
        
        return holdings
    
    def get_market_overview(self):
        """
        获取市场概况
        
        Returns:
            市场概况数据
        """
        # 获取主要指数行情
        indices = ["000001.SH", "399001.SZ", "399006.SZ"]  # 上证指数、深证成指、创业板指
        
        index_data = []
        for idx in indices:
            try:
                data = self.get_daily_quotes(idx, start_date=None, end_date=None)
                if data and len(data) > 0:
                    latest = data[-1]
                    index_data.append({
                        "code": idx,
                        "close": latest.get("close", 0),
                        "pct_chg": latest.get("pct_chg", 0)
                    })
            except:
                continue
        
        # 获取市场情绪数据（龙虎榜）
        toplist_data = self.get_top_list_data()
        
        return {
            "indices": index_data,
            "toplist": toplist_data,
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


class MockDataProvider:
    """
    模拟数据提供者（备份方案）
    当真实数据API不可用时使用
    """
    
    def __init__(self):
        self.mock_positions = [
            {
                "code": "601868.SH",
                "name": "中国能建",
                "amount": 400,
                "cost_price": 3.15,
                "current_price": 3.20,
                "type": "value",
                "industry": "基建",
                "daily_change": 1.59  # 百分比
            },
            {
                "code": "002506.SZ",
                "name": "协鑫集成",
                "amount": 400,
                "cost_price": 2.05,
                "current_price": 2.10,
                "type": "growth",
                "industry": "光伏",
                "daily_change": 2.44
            },
            {
                "code": "600821.SH",
                "name": "金开新能",
                "amount": 600,
                "cost_price": 4.10,
                "current_price": 4.20,
                "type": "concept",
                "industry": "新能源",
                "daily_change": 2.44
            }
        ]
    
    def get_all_holdings_data(self):
        """获取模拟持仓数据"""
        return self.mock_positions
    
    def get_stock_realtime_price(self, ts_code):
        """获取模拟实时价格"""
        for stock in self.mock_positions:
            if stock["code"] == ts_code:
                return stock["current_price"]
        return 0.0


# 数据提供者工厂
def get_data_provider(use_real_data=True, token=None):
    """
    获取数据提供者实例
    
    Args:
        use_real_data: 是否使用真实数据
        token: Tushare Pro API token
        
    Returns:
        数据提供者实例
    """
    if use_real_data:
        try:
            provider = RealDataProvider(token)
            # 测试API连接
            test_result = provider.get_stock_basic_info("601868.SH")
            if test_result:
                print("✅ 真实数据API连接成功")
                return provider
            else:
                print("⚠️ 真实数据API连接失败，使用模拟数据")
                return MockDataProvider()
        except Exception as e:
            print(f"⚠️ 初始化真实数据提供者失败: {e}")
            return MockDataProvider()
    else:
        print("ℹ️ 使用模拟数据模式")
        return MockDataProvider()


# 测试代码
if __name__ == "__main__":
    print("测试数据提供者模块...")
    
    # 测试模拟数据
    mock_provider = MockDataProvider()
    holdings = mock_provider.get_all_holdings_data()
    print(f"模拟持仓数据: {len(holdings)} 只股票")
    
    # 测试真实数据（需要token）
    try:
        token = os.getenv('TUSHARE_TOKEN')
        if token:
            print(f"检测到Tushare Token，测试真实数据...")
            real_provider = RealDataProvider(token)
            test_price = real_provider.get_stock_realtime_price("601868.SH")
            print(f"中国能建实时价格: {test_price}")
    except Exception as e:
        print(f"真实数据测试失败: {e}")
    
    print("测试完成！")
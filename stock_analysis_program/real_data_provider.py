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
    
    def _candidate_financial_periods(self, limit=8):
        """生成最近若干个财报期候选值（按新到旧）"""
        today = datetime.now()
        quarter_ends = [(12, 31), (9, 30), (6, 30), (3, 31)]
        periods = []
        year = today.year
        
        while len(periods) < limit:
            for month, day in quarter_ends:
                period = f"{year}{month:02d}{day:02d}"
                if period <= today.strftime("%Y%m%d"):
                    periods.append(period)
                    if len(periods) >= limit:
                        break
            year -= 1
        
        return periods
    
    def has_real_source(self):
        """Tushare 是否已配置"""
        return bool(self.tushare_token)
    
    def get_data_source_label(self):
        """获取数据源标签"""
        return "Tushare Pro API（真实数据）"
    
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
    
    def get_financial_indicators(self, ts_code, period=None):
        """
        获取财务指标数据
        
        Args:
            ts_code: 股票代码
            period: 财报期（可选，YYYYMMDD）
            
        Returns:
            财务指标数据
        """
        cache_key = f"fina_{ts_code}_{period or 'latest'}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        candidate_periods = [period] if period else self._candidate_financial_periods()
        
        for target_period in candidate_periods:
            data = self.call_tushare_api(
                "fina_indicator",
                params={
                    "ts_code": ts_code,
                    "period": target_period,
                    "type": "P"
                },
                fields="end_date,roe,gpr,npr,dt_ratio,total_revenue_ps,profit_dedt,eps_basic,or_yoy,q_profit_yoy"
            )
            
            if data and data.get("items"):
                result = self._format_financial_data(data["items"][0], data["fields"])
                self._save_to_cache(cache_key, result)
                return result
        
        return None
    
    def get_moneyflow_data(self, ts_code, start_date=None, end_date=None):
        """
        获取资金流向数据
        
        Args:
            ts_code: 股票代码
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            
        Returns:
            资金流向数据
        """
        if not end_date:
            end_date = datetime.now().strftime("%Y%m%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=10)).strftime("%Y%m%d")
        
        cache_key = f"moneyflow_{ts_code}_{start_date}_{end_date}"
        cached = self._get_from_cache(cache_key)
        if cached:
            return cached
        
        data = self.call_tushare_api(
            "moneyflow",
            params={
                "ts_code": ts_code,
                "start_date": start_date,
                "end_date": end_date
            },
            fields="trade_date,buy_sm_vol,buy_sm_amount,sell_sm_vol,sell_sm_amount,buy_md_vol,buy_md_amount,sell_md_vol,sell_md_amount,buy_lg_vol,buy_lg_amount,sell_lg_vol,sell_lg_amount,buy_elg_vol,buy_elg_amount,sell_elg_vol,sell_elg_amount,net_mf_vol,net_mf_amount"
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


class AkShareDataProvider:
    """
    AkShare备用数据提供者
    当Tushare不可用时使用AkShare作为备用数据源
    """
    
    def __init__(self):
        """初始化AkShare数据提供者"""
        try:
            import akshare as ak
            self.ak = ak
            self.available = True
            print("✅ AkShare备用数据源初始化成功")
        except ImportError:
            self.ak = None
            self.available = False
            print("⚠️ AkShare未安装，备用数据源不可用")
        
        # 缓存机制
        self.cache = {}
        self.cache_ttl = 300  # 5分钟缓存
    
    def has_real_source(self):
        """AkShare 是否可用"""
        return bool(self.available)
    
    def get_data_source_label(self):
        """获取数据源标签"""
        return "AkShare（真实数据备用源）"
    
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
                del self.cache[key]
        return None
    
    def _normalize_code(self, ts_code):
        """
        将带交易所后缀的代码转换为AkShare格式
        如: 601868.SH -> 601868, 002506.SZ -> 002506
        """
        if '.' in ts_code:
            return ts_code.split('.')[0]
        return ts_code
    
    def get_daily_quotes(self, ts_code, start_date=None, end_date=None):
        """
        获取日线行情数据
        
        Args:
            ts_code: 股票代码（带或不带交易所后缀）
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            
        Returns:
            日线数据列表
        """
        if not self.available:
            return None
        
        cache_key = f"daily_{ts_code}_{start_date}_{end_date}"
        if self._get_from_cache(cache_key):
            return self._get_from_cache(cache_key)
        
        try:
            code = self._normalize_code(ts_code)
            
            # AkShare接口: stock_zh_a_hist
            df = self.ak.stock_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date or (datetime.now() - timedelta(days=30)).strftime("%Y%m%d"),
                end_date=end_date or datetime.now().strftime("%Y%m%d"),
                adjust=""  # 不复权
            )
            
            if df is None or df.empty:
                return None
            
            # 转换为统一格式
            result = []
            for _, row in df.iterrows():
                result.append({
                    "trade_date": row.get("日期", ""),
                    "open": float(row.get("开盘", 0)),
                    "high": float(row.get("最高", 0)),
                    "low": float(row.get("最低", 0)),
                    "close": float(row.get("收盘", 0)),
                    "vol": float(row.get("成交量", 0)),
                    "amount": float(row.get("成交额", 0)),
                    "pct_chg": float(row.get("涨跌幅", 0))
                })
            
            self._save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            print(f"AkShare获取日线数据失败 {ts_code}: {e}")
            return None
    
    def get_index_daily(self, ts_code, start_date=None, end_date=None):
        """
        获取指数日线数据
        
        Args:
            ts_code: 指数代码（如 000001.SH）
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            指数日线数据
        """
        if not self.available:
            return None
        
        cache_key = f"index_{ts_code}_{start_date}_{end_date}"
        if self._get_from_cache(cache_key):
            return self._get_from_cache(cache_key)
        
        try:
            code = self._normalize_code(ts_code)
            
            # AkShare接口: index_zh_a_hist
            df = self.ak.index_zh_a_hist(
                symbol=code,
                period="daily",
                start_date=start_date or (datetime.now() - timedelta(days=30)).strftime("%Y%m%d"),
                end_date=end_date or datetime.now().strftime("%Y%m%d")
            )
            
            if df is None or df.empty:
                return None
            
            result = []
            for _, row in df.iterrows():
                result.append({
                    "trade_date": row.get("日期", ""),
                    "close": float(row.get("收盘", 0)),
                    "pct_chg": float(row.get("涨跌幅", 0))
                })
            
            self._save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            print(f"AkShare获取指数数据失败 {ts_code}: {e}")
            return None
    
    def get_north_money_flow(self, start_date=None, end_date=None):
        """
        获取北向资金流向数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            北向资金流向数据
        """
        if not self.available:
            return None
        
        cache_key = f"north_money_{start_date}_{end_date}"
        if self._get_from_cache(cache_key):
            return self._get_from_cache(cache_key)
        
        try:
            # AkShare接口: stock_hsgt_north_net_flow_in_em
            df = self.ak.stock_hsgt_north_net_flow_in_em(
                symbol="北向资金"
            )
            
            if df is None or df.empty:
                return None
            
            # 返回最新一天的数据
            latest = df.iloc[0] if len(df) > 0 else None
            if latest is not None:
                result = {
                    "trade_date": latest.get("日期", ""),
                    "net_amount": float(latest.get("当日净流入", 0)),
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                self._save_to_cache(cache_key, result)
                return result
            
            return None
            
        except Exception as e:
            print(f"AkShare获取北向资金失败: {e}")
            return None
    
    def get_limit_list(self, trade_date=None):
        """
        获取涨跌停股票列表
        
        Args:
            trade_date: 交易日期 (YYYYMMDD)
            
        Returns:
            涨跌停股票列表
        """
        if not self.available:
            return None
        
        if not trade_date:
            trade_date = datetime.now().strftime("%Y%m%d")
        
        cache_key = f"limit_list_{trade_date}"
        if self._get_from_cache(cache_key):
            return self._get_from_cache(cache_key)
        
        try:
            # AkShare接口: stock_zt_pool_em (涨停池)
            df = self.ak.stock_zt_pool_em(date=trade_date)
            
            if df is None or df.empty:
                return []
            
            result = []
            for _, row in df.iterrows():
                result.append({
                    "ts_code": row.get("代码", ""),
                    "name": row.get("名称", ""),
                    "p_change": float(row.get("涨跌幅", 0)),
                    "amount": float(row.get("成交额", 0)),
                    "reason": row.get("涨停原因类别", "")
                })
            
            self._save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            print(f"AkShare获取涨停列表失败: {e}")
            return None
    
    def get_stock_news(self, symbol=None):
        """
        获取股票新闻数据
        
        Args:
            symbol: 股票代码（可选）
            
        Returns:
            新闻列表
        """
        if not self.available:
            return None
        
        cache_key = f"news_{symbol or 'all'}"
        if self._get_from_cache(cache_key):
            return self._get_from_cache(cache_key)
        
        try:
            # AkShare接口: stock_news_em
            df = self.ak.stock_news_em(symbol=symbol or "财经新闻")
            
            if df is None or df.empty:
                return []
            
            result = []
            for _, row in df.head(20).iterrows():  # 只取最新20条
                result.append({
                    "title": row.get("新闻标题", ""),
                    "content": row.get("新闻内容", ""),
                    "time": row.get("发布时间", ""),
                    "source": row.get("新闻来源", "")
                })
            
            self._save_to_cache(cache_key, result)
            return result
            
        except Exception as e:
            print(f"AkShare获取新闻失败: {e}")
            return None
    
    def get_stock_realtime_price(self, ts_code):
        """获取实时价格（通过最新日线数据）"""
        daily_data = self.get_daily_quotes(ts_code, start_date=None, end_date=None)
        if daily_data and len(daily_data) > 0:
            latest = daily_data[-1]
            return latest.get("close")
        return None


class FallbackDataProvider:
    """
    链式回退数据提供者
    按优先级依次尝试: Tushare -> AkShare，默认不再回退到 Mock 数据
    """
    
    def __init__(self, tushare_token=None, enable_mock=False):
        """
        初始化链式回退数据提供者
        
        Args:
            tushare_token: Tushare API token
            enable_mock: 是否启用 Mock 作为最终回退
        """
        self.providers = []
        self.provider_names = []
        self.real_provider_names = []
        self.enable_mock = bool(enable_mock)
        self.last_successful_provider = None
        self.last_successful_method = None
        
        # 第一层: Tushare（主数据源）
        if tushare_token:
            try:
                tushare_provider = RealDataProvider(tushare_token)
                self.providers.append(tushare_provider)
                self.provider_names.append("Tushare")
                self.real_provider_names.append("Tushare")
                print("✅ 第一层数据源（Tushare）就绪")
            except Exception as e:
                print(f"⚠️ Tushare初始化失败: {e}")
        
        # 第二层: AkShare（备用数据源）
        try:
            akshare_provider = AkShareDataProvider()
            if akshare_provider.available:
                self.providers.append(akshare_provider)
                self.provider_names.append("AkShare")
                self.real_provider_names.append("AkShare")
                print("✅ 第二层数据源（AkShare）就绪")
        except Exception as e:
            print(f"⚠️ AkShare初始化失败: {e}")
        
        # 第三层: Mock数据（仅在显式启用时作为最终回退）
        self.mock_provider = None
        if self.enable_mock:
            self.mock_provider = MockDataProvider()
            self.providers.append(self.mock_provider)
            self.provider_names.append("Mock")
            print("✅ 第三层数据源（Mock）就绪")
        else:
            print("🚫 Mock 数据回退已禁用")
        
        print(f"📋 数据源优先级: {' -> '.join(self.provider_names) if self.provider_names else '无可用数据源'}")
    
    def has_real_source(self):
        """是否存在至少一个真实数据源"""
        return len(self.real_provider_names) > 0
    
    def get_active_provider_name(self):
        """获取最近一次成功使用的数据源名称"""
        return self.last_successful_provider
    
    def get_data_source_label(self):
        """获取当前数据源描述"""
        chain = ' -> '.join(self.provider_names) if self.provider_names else '无可用数据源'
        if self.last_successful_provider:
            return f"{self.last_successful_provider}（优先链路: {chain}）"
        if self.real_provider_names:
            return f"真实数据链路已就绪（优先链路: {chain}）"
        return "未接入真实数据源"
    
    def _mark_success(self, provider_name, method_name):
        """记录最近一次成功使用的数据源"""
        self.last_successful_provider = provider_name
        self.last_successful_method = method_name
    
    def _try_providers(self, method_name, *args, **kwargs):
        """
        依次尝试各数据提供者的指定方法
        
        Args:
            method_name: 方法名
            *args, **kwargs: 方法参数
            
        Returns:
            第一个成功的数据提供者的结果
        """
        for i, provider in enumerate(self.providers):
            try:
                method = getattr(provider, method_name, None)
                if method and callable(method):
                    result = method(*args, **kwargs)
                    if result is not None and result != [] and result != {}:
                        self.last_successful_provider = self.provider_names[i]
                        self.last_successful_method = method_name
                        print(f"✅ [{method_name}] 使用数据源: {self.provider_names[i]}")
                        return result
            except Exception as e:
                print(f"⚠️ [{method_name}] {self.provider_names[i]} 失败: {e}")
                continue
        
        print(f"❌ [{method_name}] 所有数据源均失败")
        return None
    
    # 统一接口方法
    def get_stock_basic_info(self, ts_code):
        """获取股票基本信息"""
        return self._try_providers("get_stock_basic_info", ts_code)
    
    def get_daily_quotes(self, ts_code, start_date=None, end_date=None):
        """获取日线行情"""
        return self._try_providers("get_daily_quotes", ts_code, start_date, end_date)
    
    def get_financial_indicators(self, ts_code, period=None):
        """获取财务指标"""
        return self._try_providers("get_financial_indicators", ts_code, period)
    
    def get_moneyflow_data(self, ts_code, start_date=None, end_date=None):
        """获取资金流向"""
        return self._try_providers("get_moneyflow_data", ts_code, start_date, end_date)
    
    def get_top_list_data(self, trade_date=None):
        """获取龙虎榜数据"""
        return self._try_providers("get_top_list_data", trade_date)
    
    def get_stock_realtime_price(self, ts_code):
        """获取实时价格"""
        return self._try_providers("get_stock_realtime_price", ts_code)
    
    def get_all_holdings_data(self):
        """获取所有持仓数据"""
        return self._try_providers("get_all_holdings_data")
    
    def get_market_overview(self):
        """获取市场概况"""
        return self._try_providers("get_market_overview")
    
    # 新增五个高价值数据能力
    def get_daily_basic(self, ts_code, trade_date=None):
        """
        获取每日基本面指标（PE/换手率/市净率等）
        
        Args:
            ts_code: 股票代码
            trade_date: 交易日期
            
        Returns:
            每日基本面指标数据
        """
        if not trade_date:
            trade_date = datetime.now().strftime("%Y%m%d")
        
        # 尝试从Tushare获取
        if self.providers and isinstance(self.providers[0], RealDataProvider):
            try:
                data = self.providers[0].call_tushare_api(
                    "daily_basic",
                    params={
                        "ts_code": ts_code,
                        "trade_date": trade_date
                    },
                    fields="ts_code,trade_date,close,turnover_rate,turnover_rate_f,volume_ratio,pe,pe_ttm,pb,ps,ps_ttm,dv_ratio,dv_ttm,total_mv,circ_mv"
                )
                
                if data and data.get("items"):
                    result = {}
                    fields = data["fields"]
                    item = data["items"][0]
                    for i, field in enumerate(fields):
                        if i < len(item):
                            result[field] = item[i]
                    self._mark_success("Tushare", "daily_basic")
                    print(f"✅ [daily_basic] 使用数据源: Tushare")
                    return result
            except Exception as e:
                print(f"⚠️ [daily_basic] Tushare失败: {e}")
        
        # 回退到AkShare或Mock
        print(f"⚠️ [daily_basic] Tushare不可用，尝试备用数据源")
        # AkShare没有直接的daily_basic接口，这里返回None让回退机制继续
        return None
    
    def get_moneyflow_hsgt(self, start_date=None, end_date=None):
        """
        获取北向资金真实流向
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            北向资金流向数据
        """
        # 尝试从Tushare获取
        if self.providers and isinstance(self.providers[0], RealDataProvider):
            try:
                if not start_date:
                    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
                if not end_date:
                    end_date = datetime.now().strftime("%Y%m%d")
                
                data = self.providers[0].call_tushare_api(
                    "moneyflow_hsgt",
                    params={
                        "start_date": start_date,
                        "end_date": end_date
                    },
                    fields="trade_date,ggt_ss,ggt_sz,hgt,sgt,north_money,south_money"
                )
                
                if data and data.get("items"):
                    result = []
                    fields = data["fields"]
                    for item in data["items"]:
                        item_data = {}
                        for i, field in enumerate(fields):
                            if i < len(item):
                                item_data[field] = item[i]
                        result.append(item_data)
                    self._mark_success("Tushare", "moneyflow_hsgt")
                    print(f"✅ [moneyflow_hsgt] 使用数据源: Tushare")
                    return result
            except Exception as e:
                print(f"⚠️ [moneyflow_hsgt] Tushare失败: {e}")
        
        # 回退到AkShare
        for provider in self.providers:
            if isinstance(provider, AkShareDataProvider):
                result = provider.get_north_money_flow(start_date, end_date)
                if result:
                    self._mark_success("AkShare", "moneyflow_hsgt")
                    print(f"✅ [moneyflow_hsgt] 使用数据源: AkShare")
                    return [result] if isinstance(result, dict) else result
        
        return None
    
    def get_index_daily(self, ts_code, start_date=None, end_date=None):
        """
        获取指数日线数据（含涨跌幅）
        
        Args:
            ts_code: 指数代码
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            指数日线数据
        """
        # 尝试从Tushare获取
        if self.providers and isinstance(self.providers[0], RealDataProvider):
            try:
                if not start_date:
                    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")
                if not end_date:
                    end_date = datetime.now().strftime("%Y%m%d")
                
                data = self.providers[0].call_tushare_api(
                    "index_daily",
                    params={
                        "ts_code": ts_code,
                        "start_date": start_date,
                        "end_date": end_date
                    },
                    fields="ts_code,trade_date,close,open,high,low,pre_close,change,pct_chg,vol,amount"
                )
                
                if data and data.get("items"):
                    result = []
                    fields = data["fields"]
                    for item in data["items"]:
                        item_data = {}
                        for i, field in enumerate(fields):
                            if i < len(item):
                                item_data[field] = item[i]
                        result.append(item_data)
                    self._mark_success("Tushare", "index_daily")
                    print(f"✅ [index_daily] 使用数据源: Tushare")
                    return result
            except Exception as e:
                print(f"⚠️ [index_daily] Tushare失败: {e}")
        
        # 回退到AkShare
        for provider in self.providers:
            if isinstance(provider, AkShareDataProvider):
                result = provider.get_index_daily(ts_code, start_date, end_date)
                if result:
                    self._mark_success("AkShare", "index_daily")
                    print(f"✅ [index_daily] 使用数据源: AkShare")
                    return result
        
        return None
    
    def get_limit_list_d(self, trade_date=None, limit_type="U"):
        """
        获取涨跌停真实数据
        
        Args:
            trade_date: 交易日期
            limit_type: U-涨停, D-跌停
            
        Returns:
            涨跌停股票列表
        """
        if not trade_date:
            trade_date = datetime.now().strftime("%Y%m%d")
        
        # 尝试从Tushare获取
        if self.providers and isinstance(self.providers[0], RealDataProvider):
            try:
                data = self.providers[0].call_tushare_api(
                    "limit_list_d",
                    params={
                        "trade_date": trade_date,
                        "limit_type": limit_type
                    },
                    fields="ts_code,name,close,pct_chg,turnover_rate,amount,limit_amount,fd_amount,first_time,last_time,limit_times,up_stat,up_stat_times"
                )
                
                if data and data.get("items"):
                    result = []
                    fields = data["fields"]
                    for item in data["items"]:
                        item_data = {}
                        for i, field in enumerate(fields):
                            if i < len(item):
                                item_data[field] = item[i]
                        result.append(item_data)
                    self._mark_success("Tushare", "limit_list_d")
                    print(f"✅ [limit_list_d] 使用数据源: Tushare")
                    return result
            except Exception as e:
                print(f"⚠️ [limit_list_d] Tushare失败: {e}")
        
        # 回退到AkShare
        for provider in self.providers:
            if isinstance(provider, AkShareDataProvider):
                result = provider.get_limit_list(trade_date)
                if result:
                    self._mark_success("AkShare", "limit_list_d")
                    print(f"✅ [limit_list_d] 使用数据源: AkShare")
                    return result
        
        return None
    
    def get_news(self, src=None, start_date=None, end_date=None):
        """
        获取新闻快讯数据
        
        Args:
            src: 新闻来源（可选）
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            新闻列表
        """
        # 尝试从Tushare获取
        if self.providers and isinstance(self.providers[0], RealDataProvider):
            try:
                params = {}
                if src:
                    params["src"] = src
                if start_date:
                    params["start_date"] = start_date
                if end_date:
                    params["end_date"] = end_date
                
                data = self.providers[0].call_tushare_api(
                    "news",
                    params=params,
                    fields="title,content,pub_time,src,channels"
                )
                
                if data and data.get("items"):
                    result = []
                    fields = data["fields"]
                    for item in data["items"]:
                        item_data = {}
                        for i, field in enumerate(fields):
                            if i < len(item):
                                item_data[field] = item[i]
                        result.append(item_data)
                    self._mark_success("Tushare", "news")
                    print(f"✅ [news] 使用数据源: Tushare")
                    return result
            except Exception as e:
                print(f"⚠️ [news] Tushare失败: {e}")
        
        # 回退到AkShare
        for provider in self.providers:
            if isinstance(provider, AkShareDataProvider):
                result = provider.get_stock_news()
                if result:
                    self._mark_success("AkShare", "news")
                    print(f"✅ [news] 使用数据源: AkShare")
                    return result
        
        return None


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
def get_data_provider(use_real_data=True, token=None, enable_mock=False):
    """
    获取数据提供者实例
    
    Args:
        use_real_data: 是否使用真实数据
        token: Tushare Pro API token
        enable_mock: 是否显式启用 Mock 回退
        
    Returns:
        数据提供者实例（默认仅保留真实数据链路）
    """
    if use_real_data:
        try:
            provider = FallbackDataProvider(token, enable_mock=enable_mock)
            print("✅ 真实数据链路初始化完成")
            return provider
        except Exception as e:
            print(f"⚠️ 初始化数据提供者失败: {e}")
            return FallbackDataProvider(token=None, enable_mock=enable_mock)
    if enable_mock:
        print("ℹ️ 使用 Mock 演示数据模式")
        return MockDataProvider()
    return FallbackDataProvider(token=None, enable_mock=False)


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("测试三层数据源架构")
    print("=" * 60)
    
    # 测试模拟数据
    print("\n【测试1】模拟数据提供者...")
    mock_provider = MockDataProvider()
    holdings = mock_provider.get_all_holdings_data()
    print(f"✅ 模拟持仓数据: {len(holdings)} 只股票")
    
    # 测试三层数据源架构（无 Token 也可测试 AkShare/Mock 回退）
    token = os.getenv('TUSHARE_TOKEN')
    print("\n【测试2】三层数据源架构初始化...")
    if token:
        print(f"检测到 Tushare Token: {token[:8]}...")
    else:
        print("⚠️ 未检测到 Tushare Token，将测试 AkShare / Mock 回退链路")
        
    try:
        # 初始化三层数据源
        provider = get_data_provider(use_real_data=True, token=token)
        
        print("\n【测试3】测试北向资金接口...")
        north_data = provider.get_moneyflow_hsgt() if hasattr(provider, "get_moneyflow_hsgt") else None
        if north_data:
            print(f"✅ 北向资金数据: {len(north_data)} 条记录")
            print(f"   最新: {north_data[0] if north_data else '无数据'}")
        else:
            print("⚠️ 北向资金暂无可用数据")
        
        print("\n【测试4】测试指数日线接口...")
        index_data = provider.get_index_daily("000001.SH") if hasattr(provider, "get_index_daily") else None
        if index_data:
            print(f"✅ 上证指数日线: {len(index_data)} 条记录")
            print(f"   最新: {index_data[-1] if index_data else '无数据'}")
        else:
            print("⚠️ 指数日线暂无可用数据")
        
        print("\n【测试5】测试涨停池接口...")
        limit_list = provider.get_limit_list_d() if hasattr(provider, "get_limit_list_d") else None
        if limit_list:
            print(f"✅ 涨停股票数: {len(limit_list)} 只")
        else:
            print("⚠️ 涨停池暂无可用数据")
        
        print("\n【测试6】测试实时价格...")
        price = provider.get_stock_realtime_price("601868.SH")
        print(f"✅ 中国能建实时价格: {price}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
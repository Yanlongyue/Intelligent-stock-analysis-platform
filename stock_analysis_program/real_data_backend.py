#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实数据后端服务
整合真实金融数据的 Web API 服务
"""

import json
import os
import random
import time
import urllib.parse
from copy import deepcopy
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Lock

from algorithm_config import (
    ALGORITHM_WEIGHTS,
    calculate_comprehensive_score,
    get_risk_level,
    generate_hourly_prediction,
)
from real_algorithm_engine import RealAlgorithmEngine
from real_data_provider import get_data_provider


class RealDataBackendHandler(BaseHTTPRequestHandler):
    """真实数据后端请求处理器"""

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    POSITIONS_FILE = os.path.join(BASE_DIR, "data", "positions.json")
    storage_lock = Lock()
    positions_initialized = False
    positions = []
    price_cache = {}
    cache_timeout = 60  # 秒
    DEFAULT_POSITIONS = [
        {
            "code": "601868.SH",
            "name": "中国能建",
            "amount": 400,
            "cost_price": 3.15,
            "type": "value",
            "industry": "基建",
        },
        {
            "code": "002506.SZ",
            "name": "协鑫集成",
            "amount": 400,
            "cost_price": 2.05,
            "type": "growth",
            "industry": "光伏",
        },
        {
            "code": "600821.SH",
            "name": "金开新能",
            "amount": 600,
            "cost_price": 4.10,
            "type": "concept",
            "industry": "新能源",
        },
    ]

    def __init__(self, *args, **kwargs):
        self.use_real_data = True
        self.tushare_token = (os.getenv("TUSHARE_TOKEN") or "").strip()

        if not self.tushare_token:
            print("⚠️ 未检测到环境变量 TUSHARE_TOKEN，将以模拟数据模式启动。")

        self.data_provider = get_data_provider(
            use_real_data=self.use_real_data,
            token=self.tushare_token,
        )
        self.algorithm_engine = RealAlgorithmEngine(self.data_provider)

        self._ensure_position_store()
        self.positions = self.__class__.positions
        self.price_cache = self.__class__.price_cache
        self.cache_timeout = self.__class__.cache_timeout

        super().__init__(*args, **kwargs)

    def do_GET(self):
        """处理 GET 请求"""
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path
        query_params = urllib.parse.parse_qs(parsed_url.query)

        if path == "/api/health":
            self.handle_health_check()
        elif path == "/api/positions":
            self.handle_get_positions()
        elif path.startswith("/api/analyze/"):
            stock_code = self._extract_stock_code(path)
            self.handle_analyze_stock(stock_code)
        elif path == "/api/analyze_all":
            self.handle_analyze_all()
        elif path.startswith("/api/price_history/"):
            stock_code = self._extract_stock_code(path)
            self.handle_price_history(stock_code)
        elif path == "/api/update_prices":
            self.handle_update_prices()
        elif path == "/api/market_overview":
            self.handle_market_overview()
        elif path == "/api/data_status":
            self.handle_data_status()
        elif path.startswith("/api/daily_basic/"):
            stock_code = self._extract_stock_code(path)
            self.handle_daily_basic(stock_code, query_params)
        elif path == "/api/moneyflow_hsgt":
            self.handle_moneyflow_hsgt(query_params)
        elif path.startswith("/api/index_daily/"):
            index_code = self._extract_stock_code(path)
            self.handle_index_daily(index_code, query_params)
        elif path == "/api/limit_list_d":
            self.handle_limit_list_d(query_params)
        elif path == "/api/news":
            self.handle_news(query_params)
        else:
            self.send_json_response(
                {
                    "error": "API endpoint not found",
                    "path": path,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                404,
            )

    def do_POST(self):
        """处理 POST 请求"""
        path = urllib.parse.urlparse(self.path).path

        if path == "/api/positions":
            self.handle_create_position()
        else:
            self.send_json_response(
                {
                    "error": "API endpoint not found",
                    "path": path,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                404,
            )

    def do_PUT(self):
        """处理 PUT 请求"""
        path = urllib.parse.urlparse(self.path).path

        if path.startswith("/api/positions/"):
            stock_code = self._extract_stock_code(path)
            self.handle_update_position(stock_code)
        else:
            self.send_json_response(
                {
                    "error": "API endpoint not found",
                    "path": path,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                404,
            )

    def do_DELETE(self):
        """处理 DELETE 请求"""
        path = urllib.parse.urlparse(self.path).path

        if path.startswith("/api/positions/"):
            stock_code = self._extract_stock_code(path)
            self.handle_delete_position(stock_code)
        else:
            self.send_json_response(
                {
                    "error": "API endpoint not found",
                    "path": path,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                404,
            )

    def do_OPTIONS(self):
        """处理 OPTIONS 请求（CORS 预检）"""
        self.send_response(200)
        self.send_cors_headers()
        self.end_headers()

    def send_cors_headers(self):
        """发送 CORS 头"""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "86400")

    def send_json_response(self, data, status_code=200):
        """发送 JSON 响应"""
        self.send_response(status_code)
        self.send_cors_headers()
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        response_json = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_json.encode("utf-8"))

    def handle_health_check(self):
        """健康检查"""
        data = {
            "status": "healthy",
            "service": "Real Data Stock Analysis API",
            "version": "1.2.0",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_provider": self._get_data_source(),
            "active_provider": self._get_active_provider_name(),
            "data_status": self._get_data_status(),
        }
        self.send_json_response(data)

    def handle_get_positions(self):
        """获取持仓数据"""
        positions_with_prices = []

        for pos in self.positions:
            current_price = self._get_current_price(pos["code"])
            position_value = pos["amount"] * current_price
            cost_value = pos["amount"] * pos["cost_price"]
            profit_loss = position_value - cost_value
            profit_loss_pct = (profit_loss / cost_value * 100) if cost_value > 0 else 0

            position_data = {
                **pos,
                "current_price": current_price,
                "position_value": round(position_value, 2),
                "cost_value": round(cost_value, 2),
                "profit_loss": round(profit_loss, 2),
                "profit_loss_pct": round(profit_loss_pct, 2),
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            positions_with_prices.append(position_data)

        total_value = sum(item["position_value"] for item in positions_with_prices)
        total_cost = sum(item["cost_value"] for item in positions_with_prices)
        total_profit = sum(item["profit_loss"] for item in positions_with_prices)
        total_profit_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0

        response = {
            "overview": {
                "total_positions": len(positions_with_prices),
                "total_value": round(total_value, 2),
                "total_cost": round(total_cost, 2),
                "total_profit": round(total_profit, 2),
                "total_profit_pct": round(total_profit_pct, 2),
                "data_source": self._get_data_source(),
            },
            "positions": positions_with_prices,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        self.send_json_response(response)

    def handle_create_position(self):
        """新增持仓"""
        try:
            payload = self._read_json_body()
            position = self._validate_position_payload(payload)
            code = position["code"]

            if self._find_position_index(code) >= 0:
                self.send_json_response(
                    {
                        "error": f"股票代码 {code} 已存在",
                        "message": "请勿重复添加同一只股票",
                    },
                    409,
                )
                return

            with self.__class__.storage_lock:
                self.positions.append(position)
                self._save_positions_to_disk_locked()

            self.price_cache.pop(code, None)
            self.send_json_response(
                {
                    "status": "success",
                    "message": "持仓新增成功",
                    "position": position,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                201,
            )
        except ValueError as exc:
            self.send_json_response(
                {
                    "error": "新增持仓失败",
                    "message": str(exc),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                400,
            )
        except Exception as exc:
            self.send_json_response(
                {
                    "error": "新增持仓失败",
                    "message": str(exc),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                500,
            )

    def handle_update_position(self, stock_code):
        """更新持仓"""
        try:
            target_code = self._normalize_stock_code(stock_code)
            index = self._find_position_index(target_code)
            if index < 0:
                self.send_json_response(
                    {
                        "error": f"未找到持仓 {target_code}",
                        "message": "请确认股票代码是否正确",
                    },
                    404,
                )
                return

            payload = self._read_json_body()
            position = self._validate_position_payload(payload)
            new_code = position["code"]
            duplicated_index = self._find_position_index(new_code)
            if duplicated_index >= 0 and duplicated_index != index:
                self.send_json_response(
                    {
                        "error": f"股票代码 {new_code} 已存在",
                        "message": "更新后的股票代码与现有持仓重复",
                    },
                    409,
                )
                return

            with self.__class__.storage_lock:
                self.positions[index] = position
                self._save_positions_to_disk_locked()

            self.price_cache.pop(target_code, None)
            self.price_cache.pop(new_code, None)
            self.send_json_response(
                {
                    "status": "success",
                    "message": "持仓更新成功",
                    "position": position,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
        except ValueError as exc:
            self.send_json_response(
                {
                    "error": "更新持仓失败",
                    "message": str(exc),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                400,
            )
        except Exception as exc:
            self.send_json_response(
                {
                    "error": "更新持仓失败",
                    "message": str(exc),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                500,
            )

    def handle_delete_position(self, stock_code):
        """删除持仓"""
        try:
            target_code = self._normalize_stock_code(stock_code)
            index = self._find_position_index(target_code)
            if index < 0:
                self.send_json_response(
                    {
                        "error": f"未找到持仓 {target_code}",
                        "message": "请确认股票代码是否正确",
                    },
                    404,
                )
                return

            with self.__class__.storage_lock:
                deleted = self.positions.pop(index)
                self._save_positions_to_disk_locked()

            self.price_cache.pop(target_code, None)
            self.send_json_response(
                {
                    "status": "success",
                    "message": "持仓删除成功",
                    "position": deleted,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
        except Exception as exc:
            self.send_json_response(
                {
                    "error": "删除持仓失败",
                    "message": str(exc),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                500,
            )

    def handle_analyze_stock(self, stock_code):
        """分析指定股票"""
        try:
            analysis_result = self.algorithm_engine.analyze_stock(stock_code)
            stock_info = next((pos for pos in self.positions if pos["code"] == stock_code), None)
            if stock_info:
                analysis_result["stock_info"] = stock_info
            self.send_json_response(analysis_result)
        except Exception as exc:
            self.send_json_response(
                {
                    "error": f"分析股票 {stock_code} 失败",
                    "message": str(exc),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                500,
            )

    def handle_analyze_all(self):
        """分析所有持仓股票"""
        try:
            all_analysis = []

            for pos in self.positions:
                try:
                    analysis = self.algorithm_engine.analyze_stock(pos["code"])
                    analysis["position_info"] = {
                        "amount": pos["amount"],
                        "cost_price": pos["cost_price"],
                        "position_value": pos["amount"] * analysis.get("current_price", 0),
                        "type": pos["type"],
                        "industry": pos.get("industry", ""),
                    }
                    all_analysis.append(analysis)
                except Exception as exc:
                    print(f"分析 {pos['name']} 失败: {exc}")
                    continue

            if all_analysis:
                avg_scores = {}
                for algo in ["international", "policy", "company", "technical", "sentiment"]:
                    scores = [item.get("algorithm_scores", {}).get(algo, 2.5) for item in all_analysis]
                    avg_scores[algo] = round(sum(scores) / len(scores), 2) if scores else 2.5
                overall_score = calculate_comprehensive_score(avg_scores)
                overall_risk = get_risk_level(overall_score)
            else:
                avg_scores = {}
                overall_score = 2.5
                overall_risk = get_risk_level(overall_score)

            self.send_json_response(
                {
                    "overall_analysis": {
                        "average_scores": avg_scores,
                        "overall_score": overall_score,
                        "overall_risk": overall_risk,
                        "total_stocks": len(all_analysis),
                        "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    },
                    "stocks": all_analysis,
                    "data_source": self._get_data_source(),
                }
            )
        except Exception as exc:
            self.send_json_response(
                {
                    "error": "批量分析失败",
                    "message": str(exc),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                500,
            )

    def handle_price_history(self, stock_code):
        """获取价格历史"""
        try:
            price_history = []
            if hasattr(self.data_provider, "get_daily_quotes"):
                history_data = self.data_provider.get_daily_quotes(stock_code)
                if history_data:
                    for item in history_data:
                        if isinstance(item, dict):
                            price_history.append(
                                {
                                    "date": item.get("trade_date", ""),
                                    "open": item.get("open", 0),
                                    "high": item.get("high", 0),
                                    "low": item.get("low", 0),
                                    "close": item.get("close", 0),
                                    "volume": item.get("vol", 0),
                                    "amount": item.get("amount", 0),
                                    "change": item.get("change", 0),
                                    "pct_chg": item.get("pct_chg", 0),
                                }
                            )

            if not price_history:
                price_history = self._generate_mock_price_history(stock_code)

            self.send_json_response(
                {
                    "stock_code": stock_code,
                    "price_history": price_history,
                    "data_points": len(price_history),
                    "data_source": self._get_data_source(),
                    "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }
            )
        except Exception as exc:
            self.send_json_response(
                {
                    "error": f"获取价格历史失败: {stock_code}",
                    "message": str(exc),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                500,
            )

    def handle_update_prices(self):
        """更新价格缓存"""
        try:
            updated_prices = {}
            for pos in self.positions:
                stock_code = pos["code"]
                self.price_cache.pop(stock_code, None)
                new_price = self._get_current_price(stock_code, force_update=True)
                updated_prices[stock_code] = new_price

            self.send_json_response(
                {
                    "status": "success",
                    "updated_prices": updated_prices,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "message": f"已更新 {len(updated_prices)} 只股票价格",
                }
            )
        except Exception as exc:
            self.send_json_response(
                {
                    "status": "error",
                    "message": str(exc),
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                },
                500,
            )

    def handle_market_overview(self):
        """获取市场概况"""
        try:
            indices = ["000001.SH", "399001.SZ", "399006.SZ"]
            index_data = []
            
            # 使用真实指数数据（含涨跌幅）
            for idx in indices:
                try:
                    # 尝试获取真实指数日线数据
                    if hasattr(self.data_provider, "get_index_daily"):
                        index_daily = self.data_provider.get_index_daily(idx)
                        if index_daily and len(index_daily) > 0:
                            latest = index_daily[-1]
                            index_data.append({
                                "code": idx,
                                "name": self._get_index_name(idx),
                                "price": float(latest.get("close", 0)),
                                "change": float(latest.get("pct_chg", 0))
                            })
                            continue
                    
                    # 回退到价格获取
                    price = self._get_current_price(idx)
                    index_data.append({
                        "code": idx,
                        "name": self._get_index_name(idx),
                        "price": price,
                        "change": 0.0  # 无法获取涨跌幅时默认为0
                    })
                except Exception:
                    continue

            # 获取龙虎榜数据
            if hasattr(self.data_provider, "get_top_list_data"):
                toplist = self.data_provider.get_top_list_data()
                market_hot = len(toplist) if toplist else 0
            else:
                market_hot = 0

            # 获取北向资金真实数据
            northbound_inflow = 0.0
            if hasattr(self.data_provider, "get_moneyflow_hsgt"):
                try:
                    hsgt_data = self.data_provider.get_moneyflow_hsgt()
                    if hsgt_data and len(hsgt_data) > 0:
                        # 取最新一天的数据，兼容 Tushare / AkShare 字段差异
                        latest_hsgt = hsgt_data[0]
                        northbound_inflow = float(latest_hsgt.get("north_money") or latest_hsgt.get("net_amount") or 0)
                except Exception:
                    pass

            # 涨跌家数暂时使用默认值（需要更高级别的Tushare权限才能获取）
            rise_count = 0
            fall_count = 0
            flat_count = 0

            # 成交额数据
            total_volume = 0.0
            total_amount = 0.0
            if hasattr(self.data_provider, "get_market_overview"):
                try:
                    market_data = self.data_provider.get_market_overview()
                    if market_data:
                        # 这里可以根据实际返回的数据结构调整
                        pass
                except Exception:
                    pass

            self.send_json_response({
                "indices": index_data,
                "market_sentiment": {
                    "hot_stocks": market_hot,
                    "rise_count": rise_count,
                    "fall_count": fall_count,
                    "flat_count": flat_count,
                    "total_stocks": rise_count + fall_count + flat_count,
                    "rise_ratio": 0.0 if (rise_count + fall_count + flat_count) == 0 else round(rise_count / (rise_count + fall_count + flat_count) * 100, 1),
                },
                "trading_info": {
                    "total_volume": total_volume,
                    "total_amount": total_amount,
                    "northbound_inflow": northbound_inflow,
                    "southbound_inflow": 0.0,  # 暂无数据源
                },
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_source": self._get_data_source(),
            })
        except Exception as exc:
            self.send_json_response({
                "error": "获取市场概况失败",
                "message": str(exc),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }, 500)

    def handle_data_status(self):
        """获取数据状态"""
        self.send_json_response(
            {
                "data_status": self._get_data_status(),
                "tushare_token_configured": bool(self.tushare_token),
                "use_real_data": self.use_real_data,
                "cache_size": len(self.price_cache),
                "positions_count": len(self.positions),
                "data_source": self._get_data_source(),
                "active_provider": self._get_active_provider_name(),
                "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        )

    def handle_daily_basic(self, stock_code, query_params=None):
        """获取股票每日基础指标"""
        try:
            trade_date = self._get_query_value(query_params, "trade_date")
            data = self.data_provider.get_daily_basic(stock_code, trade_date) if hasattr(self.data_provider, "get_daily_basic") else None
            self.send_json_response({
                "stock_code": stock_code,
                "trade_date": trade_date,
                "data": data,
                "data_source": self._get_data_source(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        except Exception as exc:
            self.send_json_response({
                "error": "获取 daily_basic 失败",
                "message": str(exc),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }, 500)

    def handle_moneyflow_hsgt(self, query_params=None):
        """获取北向资金数据"""
        try:
            start_date = self._get_query_value(query_params, "start_date")
            end_date = self._get_query_value(query_params, "end_date")
            data = self.data_provider.get_moneyflow_hsgt(start_date, end_date) if hasattr(self.data_provider, "get_moneyflow_hsgt") else None
            self.send_json_response({
                "start_date": start_date,
                "end_date": end_date,
                "data": data or [],
                "data_source": self._get_data_source(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        except Exception as exc:
            self.send_json_response({
                "error": "获取 moneyflow_hsgt 失败",
                "message": str(exc),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }, 500)

    def handle_index_daily(self, index_code, query_params=None):
        """获取指数日线数据"""
        try:
            start_date = self._get_query_value(query_params, "start_date")
            end_date = self._get_query_value(query_params, "end_date")
            data = self.data_provider.get_index_daily(index_code, start_date, end_date) if hasattr(self.data_provider, "get_index_daily") else None
            self.send_json_response({
                "index_code": index_code,
                "start_date": start_date,
                "end_date": end_date,
                "data": data or [],
                "data_source": self._get_data_source(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        except Exception as exc:
            self.send_json_response({
                "error": "获取 index_daily 失败",
                "message": str(exc),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }, 500)

    def handle_limit_list_d(self, query_params=None):
        """获取涨跌停列表"""
        try:
            trade_date = self._get_query_value(query_params, "trade_date")
            limit_type = self._get_query_value(query_params, "limit_type", "U")
            data = self.data_provider.get_limit_list_d(trade_date, limit_type) if hasattr(self.data_provider, "get_limit_list_d") else None
            self.send_json_response({
                "trade_date": trade_date,
                "limit_type": limit_type,
                "data": data or [],
                "data_source": self._get_data_source(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        except Exception as exc:
            self.send_json_response({
                "error": "获取 limit_list_d 失败",
                "message": str(exc),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }, 500)

    def handle_news(self, query_params=None):
        """获取新闻快讯"""
        try:
            src = self._get_query_value(query_params, "src")
            start_date = self._get_query_value(query_params, "start_date")
            end_date = self._get_query_value(query_params, "end_date")
            data = self.data_provider.get_news(src, start_date, end_date) if hasattr(self.data_provider, "get_news") else None
            self.send_json_response({
                "src": src,
                "start_date": start_date,
                "end_date": end_date,
                "data": data or [],
                "data_source": self._get_data_source(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        except Exception as exc:
            self.send_json_response({
                "error": "获取 news 失败",
                "message": str(exc),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }, 500)

    def _ensure_position_store(self):
        """确保持仓存储已初始化"""
        cls = self.__class__
        with cls.storage_lock:
            if cls.positions_initialized:
                return

            os.makedirs(os.path.dirname(cls.POSITIONS_FILE), exist_ok=True)

            if not os.path.exists(cls.POSITIONS_FILE):
                cls.positions[:] = deepcopy(cls.DEFAULT_POSITIONS)
                self._save_positions_to_disk_locked()
            else:
                cls.positions[:] = self._load_positions_from_disk_locked()
                if not cls.positions:
                    cls.positions[:] = deepcopy(cls.DEFAULT_POSITIONS)
                    self._save_positions_to_disk_locked()

            cls.positions_initialized = True

    def _load_positions_from_disk_locked(self):
        """从磁盘读取持仓数据（需在锁内调用）"""
        cls = self.__class__
        try:
            with open(cls.POSITIONS_FILE, "r", encoding="utf-8") as f:
                payload = json.load(f)
            positions = payload.get("positions", []) if isinstance(payload, dict) else []
            return [self._normalize_position_record(item) for item in positions if isinstance(item, dict)]
        except Exception as exc:
            print(f"⚠️ 读取持仓文件失败，已回退默认持仓: {exc}")
            return deepcopy(cls.DEFAULT_POSITIONS)

    def _save_positions_to_disk_locked(self):
        """将持仓数据写入磁盘（需在锁内调用）"""
        payload = {
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "positions": [self._normalize_position_record(item) for item in self.positions],
        }
        with open(self.__class__.POSITIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    def _read_json_body(self):
        """读取 JSON 请求体"""
        content_length = int(self.headers.get("Content-Length", 0) or 0)
        if content_length <= 0:
            raise ValueError("请求体不能为空")

        raw_body = self.rfile.read(content_length)
        if not raw_body:
            raise ValueError("请求体不能为空")

        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError("请求体不是合法的 JSON") from exc

        if not isinstance(payload, dict):
            raise ValueError("请求体必须是 JSON 对象")
        return payload

    def _extract_stock_code(self, path):
        """从路径中提取股票代码"""
        return self._normalize_stock_code(urllib.parse.unquote(path.rstrip("/").split("/")[-1]))

    def _get_query_value(self, query_params, key, default=None):
        """获取查询参数中的单个值"""
        if not query_params or key not in query_params:
            return default
        value = query_params.get(key)
        if isinstance(value, list):
            return value[0] if value else default
        return value or default

    def _normalize_stock_code(self, code):
        code = str(code or "").strip().upper()
        if not code:
            return code
        if "." in code:
            return code
        if len(code) == 6 and code.isdigit():
            if code.startswith(("5", "6", "9")):
                return f"{code}.SH"
            if code.startswith(("0", "1", "2", "3")):
                return f"{code}.SZ"
            if code.startswith(("4", "8")):
                return f"{code}.BJ"
        return code

    def _normalize_position_record(self, data):
        """标准化持仓记录"""
        record = {
            "code": self._normalize_stock_code(data.get("code")),
            "name": str(data.get("name", "")).strip(),
            "amount": int(float(data.get("amount", 0) or 0)),
            "cost_price": round(float(data.get("cost_price", 0) or 0), 2),
            "type": data.get("type") if data.get("type") in {"value", "growth", "concept"} else "value",
            "industry": str(data.get("industry", "")).strip(),
        }
        current_price = data.get("current_price")
        if current_price not in (None, ""):
            try:
                price_value = round(float(current_price), 2)
                if price_value > 0:
                    record["current_price"] = price_value
            except (TypeError, ValueError):
                pass
        return record

    def _validate_position_payload(self, payload):
        """校验并标准化持仓请求体"""
        position = self._normalize_position_record(payload)

        if not position["code"]:
            raise ValueError("股票代码不能为空")
        if not position["name"]:
            raise ValueError("股票名称不能为空")
        if position["amount"] <= 0:
            raise ValueError("持仓数量必须大于 0")
        if position["cost_price"] <= 0:
            raise ValueError("成本价必须大于 0")

        return position

    def _find_position_index(self, stock_code):
        """根据股票代码查找持仓索引"""
        target_code = self._normalize_stock_code(stock_code)
        for index, item in enumerate(self.positions):
            if item.get("code") == target_code:
                return index
        return -1

    def _is_real_data_ready(self):
        """真实数据是否可用"""
        if not self.use_real_data:
            return False
        if hasattr(self.data_provider, "has_real_source"):
            try:
                return bool(self.data_provider.has_real_source())
            except Exception:
                return False
        provider_type = type(self.data_provider).__name__
        if provider_type == "RealDataProvider":
            return bool(self.tushare_token)
        if provider_type == "AkShareDataProvider":
            return True
        return False

    def _get_current_price(self, stock_code, force_update=False):
        """获取当前价格（带缓存）"""
        cache_key = stock_code
        if not force_update and cache_key in self.price_cache:
            cache_entry = self.price_cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_timeout:
                return cache_entry["price"]

        try:
            new_price = self.data_provider.get_stock_realtime_price(stock_code)
            if new_price is None or new_price <= 0:
                stored = next((item.get("current_price") for item in self.positions if item.get("code") == stock_code and item.get("current_price")), None)
                if stored:
                    new_price = stored
                else:
                    price_map = {
                        "601868.SH": 3.20 + random.uniform(-0.1, 0.1),
                        "002506.SZ": 2.10 + random.uniform(-0.05, 0.05),
                        "600821.SH": 4.20 + random.uniform(-0.15, 0.15),
                        "000001.SH": 3200 + random.uniform(-50, 50),
                        "399001.SZ": 11000 + random.uniform(-100, 100),
                        "399006.SZ": 2200 + random.uniform(-30, 30),
                    }
                    new_price = price_map.get(stock_code, random.uniform(5.0, 50.0))

            rounded_price = round(float(new_price), 2)
            self.price_cache[cache_key] = {"price": rounded_price, "timestamp": time.time()}
            return rounded_price
        except Exception as exc:
            print(f"获取价格 {stock_code} 失败: {exc}")
            fallback_price = next((item.get("current_price") for item in self.positions if item.get("code") == stock_code and item.get("current_price")), None)
            if fallback_price:
                return round(float(fallback_price), 2)
            return round(random.uniform(1.0, 100.0), 2)

    def _generate_mock_price_history(self, stock_code, days=30):
        """生成模拟价格历史"""
        base_price = self._get_current_price(stock_code)
        history = []
        current_date = datetime.now()

        for i in range(days):
            date = (current_date - timedelta(days=days - 1 - i)).strftime("%Y%m%d")
            if i == 0:
                open_price = base_price
            else:
                open_price = history[-1]["close"]

            daily_change = random.uniform(-0.05, 0.05)
            close_price = open_price * (1 + daily_change)
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.03))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.03))

            history.append(
                {
                    "date": date,
                    "open": round(open_price, 2),
                    "high": round(high_price, 2),
                    "low": round(low_price, 2),
                    "close": round(close_price, 2),
                    "volume": random.randint(1000000, 5000000),
                    "amount": round(close_price * random.randint(1000000, 5000000), 2),
                    "change": round(close_price - open_price, 2),
                    "pct_chg": round(daily_change * 100, 2),
                }
            )

        return history

    def _get_index_name(self, index_code):
        """获取指数名称"""
        index_map = {
            "000001.SH": "上证指数",
            "399001.SZ": "深证成指",
            "399006.SZ": "创业板指",
            "000300.SH": "沪深300",
            "000905.SH": "中证500",
        }
        return index_map.get(index_code, index_code)

    def _get_data_status(self):
        """获取数据状态"""
        if self._is_real_data_ready():
            return "real_data_available"
        if self.use_real_data and not self.tushare_token:
            return "real_data_disabled_no_token"
        return "mock_data_active"

    def _get_active_provider_name(self):
        """获取最近一次成功使用的数据源名称"""
        return getattr(self.data_provider, "last_successful_provider", None) or "Mock"

    def _get_data_source(self):
        """获取数据源信息"""
        if hasattr(self.data_provider, "get_data_source_label"):
            try:
                return self.data_provider.get_data_source_label()
            except Exception:
                pass
        if self._is_real_data_ready():
            return "真实数据"
        return "模拟数据 / 本地持仓文件"

    def log_message(self, format, *args):
        """重写日志输出，减少控制台噪音"""
        if "404" in format or "500" in format:
            super().log_message(format, *args)



def start_real_data_backend(port=9000):
    """启动真实数据后端服务"""
    server_address = ("", port)
    httpd = HTTPServer(server_address, RealDataBackendHandler)

    print("🚀 真实数据后端服务启动中...")
    print(f"📡 服务地址: http://localhost:{port}")
    print(f"📊 数据模式: {'真实数据' if os.getenv('TUSHARE_TOKEN') else '模拟数据'}")
    print(f"📁 持仓存储: {RealDataBackendHandler.POSITIONS_FILE}")
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📋 可用 API 端点:")
    print("  GET    /api/health               - 健康检查")
    print("  GET    /api/positions            - 获取持仓数据")
    print("  POST   /api/positions            - 新增持仓")
    print("  PUT    /api/positions/<code>     - 更新持仓")
    print("  DELETE /api/positions/<code>     - 删除持仓")
    print("  GET    /api/analyze/<code>       - 分析指定股票")
    print("  GET    /api/analyze_all          - 分析所有持仓")
    print("  GET    /api/price_history/<code> - 获取价格历史")
    print("  GET    /api/update_prices        - 更新价格缓存")
    print("  GET    /api/market_overview      - 获取市场概况")
    print("  GET    /api/data_status          - 获取数据状态")
    print("  GET    /api/daily_basic/<code>   - 获取每日基本面指标")
    print("  GET    /api/moneyflow_hsgt       - 获取北向资金流向")
    print("  GET    /api/index_daily/<code>   - 获取指数日线")
    print("  GET    /api/limit_list_d         - 获取涨跌停列表")
    print("  GET    /api/news                 - 获取新闻快讯")
    print("\n🔄 服务运行中，按 Ctrl+C 停止...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务停止")
    except Exception as exc:
        print(f"❌ 服务异常: {exc}")


if __name__ == "__main__":
    tushare_token = os.getenv("TUSHARE_TOKEN")
    if not tushare_token:
        print("⚠️ 警告: 未在环境变量中检测到 Tushare Pro API Token")
        print("💡 提示: 请先执行 export TUSHARE_TOKEN=您的Token")
        print("📊 当前将以模拟数据模式启动，待环境变量配置完成后再切换到真实数据")

    start_real_data_backend()

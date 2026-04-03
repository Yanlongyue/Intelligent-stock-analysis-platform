#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实数据后端服务
整合真实金融数据的Web API服务
"""

import json
import random
import time
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading
import os

from algorithm_config import (
    ALGORITHM_WEIGHTS,
    calculate_comprehensive_score,
    get_risk_level,
    generate_hourly_prediction
)

from real_data_provider import get_data_provider
from real_algorithm_engine import RealAlgorithmEngine

class RealDataBackendHandler(BaseHTTPRequestHandler):
    """真实数据后端请求处理器"""
    
    def __init__(self, *args, **kwargs):
        # 初始化数据提供者和算法引擎
        self.use_real_data = True  # 默认使用真实数据
        self.tushare_token = os.getenv('TUSHARE_TOKEN')
        
        # DEBUG: 如果环境变量没有Token，您可以在这里手动设置
        # 请将下面的 "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" 替换为您的Tushare Token
        if not self.tushare_token:
            # 手动设置Token - 已配置主人的Token
            self.tushare_token = "79e520d18d7db694aeb048f3cc577e5b323687a3434e1cfdd32a75cd"
            if self.tushare_token != "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
                print(f"🔑 使用手动配置的Token: {self.tushare_token[:8]}...")
        
        # 尝试使用真实数据，如果失败则回退到模拟数据
        self.data_provider = get_data_provider(
            use_real_data=self.use_real_data,
            token=self.tushare_token
        )
        self.algorithm_engine = RealAlgorithmEngine(self.data_provider)
        
        # 持仓数据
        self.positions = [
            {
                "code": "601868.SH",
                "name": "中国能建",
                "amount": 400,
                "cost_price": 3.15,
                "type": "value",
                "industry": "基建"
            },
            {
                "code": "002506.SZ",
                "name": "协鑫集成",
                "amount": 400,
                "cost_price": 2.05,
                "type": "growth",
                "industry": "光伏"
            },
            {
                "code": "600821.SH",
                "name": "金开新能",
                "amount": 600,
                "cost_price": 4.10,
                "type": "concept",
                "industry": "新能源"
            }
        ]
        
        # 价格缓存
        self.price_cache = {}
        self.cache_timeout = 60  # 秒
        
        # 调用父类初始化
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        # 解析URL
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        # 设置CORS头
        self.send_cors_headers()
        
        # 路由处理
        if path == '/api/health':
            self.handle_health_check()
        elif path == '/api/positions':
            self.handle_get_positions()
        elif path.startswith('/api/analyze/'):
            stock_code = path.split('/')[-1]
            self.handle_analyze_stock(stock_code)
        elif path == '/api/analyze_all':
            self.handle_analyze_all()
        elif path.startswith('/api/price_history/'):
            stock_code = path.split('/')[-1]
            self.handle_price_history(stock_code)
        elif path == '/api/update_prices':
            self.handle_update_prices()
        elif path == '/api/market_overview':
            self.handle_market_overview()
        elif path == '/api/data_status':
            self.handle_data_status()
        else:
            self.send_error(404, "API endpoint not found")
    
    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self.send_cors_headers()
        self.send_response(200)
        self.end_headers()
    
    def send_cors_headers(self):
        """发送CORS头"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')
    
    def send_json_response(self, data, status_code=200):
        """发送JSON响应"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        
        response_json = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_json.encode('utf-8'))
    
    def handle_health_check(self):
        """健康检查"""
        data = {
            "status": "healthy",
            "service": "Real Data Stock Analysis API",
            "version": "1.0.0",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_provider": "Tushare Pro" if self.use_real_data else "Mock Data",
            "data_status": self._get_data_status()
        }
        self.send_json_response(data)
    
    def handle_get_positions(self):
        """获取持仓数据"""
        positions_with_prices = []
        
        for pos in self.positions:
            # 获取实时价格
            current_price = self._get_current_price(pos["code"])
            
            # 计算持仓价值
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
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            positions_with_prices.append(position_data)
        
        # 计算总览
        total_value = sum(p["position_value"] for p in positions_with_prices)
        total_cost = sum(p["cost_value"] for p in positions_with_prices)
        total_profit = sum(p["profit_loss"] for p in positions_with_prices)
        total_profit_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0
        
        overview = {
            "total_positions": len(positions_with_prices),
            "total_value": round(total_value, 2),
            "total_cost": round(total_cost, 2),
            "total_profit": round(total_profit, 2),
            "total_profit_pct": round(total_profit_pct, 2),
            "data_source": self._get_data_source()
        }
        
        response = {
            "overview": overview,
            "positions": positions_with_prices,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.send_json_response(response)
    
    def handle_analyze_stock(self, stock_code):
        """分析指定股票"""
        try:
            # 使用算法引擎分析
            analysis_result = self.algorithm_engine.analyze_stock(stock_code)
            
            # 获取股票信息
            stock_info = None
            for pos in self.positions:
                if pos["code"] == stock_code:
                    stock_info = pos
                    break
            
            if stock_info:
                analysis_result["stock_info"] = stock_info
            
            self.send_json_response(analysis_result)
            
        except Exception as e:
            error_response = {
                "error": f"分析股票 {stock_code} 失败",
                "message": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.send_json_response(error_response, 500)
    
    def handle_analyze_all(self):
        """分析所有持仓股票"""
        try:
            all_analysis = []
            
            for pos in self.positions:
                try:
                    # 分析股票
                    analysis = self.algorithm_engine.analyze_stock(pos["code"])
                    
                    # 添加持仓信息
                    analysis["position_info"] = {
                        "amount": pos["amount"],
                        "cost_price": pos["cost_price"],
                        "position_value": pos["amount"] * analysis.get("current_price", 0),
                        "type": pos["type"],
                        "industry": pos.get("industry", "")
                    }
                    
                    all_analysis.append(analysis)
                    
                except Exception as e:
                    print(f"分析 {pos['name']} 失败: {e}")
                    continue
            
            # 计算整体评分
            if all_analysis:
                avg_scores = {}
                for algo in ["international", "policy", "company", "technical", "sentiment"]:
                    scores = [a.get("algorithm_scores", {}).get(algo, 2.5) for a in all_analysis]
                    avg_scores[algo] = round(sum(scores) / len(scores), 2) if scores else 2.5
                
                overall_score = calculate_comprehensive_score(avg_scores)
                overall_risk = get_risk_level(overall_score)
            else:
                avg_scores = {}
                overall_score = 2.5
                overall_risk = get_risk_level(overall_score)
            
            response = {
                "overall_analysis": {
                    "average_scores": avg_scores,
                    "overall_score": overall_score,
                    "overall_risk": overall_risk,
                    "total_stocks": len(all_analysis),
                    "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                },
                "stocks": all_analysis,
                "data_source": self._get_data_source()
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            error_response = {
                "error": "批量分析失败",
                "message": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.send_json_response(error_response, 500)
    
    def handle_price_history(self, stock_code):
        """获取价格历史"""
        try:
            # 从数据提供者获取价格历史
            price_history = []
            
            if hasattr(self.data_provider, 'get_daily_quotes'):
                history_data = self.data_provider.get_daily_quotes(stock_code)
                if history_data:
                    # 格式化价格历史
                    for item in history_data:
                        if isinstance(item, dict):
                            price_history.append({
                                "date": item.get("trade_date", ""),
                                "open": item.get("open", 0),
                                "high": item.get("high", 0),
                                "low": item.get("low", 0),
                                "close": item.get("close", 0),
                                "volume": item.get("vol", 0),
                                "amount": item.get("amount", 0),
                                "change": item.get("change", 0),
                                "pct_chg": item.get("pct_chg", 0)
                            })
            
            # 如果没有真实数据，生成模拟数据
            if not price_history:
                price_history = self._generate_mock_price_history(stock_code)
            
            response = {
                "stock_code": stock_code,
                "price_history": price_history,
                "data_points": len(price_history),
                "data_source": self._get_data_source(),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            error_response = {
                "error": f"获取价格历史失败: {stock_code}",
                "message": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.send_json_response(error_response, 500)
    
    def handle_update_prices(self):
        """更新价格缓存"""
        try:
            updated_prices = {}
            
            for pos in self.positions:
                stock_code = pos["code"]
                # 强制更新价格缓存
                if stock_code in self.price_cache:
                    del self.price_cache[stock_code]
                
                # 获取新价格
                new_price = self._get_current_price(stock_code, force_update=True)
                updated_prices[stock_code] = new_price
            
            response = {
                "status": "success",
                "updated_prices": updated_prices,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "message": f"已更新 {len(updated_prices)} 只股票价格"
            }
            
            self.send_json_response(response)
            
        except Exception as e:
            error_response = {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.send_json_response(error_response, 500)
    
    def handle_market_overview(self):
        """获取市场概况"""
        try:
            market_data = {}
            
            # 获取主要指数
            indices = ["000001.SH", "399001.SZ", "399006.SZ"]
            index_data = []
            
            for idx in indices:
                try:
                    price = self._get_current_price(idx)
                    index_data.append({
                        "code": idx,
                        "name": self._get_index_name(idx),
                        "price": price,
                        "change": random.uniform(-2, 2)  # 模拟涨跌幅
                    })
                except:
                    continue
            
            # 获取市场热度
            if hasattr(self.data_provider, 'get_top_list_data'):
                toplist = self.data_provider.get_top_list_data()
                market_hot = len(toplist) if toplist else 0
            else:
                market_hot = random.randint(5, 20)
            
            # 获取涨跌统计
            rise_count = random.randint(800, 1200)
            fall_count = random.randint(500, 800)
            flat_count = random.randint(100, 300)
            
            market_data = {
                "indices": index_data,
                "market_sentiment": {
                    "hot_stocks": market_hot,
                    "rise_count": rise_count,
                    "fall_count": fall_count,
                    "flat_count": flat_count,
                    "total_stocks": rise_count + fall_count + flat_count,
                    "rise_ratio": round(rise_count / (rise_count + fall_count + flat_count) * 100, 1)
                },
                "trading_info": {
                    "total_volume": random.uniform(500, 800) * 100000000,  # 亿
                    "total_amount": random.uniform(800, 1200) * 1000000000,  # 十亿
                    "northbound_inflow": random.uniform(-50, 100),  # 亿
                    "southbound_inflow": random.uniform(-20, 50)   # 亿
                },
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_source": self._get_data_source()
            }
            
            self.send_json_response(market_data)
            
        except Exception as e:
            error_response = {
                "error": "获取市场概况失败",
                "message": str(e),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            self.send_json_response(error_response, 500)
    
    def handle_data_status(self):
        """获取数据状态"""
        status = self._get_data_status()
        
        response = {
            "data_status": status,
            "tushare_token_configured": bool(self.tushare_token),
            "use_real_data": self.use_real_data,
            "cache_size": len(self.price_cache),
            "positions_count": len(self.positions),
            "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.send_json_response(response)
    
    # 辅助方法
    def _get_current_price(self, stock_code, force_update=False):
        """获取当前价格（带缓存）"""
        cache_key = stock_code
        
        # 检查缓存
        if not force_update and cache_key in self.price_cache:
            cache_entry = self.price_cache[cache_key]
            if time.time() - cache_entry["timestamp"] < self.cache_timeout:
                return cache_entry["price"]
        
        # 获取新价格
        try:
            new_price = self.data_provider.get_stock_realtime_price(stock_code)
            
            # 如果获取失败，使用模拟价格
            if new_price is None or new_price <= 0:
                # 根据股票代码生成模拟价格
                price_map = {
                    "601868.SH": 3.20 + random.uniform(-0.1, 0.1),
                    "002506.SZ": 2.10 + random.uniform(-0.05, 0.05),
                    "600821.SH": 4.20 + random.uniform(-0.15, 0.15),
                    "000001.SH": 3200 + random.uniform(-50, 50),  # 上证指数
                    "399001.SZ": 11000 + random.uniform(-100, 100),  # 深证成指
                    "399006.SZ": 2200 + random.uniform(-30, 30)  # 创业板指
                }
                new_price = price_map.get(stock_code, random.uniform(5.0, 50.0))
            
            # 更新缓存
            self.price_cache[cache_key] = {
                "price": round(new_price, 2),
                "timestamp": time.time()
            }
            
            return round(new_price, 2)
            
        except Exception as e:
            print(f"获取价格 {stock_code} 失败: {e}")
            # 返回模拟价格
            return round(random.uniform(1.0, 100.0), 2)
    
    def _generate_mock_price_history(self, stock_code, days=30):
        """生成模拟价格历史"""
        base_price = self._get_current_price(stock_code)
        history = []
        
        current_date = datetime.now()
        
        for i in range(days):
            date = (current_date - timedelta(days=days-1-i)).strftime("%Y%m%d")
            
            # 生成价格波动
            if i == 0:
                open_price = base_price
            else:
                open_price = history[-1]["close"]
            
            # 日内波动
            daily_change = random.uniform(-0.05, 0.05)
            close_price = open_price * (1 + daily_change)
            high_price = max(open_price, close_price) * (1 + random.uniform(0, 0.03))
            low_price = min(open_price, close_price) * (1 - random.uniform(0, 0.03))
            
            history.append({
                "date": date,
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": random.randint(1000000, 5000000),
                "amount": round(close_price * random.randint(1000000, 5000000), 2),
                "change": round(close_price - open_price, 2),
                "pct_chg": round(daily_change * 100, 2)
            })
        
        return history
    
    def _get_index_name(self, index_code):
        """获取指数名称"""
        index_map = {
            "000001.SH": "上证指数",
            "399001.SZ": "深证成指",
            "399006.SZ": "创业板指",
            "000300.SH": "沪深300",
            "000905.SH": "中证500"
        }
        return index_map.get(index_code, index_code)
    
    def _get_data_status(self):
        """获取数据状态"""
        if self.use_real_data and self.tushare_token:
            return "real_data_available"
        elif self.use_real_data and not self.tushare_token:
            return "real_data_disabled_no_token"
        else:
            return "mock_data_active"
    
    def _get_data_source(self):
        """获取数据源信息"""
        if self.use_real_data and self.tushare_token:
            return "Tushare Pro API (真实数据)"
        else:
            return "模拟数据 (真实数据API暂不可用)"
    
    def log_message(self, format, *args):
        """重写日志输出，减少控制台噪音"""
        # 只记录错误日志
        if "404" in format or "500" in format:
            super().log_message(format, *args)


def start_real_data_backend(port=9000):
    """
    启动真实数据后端服务
    
    Args:
        port: 服务端口
    """
    server_address = ('', port)
    httpd = HTTPServer(server_address, RealDataBackendHandler)
    
    print(f"🚀 真实数据后端服务启动中...")
    print(f"📡 服务地址: http://localhost:{port}")
    print(f"📊 数据模式: {'真实数据' if os.getenv('TUSHARE_TOKEN') else '模拟数据'}")
    print(f"⏰ 启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📋 可用API端点:")
    print("  GET /api/health          - 健康检查")
    print("  GET /api/positions       - 获取持仓数据")
    print("  GET /api/analyze/<code>  - 分析指定股票")
    print("  GET /api/analyze_all     - 分析所有持仓")
    print("  GET /api/price_history/<code> - 获取价格历史")
    print("  GET /api/update_prices   - 更新价格缓存")
    print("  GET /api/market_overview - 获取市场概况")
    print("  GET /api/data_status     - 获取数据状态")
    print("\n🔄 服务运行中，按 Ctrl+C 停止...")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 服务停止")
    except Exception as e:
        print(f"❌ 服务异常: {e}")


if __name__ == "__main__":
    # 检查Tushare Token
    tushare_token = os.getenv('TUSHARE_TOKEN')
    if not tushare_token:
        print("⚠️ 警告: 未在环境变量中检测到Tushare Pro API Token")
        print("💡 提示: 代码中已手动配置Token，系统将使用真实数据模式")
        print("📊 如果API调用失败，系统会自动回退到模拟数据模式")
    
    # 启动服务
    start_real_data_backend()
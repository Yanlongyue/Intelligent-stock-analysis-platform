#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五维度算法后端服务
为Web界面提供算法计算API
"""

import json
import random
import time
from datetime import datetime, timedelta
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import threading

from algorithm_config import (
    ALGORITHM_WEIGHTS,
    INTERNATIONAL_FACTORS,
    POLICY_FACTORS,
    COMPANY_FACTORS,
    TECHNICAL_FACTORS,
    SENTIMENT_FACTORS,
    SCORE_MAPPING,
    RISK_LEVEL_MAPPING,
    calculate_comprehensive_score,
    get_risk_level,
    generate_hourly_prediction
)

class StockData:
    """股票数据模拟"""
    
    def __init__(self):
        self.positions = [
            {
                "code": "601868.SH",
                "name": "中国能建",
                "amount": 400,
                "cost_price": 3.15,
                "current_price": 3.20,
                "type": "value",
                "industry": "基建"
            },
            {
                "code": "002506.SZ",
                "name": "协鑫集成",
                "amount": 400,
                "cost_price": 2.05,
                "current_price": 2.10,
                "type": "growth",
                "industry": "光伏"
            },
            {
                "code": "600821.SH",
                "name": "金开新能",
                "amount": 600,
                "cost_price": 4.10,
                "current_price": 4.20,
                "type": "concept",
                "industry": "新能源"
            }
        ]
        
        # 历史价格数据
        self.price_history = {}
        self.init_price_history()
    
    def init_price_history(self):
        """初始化历史价格数据"""
        base_prices = {
            "601868.SH": 3.20,
            "002506.SZ": 2.10,
            "600821.SH": 4.20
        }
        
        for code, base_price in base_prices.items():
            prices = []
            current_price = base_price
            for i in range(30):
                # 模拟价格波动
                change = random.uniform(-0.05, 0.05)
                current_price += change
                if current_price < base_price * 0.7:
                    current_price = base_price * 0.7
                if current_price > base_price * 1.3:
                    current_price = base_price * 1.3
                prices.append(round(current_price, 2))
            self.price_history[code] = prices
    
    def get_position_summary(self):
        """获取持仓摘要"""
        total_value = 0
        total_cost = 0
        
        for pos in self.positions:
            value = pos["amount"] * pos["current_price"]
            cost = pos["amount"] * pos["cost_price"]
            total_value += value
            total_cost += cost
        
        total_profit = total_value - total_cost
        profit_percentage = (total_profit / total_cost * 100) if total_cost > 0 else 0
        
        return {
            "total_value": round(total_value, 2),
            "total_cost": round(total_cost, 2),
            "total_profit": round(total_profit, 2),
            "profit_percentage": round(profit_percentage, 2),
            "position_count": len(self.positions)
        }
    
    def update_prices(self):
        """更新股价（模拟实时数据）"""
        for pos in self.positions:
            # 随机波动
            change = random.uniform(-0.02, 0.02)
            pos["current_price"] += change
            if pos["current_price"] < 0.1:
                pos["current_price"] = 0.1
            
            # 更新历史价格
            if pos["code"] in self.price_history:
                self.price_history[pos["code"]].append(round(pos["current_price"], 2))
                if len(self.price_history[pos["code"]]) > 100:  # 保留最近100个数据点
                    self.price_history[pos["code"]] = self.price_history[pos["code"]][-100:]

class FiveDimensionAlgorithm:
    """五维度算法引擎"""
    
    def __init__(self):
        self.stock_data = StockData()
    
    def calculate_international_score(self, stock_info):
        """计算国际局势评分"""
        # 模拟算法计算
        base_score = random.randint(2, 4)
        
        # 根据行业调整
        industry_impact = {
            "新能源": 0.5,   # 受国际政策影响较大
            "光伏": 0.3,
            "基建": -0.2,   # 相对稳定
            "科技": 0.4,
            "金融": -0.1
        }
        
        adjustment = industry_impact.get(stock_info.get("industry", ""), 0)
        score = max(0, min(5, base_score + adjustment))
        
        return {
            "score": round(score, 1),
            "factors": [
                {"name": "地缘政治", "value": random.randint(2, 4), "weight": 0.3},
                {"name": "经济环境", "value": random.randint(2, 4), "weight": 0.25},
                {"name": "货币政策", "value": random.randint(2, 4), "weight": 0.25},
                {"name": "大宗商品", "value": random.randint(2, 4), "weight": 0.2}
            ],
            "description": self._get_international_description(score)
        }
    
    def calculate_policy_score(self, stock_info):
        """计算国内政策评分"""
        base_score = random.randint(2, 4)
        
        # 政策敏感性行业
        policy_sensitive = {
            "新能源": 0.8,   # 政策大力支持
            "光伏": 0.6,
            "基建": 0.7,    # 基建投资加大
            "科技": 0.5,
            "金融": 0.3
        }
        
        adjustment = policy_sensitive.get(stock_info.get("industry", ""), 0)
        score = max(0, min(5, base_score + adjustment))
        
        return {
            "score": round(score, 1),
            "factors": [
                {"name": "产业政策", "value": random.randint(2, 5), "weight": 0.35},
                {"name": "金融政策", "value": random.randint(2, 4), "weight": 0.3},
                {"name": "税收政策", "value": random.randint(2, 4), "weight": 0.2},
                {"name": "区域政策", "value": random.randint(2, 4), "weight": 0.15}
            ],
            "description": self._get_policy_description(score)
        }
    
    def calculate_company_score(self, stock_info):
        """计算企业发展评分"""
        base_score = random.randint(2, 4)
        
        # 公司类型影响
        company_type_impact = {
            "value": 0.2,    # 价值股相对稳定
            "growth": -0.1,  # 成长股波动大
            "concept": -0.3  # 概念股风险高
        }
        
        adjustment = company_type_impact.get(stock_info.get("type", ""), 0)
        score = max(0, min(5, base_score + adjustment))
        
        return {
            "score": round(score, 1),
            "factors": [
                {"name": "财务表现", "value": random.randint(2, 4), "weight": 0.4},
                {"name": "管理层", "value": random.randint(2, 4), "weight": 0.2},
                {"name": "业务扩张", "value": random.randint(2, 4), "weight": 0.25},
                {"name": "风险事件", "value": random.randint(1, 3), "weight": 0.15}
            ],
            "description": self._get_company_description(score)
        }
    
    def calculate_technical_score(self, stock_info):
        """计算技术分析评分"""
        base_score = random.randint(2, 4)
        
        # 技术面分析
        technical_indicators = {
            "trend": random.choice(["上涨", "下跌", "震荡"]),
            "volume": random.choice(["放量", "缩量", "平稳"]),
            "support": random.randint(2, 4),
            "resistance": random.randint(2, 4)
        }
        
        # 根据技术指标调整
        if technical_indicators["trend"] == "上涨":
            adjustment = 0.3
        elif technical_indicators["trend"] == "下跌":
            adjustment = -0.3
        else:
            adjustment = 0
        
        score = max(0, min(5, base_score + adjustment))
        
        return {
            "score": round(score, 1),
            "factors": [
                {"name": "趋势分析", "value": random.randint(2, 4), "weight": 0.3},
                {"name": "动量指标", "value": random.randint(2, 4), "weight": 0.25},
                {"name": "成交量", "value": random.randint(2, 4), "weight": 0.25},
                {"name": "形态识别", "value": random.randint(2, 4), "weight": 0.2}
            ],
            "indicators": technical_indicators,
            "description": self._get_technical_description(score)
        }
    
    def calculate_sentiment_score(self, stock_info):
        """计算股民情绪评分"""
        base_score = random.randint(2, 4)
        
        # 市场情绪影响
        market_sentiment = random.choice(["恐慌", "谨慎", "中性", "乐观", "狂热"])
        sentiment_map = {
            "恐慌": -0.4,
            "谨慎": -0.2,
            "中性": 0,
            "乐观": 0.2,
            "狂热": 0.4
        }
        
        adjustment = sentiment_map.get(market_sentiment, 0)
        score = max(0, min(5, base_score + adjustment))
        
        return {
            "score": round(score, 1),
            "factors": [
                {"name": "社交媒体", "value": random.randint(2, 4), "weight": 0.35},
                {"name": "新闻情绪", "value": random.randint(2, 4), "weight": 0.3},
                {"name": "市场情绪", "value": random.randint(2, 4), "weight": 0.2},
                {"name": "搜索趋势", "value": random.randint(2, 4), "weight": 0.15}
            ],
            "market_sentiment": market_sentiment,
            "description": self._get_sentiment_description(score)
        }
    
    def analyze_stock(self, stock_code):
        """分析指定股票"""
        # 获取股票信息
        stock_info = None
        for pos in self.stock_data.positions:
            if pos["code"] == stock_code:
                stock_info = pos
                break
        
        if not stock_info:
            return {"error": "股票代码不存在"}
        
        # 计算各维度评分
        international = self.calculate_international_score(stock_info)
        policy = self.calculate_policy_score(stock_info)
        company = self.calculate_company_score(stock_info)
        technical = self.calculate_technical_score(stock_info)
        sentiment = self.calculate_sentiment_score(stock_info)
        
        # 计算综合评分
        scores = {
            "international": international["score"],
            "policy": policy["score"],
            "company": company["score"],
            "technical": technical["score"],
            "sentiment": sentiment["score"]
        }
        
        comprehensive_score = calculate_comprehensive_score(scores)
        risk_level = get_risk_level(comprehensive_score)
        
        # 生成小时级预测
        hourly_predictions = generate_hourly_prediction(
            stock_info["current_price"],
            scores
        )
        
        return {
            "stock_info": stock_info,
            "algorithm_scores": {
                "international": international,
                "policy": policy,
                "company": company,
                "technical": technical,
                "sentiment": sentiment
            },
            "comprehensive_score": comprehensive_score,
            "risk_level": risk_level,
            "hourly_predictions": hourly_predictions,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def get_all_positions_analysis(self):
        """分析所有持仓股票"""
        results = []
        for pos in self.stock_data.positions:
            analysis = self.analyze_stock(pos["code"])
            results.append(analysis)
        
        return results
    
    def _get_international_description(self, score):
        descriptions = [
            "国际局势极度紧张，战争风险高，建议立即避险",
            "国际关系紧张，制裁风险增加，需要高度警惕",
            "国际局势平稳，但存在不确定性，谨慎观察",
            "国际合作加强，外部环境改善，机会存在",
            "国际局势良好，全球化推进，积极信号",
            "国际环境极佳，和平发展为主，强烈看好"
        ]
        return descriptions[min(int(score), 5)]
    
    def _get_policy_description(self, score):
        descriptions = [
            "政策严厉收紧，行业监管加强，风险极高",
            "政策偏紧，限制性措施增多，需要警惕",
            "政策中性，无明显变化，保持观察",
            "政策支持，利好措施出台，机会显现",
            "政策大力支持，产业规划明确，积极信号",
            "政策红利释放，重大利好落地，强烈推荐"
        ]
        return descriptions[min(int(score), 5)]
    
    def _get_company_description(self, score):
        descriptions = [
            "公司财务恶化，重大负面事件，建议远离",
            "业绩下滑，管理层动荡，风险较高",
            "经营平稳，无重大变化，中性看待",
            "业绩增长，业务拓展，有发展潜力",
            "高速增长，创新突破，值得关注",
            "行业龙头，核心竞争力强，强烈推荐"
        ]
        return descriptions[min(int(score), 5)]
    
    def _get_technical_description(self, score):
        descriptions = [
            "技术破位，下跌趋势确立，风险极高",
            "弱势整理，有继续下跌风险，需要警惕",
            "横盘震荡，方向不明，谨慎观察",
            "技术企稳，有反弹可能，机会存在",
            "上升趋势，技术面良好，积极信号",
            "强势上涨，技术指标完美，强烈看好"
        ]
        return descriptions[min(int(score), 5)]
    
    def _get_sentiment_description(self, score):
        descriptions = [
            "极度悲观，恐慌抛售，建议远离",
            "情绪低迷，谨慎观望，风险较高",
            "情绪中性，分歧较大，保持观察",
            "情绪回暖，信心恢复，机会显现",
            "情绪乐观，积极买入，积极信号",
            "极度乐观，狂热追捧，注意风险"
        ]
        return descriptions[min(int(score), 5)]

class AlgorithmAPIHandler(BaseHTTPRequestHandler):
    """API请求处理器"""
    
    def __init__(self, *args, **kwargs):
        self.algorithm = FiveDimensionAlgorithm()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # 设置CORS头
        self.send_cors_headers()
        
        if path == "/api/health":
            self.handle_health()
        elif path == "/api/positions":
            self.handle_positions()
        elif path.startswith("/api/analyze/"):
            stock_code = path.split("/")[-1]
            self.handle_analyze(stock_code)
        elif path == "/api/analyze_all":
            self.handle_analyze_all()
        elif path.startswith("/api/price_history/"):
            stock_code = path.split("/")[-1]
            self.handle_price_history(stock_code)
        elif path == "/api/update_prices":
            self.handle_update_prices()
        else:
            self.send_error(404, "API not found")
    
    def do_OPTIONS(self):
        """处理OPTIONS请求（CORS预检）"""
        self.send_cors_headers()
        self.send_response(200)
        self.end_headers()
    
    def send_cors_headers(self):
        """发送CORS头"""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Max-Age", "86400")
    
    def send_json_response(self, data, status=200):
        """发送JSON响应"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_cors_headers()
        self.end_headers()
        
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response.encode("utf-8"))
    
    def handle_health(self):
        """健康检查"""
        self.send_json_response({
            "status": "healthy",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "service": "five-dimension-algorithm-api",
            "version": "1.0.0"
        })
    
    def handle_positions(self):
        """获取持仓信息"""
        positions = self.algorithm.stock_data.positions
        summary = self.algorithm.stock_data.get_position_summary()
        
        self.send_json_response({
            "positions": positions,
            "summary": summary,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    def handle_analyze(self, stock_code):
        """分析指定股票"""
        try:
            result = self.algorithm.analyze_stock(stock_code)
            self.send_json_response(result)
        except Exception as e:
            self.send_json_response({
                "error": str(e),
                "stock_code": stock_code
            }, 500)
    
    def handle_analyze_all(self):
        """分析所有持仓股票"""
        try:
            results = self.algorithm.get_all_positions_analysis()
            
            # 计算整体风险
            total_score = 0
            for result in results:
                total_score += result.get("comprehensive_score", 0)
            
            avg_score = total_score / len(results) if results else 0
            overall_risk = get_risk_level(avg_score)
            
            self.send_json_response({
                "results": results,
                "overall_score": round(avg_score, 2),
                "overall_risk": overall_risk,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
        except Exception as e:
            self.send_json_response({
                "error": str(e)
            }, 500)
    
    def handle_price_history(self, stock_code):
        """获取价格历史"""
        if stock_code in self.algorithm.stock_data.price_history:
            prices = self.algorithm.stock_data.price_history[stock_code]
            self.send_json_response({
                "stock_code": stock_code,
                "prices": prices,
                "count": len(prices),
                "latest": prices[-1] if prices else 0
            })
        else:
            self.send_json_response({
                "error": "股票代码不存在",
                "stock_code": stock_code
            }, 404)
    
    def handle_update_prices(self):
        """更新股价"""
        self.algorithm.stock_data.update_prices()
        self.send_json_response({
            "message": "股价已更新",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

def run_api_server(port=9000):
    """运行API服务器"""
    server_address = ("", port)
    httpd = HTTPServer(server_address, AlgorithmAPIHandler)
    
    print(f"✅ 五维度算法API服务器已启动")
    print(f"🌐 访问地址: http://localhost:{port}")
    print(f"📊 API端点:")
    print(f"  • GET /api/health          - 健康检查")
    print(f"  • GET /api/positions       - 获取持仓")
    print(f"  • GET /api/analyze/<code>  - 分析股票")
    print(f"  • GET /api/analyze_all     - 分析所有持仓")
    print(f"  • GET /api/price_history/<code> - 价格历史")
    print(f"  • GET /api/update_prices   - 更新股价")
    print(f"\n💡 提示: 按 Ctrl+C 停止服务器")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 正在停止服务器...")
        httpd.shutdown()
        print("✅ 服务器已停止")

if __name__ == "__main__":
    run_api_server()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五维度算法后端服务 - 网络访问版
为Web界面提供算法计算API，支持局域网访问
"""

import json
import random
import time
import socket
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

def get_local_ip():
    """获取本机局域网IP地址"""
    try:
        # 创建一个UDP套接字
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # 不需要真的连接，只是为了获取本地IP
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print(f"⚠️ 无法获取IP地址: {e}")
        return "localhost"

def check_port_available(port, host='0.0.0.0'):
    """检查端口是否可用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return True
        except OSError:
            return False

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
    
    def get_positions(self):
        """获取持仓数据"""
        return self.positions
    
    def update_prices(self):
        """更新股价（模拟）"""
        for pos in self.positions:
            # 随机波动
            change = (random.random() - 0.5) * 0.1
            pos["current_price"] += change
            if pos["current_price"] < 0.1:
                pos["current_price"] = 0.1
            
            # 保留两位小数
            pos["current_price"] = round(pos["current_price"], 2)
        
        return self.positions
    
    def get_stock_info(self, stock_code):
        """获取指定股票信息"""
        for pos in self.positions:
            if pos["code"] == stock_code:
                return pos
        return None

class AlgorithmService:
    """算法服务"""
    
    def __init__(self):
        self.stock_data = StockData()
    
    def calculate_international_score(self, stock_code):
        """计算国际局势算法分数"""
        # 模拟国际局势评分 (0-5)
        base_score = random.uniform(2.0, 4.5)
        
        # 添加一些随机波动
        adjustment = random.uniform(-0.5, 0.5)
        score = max(0, min(5, base_score + adjustment))
        
        description = self.get_score_description(score, "international")
        
        return {
            "score": round(score, 2),
            "description": description,
            "factors": INTERNATIONAL_FACTORS
        }
    
    def calculate_policy_score(self, stock_code):
        """计算国内政策算法分数"""
        base_score = random.uniform(2.5, 4.8)
        adjustment = random.uniform(-0.4, 0.4)
        score = max(0, min(5, base_score + adjustment))
        
        description = self.get_score_description(score, "policy")
        
        return {
            "score": round(score, 2),
            "description": description,
            "factors": POLICY_FACTORS
        }
    
    def calculate_company_score(self, stock_code):
        """计算企业发展异动分数"""
        base_score = random.uniform(2.0, 4.7)
        adjustment = random.uniform(-0.6, 0.6)
        score = max(0, min(5, base_score + adjustment))
        
        description = self.get_score_description(score, "company")
        
        return {
            "score": round(score, 2),
            "description": description,
            "factors": COMPANY_FACTORS
        }
    
    def calculate_technical_score(self, stock_code):
        """计算技术侧分析算法分数"""
        base_score = random.uniform(2.2, 4.6)
        adjustment = random.uniform(-0.5, 0.5)
        score = max(0, min(5, base_score + adjustment))
        
        description = self.get_score_description(score, "technical")
        
        return {
            "score": round(score, 2),
            "description": description,
            "factors": TECHNICAL_FACTORS
        }
    
    def calculate_sentiment_score(self, stock_code):
        """计算股民情绪算法分数"""
        base_score = random.uniform(2.3, 4.4)
        adjustment = random.uniform(-0.7, 0.7)
        score = max(0, min(5, base_score + adjustment))
        
        description = self.get_score_description(score, "sentiment")
        
        return {
            "score": round(score, 2),
            "description": description,
            "factors": SENTIMENT_FACTORS
        }
    
    def get_score_description(self, score, algorithm_type):
        """获取分数描述"""
        if score <= 1:
            level = "严重不利"
        elif score <= 2:
            level = "较为不利"
        elif score <= 3:
            level = "中性偏空"
        elif score <= 4:
            level = "中性偏好"
        else:
            level = "重大利好"
        
        algorithm_names = {
            "international": "国际局势算法",
            "policy": "国内政策算法",
            "company": "企业发展异动算法",
            "technical": "技术侧分析算法",
            "sentiment": "股民情绪算法"
        }
        
        return f"{algorithm_names.get(algorithm_type, algorithm_type)}: {level} ({score:.1f}分)"
    
    def analyze_stock(self, stock_code):
        """分析指定股票"""
        stock_info = self.stock_data.get_stock_info(stock_code)
        if not stock_info:
            return {"error": f"股票代码 {stock_code} 不存在"}
        
        # 计算各维度分数
        international = self.calculate_international_score(stock_code)
        policy = self.calculate_policy_score(stock_code)
        company = self.calculate_company_score(stock_code)
        technical = self.calculate_technical_score(stock_code)
        sentiment = self.calculate_sentiment_score(stock_code)
        
        # 计算综合评分
        algorithm_scores = {
            "international": international["score"],
            "policy": policy["score"],
            "company": company["score"],
            "technical": technical["score"],
            "sentiment": sentiment["score"]
        }
        
        comprehensive_score = calculate_comprehensive_score(algorithm_scores)
        risk_level = get_risk_level(comprehensive_score)
        
        # 生成小时级预测
        current_price = stock_info["current_price"]
        hourly_predictions = generate_hourly_prediction(current_price, comprehensive_score)
        
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
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def analyze_all_positions(self):
        """分析所有持仓股票"""
        positions = self.stock_data.get_positions()
        results = []
        
        for pos in positions:
            analysis = self.analyze_stock(pos["code"])
            if "error" not in analysis:
                results.append(analysis)
        
        return {
            "total_positions": len(positions),
            "analyzed": len(results),
            "analyses": results
        }

class APIRequestHandler(BaseHTTPRequestHandler):
    """API请求处理器"""
    
    def __init__(self, *args, **kwargs):
        self.algorithm_service = AlgorithmService()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """处理GET请求"""
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        # 设置CORS头部
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response_data = {}
        
        try:
            if path == '/api/health':
                response_data = {
                    "status": "healthy",
                    "service": "五维度股票算法服务",
                    "version": "1.0.0",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
            
            elif path == '/api/positions':
                positions = self.algorithm_service.stock_data.get_positions()
                response_data = {
                    "status": "success",
                    "positions": positions,
                    "count": len(positions)
                }
            
            elif path.startswith('/api/analyze/'):
                stock_code = path.split('/')[-1]
                analysis = self.algorithm_service.analyze_stock(stock_code)
                response_data = analysis
            
            elif path == '/api/analyze_all':
                analysis = self.algorithm_service.analyze_all_positions()
                response_data = analysis
            
            elif path == '/api/update_prices':
                updated_positions = self.algorithm_service.stock_data.update_prices()
                response_data = {
                    "status": "success",
                    "message": "股价已更新",
                    "positions": updated_positions
                }
            
            elif path.startswith('/api/price_history/'):
                stock_code = path.split('/')[-1]
                # 模拟价格历史数据
                price_history = []
                base_price = random.uniform(2.0, 5.0)
                
                for i in range(30, -1, -1):
                    date = datetime.now() - timedelta(days=i)
                    price = base_price + random.uniform(-0.3, 0.3)
                    price_history.append({
                        "date": date.strftime("%Y-%m-%d"),
                        "price": round(price, 2),
                        "volume": random.randint(100000, 500000)
                    })
                
                response_data = {
                    "stock_code": stock_code,
                    "price_history": price_history
                }
            
            else:
                response_data = {
                    "error": "API路径不存在",
                    "available_apis": [
                        "/api/health",
                        "/api/positions",
                        "/api/analyze/<stock_code>",
                        "/api/analyze_all",
                        "/api/price_history/<stock_code>",
                        "/api/update_prices"
                    ]
                }
        
        except Exception as e:
            response_data = {
                "error": f"服务器内部错误: {str(e)}"
            }
        
        # 发送响应
        self.wfile.write(json.dumps(response_data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def do_OPTIONS(self):
        """处理OPTIONS请求（用于CORS预检）"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

def main():
    """主函数"""
    print("🚀 五维度算法后端服务 - 网络访问版")
    print("=" * 50)
    
    # 获取本地IP
    local_ip = get_local_ip()
    print(f"📍 您的局域网IP地址: {local_ip}")
    
    # 设置端口
    port = 9000
    
    # 检查端口是否可用
    if not check_port_available(port):
        print(f"❌ 端口 {port} 已被占用，正在尝试其他端口...")
        for alt_port in [9001, 9002, 9003, 9004, 9005]:
            if check_port_available(alt_port):
                port = alt_port
                print(f"✅ 使用端口 {alt_port}")
                break
        else:
            print("❌ 找不到可用端口，请关闭其他占用端口的程序")
            return
    
    # 创建服务器
    server_address = ('0.0.0.0', port)
    httpd = HTTPServer(server_address, APIRequestHandler)
    
    print(f"✅ API服务已启动")
    print(f"📡 监听地址: 0.0.0.0:{port}")
    print("\n🔗 访问地址：")
    print(f"   1. 本地访问: http://localhost:{port}/api/health")
    print(f"   2. 局域网访问: http://{local_ip}:{port}/api/health")
    print(f"   3. 所有网络接口: http://0.0.0.0:{port}/api/health")
    print("\n📱 在其他电脑上访问：")
    print(f"   在浏览器中输入: http://{local_ip}:{port}/api/health")
    print("\n🔒 防火墙提示：")
    print("   如果无法访问，请确保防火墙允许端口 {port} 的入站连接")
    print("=" * 50)
    
    try:
        # 启动服务器
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 正在停止服务...")
        httpd.server_close()
        print("✅ 服务已停止")

if __name__ == "__main__":
    main()
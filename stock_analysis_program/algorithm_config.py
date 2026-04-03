#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
五维度算法参数配置
"""

# ==============================
# 五维度算法权重配置
# ==============================

ALGORITHM_WEIGHTS = {
    "international": 0.20,  # 国际局势算法权重
    "policy": 0.20,         # 国内政策算法权重
    "company": 0.25,        # 企业发展异动算法权重
    "technical": 0.20,      # 技术侧分析算法权重
    "sentiment": 0.15       # 股民情绪算法权重
}

# ==============================
# 国际局势算法参数
# ==============================

INTERNATIONAL_FACTORS = {
    "geopolitical_tension": {
        "name": "地缘政治紧张度",
        "weight": 0.30,
        "indicators": ["中美关系", "中东局势", "俄乌冲突", "台海局势"]
    },
    "economic_environment": {
        "name": "国际经济环境",
        "weight": 0.25,
        "indicators": ["美元指数", "美债收益率", "全球通胀", "贸易战影响"]
    },
    "monetary_policy": {
        "name": "国际货币政策",
        "weight": 0.25,
        "indicators": ["美联储政策", "欧洲央行", "日本央行", "全球利率"]
    },
    "commodity_prices": {
        "name": "大宗商品价格",
        "weight": 0.20,
        "indicators": ["原油价格", "黄金价格", "铜价", "农产品价格"]
    }
}

# ==============================
# 国内政策算法参数
# ==============================

POLICY_FACTORS = {
    "industry_policy": {
        "name": "产业政策",
        "weight": 0.35,
        "indicators": ["十四五规划", "新兴产业扶持", "传统产业转型", "环保政策"]
    },
    "financial_policy": {
        "name": "金融政策",
        "weight": 0.30,
        "indicators": ["货币政策", "信贷政策", "资本市场改革", "监管政策"]
    },
    "tax_policy": {
        "name": "税收政策",
        "weight": 0.20,
        "indicators": ["企业所得税", "增值税", "个人所得税", "税收优惠"]
    },
    "regional_policy": {
        "name": "区域政策",
        "weight": 0.15,
        "indicators": ["粤港澳大湾区", "长三角一体化", "京津冀协同", "西部大开发"]
    }
}

# ==============================
# 企业发展异动算法参数
# ==============================

COMPANY_FACTORS = {
    "financial_performance": {
        "name": "财务表现",
        "weight": 0.40,
        "indicators": ["营收增长率", "净利润率", "ROE", "负债率"]
    },
    "management_change": {
        "name": "管理层变动",
        "weight": 0.20,
        "indicators": ["董事长变更", "CEO更换", "CFO变动", "董事会调整"]
    },
    "business_expansion": {
        "name": "业务扩张",
        "weight": 0.25,
        "indicators": ["新项目投资", "并购重组", "产能扩张", "海外业务"]
    },
    "risk_events": {
        "name": "风险事件",
        "weight": 0.15,
        "indicators": ["法律诉讼", "行政处罚", "安全事故", "信誉危机"]
    }
}

# ==============================
# 技术侧分析算法参数
# ==============================

TECHNICAL_FACTORS = {
    "trend_analysis": {
        "name": "趋势分析",
        "weight": 0.30,
        "indicators": ["移动平均线", "MACD", "布林带", "趋势线"]
    },
    "momentum_indicators": {
        "name": "动量指标",
        "weight": 0.25,
        "indicators": ["RSI", "KDJ", "威廉指标", "CCI"]
    },
    "volume_analysis": {
        "name": "成交量分析",
        "weight": 0.25,
        "indicators": ["量价关系", "成交量均线", "OBV", "资金流向"]
    },
    "pattern_recognition": {
        "name": "形态识别",
        "weight": 0.20,
        "indicators": ["头肩形态", "双顶双底", "三角形整理", "旗形整理"]
    }
}

# ==============================
# 股民情绪算法参数
# ==============================

SENTIMENT_FACTORS = {
    "social_media": {
        "name": "社交媒体情绪",
        "weight": 0.35,
        "indicators": ["微博讨论热度", "股吧情绪", "雪球关注度", "微信公众号"]
    },
    "news_sentiment": {
        "name": "新闻情绪",
        "weight": 0.30,
        "indicators": ["财经新闻", "公司公告", "分析师报告", "政策解读"]
    },
    "market_sentiment": {
        "name": "市场情绪",
        "weight": 0.20,
        "indicators": ["恐慌指数", "投资者信心", "融资融券", "北向资金"]
    },
    "search_trends": {
        "name": "搜索趋势",
        "weight": 0.15,
        "indicators": ["百度搜索指数", "谷歌趋势", "同花顺搜索", "东方财富搜索"]
    }
}

# ==============================
# 评分映射表
# ==============================

SCORE_MAPPING = {
    0: {
        "name": "严重不利",
        "color": "#e74c3c",  # 红色
        "description": "极度负面，建议立即减仓或清仓",
        "weight_adjustment": -0.3  # 权重调整系数
    },
    1: {
        "name": "较为不利", 
        "color": "#e67e22",  # 橙色
        "description": "负面因素较多，需要警惕",
        "weight_adjustment": -0.15
    },
    2: {
        "name": "中性偏空",
        "color": "#f1c40f",  # 黄色
        "description": "存在不确定性，谨慎观察",
        "weight_adjustment": -0.05
    },
    3: {
        "name": "中性偏好",
        "color": "#2ecc71",  # 浅绿色
        "description": "机会与风险并存，可适量持有",
        "weight_adjustment": 0.05
    },
    4: {
        "name": "较为有利",
        "color": "#27ae60",  # 绿色
        "description": "积极信号较多，可以考虑加仓",
        "weight_adjustment": 0.15
    },
    5: {
        "name": "重大利好",
        "color": "#1abc9c",  # 深绿色
        "description": "强烈正面信号，推荐增持",
        "weight_adjustment": 0.25
    }
}

# ==============================
# 风险等级映射
# ==============================

RISK_LEVEL_MAPPING = {
    "0-1.0": {
        "level": "极高风险",
        "color": "#c0392b",
        "suggestion": "立即清仓，远离风险",
        "position_limit": 0.05  # 仓位限制
    },
    "1.1-2.0": {
        "level": "高风险",
        "color": "#e74c3c",
        "suggestion": "大幅减仓，严格止损",
        "position_limit": 0.10
    },
    "2.1-3.0": {
        "level": "中高风险",
        "color": "#f39c12",
        "suggestion": "控制仓位，谨慎持有",
        "position_limit": 0.15
    },
    "3.1-4.0": {
        "level": "中等风险",
        "color": "#f1c40f",
        "suggestion": "可以持有，注意监控",
        "position_limit": 0.20
    },
    "4.1-4.5": {
        "level": "中低风险",
        "color": "#2ecc71",
        "suggestion": "适合持有，可适量加仓",
        "position_limit": 0.25
    },
    "4.6-5.0": {
        "level": "低风险",
        "color": "#27ae60",
        "suggestion": "推荐持有或加仓",
        "position_limit": 0.30
    }
}

# ==============================
# 小时级预测参数
# ==============================

HOURLY_PREDICTION_PARAMS = {
    "time_slots": [
        {"name": "09:30-10:30", "volatility_factor": 1.2, "trend_weight": 0.3},
        {"name": "10:30-11:30", "volatility_factor": 1.1, "trend_weight": 0.4},
        {"name": "13:00-14:00", "volatility_factor": 1.0, "trend_weight": 0.5},
        {"name": "14:00-15:00", "volatility_factor": 1.3, "trend_weight": 0.6}
    ],
    "algorithm_weights": {
        "international": 0.15,
        "policy": 0.15,
        "company": 0.20,
        "technical": 0.30,
        "sentiment": 0.20
    }
}

# ==============================
# 数据源配置
# ==============================

DATA_SOURCES = {
    "international": [
        "路透社", "彭博社", "华尔街日报", "CNBC", "BBC"
    ],
    "policy": [
        "中国政府网", "发改委", "证监会", "央行", "财政部"
    ],
    "company": [
        "公司公告", "财报", "交易所", "信用评级", "行业报告"
    ],
    "technical": [
        "Tushare", "聚宽", "万得", "同花顺", "东方财富"
    ],
    "sentiment": [
        "微博", "雪球", "股吧", "微信公众号", "财经新闻"
    ]
}

# ==============================
# 工具函数
# ==============================

def get_score_color(score):
    """根据分数获取颜色"""
    if score <= 1:
        return SCORE_MAPPING[0]["color"]
    elif score <= 2:
        return SCORE_MAPPING[1]["color"]
    elif score <= 3:
        return SCORE_MAPPING[2]["color"]
    elif score <= 4:
        return SCORE_MAPPING[3]["color"]
    else:
        return SCORE_MAPPING[4]["color"]

def get_risk_level(comprehensive_score):
    """根据综合评分获取风险等级"""
    for key, config in RISK_LEVEL_MAPPING.items():
        low, high = map(float, key.split("-"))
        if low <= comprehensive_score <= high:
            return config
    return RISK_LEVEL_MAPPING["2.1-3.0"]  # 默认中高风险

def calculate_comprehensive_score(scores):
    """计算综合评分"""
    total = 0
    for algo, score in scores.items():
        if algo in ALGORITHM_WEIGHTS:
            total += score * ALGORITHM_WEIGHTS[algo]
    return round(total, 2)

def generate_hourly_prediction(base_price, algorithm_scores):
    """生成小时级预测"""
    import random
    
    predictions = []
    for slot in HOURLY_PREDICTION_PARAMS["time_slots"]:
        # 基于算法评分计算调整因子
        adjustment = 0
        for algo, score in algorithm_scores.items():
            if algo in HOURLY_PREDICTION_PARAMS["algorithm_weights"]:
                # 将0-5分转换为-0.1到0.1的调整范围
                normalized_score = (score - 2.5) / 25  # 2.5为中性点
                weight = HOURLY_PREDICTION_PARAMS["algorithm_weights"][algo]
                adjustment += normalized_score * weight
        
        # 添加随机波动
        volatility = random.uniform(-0.02, 0.02) * slot["volatility_factor"]
        
        # 计算预测价格区间
        predicted_price = base_price * (1 + adjustment + volatility)
        lower_bound = predicted_price * (1 - 0.015 * slot["volatility_factor"])
        upper_bound = predicted_price * (1 + 0.015 * slot["volatility_factor"])
        
        predictions.append({
            "time_slot": slot["name"],
            "lower": round(lower_bound, 2),
            "upper": round(upper_bound, 2),
            "mid": round(predicted_price, 2),
            "volatility": round(volatility * 100, 2)
        })
    
    return predictions
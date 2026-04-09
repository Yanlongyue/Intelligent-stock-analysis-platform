#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技术分析建议模块
基于实时行情数据生成操作建议
"""

from datetime import datetime
from typing import Dict, Any, Optional


class TechnicalAdvisor:
    """技术分析建议生成器"""
    
    # 建议类型
    ADVICE_HOLD = "hold"           # 保持观望
    ADVICE_ADD_LIGHT = "add_light" # 轻仓加仓
    ADVICE_ADD_MODERATE = "add_moderate" # 中等加仓
    ADVICE_ADD_HEAVY = "add_heavy" # 重仓加仓
    ADVICE_REDUCE_LIGHT = "reduce_light" # 轻仓减仓
    ADVICE_REDUCE_MODERATE = "reduce_moderate" # 中等减仓
    ADVICE_REDUCE_HEAVY = "reduce_heavy" # 重仓减仓
    ADVICE_CLEAR = "clear"         # 清仓
    
    # 建议标签映射
    ADVICE_LABELS = {
        ADVICE_HOLD: "保持观望",
        ADVICE_ADD_LIGHT: "轻仓加仓",
        ADVICE_ADD_MODERATE: "中等加仓",
        ADVICE_ADD_HEAVY: "重仓加仓",
        ADVICE_REDUCE_LIGHT: "轻仓减仓",
        ADVICE_REDUCE_MODERATE: "中等减仓",
        ADVICE_REDUCE_HEAVY: "重仓减仓",
        ADVICE_CLEAR: "建议清仓"
    }
    
    # 建议样式类名（前端用）
    ADVICE_CLASSES = {
        ADVICE_HOLD: "neutral",
        ADVICE_ADD_LIGHT: "buy-light",
        ADVICE_ADD_MODERATE: "buy-moderate",
        ADVICE_ADD_HEAVY: "buy-heavy",
        ADVICE_REDUCE_LIGHT: "sell-light",
        ADVICE_REDUCE_MODERATE: "sell-moderate",
        ADVICE_REDUCE_HEAVY: "sell-heavy",
        ADVICE_CLEAR: "sell-clear"
    }
    
    @classmethod
    def analyze_intraday_trend(cls, snapshot: Dict[str, Any], cost_price: Optional[float] = None, 
                               position_type: str = "value") -> Dict[str, Any]:
        """
        分析日内趋势并生成操作建议
        
        Args:
            snapshot: 实时行情快照
            cost_price: 成本价（用于判断盈亏状态）
            position_type: 持仓类型 (value/growth/concept)
            
        Returns:
            包含建议和分析结果的字典
        """
        if not snapshot or snapshot.get("current_price", 0) <= 0:
            return cls._empty_advice()
        
        current_price = snapshot.get("current_price", 0)
        open_price = snapshot.get("open", current_price)
        high_price = snapshot.get("high", current_price)
        low_price = snapshot.get("low", current_price)
        pre_close = snapshot.get("pre_close", current_price)
        pct_chg = snapshot.get("pct_chg", 0)
        turnover = snapshot.get("turnover", 0)
        
        # 计算日内趋势指标
        price_vs_open = ((current_price - open_price) / open_price * 100) if open_price > 0 else 0
        price_vs_high = ((high_price - current_price) / high_price * 100) if high_price > 0 else 0
        intraday_range = ((high_price - low_price) / pre_close * 100) if pre_close > 0 else 0
        
        # 计算盈亏状态
        profit_pct = 0
        if cost_price and cost_price > 0:
            profit_pct = ((current_price - cost_price) / cost_price * 100)
        
        # 根据持仓类型调整策略参数
        params = cls._get_strategy_params(position_type)
        
        # 综合评分系统（满分100）
        score = 0
        score_breakdown = {}
        
        # 1. 涨跌幅评分 (-30 ~ +30)
        if pct_chg >= params["strong_rise_threshold"]:
            score += 25
            score_breakdown["涨跌幅"] = "强势上涨 (+25)"
        elif pct_chg >= params["moderate_rise_threshold"]:
            score += 15
            score_breakdown["涨跌幅"] = "温和上涨 (+15)"
        elif pct_chg >= 0:
            score += 5
            score_breakdown["涨跌幅"] = "微涨 (+5)"
        elif pct_chg >= params["moderate_fall_threshold"]:
            score -= 10
            score_breakdown["涨跌幅"] = "温和下跌 (-10)"
        elif pct_chg >= params["strong_fall_threshold"]:
            score -= 20
            score_breakdown["涨跌幅"] = "明显下跌 (-20)"
        else:
            score -= 30
            score_breakdown["涨跌幅"] = "大幅下跌 (-30)"
        
        # 2. 日内趋势评分 (-20 ~ +20)
        if price_vs_open >= 2:
            score += 15
            score_breakdown["日内趋势"] = "开盘后强势 (+15)"
        elif price_vs_open >= 0.5:
            score += 10
            score_breakdown["日内趋势"] = "开盘后上涨 (+10)"
        elif price_vs_open >= -0.5:
            score += 0
            score_breakdown["日内趋势"] = "横盘震荡 (0)"
        elif price_vs_open >= -2:
            score -= 10
            score_breakdown["日内趋势"] = "开盘后下跌 (-10)"
        else:
            score -= 20
            score_breakdown["日内趋势"] = "开盘后跳水 (-20)"
        
        # 3. 位置评分 (-15 ~ +15)
        # 当前价格在日内高低点区间的位置
        if intraday_range > 0:
            position_in_range = (current_price - low_price) / (high_price - low_price)
            if position_in_range >= 0.8:
                score += 15
                score_breakdown["位置"] = "接近日内高点 (+15)"
            elif position_in_range >= 0.6:
                score += 10
                score_breakdown["位置"] = "处于高位 (+10)"
            elif position_in_range >= 0.4:
                score += 5
                score_breakdown["位置"] = "处于中位 (+5)"
            elif position_in_range >= 0.2:
                score -= 5
                score_breakdown["位置"] = "处于低位 (-5)"
            else:
                score -= 15
                score_breakdown["位置"] = "接近日内低点 (-15)"
        
        # 4. 换手率评分 (概念股更看重换手率)
        if position_type == "concept":
            if turnover >= 10:
                score += 15
                score_breakdown["换手率"] = "极度活跃 (+15)"
            elif turnover >= 5:
                score += 10
                score_breakdown["换手率"] = "非常活跃 (+10)"
            elif turnover >= 2:
                score += 5
                score_breakdown["换手率"] = "比较活跃 (+5)"
            elif turnover >= 0.5:
                score += 0
                score_breakdown["换手率"] = "正常换手 (0)"
            else:
                score -= 5
                score_breakdown["换手率"] = "交投清淡 (-5)"
        else:
            # 价值股/成长股更看重稳定性
            if turnover >= 8:
                score -= 5
                score_breakdown["换手率"] = "换手过高，警惕 (-5)"
            elif turnover >= 3:
                score += 5
                score_breakdown["换手率"] = "换手正常 (+5)"
            elif turnover >= 1:
                score += 3
                score_breakdown["换手率"] = "换手偏低 (+3)"
            else:
                score += 0
                score_breakdown["换手率"] = "换手极低 (0)"
        
        # 5. 盈亏状态调整
        if profit_pct is not None:
            if profit_pct >= 20:
                score -= 10  # 获利较多，建议减仓
                score_breakdown["盈亏状态"] = "获利丰厚，注意止盈 (-10)"
            elif profit_pct >= 10:
                score -= 5
                score_breakdown["盈亏状态"] = "有一定获利 (-5)"
            elif profit_pct <= -10:
                score += 5  # 亏损较多，可逢低补仓
                score_breakdown["盈亏状态"] = "亏损较大，可考虑补仓 (+5)"
            elif profit_pct <= -20:
                score += 10
                score_breakdown["盈亏状态"] = "深度亏损，建议补仓 (+10)"
        
        # 根据总分生成建议
        advice_type, reason = cls._score_to_advice(score, pct_chg, profit_pct, position_type, params)
        
        # 计算建议仓位变化
        suggested_action = cls._get_suggested_action(advice_type, score)
        
        return {
            "advice_type": advice_type,
            "advice_label": cls.ADVICE_LABELS.get(advice_type, "未知"),
            "advice_class": cls.ADVICE_CLASSES.get(advice_type, "neutral"),
            "score": score,
            "score_breakdown": score_breakdown,
            "reason": reason,
            "suggested_action": suggested_action,
            "current_pct_chg": round(pct_chg, 2),
            "current_profit_pct": round(profit_pct, 2) if profit_pct is not None else None,
            "intraday_range": round(intraday_range, 2),
            "turnover": round(turnover, 2),
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    @classmethod
    def _get_strategy_params(cls, position_type: str) -> Dict[str, float]:
        """根据持仓类型获取策略参数"""
        params = {
            "value": {
                "strong_rise_threshold": 3,      # 强势股判定
                "moderate_rise_threshold": 1,    # 温和上涨判定
                "moderate_fall_threshold": -1,   # 温和下跌判定
                "strong_fall_threshold": -3,     # 弱势股判定
                "stop_loss_pct": -5,             # 止损线
                "take_profit_pct": 10            # 止盈线
            },
            "growth": {
                "strong_rise_threshold": 4,
                "moderate_rise_threshold": 1.5,
                "moderate_fall_threshold": -1.5,
                "strong_fall_threshold": -4,
                "stop_loss_pct": -4,
                "take_profit_pct": 15
            },
            "concept": {
                "strong_rise_threshold": 5,
                "moderate_rise_threshold": 2,
                "moderate_fall_threshold": -2,
                "strong_fall_threshold": -5,
                "stop_loss_pct": -3,
                "take_profit_pct": 10
            }
        }
        return params.get(position_type, params["value"])
    
    @classmethod
    def _score_to_advice(cls, score: int, pct_chg: float, profit_pct: Optional[float], 
                         position_type: str, params: Dict[str, float]) -> tuple:
        """将评分转换为建议类型和原因"""
        
        reasons = []
        
        # 根据评分区间确定建议
        if score >= 50:
            advice = cls.ADVICE_ADD_HEAVY
            reasons.append("技术面强势，多头信号明显")
        elif score >= 35:
            advice = cls.ADVICE_ADD_MODERATE
            reasons.append("技术面偏多，可适当加仓")
        elif score >= 20:
            advice = cls.ADVICE_ADD_LIGHT
            reasons.append("技术面略有好转，可轻仓试探")
        elif score >= -10:
            advice = cls.ADVICE_HOLD
            reasons.append("技术面中性，建议观望")
        elif score >= -25:
            advice = cls.ADVICE_REDUCE_LIGHT
            reasons.append("技术面偏弱，可考虑减仓")
        elif score >= -40:
            advice = cls.ADVICE_REDUCE_MODERATE
            reasons.append("技术面走弱，建议减仓")
        elif score >= -55:
            advice = cls.ADVICE_REDUCE_HEAVY
            reasons.append("技术面明显走弱，大幅减仓")
        else:
            advice = cls.ADVICE_CLEAR
            reasons.append("技术面极度弱势，建议清仓")
        
        # 追加具体原因
        if pct_chg >= params["strong_rise_threshold"]:
            reasons.append(f"当日涨幅{pct_chg:.2f}%，表现强势")
        elif pct_chg <= params["strong_fall_threshold"]:
            reasons.append(f"当日跌幅{abs(pct_chg):.2f}%，走势较弱")
        
        if profit_pct is not None:
            if profit_pct <= params["stop_loss_pct"]:
                reasons.append(f"已跌破止损线({params['stop_loss_pct']}%)")
            elif profit_pct >= params["take_profit_pct"]:
                reasons.append(f"已达到止盈目标({params['take_profit_pct']}%)")
        
        return advice, "；".join(reasons)
    
    @classmethod
    def _get_suggested_action(cls, advice_type: str, score: int) -> Dict[str, Any]:
        """获取建议的具体操作"""
        actions = {
            cls.ADVICE_HOLD: {
                "action": "观望",
                "position_change": "维持现有仓位",
                "target_pct": None
            },
            cls.ADVICE_ADD_LIGHT: {
                "action": "加仓",
                "position_change": "增加10-20%仓位",
                "target_pct": "10-20%"
            },
            cls.ADVICE_ADD_MODERATE: {
                "action": "加仓",
                "position_change": "增加20-40%仓位",
                "target_pct": "20-40%"
            },
            cls.ADVICE_ADD_HEAVY: {
                "action": "加仓",
                "position_change": "增加40%以上仓位",
                "target_pct": "40%+"
            },
            cls.ADVICE_REDUCE_LIGHT: {
                "action": "减仓",
                "position_change": "减少10-20%仓位",
                "target_pct": "10-20%"
            },
            cls.ADVICE_REDUCE_MODERATE: {
                "action": "减仓",
                "position_change": "减少20-40%仓位",
                "target_pct": "20-40%"
            },
            cls.ADVICE_REDUCE_HEAVY: {
                "action": "减仓",
                "position_change": "减少40%以上仓位",
                "target_pct": "40%+"
            },
            cls.ADVICE_CLEAR: {
                "action": "清仓",
                "position_change": "卖出全部持仓",
                "target_pct": "100%"
            }
        }
        return actions.get(advice_type, actions[cls.ADVICE_HOLD])
    
    @classmethod
    def _empty_advice(cls) -> Dict[str, Any]:
        """返回空建议"""
        return {
            "advice_type": cls.ADVICE_HOLD,
            "advice_label": "数据不足",
            "advice_class": "neutral",
            "score": 0,
            "score_breakdown": {},
            "reason": "暂无实时数据，无法生成建议",
            "suggested_action": {
                "action": "观望",
                "position_change": "维持现有仓位",
                "target_pct": None
            },
            "current_pct_chg": None,
            "current_profit_pct": None,
            "intraday_range": None,
            "turnover": None,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


# 便捷函数
def analyze_stock_advice(snapshot: Dict[str, Any], cost_price: Optional[float] = None,
                        position_type: str = "value") -> Dict[str, Any]:
    """
    快速分析股票并生成建议
    
    Args:
        snapshot: 实时行情快照
        cost_price: 成本价
        position_type: 持仓类型
        
    Returns:
        建议数据
    """
    return TechnicalAdvisor.analyze_intraday_trend(snapshot, cost_price, position_type)
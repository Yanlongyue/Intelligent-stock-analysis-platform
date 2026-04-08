#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
真实数据算法引擎
当前仅保留真实行情/基础信息读取；五维真实因子模型尚未完成，明确停用模拟评分与模拟预测。
"""

from datetime import datetime


class RealAlgorithmEngine:
    """真实数据算法引擎（已停用模拟分析输出）"""

    def __init__(self, data_provider):
        """初始化算法引擎"""
        self.data_provider = data_provider

    def analyze_stock(self, stock_code):
        """分析指定股票，仅返回真实数据可见范围内的结果"""
        try:
            stock_data = self._get_stock_data(stock_code)
            if not stock_data:
                return self._build_unavailable_analysis(
                    stock_code,
                    reason="缺少真实行情数据，已停止输出模拟分析结果",
                )

            current_price = stock_data.get("current_price")
            if current_price in (None, "", 0, 0.0):
                return self._build_unavailable_analysis(
                    stock_code,
                    stock_data=stock_data,
                    reason="当前未获取到可信实时价格，已停止输出模拟分析结果",
                )

            return self._build_unavailable_analysis(
                stock_code,
                stock_data=stock_data,
                reason="当前仅保留真实行情与基础数据，五维真实因子模型尚未完成，已停用模拟评分与模拟预测",
            )
        except Exception as exc:
            print(f"分析股票 {stock_code} 失败: {exc}")
            return self._build_unavailable_analysis(stock_code, reason=f"分析失败：{exc}")

    def _build_unavailable_analysis(self, stock_code, stock_data=None, reason="暂无真实分析数据"):
        """构建不可用分析结果，避免任何模拟评分回退"""
        stock_data = stock_data or {}
        provider_label = "真实数据链路"
        if hasattr(self.data_provider, "get_data_source_label"):
            try:
                provider_label = self.data_provider.get_data_source_label()
            except Exception:
                pass

        current_price = stock_data.get("current_price")
        try:
            current_price = round(float(current_price), 2) if current_price not in (None, "") else None
        except (TypeError, ValueError):
            current_price = None

        return {
            "stock_code": stock_code,
            "stock_name": stock_data.get("name") or stock_data.get("stock_name") or stock_code,
            "current_price": current_price,
            "algorithm_scores": {},
            "comprehensive_score": None,
            "risk_level": "待补充",
            "trading_signal": "暂无真实分析",
            "key_signals": [
                "已停用模拟评分与模拟预测",
                "当前接口仅返回真实行情/基础信息，不再伪造五维分数",
                reason,
            ],
            "action_plan": {
                "position": "等待真实因子模型完成后再生成建议",
                "stop_loss": "待真实策略模块输出",
                "take_profit": "待真实策略模块输出",
                "note": reason,
            },
            "hourly_predictions": [],
            "analysis_status": "unavailable",
            "analysis_message": reason,
            "data_source": provider_label,
            "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _get_stock_data(self, stock_code):
        """获取股票真实数据快照"""
        if hasattr(self.data_provider, "get_all_holdings_data"):
            try:
                holdings = self.data_provider.get_all_holdings_data()
            except Exception:
                holdings = None

            if isinstance(holdings, list):
                for stock in holdings:
                    if isinstance(stock, dict) and stock.get("code") == stock_code:
                        normalized = dict(stock)
                        if not normalized.get("name"):
                            normalized["name"] = stock_code
                        return normalized

        current_price = None
        if hasattr(self.data_provider, "get_stock_realtime_price"):
            try:
                current_price = self.data_provider.get_stock_realtime_price(stock_code)
            except Exception:
                current_price = None

        return {
            "code": stock_code,
            "name": stock_code,
            "current_price": current_price,
        }


if __name__ == "__main__":
    from real_data_provider import get_data_provider

    provider = get_data_provider(use_real_data=True)
    engine = RealAlgorithmEngine(provider)

    for stock in ["601868.SH", "002506.SZ", "600821.SH"]:
        result = engine.analyze_stock(stock)
        print(f"\n{result.get('stock_name', stock)} 分析结果:")
        print(f"  当前价格: {result.get('current_price')}")
        print(f"  分析状态: {result.get('analysis_status')}")
        print(f"  说明: {result.get('analysis_message')}")
        print(f"  数据来源: {result.get('data_source')}")

    print("\n测试完成！")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析引擎模块
实现七步法分析的核心逻辑
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class AnalysisEngine:
    """股票分析引擎"""
    
    def __init__(self, config):
        """
        初始化分析引擎
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.analysis_results = {}
        logger.info("分析引擎初始化完成")
    
    def step1_deep_review(self, stocks_data: Dict, predictions: Dict) -> Dict:
        """
        第1步：深度复盘
        
        Args:
            stocks_data: 今日实际数据 {ts_code: {close, pct_chg, ...}}
            predictions: 昨日预测数据 {ts_code: {predicted_price_range, ...}}
        
        Returns:
            Dict: 复盘结果
        """
        logger.info("执行第1步：深度复盘")
        
        results = {
            'accuracy_stats': [],
            'overall_performance': {},
            'market_summary': {}
        }
        
        # 计算每只股票的预测准确性
        direction_correct_count = 0
        total_amplitude_error = 0
        total_score = 0
        stock_count = len(stocks_data)
        
        for ts_code, actual_data in stocks_data.items():
            if ts_code not in predictions:
                logger.warning(f"未找到预测数据: {ts_code}")
                continue
            
            pred_data = predictions[ts_code]
            
            # 计算准确性
            accuracy = self._calculate_accuracy(pred_data, actual_data)
            
            # 统计
            if accuracy['direction_accuracy'] == 1.0:
                direction_correct_count += 1
            total_amplitude_error += abs(accuracy['amplitude_error'])
            total_score += accuracy['overall_score']
            
            # 保存结果
            results['accuracy_stats'].append({
                'ts_code': ts_code,
                'stock_name': pred_data.get('stock_name', '未知'),
                'predicted_range': pred_data['predicted_price_range'],
                'actual_close': actual_data['close'],
                'actual_pct_chg': actual_data['pct_chg'],
                'direction_accuracy': accuracy['direction_accuracy'],
                'amplitude_accuracy': accuracy['amplitude_accuracy'],
                'overall_score': accuracy['overall_score']
            })
        
        # 计算整体表现
        if stock_count > 0:
            results['overall_performance'] = {
                'direction_accuracy': direction_correct_count / stock_count,
                'average_amplitude_error': total_amplitude_error / stock_count,
                'overall_score': total_score / stock_count,
                'total_stocks': stock_count
            }
        
        # 生成市场表现总结
        results['market_summary'] = self._generate_market_summary(stocks_data)
        
        logger.info(f"第1步完成: 方向准确率={results['overall_performance'].get('direction_accuracy', 0):.2%}")
        
        return results
    
    def step2_error_analysis(self, accuracy_stats: List[Dict], market_data: Dict) -> Dict:
        """
        第2步：误差分析
        
        Args:
            accuracy_stats: 准确性统计数据
            market_data: 市场数据
        
        Returns:
            Dict: 误差分析结果
        """
        logger.info("执行第2步：误差分析")
        
        results = {
            'error_reasons': [],
            'model_optimization': {}
        }
        
        # 分析系统性误差原因
        error_reasons = self._analyze_error_reasons(accuracy_stats, market_data)
        results['error_reasons'] = error_reasons
        
        # 提出模型优化方案
        optimization = self._propose_model_optimization(error_reasons)
        results['model_optimization'] = optimization
        
        logger.info(f"第2步完成: 识别{len(error_reasons)}个主要误差原因")
        
        return results
    
    def step3_tomorrow_prediction(self, stocks_data: Dict, market_data: Dict, config_params: Dict) -> Dict:
        """
        第3步：明日预测
        
        Args:
            stocks_data: 今日股票数据
            market_data: 市场数据
            config_params: 配置参数
        
        Returns:
            Dict: 明日预测结果
        """
        logger.info("执行第3步：明日预测")
        
        results = {
            'market_environment': {},
            'stock_predictions': []
        }
        
        # 分析总体市场环境
        results['market_environment'] = self._analyze_market_environment(market_data)
        
        # 为每只股票生成小时级预测
        for ts_code, stock_data in stocks_data.items():
            prediction = self._generate_stock_prediction(ts_code, stock_data, market_data, config_params)
            results['stock_predictions'].append(prediction)
        
        logger.info(f"第3步完成: 生成{len(results['stock_predictions'])}只股票的预测")
        
        return results
    
    def step4_investment_plan(self, stock_predictions: List[Dict], config_params: Dict) -> Dict:
        """
        第4步：投资计划
        
        Args:
            stock_predictions: 股票预测数据
            config_params: 配置参数
        
        Returns:
            Dict: 投资计划
        """
        logger.info("执行第4步：投资计划")
        
        results = {
            'total_position_advice': {},
            'stock_plans': []
        }
        
        # 总体仓位建议
        results['total_position_advice'] = {
            'max_position': config_params.get('max_total_position', 0.45),
            'single_stock_max': config_params.get('max_single_position', 0.15),
            'suggested_position': self._calculate_suggested_position(stock_predictions)
        }
        
        # 每只股票的具体投资计划
        for pred in stock_predictions:
            plan = self._generate_stock_plan(pred, config_params)
            results['stock_plans'].append(plan)
        
        logger.info(f"第4步完成: 制定{len(results['stock_plans'])}只股票的投资计划")
        
        return results
    
    def step5_risk_control(self, stock_plans: List[Dict], market_data: Dict) -> Dict:
        """
        第5步：风险控制
        
        Args:
            stock_plans: 投资计划
            market_data: 市场数据
        
        Returns:
            Dict: 风险控制方案
        """
        logger.info("执行第5步：风险控制")
        
        results = {
            'international_monitoring': [],
            'operation_discipline': {},
            'position_control': {},
            'risk_level': 0
        }
        
        # 国际局势监控要点
        results['international_monitoring'] = self._generate_international_monitoring(market_data)
        
        # 操作纪律
        results['operation_discipline'] = {
            'stop_loss_rules': {
                'high_risk': 0.03,
                'medium_risk': 0.05,
                'low_risk': 0.07
            },
            'batch_operation': [0.3, 0.4, 0.3],
            'profit_taking': [0.3, 0.3, 0.4]
        }
        
        # 仓位控制
        results['position_control'] = self._calculate_position_control(stock_plans)
        
        # 风险等级评估
        results['risk_level'] = self._assess_risk_level(market_data, stock_plans)
        
        logger.info(f"第5步完成: 风险等级={results['risk_level']:.1f}/10")
        
        return results
    
    def step6_other_recommendations(self, market_data: Dict, config_params: Dict) -> Dict:
        """
        第6步：其他推荐
        
        Args:
            market_data: 市场数据
            config_params: 配置参数
        
        Returns:
            Dict: 其他股票推荐
        """
        logger.info("执行第6步：其他推荐")
        
        results = {
            'recommended_stocks': []
        }
        
        # 推荐潜力股票
        recommended = self._recommend_potential_stocks(market_data, config_params)
        results['recommended_stocks'] = recommended
        
        logger.info(f"第6步完成: 推荐{len(recommended)}只潜力股票")
        
        return results
    
    # ==================== 辅助方法 ====================
    
    def _calculate_accuracy(self, pred_data: Dict, actual_data: Dict) -> Dict:
        """计算预测准确性"""
        pred_range = pred_data.get('predicted_price_range', (0, 0))
        pred_mid = (pred_range[0] + pred_range[1]) / 2
        actual_close = actual_data.get('close', 0)
        actual_pct_chg = actual_data.get('pct_chg', 0)
        pre_close = actual_data.get('pre_close', actual_close)
        
        # 方向准确性
        predicted_direction = 1 if pred_mid > pre_close else -1
        actual_direction = 1 if actual_pct_chg > 0 else -1
        direction_accuracy = 1.0 if predicted_direction == actual_direction else 0.0
        
        # 幅度准确性
        predicted_amplitude = pred_data.get('predicted_amplitude', 0)
        amplitude_error = abs(predicted_amplitude - abs(actual_pct_chg))
        amplitude_accuracy = max(0, 1 - amplitude_error / 10)
        
        # 综合评分
        overall_score = (direction_accuracy * 0.6 + amplitude_accuracy * 0.4) * 10
        
        return {
            'direction_accuracy': direction_accuracy,
            'amplitude_accuracy': amplitude_accuracy,
            'amplitude_error': amplitude_error,
            'overall_score': overall_score
        }
    
    def _generate_market_summary(self, stocks_data: Dict) -> Dict:
        """生成市场表现总结"""
        if not stocks_data:
            return {}
        
        up_count = sum(1 for data in stocks_data.values() if data.get('pct_chg', 0) > 0)
        down_count = len(stocks_data) - up_count
        avg_change = np.mean([data.get('pct_chg', 0) for data in stocks_data.values()])
        
        return {
            'up_count': up_count,
            'down_count': down_count,
            'average_change': avg_change,
            'market_sentiment': 'bullish' if avg_change > 0 else 'bearish'
        }
    
    def _analyze_error_reasons(self, accuracy_stats: List[Dict], market_data: Dict) -> List[Dict]:
        """分析误差原因"""
        reasons = []
        
        # 分析方向准确率
        direction_accuracy = sum(1 for stat in accuracy_stats if stat['direction_accuracy'] == 1.0) / len(accuracy_stats) if accuracy_stats else 0
        
        if direction_accuracy < 0.5:
            reasons.append({
                'category': '国际风险传导',
                'description': '国际风险传导机制失效，对市场影响评估不足',
                'severity': 'high'
            })
        
        # 分析幅度误差
        avg_amplitude_error = np.mean([abs(stat.get('amplitude_error', 0)) for stat in accuracy_stats])
        
        if avg_amplitude_error > 2:
            reasons.append({
                'category': '技术面分析',
                'description': '技术面反弹或下跌力度评估偏差较大',
                'severity': 'medium'
            })
        
        # 基本面风险
        reasons.append({
            'category': '基本面风险',
            'description': '个股基本面风险差异未充分评估',
            'severity': 'medium'
        })
        
        # 市场情绪
        reasons.append({
            'category': '市场情绪',
            'description': '市场情绪改善或恶化超预期',
            'severity': 'medium'
        })
        
        return reasons
    
    def _propose_model_optimization(self, error_reasons: List[Dict]) -> Dict:
        """提出模型优化方案"""
        optimization = {
            'weight_adjustments': [],
            'parameter_changes': []
        }
        
        # 根据误差原因调整权重
        for reason in error_reasons:
            if reason['category'] == '国际风险传导':
                optimization['weight_adjustments'].append({
                    'factor': 'international_risk',
                    'old_weight': 0.55,
                    'new_weight': 0.60,
                    'reason': reason['description']
                })
            elif reason['category'] == '技术面分析':
                optimization['weight_adjustments'].append({
                    'factor': 'technical_analysis',
                    'old_weight': 0.40,
                    'new_weight': 0.45,
                    'reason': reason['description']
                })
        
        return optimization
    
    def _analyze_market_environment(self, market_data: Dict) -> Dict:
        """分析市场环境"""
        return {
            'international_risk': 'high',
            'domestic_policy': 'neutral',
            'capital_flow': 'tight',
            'market_sentiment': 'pessimistic'
        }
    
    def _generate_stock_prediction(self, ts_code: str, stock_data: Dict, market_data: Dict, config_params: Dict) -> Dict:
        """生成单只股票的预测"""
        # 简化的预测逻辑（实际应更复杂）
        current_close = stock_data.get('close', 0)
        current_change = stock_data.get('pct_chg', 0)
        
        # 基于当前趋势和市场环境预测
        predicted_change = current_change * 0.5  # 简单的惯性预测
        
        pred_low = current_close * (1 + predicted_change/100 - 0.015)
        pred_high = current_close * (1 + predicted_change/100 + 0.015)
        
        return {
            'ts_code': ts_code,
            'stock_name': stock_data.get('stock_name', '未知'),
            'current_close': current_close,
            'predicted_range': (round(pred_low, 2), round(pred_high, 2)),
            'predicted_amplitude': abs(predicted_change),
            'risk_level': 'medium',
            'fundamental_score': 6.5,
            'time_predictions': [
                {'time': '09:30-10:30', 'price_range': (pred_low, pred_high), 'operation': '观察为主'},
                {'time': '10:30-11:30', 'price_range': (pred_low, pred_high), 'operation': '轻仓试探'},
                {'time': '13:00-14:00', 'price_range': (pred_low, pred_high), 'operation': '持有观察'},
                {'time': '14:00-15:00', 'price_range': (pred_low, pred_high), 'operation': '趋势跟踪'}
            ]
        }
    
    def _calculate_suggested_position(self, stock_predictions: List[Dict]) -> float:
        """计算建议仓位"""
        # 简单的平均风险评分
        avg_risk = np.mean([pred.get('fundamental_score', 5) for pred in stock_predictions])
        
        if avg_risk >= 7:
            return 0.35
        elif avg_risk >= 5:
            return 0.25
        else:
            return 0.15
    
    def _generate_stock_plan(self, prediction: Dict, config_params: Dict) -> Dict:
        """生成单只股票的投资计划"""
        return {
            'ts_code': prediction['ts_code'],
            'stock_name': prediction['stock_name'],
            'operation_advice': '谨慎参与',
            'suggested_position': 0.08,
            'buy_range': prediction['predicted_range'],
            'target_price': prediction['predicted_range'][1] * 1.05,
            'stop_loss_price': prediction['predicted_range'][0] * 0.97
        }
    
    def _generate_international_monitoring(self, market_data: Dict) -> List[str]:
        """生成国际监控要点"""
        return [
            '美元指数走势',
            '美联储政策预期',
            '中东局势发展',
            '原油价格变化',
            'VIX恐慌指数'
        ]
    
    def _calculate_position_control(self, stock_plans: List[Dict]) -> Dict:
        """计算仓位控制"""
        total_position = sum(plan.get('suggested_position', 0) for plan in stock_plans)
        
        return {
            'total_position': min(total_position, 0.45),
            'single_stock_max': 0.15,
            'sector_max': 0.20
        }
    
    def _assess_risk_level(self, market_data: Dict, stock_plans: List[Dict]) -> float:
        """评估风险等级"""
        # 简化的风险评估
        return 7.5  # 0-10分
    
    def _recommend_potential_stocks(self, market_data: Dict, config_params: Dict) -> List[Dict]:
        """推荐潜力股票"""
        # 简化的推荐逻辑
        return [
            {
                'ts_code': '600519.SH',
                'stock_name': '贵州茅台',
                'reason': '避险属性强，基本面稳健',
                'target_price': 1500,
                'stop_loss': 1420,
                'suggested_position': 0.12
            },
            {
                'ts_code': '603259.SH',
                'stock_name': '药明康德',
                'reason': '医药研发龙头，成长性好',
                'target_price': 105,
                'stop_loss': 94,
                'suggested_position': 0.10
            },
            {
                'ts_code': '300750.SZ',
                'stock_name': '宁德时代',
                'reason': '新能源龙头，政策支持',
                'target_price': 420,
                'stop_loss': 390,
                'suggested_position': 0.10
            }
        ]


def test_analysis_engine():
    """测试分析引擎"""
    from config.settings import config
    
    print("\n" + "="*60)
    print("测试分析引擎")
    print("="*60)
    
    engine = AnalysisEngine(config)
    
    # 模拟数据
    stocks_data = {
        '002506.SZ': {'close': 4.82, 'pct_chg': 1.47, 'pre_close': 4.75, 'stock_name': '协鑫集成'},
        '600821.SH': {'close': 9.04, 'pct_chg': 2.96, 'pre_close': 8.78, 'stock_name': '金开新能'}
    }
    
    predictions = {
        '002506.SZ': {'predicted_price_range': (4.55, 4.70), 'predicted_amplitude': 1.5, 'stock_name': '协鑫集成'},
        '600821.SH': {'predicted_price_range': (8.55, 8.70), 'predicted_amplitude': 1.0, 'stock_name': '金开新能'}
    }
    
    # 测试第1步
    print("\n1. 测试第1步：深度复盘")
    result = engine.step1_deep_review(stocks_data, predictions)
    print(f"✅ 方向准确率: {result['overall_performance'].get('direction_accuracy', 0):.2%}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_analysis_engine()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据获取模块
核心原则：数据是分析的基石，数据错了，分析再多都是错的
"""

import tushare as ts
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re

logger = logging.getLogger(__name__)

class DataFetcher:
    """股票数据获取器"""
    
    def __init__(self, token: str):
        """
        初始化数据获取器
        
        Args:
            token: Tushare Pro API Token
        """
        self.token = token
        ts.set_token(token)
        self.pro = ts.pro_api()
        logger.info("数据获取器初始化完成")
    
    def get_stock_daily_data(self, ts_code: str, trade_date: str) -> Optional[Dict]:
        """
        获取指定日期的股票日线数据
        
        Args:
            ts_code: 股票代码（如：000001.SZ）
            trade_date: 交易日期（格式：YYYYMMDD 或 YYYY-MM-DD）
        
        Returns:
            Dict: 股票日线数据，失败返回None
        """
        try:
            # 统一日期格式
            trade_date = trade_date.replace('-', '')
            
            logger.info(f"获取股票数据: {ts_code}, 日期: {trade_date}")
            
            # 使用daily接口获取日线数据
            df = self.pro.daily(ts_code=ts_code, trade_date=trade_date)
            
            if df.empty:
                logger.warning(f"未找到数据: {ts_code}, {trade_date}")
                return None
            
            # 转换为字典
            data = df.iloc[0].to_dict()
            
            # 验证关键数据
            if pd.isna(data.get('close')) or data.get('close') == 0:
                logger.error(f"数据异常: 收盘价为空或为0")
                return None
            
            logger.info(f"成功获取数据: {ts_code}, 收盘价: {data['close']}, 涨跌幅: {data['pct_chg']:.2f}%")
            
            return data
            
        except Exception as e:
            logger.error(f"获取股票数据失败: {ts_code}, {trade_date}, 错误: {str(e)}")
            return None
    
    def get_previous_trading_day(self, trade_date: str) -> Optional[str]:
        """
        获取上一个交易日
        
        Args:
            trade_date: 当前交易日期（格式：YYYYMMDD 或 YYYY-MM-DD）
        
        Returns:
            str: 上一个交易日（格式：YYYYMMDD），失败返回None
        """
        try:
            # 统一日期格式
            trade_date = trade_date.replace('-', '')
            
            # 获取交易日历
            df = self.pro.trade_cal(exchange='SSE', start_date=trade_date, end_date=trade_date)
            
            if df.empty:
                logger.warning(f"未找到交易日历: {trade_date}")
                return None
            
            # 如果当天不是交易日，往前找最近的交易日
            if df.iloc[0]['is_open'] == 0:
                logger.warning(f"{trade_date} 不是交易日")
                # 往前找10天内的交易日
                start_date = (datetime.strptime(trade_date, '%Y%m%d') - timedelta(days=10)).strftime('%Y%m%d')
                df = self.pro.trade_cal(exchange='SSE', start_date=start_date, end_date=trade_date, is_open='1')
                if df.empty:
                    return None
                return df.iloc[-1]['cal_date']
            
            # 往前找上一个交易日
            start_date = (datetime.strptime(trade_date, '%Y%m%d') - timedelta(days=10)).strftime('%Y%m%d')
            df = self.pro.trade_cal(exchange='SSE', start_date=start_date, end_date=trade_date, is_open='1')
            
            if len(df) < 2:
                logger.warning(f"未找到上一个交易日")
                return None
            
            return df.iloc[-2]['cal_date']
            
        except Exception as e:
            logger.error(f"获取上一个交易日失败: {trade_date}, 错误: {str(e)}")
            return None
    
    def parse_prediction_from_report(self, report_path: str) -> Dict[str, Dict]:
        """
        从昨日报告中解析预测数据
        
        Args:
            report_path: 报告文件路径
        
        Returns:
            Dict: 预测数据字典 {股票代码: {预测价格区间, 预测涨跌幅, ...}}
        """
        try:
            logger.info(f"解析预测报告: {report_path}")
            
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            predictions = {}
            
            # 解析每只股票的预测
            # 模式：匹配股票代码和预测价格区间
            # 例如：| **002506.SZ** | 协鑫集成 | **4.70-4.85元** | ±1.5% |
            pattern = r'\|\s*\*\*([0-9]{6}\.[A-Z]{2})\*\*\s*\|([^|]+)\|[^|]*\*\*([\d.]+)-([\d.]+)元\*\*\s*\|[^|]*±([\d.]+)%\s*\|'
            
            matches = re.findall(pattern, content)
            
            for match in matches:
                ts_code = match[0]
                stock_name = match[1].strip()
                price_low = float(match[2])
                price_high = float(match[3])
                amplitude = float(match[4])
                
                predictions[ts_code] = {
                    'stock_name': stock_name,
                    'predicted_price_range': (price_low, price_high),
                    'predicted_amplitude': amplitude,
                    'predicted_mid_price': (price_low + price_high) / 2
                }
                
                logger.info(f"解析预测: {ts_code} {stock_name}, 预测区间: {price_low}-{price_high}元")
            
            logger.info(f"成功解析 {len(predictions)} 只股票的预测数据")
            return predictions
            
        except Exception as e:
            logger.error(f"解析预测报告失败: {report_path}, 错误: {str(e)}")
            return {}
    
    def calculate_accuracy(self, predicted: Dict, actual: Dict) -> Dict:
        """
        计算预测准确性
        
        Args:
            predicted: 预测数据 {predicted_price_range, predicted_amplitude, ...}
            actual: 实际数据 {close, pct_chg, ...}
        
        Returns:
            Dict: 准确性指标 {direction_accuracy, amplitude_accuracy, overall_score}
        """
        try:
            pred_range = predicted.get('predicted_price_range', (0, 0))
            pred_mid = predicted.get('predicted_mid_price', 0)
            actual_close = actual.get('close', 0)
            actual_pct_chg = actual.get('pct_chg', 0)
            
            # 方向准确性
            # 预测涨跌方向是否正确
            predicted_direction = 1 if pred_mid > actual.get('pre_close', actual_close) else -1
            actual_direction = 1 if actual_pct_chg > 0 else -1
            direction_accuracy = 1.0 if predicted_direction == actual_direction else 0.0
            
            # 幅度准确性
            # 预测涨跌幅与实际涨跌幅的差异
            predicted_amplitude = predicted.get('predicted_amplitude', 0)
            amplitude_diff = abs(predicted_amplitude - abs(actual_pct_chg))
            amplitude_accuracy = max(0, 1 - amplitude_diff / 10)  # 简单的准确度计算
            
            # 综合评分
            overall_score = (direction_accuracy * 0.6 + amplitude_accuracy * 0.4) * 10
            
            result = {
                'direction_accuracy': direction_accuracy,
                'amplitude_accuracy': amplitude_accuracy,
                'overall_score': overall_score,
                'predicted_range': pred_range,
                'actual_close': actual_close,
                'actual_pct_chg': actual_pct_chg
            }
            
            logger.info(f"准确性计算: 方向准确率={direction_accuracy:.2%}, 幅度准确率={amplitude_accuracy:.2%}, 综合评分={overall_score:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"计算准确性失败: {str(e)}")
            return {
                'direction_accuracy': 0,
                'amplitude_accuracy': 0,
                'overall_score': 0
            }
    
    def get_market_overview(self, trade_date: str) -> Dict:
        """
        获取市场概况
        
        Args:
            trade_date: 交易日期（格式：YYYYMMDD 或 YYYY-MM-DD）
        
        Returns:
            Dict: 市场概况数据
        """
        try:
            trade_date = trade_date.replace('-', '')
            
            # 获取上证指数
            sh_index = self.pro.index_daily(ts_code='000001.SH', trade_date=trade_date)
            
            # 获取深证成指
            sz_index = self.pro.index_daily(ts_code='399001.SZ', trade_date=trade_date)
            
            # 获取创业板指
            cyb_index = self.pro.index_daily(ts_code='399006.SZ', trade_date=trade_date)
            
            market_data = {
                'trade_date': trade_date,
                'sh_index': sh_index.iloc[0].to_dict() if not sh_index.empty else None,
                'sz_index': sz_index.iloc[0].to_dict() if not sz_index.empty else None,
                'cyb_index': cyb_index.iloc[0].to_dict() if not cyb_index.empty else None
            }
            
            logger.info(f"获取市场概况成功: {trade_date}")
            return market_data
            
        except Exception as e:
            logger.error(f"获取市场概况失败: {trade_date}, 错误: {str(e)}")
            return {}


def test_data_fetcher():
    """测试数据获取器"""
    from config.tushare_config import TOKEN
    
    print("\n" + "="*60)
    print("测试数据获取器")
    print("="*60)
    
    fetcher = DataFetcher(TOKEN)
    
    # 测试获取股票数据
    print("\n1. 测试获取股票数据")
    data = fetcher.get_stock_daily_data('000001.SZ', '20260401')
    if data:
        print(f"✅ 成功获取数据: 收盘价={data['close']}, 涨跌幅={data['pct_chg']:.2f}%")
    else:
        print("❌ 获取数据失败")
    
    # 测试获取上一个交易日
    print("\n2. 测试获取上一个交易日")
    prev_day = fetcher.get_previous_trading_day('20260401')
    if prev_day:
        print(f"✅ 上一个交易日: {prev_day}")
    else:
        print("❌ 获取上一个交易日失败")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_data_fetcher()

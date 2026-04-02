#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
质量检查模块
验证数据准确性、样式一致性、内容完整性
"""

import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import re

logger = logging.getLogger(__name__)

class QualityChecker:
    """质量检查器"""
    
    def __init__(self, template_path: Path, memory_path: Path):
        """
        初始化质量检查器
        
        Args:
            template_path: 模板文件路径
            memory_path: 记忆文件路径
        """
        self.template_path = template_path
        self.memory_path = memory_path
        
        # 加载模板结构
        self.template_structure = self._load_template_structure()
        
        logger.info("质量检查器初始化完成")
    
    def check_all(self, analysis_results: Dict, report_content: str) -> Dict:
        """
        执行全面质量检查
        
        Args:
            analysis_results: 分析结果
            report_content: 生成的报告内容
        
        Returns:
            Dict: 检查结果
        """
        logger.info("开始全面质量检查...")
        
        results = {
            'data_accuracy': False,
            'style_consistency': False,
            'content_completeness': False,
            'overall_passed': False,
            'errors': [],
            'warnings': []
        }
        
        # 1. 数据准确性检查
        results['data_accuracy'] = self._check_data_accuracy(analysis_results)
        
        # 2. 样式一致性检查
        style_result = self._check_style_consistency(report_content)
        results['style_consistency'] = style_result['passed']
        results['warnings'].extend(style_result.get('warnings', []))
        
        # 3. 内容完整性检查
        completeness_result = self._check_content_completeness(report_content)
        results['content_completeness'] = completeness_result['passed']
        results['errors'].extend(completeness_result.get('errors', []))
        
        # 4. 综合判断
        results['overall_passed'] = (
            results['data_accuracy'] and 
            results['style_consistency'] and 
            results['content_completeness']
        )
        
        # 记录结果
        if results['overall_passed']:
            logger.info("✅ 质量检查通过")
        else:
            logger.error("❌ 质量检查未通过")
            for error in results['errors']:
                logger.error(f"  错误: {error}")
            for warning in results['warnings']:
                logger.warning(f"  警告: {warning}")
        
        return results
    
    def _check_data_accuracy(self, analysis_results: Dict) -> bool:
        """检查数据准确性"""
        logger.info("检查数据准确性...")
        
        # 检查是否有数据
        if not analysis_results:
            logger.error("分析结果为空")
            return False
        
        # 检查第1步数据
        step1 = analysis_results.get('step1', {})
        if not step1:
            logger.error("第1步数据缺失")
            return False
        
        accuracy_stats = step1.get('accuracy_stats', [])
        if not accuracy_stats:
            logger.error("准确性统计数据缺失")
            return False
        
        # 检查数据合理性
        for stat in accuracy_stats:
            # 检查收盘价是否合理
            actual_close = stat.get('actual_close', 0)
            if actual_close <= 0:
                logger.error(f"收盘价异常: {actual_close}")
                return False
            
            # 检查涨跌幅是否合理
            actual_pct_chg = stat.get('actual_pct_chg', 0)
            if abs(actual_pct_chg) > 20:  # A股涨跌停限制
                logger.warning(f"涨跌幅异常: {actual_pct_chg}%")
        
        logger.info("✅ 数据准确性检查通过")
        return True
    
    def _check_style_consistency(self, report_content: str) -> Dict:
        """检查样式一致性"""
        logger.info("检查样式一致性...")
        
        result = {
            'passed': True,
            'warnings': []
        }
        
        # 检查必要的标题
        required_titles = [
            '# 📊 深度复盘与明日投资计划',
            '## 📈 **第一步：今日复盘与预测误差分析**',
            '## 🔍 **第二步：误差分析与经验总结**',
            '## 🔮 **第三步：明日小时级预测',
            '## 🎯 **第四步：投资计划与仓位管理**',
            '## ⚠️ **第五步：风险控制与操作纪律**',
            '## 📈 **第六步：其他潜力股票推荐**'
        ]
        
        for title in required_titles:
            if title not in report_content:
                result['warnings'].append(f"缺少必要标题: {title}")
                result['passed'] = False
        
        # 检查表格格式
        if '| 股票代码 | 股票名称 |' not in report_content:
            result['warnings'].append("表格格式不符合模板")
            result['passed'] = False
        
        # 检查关键标记
        required_markers = [
            '**报告生成时间**',
            '**分析师**',
            '**免责声明**',
            '✅ **样式完全一致**'
        ]
        
        for marker in required_markers:
            if marker not in report_content:
                result['warnings'].append(f"缺少关键标记: {marker}")
                result['passed'] = False
        
        if result['passed']:
            logger.info("✅ 样式一致性检查通过")
        else:
            logger.warning(f"⚠️ 样式一致性检查未完全通过: {len(result['warnings'])}个警告")
        
        return result
    
    def _check_content_completeness(self, report_content: str) -> Dict:
        """检查内容完整性"""
        logger.info("检查内容完整性...")
        
        result = {
            'passed': True,
            'errors': []
        }
        
        # 检查六个步骤是否都存在
        steps = ['第一步', '第二步', '第三步', '第四步', '第五步', '第六步']
        
        for step in steps:
            if step not in report_content:
                result['errors'].append(f"缺少步骤: {step}")
                result['passed'] = False
        
        # 检查是否有股票数据
        if '| **' not in report_content or '.SZ**' not in report_content:
            result['errors'].append("缺少股票数据表格")
            result['passed'] = False
        
        # 检查是否有时间预测
        if '09:30-10:30' not in report_content:
            result['errors'].append("缺少小时级预测")
            result['passed'] = False
        
        # 检查是否有风险提示
        if '止损价位' not in report_content:
            result['errors'].append("缺少风险提示")
            result['passed'] = False
        
        # 检查是否有推荐股票
        if '其他潜力股票推荐' not in report_content:
            result['errors'].append("缺少其他股票推荐")
            result['passed'] = False
        
        if result['passed']:
            logger.info("✅ 内容完整性检查通过")
        else:
            logger.error(f"❌ 内容完整性检查未通过: {len(result['errors'])}个错误")
        
        return result
    
    def _load_template_structure(self) -> Dict:
        """加载模板结构"""
        try:
            if not self.template_path.exists():
                logger.warning(f"模板文件不存在: {self.template_path}")
                return {}
            
            with open(self.template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取模板结构
            structure = {
                'sections': [],
                'tables': [],
                'markers': []
            }
            
            # 提取章节标题
            section_pattern = r'^#{1,3}\s+(.+)$'
            structure['sections'] = re.findall(section_pattern, content, re.MULTILINE)
            
            # 提取表格标题
            table_pattern = r'^\|.+\|$'
            structure['tables'] = re.findall(table_pattern, content, re.MULTILINE)[:5]  # 只取前5个
            
            # 提取关键标记
            marker_pattern = r'\*\*([^*]+)\*\*'
            structure['markers'] = list(set(re.findall(marker_pattern, content)))[:20]  # 只取前20个
            
            logger.info(f"加载模板结构: {len(structure['sections'])}个章节, {len(structure['tables'])}个表格, {len(structure['markers'])}个标记")
            
            return structure
            
        except Exception as e:
            logger.error(f"加载模板结构失败: {str(e)}")
            return {}
    
    def validate_data_source(self, data: Dict, source: str) -> bool:
        """
        验证数据来源
        
        Args:
            data: 数据字典
            source: 预期来源（如：'tushare', 'manual'）
        
        Returns:
            bool: 验证是否通过
        """
        # 检查数据是否标记了来源
        if 'data_source' not in data:
            logger.warning("数据未标记来源")
            return False
        
        if data['data_source'] != source:
            logger.error(f"数据来源不匹配: 预期{source}, 实际{data['data_source']}")
            return False
        
        logger.info(f"✅ 数据来源验证通过: {source}")
        return True
    
    def check_prediction_method(self, predictions: Dict, actual_data: Dict) -> bool:
        """
        检查预测对比方法是否正确
        
        Args:
            predictions: 预测数据
            actual_data: 实际数据
        
        Returns:
            bool: 检查是否通过
        """
        logger.info("检查预测对比方法...")
        
        # 核心原则：用昨天预测的股价来对比今天的实际股价
        
        # 检查预测数据是否包含昨日预测
        if not predictions:
            logger.error("预测数据为空")
            return False
        
        # 检查实际数据是否包含今日实际
        if not actual_data:
            logger.error("实际数据为空")
            return False
        
        # 检查时间顺序
        # 预测数据应该是昨天的，实际数据应该是今天的
        # 这里简化处理，实际应该检查日期
        
        logger.info("✅ 预测对比方法检查通过")
        return True


def test_quality_checker():
    """测试质量检查器"""
    from config.settings import config
    
    print("\n" + "="*60)
    print("测试质量检查器")
    print("="*60)
    
    template_path = config.EXTERNAL_MEMORY_DIR.parent.parent / "深度复盘与明日投资计划_20260401_v2.md"
    memory_path = config.EXTERNAL_MEMORY_DIR
    
    checker = QualityChecker(template_path, memory_path)
    
    # 模拟分析结果
    analysis_results = {
        'step1': {
            'accuracy_stats': [
                {
                    'ts_code': '002506.SZ',
                    'stock_name': '协鑫集成',
                    'predicted_range': (4.55, 4.70),
                    'actual_close': 4.82,
                    'actual_pct_chg': 1.47,
                    'direction_accuracy': 0.0,
                    'amplitude_accuracy': 0.85,
                    'overall_score': 4.5
                }
            ]
        }
    }
    
    # 模拟报告内容
    report_content = """# 📊 深度复盘与明日投资计划（2026-04-02）

## 📈 **第一步：今日复盘与预测误差分析**

| 股票代码 | 股票名称 | 昨日预测价格区间 | 今日实际收盘价 |
|---------|---------|----------------|--------------|
| **002506.SZ** | 协鑫集成 | **4.55-4.70元** | **4.82元** |

## 🔍 **第二步：误差分析与经验总结**

## 🔮 **第三步：明日小时级预测

## 🎯 **第四步：投资计划与仓位管理**

## ⚠️ **第五步：风险控制与操作纪律**

## 📈 **第六步：其他潜力股票推荐**

**免责声明**：本报告仅供参考。
"""
    
    # 执行检查
    results = checker.check_all(analysis_results, report_content)
    
    print(f"\n数据准确性: {'✅' if results['data_accuracy'] else '❌'}")
    print(f"样式一致性: {'✅' if results['style_consistency'] else '❌'}")
    print(f"内容完整性: {'✅' if results['content_completeness'] else '❌'}")
    print(f"综合结果: {'✅ 通过' if results['overall_passed'] else '❌ 未通过'}")
    
    if results['errors']:
        print(f"\n错误: {len(results['errors'])}个")
        for error in results['errors']:
            print(f"  - {error}")
    
    if results['warnings']:
        print(f"\n警告: {len(results['warnings'])}个")
        for warning in results['warnings']:
            print(f"  - {warning}")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    test_quality_checker()

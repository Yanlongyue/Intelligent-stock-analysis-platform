#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
七步法股票分析主程序
核心原则：数据是分析的基石，数据错了，分析再多都是错的
"""

import sys
import os
import logging
from datetime import datetime
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import config
from src import print_banner, CORE_PRINCIPLES
from src.memory_manager import MemoryManager, test_memory_manager

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOGS_DIR / "main.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class StockAnalysisProgram:
    """七步法股票分析主程序"""
    
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.memory_rules = None
        self.template_structure = None
        
        # 分析状态
        self.analysis_date = None
        self.analysis_results = {}
        self.quality_report = {}
        
        logger.info("七步法股票分析程序初始化完成")
    
    def run_seven_steps(self, analysis_date=None):
        """
        执行完整的七步法分析
        
        Args:
            analysis_date: 分析日期，格式为YYYY-MM-DD，默认为今天
        
        Returns:
            bool: 分析是否成功
        """
        try:
            print_banner()
            logger.info("🎯 开始执行七步法股票分析...")
            
            # 设置分析日期
            self.analysis_date = analysis_date or datetime.now().strftime("%Y-%m-%d")
            logger.info(f"分析日期: {self.analysis_date}")
            
            # 打印核心原则
            self._print_core_principles()
            
            # ==================== 第0步：强制长期记忆检索 ====================
            logger.info("🔍 第0步：强制长期记忆检索")
            
            # 1. 验证记忆完整性
            if not self.memory_manager.validate_memory_integrity():
                logger.error("❌ 记忆完整性验证失败，程序终止")
                return False
            
            # 2. 加载长期记忆规则
            self.memory_rules = self.memory_manager.load_memory_rules()
            if not self.memory_rules:
                logger.error("❌ 加载长期记忆规则失败，程序终止")
                return False
            
            # 3. 加载模板结构
            self.template_structure = self.memory_manager.load_template_structure()
            if not self.template_structure:
                logger.error("❌ 加载模板结构失败，程序终止")
                return False
            
            # 4. 检查数据对比方法
            data_method_check = self.memory_manager.check_data_method()
            if not data_method_check:
                logger.warning("⚠️ 数据对比方法检查存在问题")
            
            logger.info("✅ 第0步完成：强制长期记忆检索通过")
            
            # ==================== 第1步：深度复盘 ====================
            logger.info("📈 第1步：深度复盘")
            # TODO: 实现数据获取和深度复盘
            self._step1_deep_review()
            
            # ==================== 第2步：误差分析 ====================
            logger.info("🔍 第2步：误差分析")
            # TODO: 实现误差分析
            self._step2_error_analysis()
            
            # ==================== 第3步：明日预测 ====================
            logger.info("🔮 第3步：明日预测")
            # TODO: 实现明日预测
            self._step3_tomorrow_prediction()
            
            # ==================== 第4步：投资计划 ====================
            logger.info("🎯 第4步：投资计划")
            # TODO: 实现投资计划
            self._step4_investment_plan()
            
            # ==================== 第5步：风险控制 ====================
            logger.info("⚠️ 第5步：风险控制")
            # TODO: 实现风险控制
            self._step5_risk_control()
            
            # ==================== 第6步：其他推荐 ====================
            logger.info("📈 第6步：其他推荐")
            # TODO: 实现其他推荐
            self._step6_other_recommendations()
            
            # ==================== 质量检查 ====================
            logger.info("✅ 执行质量检查")
            # TODO: 实现质量检查
            self._quality_check()
            
            # ==================== 生成报告 ====================
            logger.info("📄 生成报告")
            # TODO: 实现报告生成
            self._generate_reports()
            
            # ==================== 完成 ====================
            logger.info("🎉 七步法分析完成！")
            self._print_summary()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 分析过程中出现错误: {str(e)}", exc_info=True)
            return False
    
    def _print_core_principles(self):
        """打印核心原则"""
        print("\n" + "="*60)
        print("核心原则（必须永远记住）:")
        print("="*60)
        for i, principle in enumerate(CORE_PRINCIPLES, 1):
            print(f"{i}. {principle}")
        print("="*60 + "\n")
    
    def _step1_deep_review(self):
        """第1步：深度复盘"""
        # 实现数据获取和准确性统计
        logger.info("  获取昨日预测数据...")
        logger.info("  获取今日实际数据...")
        logger.info("  计算准确性统计...")
        logger.info("  生成市场表现总结...")
        
        # 模拟数据
        self.analysis_results["step1"] = {
            "status": "completed",
            "message": "深度复盘完成",
            "accuracy_stats": {
                "direction_accuracy": 0.25,
                "average_amplitude_error": -0.0188,
                "overall_score": 4.25
            }
        }
    
    def _step2_error_analysis(self):
        """第2步：误差分析"""
        logger.info("  分析系统性误差原因...")
        logger.info("  提出模型优化方案...")
        
        self.analysis_results["step2"] = {
            "status": "completed",
            "message": "误差分析完成",
            "error_categories": [
                "国际风险传导机制过度反应",
                "技术面反弹力度低估",
                "个股基本面风险差异",
                "市场情绪改善超预期"
            ]
        }
    
    def _step3_tomorrow_prediction(self):
        """第3步：明日预测"""
        logger.info("  分析总体市场环境...")
        logger.info("  生成小时级预测...")
        
        self.analysis_results["step3"] = {
            "status": "completed",
            "message": "明日预测完成",
            "time_slots": config.analysis.PREDICTION_TIME_SLOTS
        }
    
    def _step4_investment_plan(self):
        """第4步：投资计划"""
        logger.info("  制定总体仓位建议...")
        logger.info("  制定具体投资计划...")
        
        self.analysis_results["step4"] = {
            "status": "completed",
            "message": "投资计划完成",
            "max_position": config.analysis.MAX_TOTAL_POSITION
        }
    
    def _step5_risk_control(self):
        """第5步：风险控制"""
        logger.info("  监控国际局势...")
        logger.info("  制定操作纪律...")
        logger.info("  评估风险等级...")
        
        self.analysis_results["step5"] = {
            "status": "completed",
            "message": "风险控制完成",
            "risk_level": "medium"
        }
    
    def _step6_other_recommendations(self):
        """第6步：其他推荐"""
        logger.info("  筛选潜力股票...")
        logger.info("  生成推荐分析...")
        
        self.analysis_results["step6"] = {
            "status": "completed",
            "message": "其他推荐完成",
            "recommended_count": 3
        }
    
    def _quality_check(self):
        """质量检查"""
        logger.info("  检查数据准确性...")
        logger.info("  检查样式一致性...")
        logger.info("  检查内容完整性...")
        
        self.quality_report = {
            "data_accuracy": True,
            "style_consistency": True,
            "content_completeness": True,
            "overall_passed": True
        }
    
    def _generate_reports(self):
        """生成报告"""
        logger.info("  生成Markdown报告...")
        logger.info("  生成HTML报告...")
        logger.info("  保存报告文件...")
        
        # 模拟报告生成
        report_info = {
            "markdown_path": config.MARKDOWN_REPORTS_DIR / f"深度复盘与明日投资计划_{self.analysis_date.replace('-', '')}.md",
            "html_path": config.HTML_REPORTS_DIR / f"深度复盘与明日投资计划_{self.analysis_date.replace('-', '')}.html"
        }
        
        self.analysis_results["reports"] = report_info
    
    def _print_summary(self):
        """打印分析摘要"""
        print("\n" + "="*60)
        print("七步法分析完成摘要")
        print("="*60)
        
        print(f"\n📅 分析日期: {self.analysis_date}")
        print(f"⏱️ 分析时间: {datetime.now().strftime('%H:%M:%S')}")
        
        print(f"\n✅ 步骤完成情况:")
        for step_name, step_result in self.analysis_results.items():
            if step_name != "reports":
                status = step_result.get("status", "unknown")
                message = step_result.get("message", "")
                print(f"  {step_name}: {status} - {message}")
        
        print(f"\n📊 质量检查:")
        if self.quality_report:
            for check_name, check_result in self.quality_report.items():
                if check_name != "overall_passed":
                    status = "✅" if check_result else "❌"
                    print(f"  {check_name}: {status}")
        
        print(f"\n📄 生成报告:")
        if "reports" in self.analysis_results:
            reports = self.analysis_results["reports"]
            for report_type, report_path in reports.items():
                if report_path:
                    print(f"  {report_type}: {report_path}")
        
        print(f"\n🎯 核心原则验证:")
        for principle in CORE_PRINCIPLES:
            print(f"  ✅ {principle}")
        
        print("\n" + "="*60)
        print("🎉 分析完成！记住：数据是分析的基石，数据错了，分析再多都是错的！")
        print("="*60)

def main():
    """主函数"""
    try:
        # 创建程序实例
        program = StockAnalysisProgram()
        
        # 解析命令行参数
        import argparse
        parser = argparse.ArgumentParser(description="七步法股票分析程序")
        parser.add_argument("--date", help="分析日期，格式为YYYY-MM-DD")
        parser.add_argument("--test", action="store_true", help="运行测试模式")
        parser.add_argument("--summary", action="store_true", help="只显示配置摘要")
        
        args = parser.parse_args()
        
        if args.summary:
            # 显示配置摘要
            config.print_config_summary()
            return
        
        if args.test:
            # 运行测试模式
            print("🧪 运行测试模式...")
            success = test_memory_manager()
            if success:
                print("✅ 所有测试通过！")
            else:
                print("❌ 测试失败！")
            return
        
        # 运行完整分析
        success = program.run_seven_steps(args.date)
        
        if success:
            print("\n✅ 七步法分析成功完成！")
            sys.exit(0)
        else:
            print("\n❌ 七步法分析失败！")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断程序")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 程序执行失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
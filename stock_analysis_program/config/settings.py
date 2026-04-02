#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
七步法股票分析程序 - 配置文件
核心原则：数据是分析的基石，数据错了，分析再多都是错的
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
HISTORICAL_DATA_DIR = DATA_DIR / "historical_data"
PREDICTIONS_DIR = DATA_DIR / "predictions"
CACHE_DIR = DATA_DIR / "cache"

# 报告目录
REPORTS_DIR = PROJECT_ROOT / "reports"
MARKDOWN_REPORTS_DIR = REPORTS_DIR / "markdown"
HTML_REPORTS_DIR = REPORTS_DIR / "html"
BACKUP_REPORTS_DIR = REPORTS_DIR / "backup"

# 模板目录
TEMPLATES_DIR = PROJECT_ROOT / "templates"
MARKDOWN_TEMPLATE_FILE = TEMPLATES_DIR / "report_template.md"
HTML_TEMPLATE_FILE = TEMPLATES_DIR / "report_template.html"
MEMORY_TEMPLATE_FILE = TEMPLATES_DIR / "memory_template.md"

# 日志目录
LOGS_DIR = PROJECT_ROOT / "logs"
ERROR_LOG_FILE = LOGS_DIR / "error.log"
ANALYSIS_LOG_FILE = LOGS_DIR / "analysis.log"
MEMORY_LOG_FILE = LOGS_DIR / "memory.log"
QUALITY_LOG_FILE = LOGS_DIR / "quality.log"

# 外部记忆文件路径（从现有项目中读取）
EXTERNAL_MEMORY_PATH = Path("/Users/yandada/WorkBuddy/Claw/.workbuddy/memory/MEMORY.md")
EXTERNAL_TEMPLATE_PATH = Path("/Users/yandada/WorkBuddy/Claw/深度复盘与明日投资计划_20260401_v2.md")

# 默认分析股票
DEFAULT_STOCKS: List[str] = [
    "002506.SZ",  # 协鑫集成
    "600821.SH",  # 金开新能
    "002470.SZ",  # 金正大
    "601868.SH",  # 中国能建
]

# 推荐股票池
RECOMMENDATION_STOCKS: List[str] = [
    "600519.SH",  # 贵州茅台
    "603259.SH",  # 药明康德
    "300750.SZ",  # 宁德时代
    "000858.SZ",  # 五粮液
    "000333.SZ",  # 美的集团
    "002415.SZ",  # 海康威视
    "601318.SH",  # 中国平安
    "000001.SZ",  # 平安银行
    "600036.SH",  # 招商银行
    "601888.SH",  # 中国中免
]

# 分析参数配置
class AnalysisConfig:
    """分析参数配置"""
    
    # 时间配置
    ANALYSIS_TIME = "17:00"  # 每天17:00执行分析
    MARKET_OPEN_TIME = "09:30"
    MARKET_CLOSE_TIME = "15:00"
    
    # 预测时间段
    PREDICTION_TIME_SLOTS = [
        ("09:30", "10:30"),
        ("10:30", "11:30"),
        ("13:00", "14:00"),
        ("14:00", "15:00"),
    ]
    
    # 准确性计算参数
    DIRECTION_ACCURACY_THRESHOLD = 0.5  # 方向准确率阈值
    AMPLITUDE_ACCURACY_THRESHOLD = 0.05  # 幅度准确率阈值（5%）
    
    # 评分参数
    MAX_SCORE = 10  # 最高分
    DIRECTION_WEIGHT = 0.6  # 方向准确率权重
    AMPLITUDE_WEIGHT = 0.4  # 幅度准确率权重
    
    # 风险等级参数
    RISK_LEVELS = {
        "high": {"threshold": 8.0, "color": "red", "stop_loss": 0.03},
        "medium_high": {"threshold": 6.0, "color": "orange", "stop_loss": 0.05},
        "medium": {"threshold": 4.0, "color": "yellow", "stop_loss": 0.07},
        "low": {"threshold": 0.0, "color": "green", "stop_loss": 0.10},
    }
    
    # 仓位管理参数
    MAX_TOTAL_POSITION = 0.45  # 总仓位上限45%
    MAX_SINGLE_POSITION = 0.15  # 单股仓位上限15%
    POSITION_TIERS = {
        "tier1": {"weight": 0.4, "description": "主力仓位"},
        "tier2": {"weight": 0.3, "description": "防守仓位"},
        "tier3": {"weight": 0.3, "description": "试探仓位"},
    }
    
    # 模型权重参数（基于20260401_v2模板）
    MODEL_WEIGHTS = {
        "international_risk": 0.55,  # 国际风险权重
        "fundamental": 0.65,  # 基本面权重
        "technical": 0.40,  # 技术面权重
        "sentiment": 0.25,  # 情绪面权重
        "capital": 0.20,  # 资金面权重
    }

# 日志配置
class LogConfig:
    """日志配置"""
    
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    
    # 日志文件大小限制（MB）
    MAX_LOG_SIZE = 10
    BACKUP_COUNT = 5

# 数据源配置
class DataSourceConfig:
    """数据源配置"""
    
    # Tushare Pro API配置
    TUSHARE_TOKEN = ""  # 需要在tushare_config.py中配置
    TUSHARE_TIMEOUT = 30  # 请求超时时间（秒）
    TUSHARE_RETRY_COUNT = 3  # 重试次数
    
    # 数据缓存配置
    CACHE_ENABLED = True
    CACHE_EXPIRE_HOURS = 24  # 缓存过期时间（小时）
    
    # 数据验证配置
    VALIDATE_DATA = True
    CROSS_VALIDATION_SOURCES = []  # 交叉验证数据源

# 报告生成配置
class ReportConfig:
    """报告生成配置"""
    
    # 报告格式配置
    REPORT_ENCODING = "utf-8"
    REPORT_DATE_FORMAT = "%Y年%m月%d日"
    REPORT_FILENAME_FORMAT = "深度复盘与明日投资计划_%Y%m%d"
    
    # Markdown配置
    MARKDOWN_EXTENSIONS = [
        "tables",  # 表格支持
        "fenced_code",  # 代码块
        "toc",  # 目录
        "nl2br",  # 换行转<br>
    ]
    
    # HTML配置
    HTML_TITLE = "深度复盘与明日投资计划"
    HTML_STYLE = "default"  # 可选：default, dark, minimal
    HTML_INCLUDE_CSS = True
    HTML_INCLUDE_JS = True
    
    # 下载功能配置
    ENABLE_DOWNLOAD = True
    DOWNLOAD_FORMATS = ["md", "html", "pdf"]  # 支持下载的格式

# 质量检查配置
class QualityConfig:
    """质量检查配置"""
    
    # 检查项配置
    CHECKS = {
        "data_accuracy": True,
        "style_consistency": True,
        "content_completeness": True,
        "function_completeness": True,
    }
    
    # 数据准确性检查
    DATA_ACCURACY_THRESHOLD = 0.99  # 数据准确性阈值（99%）
    ALLOW_DATA_CORRECTION = True  # 允许数据纠正
    MAX_CORRECTION_ATTEMPTS = 3  # 最大纠正尝试次数
    
    # 样式一致性检查
    STYLE_TOLERANCE = 0.95  # 样式一致性容忍度（95%）
    ALLOW_STYLE_ADJUSTMENT = True  # 允许样式调整
    
    # 错误处理
    STOP_ON_CRITICAL_ERROR = True  # 关键错误时停止
    GENERATE_ERROR_REPORT = True  # 生成错误报告
    NOTIFY_ON_ERROR = False  # 错误时通知

# 调度配置
class SchedulerConfig:
    """调度配置"""
    
    # 定时任务配置
    ENABLE_SCHEDULER = True
    SCHEDULE_TYPE = "daily"  # daily, weekly, monthly
    
    # 执行时间配置
    EXECUTION_TIME = "17:00"  # 每天执行时间
    EXECUTION_DAY = "mon-fri"  # 执行日（周一到周五）
    
    # 重试配置
    MAX_RETRIES = 3  # 最大重试次数
    RETRY_DELAY = 300  # 重试延迟（秒）
    
    # 超时配置
    EXECUTION_TIMEOUT = 3600  # 执行超时时间（秒）

# 系统配置
class SystemConfig:
    """系统配置"""
    
    # 系统资源限制
    MAX_MEMORY_USAGE = 0.8  # 最大内存使用率
    MAX_CPU_USAGE = 0.7  # 最大CPU使用率
    MAX_DISK_USAGE = 0.9  # 最大磁盘使用率
    
    # 性能监控
    ENABLE_MONITORING = True
    MONITORING_INTERVAL = 60  # 监控间隔（秒）
    
    # 清理配置
    ENABLE_CLEANUP = True
    CLEANUP_SCHEDULE = "weekly"  # 清理计划
    MAX_REPORT_AGE = 30  # 报告最大保存天数
    MAX_LOG_AGE = 7  # 日志最大保存天数

# 导出配置类
class Config:
    """主配置类"""
    
    # 目录配置
    PROJECT_ROOT = PROJECT_ROOT
    DATA_DIR = DATA_DIR
    REPORTS_DIR = REPORTS_DIR
    TEMPLATES_DIR = TEMPLATES_DIR
    LOGS_DIR = LOGS_DIR
    
    # 外部文件路径
    EXTERNAL_MEMORY_PATH = EXTERNAL_MEMORY_PATH
    EXTERNAL_TEMPLATE_PATH = EXTERNAL_TEMPLATE_PATH
    
    # 股票配置
    DEFAULT_STOCKS = DEFAULT_STOCKS
    RECOMMENDATION_STOCKS = RECOMMENDATION_STOCKS
    
    # 配置实例
    analysis = AnalysisConfig()
    log = LogConfig()
    data_source = DataSourceConfig()
    report = ReportConfig()
    quality = QualityConfig()
    scheduler = SchedulerConfig()
    system = SystemConfig()
    
    # 核心原则（必须永远记住）
    CORE_PRINCIPLES = [
        "数据是分析的基石，数据错了，分析再多都是错的",
        "对比方法必须正确：用昨天预测的股价来对比今天的实际股价",
        "样式布局必须一致：保持与模板完全相同的结构和排版",
        "强制记忆检索必须执行：每次分析前必须读取长期记忆",
    ]
    
    @classmethod
    def ensure_directories(cls):
        """确保所有目录都存在"""
        directories = [
            DATA_DIR, HISTORICAL_DATA_DIR, PREDICTIONS_DIR, CACHE_DIR,
            REPORTS_DIR, MARKDOWN_REPORTS_DIR, HTML_REPORTS_DIR, BACKUP_REPORTS_DIR,
            TEMPLATES_DIR, LOGS_DIR,
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print(f"✅ 目录已创建: {directory}")
        
        # 检查外部文件是否存在
        if not cls.EXTERNAL_MEMORY_PATH.exists():
            print(f"⚠️ 警告：外部记忆文件不存在: {cls.EXTERNAL_MEMORY_PATH}")
        
        if not cls.EXTERNAL_TEMPLATE_PATH.exists():
            print(f"⚠️ 警告：外部模板文件不存在: {cls.EXTERNAL_TEMPLATE_PATH}")
    
    @classmethod
    def print_config_summary(cls):
        """打印配置摘要"""
        print("\n" + "="*60)
        print("七步法股票分析程序 - 配置摘要")
        print("="*60)
        
        print(f"\n📁 目录配置:")
        print(f"  项目根目录: {cls.PROJECT_ROOT}")
        print(f"  数据目录: {cls.DATA_DIR}")
        print(f"  报告目录: {cls.REPORTS_DIR}")
        print(f"  模板目录: {cls.TEMPLATES_DIR}")
        print(f"  日志目录: {cls.LOGS_DIR}")
        
        print(f"\n📊 股票配置:")
        print(f"  默认分析股票: {', '.join(cls.DEFAULT_STOCKS)}")
        print(f"  推荐股票数量: {len(cls.RECOMMENDATION_STOCKS)}")
        
        print(f"\n⚙️ 分析参数:")
        print(f"  分析时间: {cls.analysis.ANALYSIS_TIME}")
        print(f"  总仓位上限: {cls.analysis.MAX_TOTAL_POSITION*100}%")
        print(f"  单股仓位上限: {cls.analysis.MAX_SINGLE_POSITION*100}%")
        
        print(f"\n🎯 核心原则:")
        for i, principle in enumerate(cls.CORE_PRINCIPLES, 1):
            print(f"  {i}. {principle}")
        
        print("\n" + "="*60)

# 确保目录存在
Config.ensure_directories()

# 导出配置实例
config = Config()

if __name__ == "__main__":
    # 测试配置
    config.print_config_summary()
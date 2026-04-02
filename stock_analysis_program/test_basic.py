#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
七步法股票分析程序 - 基础测试脚本
测试记忆管理模块和核心功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.append(str(Path(__file__).parent))

from src.memory_manager import MemoryManager, test_memory_manager
from config.settings import config

def test_directory_structure():
    """测试目录结构"""
    print("🧪 测试目录结构...")
    
    directories = [
        config.PROJECT_ROOT,
        config.DATA_DIR,
        config.HISTORICAL_DATA_DIR,
        config.PREDICTIONS_DIR,
        config.CACHE_DIR,
        config.REPORTS_DIR,
        config.MARKDOWN_REPORTS_DIR,
        config.HTML_REPORTS_DIR,
        config.BACKUP_REPORTS_DIR,
        config.TEMPLATES_DIR,
        config.LOGS_DIR,
    ]
    
    all_exists = True
    for directory in directories:
        if directory.exists():
            print(f"✅ {directory} 存在")
        else:
            print(f"❌ {directory} 不存在")
            all_exists = False
    
    return all_exists

def test_configuration():
    """测试配置"""
    print("\n🧪 测试配置...")
    
    # 打印配置摘要
    config.print_config_summary()
    
    # 检查核心原则
    print(f"\n🎯 核心原则数量: {len(config.CORE_PRINCIPLES)}")
    for i, principle in enumerate(config.CORE_PRINCIPLES, 1):
        print(f"  {i}. {principle}")
    
    return True

def test_memory_files():
    """测试记忆文件"""
    print("\n🧪 测试记忆文件...")
    
    # 检查外部记忆文件
    if config.EXTERNAL_MEMORY_PATH.exists():
        print(f"✅ 外部记忆文件存在: {config.EXTERNAL_MEMORY_PATH}")
        
        # 读取文件内容
        with open(config.EXTERNAL_MEMORY_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查核心原则是否存在
        principles_found = 0
        for principle in config.CORE_PRINCIPLES:
            if principle in content:
                principles_found += 1
        
        print(f"✅ 核心原则匹配: {principles_found}/{len(config.CORE_PRINCIPLES)}")
    else:
        print(f"❌ 外部记忆文件不存在: {config.EXTERNAL_MEMORY_PATH}")
        return False
    
    # 检查外部模板文件
    if config.EXTERNAL_TEMPLATE_PATH.exists():
        print(f"✅ 外部模板文件存在: {config.EXTERNAL_TEMPLATE_PATH}")
        
        # 读取文件内容
        with open(config.EXTERNAL_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键元素
        checks = {
            "标题格式": "# 📊 深度复盘与明日投资计划" in content,
            "步骤分隔符": "---" in content,
            "表格格式": "|" in content,
            "风险等级": "**高风险**" in content or "**中风险**" in content or "**低风险**" in content,
        }
        
        passed_checks = sum(checks.values())
        total_checks = len(checks)
        
        print(f"✅ 模板关键元素检查: {passed_checks}/{total_checks}")
        
        for check_name, check_result in checks.items():
            status = "✅" if check_result else "❌"
            print(f"  {status} {check_name}")
    else:
        print(f"❌ 外部模板文件不存在: {config.EXTERNAL_TEMPLATE_PATH}")
        return False
    
    return True

def test_memory_manager():
    """测试记忆管理器"""
    print("\n🧪 测试记忆管理器...")
    
    try:
        # 创建记忆管理器实例
        manager = MemoryManager()
        
        # 验证记忆完整性
        if not manager.validate_memory_integrity():
            print("❌ 记忆完整性验证失败")
            return False
        
        # 加载记忆规则
        memory_rules = manager.load_memory_rules()
        if not memory_rules:
            print("❌ 加载记忆规则失败")
            return False
        
        print(f"✅ 记忆规则加载成功: {len(memory_rules)} 条规则")
        
        # 加载模板结构
        template_structure = manager.load_template_structure()
        if not template_structure:
            print("❌ 加载模板结构失败")
            return False
        
        print(f"✅ 模板结构加载成功: {len(template_structure.get('sections', []))} 个章节")
        
        # 打印摘要
        manager.print_memory_summary()
        
        return True
        
    except Exception as e:
        print(f"❌ 记忆管理器测试失败: {str(e)}")
        return False

def test_main_program():
    """测试主程序"""
    print("\n🧪 测试主程序...")
    
    try:
        # 导入主程序
        from src.main import StockAnalysisProgram
        
        # 创建程序实例
        program = StockAnalysisProgram()
        
        print("✅ 主程序实例创建成功")
        
        # 测试核心原则打印
        print("\n🎯 测试核心原则打印:")
        program._print_core_principles()
        
        return True
        
    except Exception as e:
        print(f"❌ 主程序测试失败: {str(e)}")
        return False

def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("七步法股票分析程序 - 基础测试")
    print("="*60)
    
    tests = [
        ("目录结构", test_directory_structure),
        ("配置", test_configuration),
        ("记忆文件", test_memory_files),
        ("记忆管理器", test_memory_manager),
        ("主程序", test_main_program),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n📋 运行测试: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            status = "✅" if result else "❌"
            print(f"{status} {test_name}测试完成")
        except Exception as e:
            print(f"❌ {test_name}测试失败: {str(e)}")
            results.append((test_name, False))
    
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed_tests = sum(1 for _, result in results if result)
    total_tests = len(results)
    
    print(f"\n📊 测试统计:")
    print(f"  总测试数: {total_tests}")
    print(f"  通过测试: {passed_tests}")
    print(f"  失败测试: {total_tests - passed_tests}")
    print(f"  通过率: {passed_tests/total_tests:.1%}")
    
    print(f"\n📋 详细结果:")
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")
    
    print("\n" + "="*60)
    
    if passed_tests == total_tests:
        print("🎉 所有测试通过！程序基础功能正常")
        return True
    else:
        print("⚠️ 部分测试失败，需要修复")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n✅ 基础测试完成，程序可以正常运行")
        print("\n下一步:")
        print("1. 配置Tushare Token")
        print("2. 运行完整分析: python src/main.py")
        print("3. 查看生成报告")
    else:
        print("\n❌ 基础测试失败，需要修复问题")
        print("\n需要修复:")
        print("1. 检查目录结构")
        print("2. 检查配置文件")
        print("3. 检查记忆文件")
    
    sys.exit(0 if success else 1)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
记忆管理模块 - 对应第0步：强制长期记忆检索
核心原则：数据是分析的基石，数据错了，分析再多都是错的
"""

import re
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import logging

from config.settings import config

# 设置日志
logger = logging.getLogger(__name__)

class MemoryManager:
    """记忆管理器 - 负责第0步：强制长期记忆检索"""
    
    def __init__(self):
        self.memory_rules = {}
        self.template_structure = {}
        self.core_principles = []
        
    def load_memory_rules(self) -> Dict[str, Any]:
        """
        加载长期记忆规则
        从外部记忆文件读取规则和教训
        """
        try:
            memory_path = config.EXTERNAL_MEMORY_PATH
            
            if not memory_path.exists():
                logger.error(f"记忆文件不存在: {memory_path}")
                raise FileNotFoundError(f"记忆文件不存在: {memory_path}")
            
            with open(memory_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析记忆内容
            self.memory_rules = self._parse_memory_content(content)
            
            # 提取核心原则
            self.core_principles = self._extract_core_principles(content)
            
            logger.info(f"✅ 长期记忆规则加载成功，共{len(self.memory_rules)}条规则")
            logger.info(f"✅ 核心原则: {len(self.core_principles)}条")
            
            return self.memory_rules
            
        except Exception as e:
            logger.error(f"❌ 加载长期记忆规则失败: {str(e)}")
            raise
    
    def _parse_memory_content(self, content: str) -> Dict[str, Any]:
        """解析记忆内容，提取规则"""
        rules = {}
        
        # 提取用户最新指示部分
        user_instructions_match = re.search(
            r'## 用户最新指示.*?\n(.*?)(?=\n##|\n---|\n\*\*|\Z)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        
        if user_instructions_match:
            instructions_text = user_instructions_match.group(1)
            
            # 提取强制前置任务
            forced_task_match = re.search(
                r'### \*\*强制前置任务.*?\n(.*?)(?=\n###|\n##|\Z)',
                instructions_text,
                re.DOTALL
            )
            
            if forced_task_match:
                forced_task = forced_task_match.group(1)
                rules['forced_task'] = self._parse_forced_task(forced_task)
            
            # 提取六步节奏
            six_steps_match = re.search(
                r'### \*\*严格执行六步节奏.*?\n(.*?)(?=\n###|\n##|\Z)',
                instructions_text,
                re.DOTALL
            )
            
            if six_steps_match:
                six_steps = six_steps_match.group(1)
                rules['six_steps'] = self._parse_six_steps(six_steps)
            
            # 提取报告模板核心要素
            template_elements_match = re.search(
                r'### \*\*报告模板核心要素.*?\n(.*?)(?=\n###|\n##|\Z)',
                instructions_text,
                re.DOTALL
            )
            
            if template_elements_match:
                template_elements = template_elements_match.group(1)
                rules['template_elements'] = self._parse_template_elements(template_elements)
            
            # 提取重要教训
            important_lessons_match = re.search(
                r'### \*\*重要教训.*?\n(.*?)(?=\n###|\n##|\Z)',
                instructions_text,
                re.DOTALL
            )
            
            if important_lessons_match:
                important_lessons = important_lessons_match.group(1)
                rules['important_lessons'] = self._parse_important_lessons(important_lessons)
        
        return rules
    
    def _parse_forced_task(self, text: str) -> Dict[str, Any]:
        """解析强制前置任务"""
        task = {
            "purpose": [],
            "requirements": []
        }
        
        # 提取目的
        purpose_match = re.search(r'目的.*?\n(.*?)(?=\n具体执行要求|\Z)', text, re.DOTALL)
        if purpose_match:
            purpose_text = purpose_match.group(1)
            # 提取编号列表
            purposes = re.findall(r'\d+\.\s*\*\*(.*?)\*\*', purpose_text)
            task["purpose"] = purposes
        
        # 提取执行要求
        requirements_match = re.search(r'具体执行要求.*?\n(.*?)(?=\Z)', text, re.DOTALL)
        if requirements_match:
            requirements_text = requirements_match.group(1)
            # 提取编号列表
            requirements = re.findall(r'\d+\.\s*\*\*(.*?)\*\*', requirements_text)
            task["requirements"] = requirements
        
        return task
    
    def _parse_six_steps(self, text: str) -> List[Dict[str, str]]:
        """解析六步节奏"""
        steps = []
        
        # 提取步骤
        step_pattern = r'\d+\.\s*\*\*(.*?)\*\*\s*:\s*(.*?)(?=\n\d+\.|\Z)'
        step_matches = re.findall(step_pattern, text, re.DOTALL)
        
        for i, (name, description) in enumerate(step_matches, 1):
            steps.append({
                "step": i,
                "name": name.strip(),
                "description": description.strip()
            })
        
        return steps
    
    def _parse_template_elements(self, text: str) -> Dict[str, Any]:
        """解析报告模板核心要素"""
        elements = {}
        
        # 提取各部分
        sections = re.split(r'#### \*\*', text)
        
        for section in sections:
            if not section.strip():
                continue
            
            # 提取部分名称
            section_match = re.match(r'([^}]+)\*\*\s*\n(.*)', section, re.DOTALL)
            if section_match:
                section_name = section_match.group(1).strip()
                section_content = section_match.group(2).strip()
                
                elements[section_name] = self._parse_section_content(section_content)
        
        return elements
    
    def _parse_section_content(self, text: str) -> List[str]:
        """解析部分内容"""
        items = []
        
        # 提取列表项
        list_items = re.findall(r'-\s*\*\*(.*?)\*\*', text)
        items.extend(list_items)
        
        # 提取普通列表项
        plain_items = re.findall(r'-\s*([^*].*?)(?=\n-|\n\s*\d+\.|\Z)', text, re.DOTALL)
        items.extend([item.strip() for item in plain_items])
        
        return items
    
    def _parse_important_lessons(self, text: str) -> List[str]:
        """解析重要教训"""
        lessons = []
        
        # 提取编号列表
        lesson_pattern = r'\d+\.\s*\*\*(.*?)\*\*'
        lesson_matches = re.findall(lesson_pattern, text)
        
        lessons.extend(lesson_matches)
        
        return lessons
    
    def _extract_core_principles(self, content: str) -> List[str]:
        """提取核心原则"""
        principles = []
        
        # 提取重要教训部分的核心原则
        important_lessons_match = re.search(
            r'### \*\*重要教训.*?\n(.*?)(?=\n###|\n##|\Z)',
            content,
            re.DOTALL
        )
        
        if important_lessons_match:
            lessons_text = important_lessons_match.group(1)
            # 提取编号列表
            lessons = re.findall(r'\d+\.\s*\*\*(.*?)\*\*', lessons_text)
            principles.extend(lessons)
        
        # 添加系统配置中的核心原则
        principles.extend(config.CORE_PRINCIPLES)
        
        # 去重
        unique_principles = []
        for principle in principles:
            if principle not in unique_principles:
                unique_principles.append(principle)
        
        return unique_principles
    
    def load_template_structure(self) -> Dict[str, Any]:
        """
        加载模板结构
        从外部模板文件读取结构信息
        """
        try:
            template_path = config.EXTERNAL_TEMPLATE_PATH
            
            if not template_path.exists():
                logger.error(f"模板文件不存在: {template_path}")
                raise FileNotFoundError(f"模板文件不存在: {template_path}")
            
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析模板结构
            self.template_structure = self._parse_template_structure(content)
            
            logger.info(f"✅ 模板结构加载成功，共{len(self.template_structure)}个部分")
            
            return self.template_structure
            
        except Exception as e:
            logger.error(f"❌ 加载模板结构失败: {str(e)}")
            raise
    
    def _parse_template_structure(self, content: str) -> Dict[str, Any]:
        """解析模板结构"""
        structure = {
            "metadata": {},
            "sections": [],
            "tables": [],
            "formatting": {}
        }
        
        # 提取元数据
        structure["metadata"] = self._extract_metadata(content)
        
        # 提取章节结构
        structure["sections"] = self._extract_sections(content)
        
        # 提取表格结构
        structure["tables"] = self._extract_tables(content)
        
        # 提取格式信息
        structure["formatting"] = self._extract_formatting(content)
        
        return structure
    
    def _extract_metadata(self, content: str) -> Dict[str, str]:
        """提取元数据"""
        metadata = {}
        
        # 提取报告标题
        title_match = re.search(r'^#\s*(.*?)$', content, re.MULTILINE)
        if title_match:
            metadata["title"] = title_match.group(1).strip()
        
        # 提取报告信息
        info_patterns = {
            "report_time": r'报告生成时间.*?(\d{4}年\d{1,2}月\d{1,2}日\s*\d{1,2}:\d{2})',
            "analyst": r'分析师.*?([^\n]+)',
            "investor_type": r'适用投资者.*?([^\n]+)',
            "market_condition": r'市场状况.*?([^\n]+)',
        }
        
        for key, pattern in info_patterns.items():
            match = re.search(pattern, content)
            if match:
                metadata[key] = match.group(1).strip()
        
        return metadata
    
    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """提取章节结构"""
        sections = []
        
        # 提取所有二级标题
        section_pattern = r'##\s*(.*?)\s*\n(.*?)(?=\n##|\Z)'
        section_matches = re.findall(section_pattern, content, re.DOTALL)
        
        for i, (title, body) in enumerate(section_matches, 1):
            section = {
                "id": i,
                "title": title.strip(),
                "level": 2,
                "content_length": len(body.strip()),
                "has_tables": "|" in body,
                "has_lists": "- " in body or r'\d+\.' in body,
                "subsections": self._extract_subsections(body)
            }
            sections.append(section)
        
        return sections
    
    def _extract_subsections(self, content: str) -> List[Dict[str, Any]]:
        """提取子章节"""
        subsections = []
        
        # 提取三级标题
        subsection_pattern = r'###\s*(.*?)\s*\n(.*?)(?=\n###|\n##|\Z)'
        subsection_matches = re.findall(subsection_pattern, content, re.DOTALL)
        
        for i, (title, body) in enumerate(subsection_matches, 1):
            subsection = {
                "id": i,
                "title": title.strip(),
                "level": 3,
                "content_length": len(body.strip()),
                "has_tables": "|" in body,
                "has_lists": "- " in body or r'\d+\.' in body
            }
            subsections.append(subsection)
        
        return subsections
    
    def _extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """提取表格结构"""
        tables = []
        
        # 提取所有表格
        table_pattern = r'(\|.*?\|\n\|.*?\|\n(?:\|.*?\|\n)*)'
        table_matches = re.findall(table_pattern, content, re.DOTALL)
        
        for i, table_text in enumerate(table_matches, 1):
            lines = table_text.strip().split('\n')
            
            if len(lines) < 2:
                continue
            
            # 解析表头
            headers = [cell.strip() for cell in lines[0].strip('|').split('|')]
            
            # 解析分隔线
            separator = lines[1]
            
            # 解析数据行
            data_rows = []
            for line in lines[2:]:
                if line.strip() and '|' in line:
                    row = [cell.strip() for cell in line.strip('|').split('|')]
                    data_rows.append(row)
            
            table = {
                "id": i,
                "headers": headers,
                "row_count": len(data_rows),
                "column_count": len(headers),
                "sample_data": data_rows[:3] if data_rows else []
            }
            tables.append(table)
        
        return tables
    
    def _extract_formatting(self, content: str) -> Dict[str, Any]:
        """提取格式信息"""
        formatting = {
            "headings": {},
            "lists": {},
            "emphasis": {},
            "separators": {}
        }
        
        # 统计标题级别
        for level in range(1, 7):
            pattern = r'^#{' + str(level) + r'}\s+(.*?)$'
            matches = re.findall(pattern, content, re.MULTILINE)
            formatting["headings"][f"h{level}"] = len(matches)
        
        # 统计列表
        formatting["lists"]["unordered"] = len(re.findall(r'^\s*-\s+', content, re.MULTILINE))
        formatting["lists"]["ordered"] = len(re.findall(r'^\s*\d+\.\s+', content, re.MULTILINE))
        
        # 统计强调
        formatting["emphasis"]["bold"] = len(re.findall(r'\*\*(.*?)\*\*', content))
        formatting["emphasis"]["italic"] = len(re.findall(r'\*(.*?)\*', content))
        
        # 统计分隔符
        formatting["separators"]["horizontal"] = len(re.findall(r'^---\s*$', content, re.MULTILINE))
        
        return formatting
    
    def check_style_consistency(self, content: str, template_structure: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查样式布局一致性
        必须与模板完全一致
        """
        try:
            checks = {
                "title_format": False,
                "info_header": False,
                "section_separators": False,
                "table_format": False,
                "risk_levels": False
            }
            
            # 1. 检查报告标题格式
            title_pattern = r'^#\s*📊\s*深度复盘与明日投资计划.*?$'
            if re.search(title_pattern, content, re.MULTILINE):
                checks["title_format"] = True
            
            # 2. 检查报告信息头
            required_info = ["报告生成时间", "分析师", "适用投资者", "市场状况"]
            info_found = 0
            for info in required_info:
                if info in content[:500]:  # 在前500字符中查找
                    info_found += 1
            
            checks["info_header"] = info_found >= len(required_info)
            
            # 3. 检查步骤分隔符
            separator_count = len(re.findall(r'^---\s*$', content, re.MULTILINE))
            expected_separators = len([s for s in template_structure.get("sections", []) if s["level"] == 2])
            checks["section_separators"] = separator_count >= expected_separators
            
            # 4. 检查表格格式
            table_lines = [line for line in content.split('\n') if '|' in line]
            if table_lines:
                # 检查是否有完整的表格格式（包含分隔线）
                has_complete_tables = any('---' in line for line in table_lines)
                checks["table_format"] = has_complete_tables
            
            # 5. 检查风险等级标识
            risk_levels = ["高风险", "中高风险", "中风险", "低风险"]
            risk_found = 0
            for risk in risk_levels:
                if f"**{risk}**" in content:
                    risk_found += 1
            
            checks["risk_levels"] = risk_found >= 2  # 至少要有2种风险等级
            
            # 计算一致性分数
            passed_checks = sum(1 for check in checks.values() if check)
            total_checks = len(checks)
            consistency_score = passed_checks / total_checks
            
            result = {
                "checks": checks,
                "consistency_score": consistency_score,
                "passed": consistency_score >= config.quality.STYLE_TOLERANCE,
                "message": f"样式一致性检查: {passed_checks}/{total_checks} 通过"
            }
            
            logger.info(f"样式一致性检查: {result['message']}, 分数: {consistency_score:.2%}")
            
            return result
            
        except Exception as e:
            logger.error(f"样式一致性检查失败: {str(e)}")
            return {
                "checks": {},
                "consistency_score": 0.0,
                "passed": False,
                "message": f"样式一致性检查失败: {str(e)}"
            }
    
    def check_data_method(self) -> Dict[str, Any]:
        """
        检查数据对比方法
        必须使用"昨天预测的股价来对比今天的实际股价"
        """
        try:
            checks = {
                "data_source_tushare": False,
                "comparison_method": False,
                "accuracy_calculation": False,
                "data_validation": False
            }
            
            # 这些检查需要在数据获取和分析阶段验证
            # 这里只记录检查项，实际检查在相应模块中执行
            
            result = {
                "checks": checks,
                "requirements": [
                    "数据来源：必须使用Tushare Pro API获取当日实际股价",
                    "对比方法：必须使用'昨天预测的股价来对比今天的实际股价'",
                    "准确性计算：必须计算方向准确率、幅度准确率、综合评分",
                    "数据验证：必须验证数据准确性，确保没有使用错误数据"
                ],
                "message": "数据对比方法检查项已记录，将在分析阶段验证"
            }
            
            logger.info("数据对比方法检查项已记录")
            
            return result
            
        except Exception as e:
            logger.error(f"数据对比方法检查失败: {str(e)}")
            return {
                "checks": {},
                "requirements": [],
                "message": f"数据对比方法检查失败: {str(e)}"
            }
    
    def validate_memory_integrity(self) -> bool:
        """验证记忆完整性"""
        try:
            # 检查记忆文件是否存在
            if not config.EXTERNAL_MEMORY_PATH.exists():
                logger.error("记忆文件不存在")
                return False
            
            # 检查模板文件是否存在
            if not config.EXTERNAL_TEMPLATE_PATH.exists():
                logger.error("模板文件不存在")
                return False
            
            # 检查记忆内容是否包含核心原则
            with open(config.EXTERNAL_MEMORY_PATH, 'r', encoding='utf-8') as f:
                memory_content = f.read()
            
            core_principles_found = 0
            for principle in config.CORE_PRINCIPLES:
                if principle in memory_content:
                    core_principles_found += 1
            
            if core_principles_found < len(config.CORE_PRINCIPLES):
                logger.warning(f"记忆文件中只找到 {core_principles_found}/{len(config.CORE_PRINCIPLES)} 条核心原则")
            
            logger.info("✅ 记忆完整性验证通过")
            return True
            
        except Exception as e:
            logger.error(f"❌ 记忆完整性验证失败: {str(e)}")
            return False
    
    def print_memory_summary(self):
        """打印记忆摘要"""
        print("\n" + "="*60)
        print("长期记忆摘要 - 第0步：强制长期记忆检索")
        print("="*60)
        
        print(f"\n🔍 记忆规则加载: {'✅' if self.memory_rules else '❌'}")
        print(f"📋 模板结构加载: {'✅' if self.template_structure else '❌'}")
        print(f"🎯 核心原则数量: {len(self.core_principles)}")
        
        if self.memory_rules:
            print(f"\n📋 强制前置任务:")
            if "forced_task" in self.memory_rules:
                task = self.memory_rules["forced_task"]
                print(f"   目的: {len(task.get('purpose', []))} 条")
                print(f"   要求: {len(task.get('requirements', []))} 条")
            
            print(f"\n🚀 六步节奏:")
            if "six_steps" in self.memory_rules:
                steps = self.memory_rules["six_steps"]
                for step in steps:
                    print(f"   步骤{step['step']}: {step['name']}")
            
            print(f"\n⚠️ 重要教训:")
            if "important_lessons" in self.memory_rules:
                lessons = self.memory_rules["important_lessons"]
                for i, lesson in enumerate(lessons, 1):
                    print(f"   {i}. {lesson}")
        
        print(f"\n💾 模板结构:")
        if self.template_structure:
            print(f"   章节数量: {len(self.template_structure.get('sections', []))}")
            print(f"   表格数量: {len(self.template_structure.get('tables', []))}")
            print(f"   格式元素: {self.template_structure.get('formatting', {})}")
        
        print(f"\n🎯 核心原则:")
        for i, principle in enumerate(self.core_principles, 1):
            print(f"   {i}. {principle}")
        
        print("\n" + "="*60)

# 测试函数
def test_memory_manager():
    """测试记忆管理器"""
    print("🧪 测试记忆管理器...")
    
    manager = MemoryManager()
    
    try:
        # 验证记忆完整性
        if not manager.validate_memory_integrity():
            print("❌ 记忆完整性验证失败")
            return False
        
        # 加载记忆规则
        memory_rules = manager.load_memory_rules()
        print(f"✅ 记忆规则加载成功: {len(memory_rules)} 条规则")
        
        # 加载模板结构
        template_structure = manager.load_template_structure()
        print(f"✅ 模板结构加载成功: {len(template_structure.get('sections', []))} 个章节")
        
        # 打印摘要
        manager.print_memory_summary()
        
        print("✅ 记忆管理器测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 记忆管理器测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_memory_manager()
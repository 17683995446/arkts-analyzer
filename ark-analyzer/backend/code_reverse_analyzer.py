#!/usr/bin/env python3
"""
代码逆向分析工具
第二步：先逆向 - 通读代码梳理架构、流程、入参、分支、规则、边界、异常
"""

import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, field

sys.path.insert(0, str(Path(__file__).parent / "src"))


@dataclass
class FunctionAnalysis:
    """函数分析结果"""
    name: str
    file_path: str
    line_number: int
    parameters: List[str]
    return_type: str
    branches: List[str] = field(default_factory=list)
    exceptions: List[str] = field(default_factory=list)
    nested_calls: List[str] = field(default_factory=list)
    complexity_score: int = 0


class CodeReverseAnalyzer:
    """代码逆向分析器"""
    
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.backend_src = self.project_root / "backend" / "src"
        self.analyses: Dict[str, FunctionAnalysis] = {}
        
    def analyze_all(self):
        """分析所有核心代码"""
        print("=" * 100)
        print("🔍 第二步：逆向分析所有核心代码")
        print("=" * 100)
        
        modules = [
            ("数据库连接", self.backend_src / "database" / "connection.py"),
            ("同步引擎", self.backend_src / "services" / "synchronization_engine.py"),
            ("解析器", self.backend_src / "services" / "arkts_parser_service.py"),
            ("文件监控", self.backend_src / "services" / "file_watcher_service.py"),
            ("配置模块", self.backend_src / "config.py"),
        ]
        
        for module_name, module_path in modules:
            if module_path.exists():
                self._analyze_module(module_name, module_path)
                
        self._print_analysis_summary()
        
    def _analyze_module(self, module_name: str, module_path: Path):
        """分析单个模块"""
        print(f"\n📦 分析模块: {module_name}")
        print("-" * 100)
        
        content = module_path.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # 提取所有函数定义
        function_patterns = [
            r'^(?:async\s+)?def\s+(\w+)\s*\((.*?)\)(?:\s*->\s*(\w+))?\s*:',
            r'^(?:async\s+)?async\s+def\s+(\w+)\s*\((.*?)\)(?:\s*->\s*(\w+))?\s*:',
        ]
        
        current_function = None
        current_lines = []
        in_docstring = False
        brace_count = 0
        
        for idx, line in enumerate(lines, 1):
            # 跳过空行和注释
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
                
            # 检测文档字符串
            if '"""' in stripped or "'''" in stripped:
                in_docstring = not in_docstring
                continue
                
            if in_docstring:
                continue
                
            # 检测函数定义
            for pattern in function_patterns:
                match = re.match(pattern, stripped)
                if match:
                    # 保存前一个函数
                    if current_function:
                        self._analyze_function_details(
                            current_function, 
                            current_lines, 
                            module_path
                        )
                        
                    func_name = match.group(1)
                    params = [p.strip() for p in match.group(2).split(',') if p.strip()]
                    return_type = match.group(3) or "None"
                    
                    current_function = func_name
                    current_lines = [line]
                    
                    print(f"  ✅ 发现函数: {func_name}()")
                    print(f"     参数: {params}")
                    print(f"     返回: {return_type}")
                    
                    self.analyses[f"{module_path.name}::{func_name}"] = FunctionAnalysis(
                        name=func_name,
                        file_path=str(module_path),
                        line_number=idx,
                        parameters=params,
                        return_type=return_type
                    )
                    break
            else:
                if current_function:
                    current_lines.append(line)
                    
        # 分析最后一个函数
        if current_function:
            self._analyze_function_details(current_function, current_lines, module_path)
            
    def _analyze_function_details(
        self, 
        func_name: str, 
        lines: List[str], 
        file_path: Path
    ):
        """分析函数细节"""
        key = f"{file_path.name}::{func_name}"
        if key not in self.analyses:
            return
            
        analysis = self.analyses[key]
        
        # 统计代码行数
        code_lines = [l for l in lines if l.strip()]
        analysis.complexity_score = len(code_lines)
        
        # 提取分支（if/for/while）
        for line in lines:
            if re.match(r'^\s*if\s+', line):
                analysis.branches.append(f"IF: {line.strip()[:50]}")
            elif re.match(r'^\s*for\s+', line):
                analysis.branches.append(f"FOR: {line.strip()[:50]}")
            elif re.match(r'^\s*while\s+', line):
                analysis.branches.append(f"WHILE: {line.strip()[:50]}")
            elif re.match(r'^\s*try\s*:', line):
                analysis.branches.append("TRY")
            elif re.match(r'^\s*except\s+', line):
                analysis.exceptions.append(line.strip()[:60])
                
        # 提取嵌套调用
        call_pattern = r'(\w+)\s*\('
        for line in lines:
            calls = re.findall(call_pattern, line)
            for call in calls:
                if call not in ['if', 'for', 'while', 'return', 'print', 'len', 'range']:
                    analysis.nested_calls.append(call)
                    
    def _print_analysis_summary(self):
        """打印分析总结"""
        print("\n" + "=" * 100)
        print("📊 逆向分析总结")
        print("=" * 100)
        
        print(f"\n共分析 {len(self.analyses)} 个函数/方法")
        
        # 按复杂度排序
        sorted_funcs = sorted(
            self.analyses.values(),
            key=lambda x: x.complexity_score,
            reverse=True
        )
        
        print("\n🔝 Top 10 复杂函数:")
        for i, func in enumerate(sorted_funcs[:10], 1):
            print(f"  {i}. {func.name}() - {func.complexity_score} 行代码")
            if func.branches:
                print(f"     分支: {len(func.branches)} 个")
            if func.exceptions:
                print(f"     异常: {len(func.exceptions)} 个")
                
    def generate_test_matrix(self) -> List[Dict[str, Any]]:
        """生成测试矩阵"""
        test_matrix = []
        
        for key, analysis in self.analyses.items():
            # 为每个函数生成测试用例
            test_case = {
                "function": analysis.name,
                "file": analysis.file_path,
                "line": analysis.line_number,
                "params": analysis.parameters,
                "return_type": analysis.return_type,
                "test_scenarios": []
            }
            
            # 参数测试场景
            for param in analysis.parameters:
                test_case["test_scenarios"].append({
                    "scenario": f"参数 {param} 为空",
                    "expected": "应处理或报错"
                })
                test_case["test_scenarios"].append({
                    "scenario": f"参数 {param} 为 None",
                    "expected": "应处理或报错"
                })
                
            # 分支测试场景
            for branch in analysis.branches[:3]:  # 最多3个
                test_case["test_scenarios"].append({
                    "scenario": f"触发分支: {branch}",
                    "expected": "应正确执行"
                })
                
            # 异常测试场景
            for exc in analysis.exceptions:
                test_case["test_scenarios"].append({
                    "scenario": f"触发异常: {exc}",
                    "expected": "应正确捕获"
                })
                
            test_matrix.append(test_case)
            
        return test_matrix


if __name__ == "__main__":
    analyzer = CodeReverseAnalyzer("/workspace/ark-analyzer")
    analyzer.analyze_all()
    
    # 生成测试矩阵
    matrix = analyzer.generate_test_matrix()
    print("\n" + "=" * 100)
    print(f"📋 生成了 {len(matrix)} 个测试用例矩阵")
    print("=" * 100)

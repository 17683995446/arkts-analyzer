"""
ArkAnalyzer解析器模块
文件名: arkts_parser_service.py
用途: 解析ArkTS代码，提取类、方法、调用关系等
"""
import re
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ParsedClass:
    """解析后的类信息"""
    name: str
    line_number: int
    extends: List[str] = field(default_factory=list)
    implements: List[str] = field(default_factory=list)
    is_component: bool = False
    methods: List['ParsedMethod'] = field(default_factory=list)
    properties: List['ParsedProperty'] = field(default_factory=list)


@dataclass
class ParsedMethod:
    """解析后的方法信息"""
    name: str
    line_number: int
    params: str = ""
    return_type: str = ""
    is_async: bool = False
    calls: List[str] = field(default_factory=list)


@dataclass
class ParsedProperty:
    """解析后的属性信息"""
    name: str
    line_number: int
    property_type: str = ""
    is_state: bool = False


@dataclass
class ParsedFile:
    """解析后的文件信息"""
    path: str
    classes: List[ParsedClass] = field(default_factory=list)
    standalone_functions: List[ParsedMethod] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    component_usages: List[Tuple[str, str]] = field(default_factory=list)


class ArkTSParser:
    """ArkTS代码解析器"""
    
    COMPONENT_DECORATOR = "@Component"
    STATE_DECORATOR = "@State"
    LINK_DECORATOR = "@Link"
    PROP_DECORATOR = "@Prop"
    OBSERVED_DECORATOR = "@Observed"
    
    def __init__(self):
        self.current_file_path: str = ""
        self.known_classes: Set[str] = set()
    
    def parse_file(self, file_path: str, content: str) -> ParsedFile:
        """解析ArkTS文件"""
        self.current_file_path = file_path
        parsed_file = ParsedFile(path=file_path)
        
        lines = content.split('\n')
        
        self._extract_imports(content, parsed_file)
        self._extract_classes(lines, parsed_file)
        self._extract_standalone_functions(lines, parsed_file)
        self._extract_component_usages(content, parsed_file)
        
        self.known_classes.update(cls.name for cls in parsed_file.classes)
        
        logger.debug(f"解析文件 {file_path}: "
                    f"发现 {len(parsed_file.classes)} 个类, "
                    f"{len(parsed_file.standalone_functions)} 个函数")
        
        return parsed_file
    
    def _extract_imports(self, content: str, parsed_file: ParsedFile):
        """提取import语句"""
        import_pattern = r'import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
        matches = re.findall(import_pattern, content)
        parsed_file.imports.extend(matches)
    
    def _extract_classes(self, lines: List[str], parsed_file: ParsedFile):
        """提取类和组件定义"""
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if self._is_class_definition(line) or self._is_struct_definition(line):
                class_info = self._parse_class_definition(lines, i, parsed_file)
                if class_info:
                    parsed_file.classes.append(class_info)
            
            i += 1
    
    def _is_class_definition(self, line: str) -> bool:
        """检查是否是类定义"""
        patterns = [
            r'^export\s+class\s+\w+',
            r'^class\s+\w+',
            r'^export\s+default\s+class\s+\w+'
        ]
        return any(re.match(pattern, line) for pattern in patterns)
    
    def _is_struct_definition(self, line: str) -> bool:
        """检查是否是struct定义（ArkTS组件）"""
        patterns = [
            r'^export\s+struct\s+\w+',
            r'^struct\s+\w+',
            r'^export\s+default\s+struct\s+\w+'
        ]
        return any(re.match(pattern, line) for pattern in patterns)
    
    def _parse_class_definition(
        self,
        lines: List[str],
        start_line: int,
        parsed_file: ParsedFile
    ) -> Optional[ParsedClass]:
        """解析类或struct定义"""
        line = lines[start_line].strip()
        
        extends_match = re.search(r'extends\s+(\w+)', line)
        implements_match = re.search(r'implements\s+([\w,\s]+)', line)
        
        # 同时支持 class 和 struct
        class_name_match = re.search(r'(?:export\s+)?(?:default\s+)?(?:class|struct)\s+(\w+)', line)
        
        if not class_name_match:
            return None
        
        class_name = class_name_match.group(1)
        
        # 检查装饰器 - 检查前面多行！
        is_component = False
        check_back = min(start_line, 5)  # 检查前面5行
        for i in range(check_back):
            check_line = lines[start_line - 1 - i].strip()
            if self.COMPONENT_DECORATOR in check_line:
                is_component = True
                break
        
        parsed_class = ParsedClass(
            name=class_name,
            line_number=start_line + 1,
            extends=[extends_match.group(1)] if extends_match else [],
            implements=[p.strip() for p in implements_match.group(1).split(',')] if implements_match else [],
            is_component=is_component
        )
        
        brace_count = line.count('{') - line.count('}')
        current_line = start_line + 1
        
        while current_line < len(lines) and brace_count > 0:
            current_line_content = lines[current_line].strip()
            
            if current_line_content.startswith('@'):
                if self.COMPONENT_DECORATOR in current_line_content:
                    parsed_class.is_component = True
                current_line += 1
                continue
            
            method_match = re.match(r'(?:public\s+|private\s+|protected\s+)?(?:async\s+)?(\w+)\s*\([^)]*\)(?:\s*:\s*\w+)?\s*\{', current_line_content)
            if method_match and not current_line_content.startswith('if') and not current_line_content.startswith('for'):
                method_name = method_match.group(1)
                parsed_method = self._parse_method(lines, current_line, method_name)
                if parsed_method:
                    parsed_class.methods.append(parsed_method)
            
            property_match = re.match(r'@(\w+)\s+(\w+)(?:\s*:\s*(\w+))?', current_line_content)
            if property_match:
                decorator_name = property_match.group(1)
                prop_name = property_match.group(2)
                prop_type = property_match.group(3) or "unknown"
                
                parsed_property = ParsedProperty(
                    name=prop_name,
                    line_number=current_line + 1,
                    property_type=prop_type,
                    is_state=decorator_name in ['State', 'Link', 'Prop']
                )
                parsed_class.properties.append(parsed_property)
            
            brace_count += current_line_content.count('{') - current_line_content.count('}')
            current_line += 1
        
        return parsed_class
    
    def _parse_method(
        self,
        lines: List[str],
        start_line: int,
        method_name: str
    ) -> Optional[ParsedMethod]:
        """解析方法定义"""
        line = lines[start_line].strip()
        
        params_match = re.search(r'\(([^)]*)\)', line)
        params = params_match.group(1) if params_match else ""
        
        return_type_match = re.search(r'\)\s*:\s*([^{]+)', line)
        return_type = return_type_match.group(1).strip() if return_type_match else ""
        
        is_async = 'async' in line
        
        parsed_method = ParsedMethod(
            name=method_name,
            line_number=start_line + 1,
            params=params,
            return_type=return_type,
            is_async=is_async
        )
        
        return parsed_method
    
    def _extract_standalone_functions(self, lines: List[str], parsed_file: ParsedFile):
        """提取独立函数"""
        for i, line in enumerate(lines):
            line = line.strip()
            
            if re.match(r'^(?:export\s+)?(?:async\s+)?function\s+\w+', line):
                func_match = re.search(r'(?:export\s+)?(?:async\s+)?function\s+(\w+)', line)
                if func_match:
                    func_name = func_match.group(1)
                    parsed_method = self._parse_method(lines, i, func_name)
                    if parsed_method:
                        parsed_file.standalone_functions.append(parsed_method)
    
    def _extract_component_usages(self, content: str, parsed_file: ParsedFile):
        """提取@Component组件使用"""
        pattern = r'new\s+(\w+)\s*\('
        matches = re.findall(pattern, content)
        
        for component_name in matches:
            if component_name in self.known_classes:
                parsed_file.component_usages.append((component_name, component_name))

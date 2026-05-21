#!/usr/bin/env python3
"""
超级混乱项目生成器 - 第9轮测试专用
生成前所未有的极端混乱、超级大规模的项目
"""
import os
import random
import string
from pathlib import Path
from typing import List, Dict, Tuple


class SuperChaosProjectGenerator:
    """
    超级混乱项目生成器
    生成 5000+ 个文件的超级大规模混乱项目
    """
    
    def __init__(self, output_dir: str = "/tmp/super-chaos-project"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_chaos_on_steroids(self):
        """生成超级混乱项目"""
        scenarios = []
        print("=" * 100)
        print("🔥 第9轮 - 超级混乱项目生成器开始工作 🔥")
        print("=" * 100)
        
        # 生成超级大规模的测试文件
        print("\n📁 生成100个超级巨大的类文件...")
        for i in range(100):
            scenarios.extend(self._generate_super_huge_class(i))
            
        print("\n📁 生成1000个混合场景的组件文件...")
        for i in range(1000):
            scenarios.extend(self._generate_super_mixed_component(i))
            
        print("\n📁 生成500个极端混乱的边缘文件...")
        for i in range(500):
            scenarios.extend(self._generate_super_edge_case(i))
            
        print("\n📁 生成1000个正常的混合文件...")
        for i in range(1000):
            scenarios.extend(self._generate_normal_mixed_file(i))
            
        print("\n📁 生成500个深度嵌套文件...")
        for i in range(500):
            scenarios.extend(self._generate_super_deep_nested(i))
            
        print("\n📁 生成500个编码混乱文件...")
        for i in range(500):
            scenarios.extend(self._generate_super_encoding_chaos(i))
            
        print("\n📁 生成1000个微小/空/几乎空文件...")
        for i in range(1000):
            scenarios.extend(self._generate_super_tiny_file(i))
            
        total_files = len(scenarios)
        print(f"\n✅ 超级混乱项目生成完成！共 {total_files} 个文件！")
        
        return scenarios
        
    def _generate_super_huge_class(self, index: int) -> List[Path]:
        """生成超级巨大的类文件"""
        file_path = self.output_dir / f"super_huge_class_{index:04d}.ets"
        
        content = f"class SuperHugeClass{index} {{\n"
        
        # 生成 500 个属性
        for i in range(500):
            content += f"    property{i}: string = \"value_{i}\";\n"
            
        # 生成 200 个方法
        for i in range(200):
            content += f"\n    method{i}() {{\n"
            content += f"        return \"result_from_method_{i}\";\n"
            content += f"    }}\n"
            
        content += "}\n"
        
        file_path.write_text(content, encoding='utf-8')
        return [file_path]
        
    def _generate_super_mixed_component(self, index: int) -> List[Path]:
        """生成超级混合的组件文件"""
        file_path = self.output_dir / f"super_mixed_component_{index:04d}.ets"
        
        decorators = []
        if random.random() > 0.3:
            decorators.append("@Component")
        if random.random() > 0.5:
            decorators.append("@Observed")
        if random.random() > 0.7:
            decorators.append("@Entry")
            
        decorator_lines = "\n".join(decorators)
        
        properties = []
        for i in range(random.randint(2, 15)):
            prop_type = random.choice(["@State", "@Prop", "@Link", ""])
            var_name = f"property_{i}"
            var_type = random.choice(["string", "number", "boolean", "any"])
            default_value = random.choice(["\"test\"", "0", "true", "null"])
            properties.append(f"    {prop_type} {var_name}: {var_type} = {default_value};")
            
        methods = []
        for i in range(random.randint(1, 10)):
            method_name = f"method_{i}"
            methods.append(f"    {method_name}() {{ return \"result\"; }}")
            
        struct_name = f"SuperMixedComponent{index}"
        
        content = f"{decorator_lines}\nstruct {struct_name} {{\n"
        content += "\n".join(properties)
        content += "\n\n"
        content += "    build() {\n"
        content += "        Column() {\n"
        content += "            Text(\"Mixed Component\");\n"
        content += "        }\n"
        content += "    }\n\n"
        content += "\n".join(methods)
        content += "\n}\n"
        
        file_path.write_text(content, encoding='utf-8')
        return [file_path]
        
    def _generate_super_edge_case(self, index: int) -> List[Path]:
        """生成超级边缘情况文件"""
        edge_type = random.randint(0, 7)
        
        if edge_type == 0:
            # 超长单行
            content = "class EdgeCase{method0(){return1;}method1(){return2;}method2(){return3;}}"
            for _ in range(20):
                content += f"method{random.randint(0,1000)}(){{return{random.randint(0,1000)};}}"
        elif edge_type == 1:
            # 几乎全是注释
            content = "/*"
            for i in range(100):
                content += f"Line {i} of comments. Let's add more comments. ";
            content += "*/\nclass Minimal{}\n"
        elif edge_type == 2:
            # 混合各种空白字符
            content = "class   WhitespaceChaos   {\n"
            for i in range(20):
                indent = " " * random.randint(1, 20)
                content += f"{indent}method{i}(){{}}\n"
            content += "}"
        elif edge_type == 3:
            # 混合大小写命名
            content = "class mixedCaseClass{}\n"
            content += "class MIXEDCASECLASS{}\n"
            content += "class Mixed_Case_123{}\n"
        elif edge_type == 4:
            # 空的或几乎空的
            if index % 3 == 0:
                content = ""
            elif index % 3 == 1:
                content = "class X{}\n"
            else:
                content = "@Component\nstruct Y{build(){}}\n"
        elif edge_type == 5:
            # 大量导入
            content = ""
            for i in range(100):
                content += f"import {{ Module{i} }} from \"module{i}\";\n"
            content += "\nclass MainClass{}\n"
        elif edge_type == 6:
            # 编码混乱 - 混合语言
            content = f"""@Component
struct MixedEncoding{index} {{
    @State chinese_prop: string = "你好世界";
    @State japanese_prop: string = "こんにちは";
    @State emoji_prop: string = "🎉🎯";
    build() {{
        Text("混合编码测试");
    }}
}}
"""
        else:
            # 超长字符串
            long_str = "".join(random.choices(string.ascii_letters + string.digits, k=10000))
            content = f"class LongString{index} {{ data: string = \"{long_str}\"; }}\n"
            
        file_path = self.output_dir / f"super_edge_case_{index:04d}.ets"
        file_path.write_text(content, encoding='utf-8')
        return [file_path]
        
    def _generate_normal_mixed_file(self, index: int) -> List[Path]:
        """生成正常的混合文件 - 既有class也有struct"""
        file_path = self.output_dir / f"normal_mixed_{index:04d}.ets"
        
        has_struct = random.random() > 0.3
        has_class = random.random() > 0.3
        
        content = ""
        
        if has_class:
            content += f"class NormalClass{index} {{\n"
            content += "    value: number = 0;\n"
            content += "    update() { this.value++; }\n"
            content += "}\n\n"
            
        if has_struct:
            content += f"@Component\nstruct NormalComponent{index} {{\n"
            content += "    @State count: number = 0;\n"
            content += "    build() { Text(\"Normal\"); }\n"
            content += "}\n"
            
        if not has_class and not has_struct:
            content += f"class Fallback{index} {{}}\n"
            
        file_path.write_text(content, encoding='utf-8')
        return [file_path]
        
    def _generate_super_deep_nested(self, index: int) -> List[Path]:
        """生成超级深度嵌套文件"""
        file_path = self.output_dir / f"super_deep_nested_{index:04d}.ets"
        
        nesting_depth = random.randint(5, 20)
        content = ""
        
        indent = ""
        for i in range(nesting_depth):
            content += f"{indent}class Level{i} {{\n"
            indent += "    "
            
        content += f"{indent}data: number = {index};\n"
        
        for i in range(nesting_depth - 1, -1, -1):
            indent = "    " * i
            content += f"{indent}}}\n"
            
        file_path.write_text(content, encoding='utf-8')
        return [file_path]
        
    def _generate_super_encoding_chaos(self, index: int) -> List[Path]:
        """生成超级编码混乱文件"""
        file_path = self.output_dir / f"super_encoding_{index:04d}.ets"
        
        content = ""
        
        # 混合各种 Unicode 字符
        if random.random() > 0.5:
            content += "/* 包含各种字符的测试文件 */\n"
            
        content += f"class EncodingTest{index} {{\n"
        content += "    normal: string = \"normal\";\n"
        content += "    中文: string = \"测试中文\";\n"
        content += "    にほんご: string = \"日本語\";\n"
        content += "    emoji: string = \"🎉🚀🎯✅\";\n"
        content += "    mixed: string = \"hello 世界 🌍\";\n"
        content += "}\n"
        
        file_path.write_text(content, encoding='utf-8')
        return [file_path]
        
    def _generate_super_tiny_file(self, index: int) -> List[Path]:
        """生成超级微小文件"""
        file_path = self.output_dir / f"super_tiny_{index:04d}.ets"
        
        tiny_type = index % 5
        
        if tiny_type == 0:
            content = ""  # 完全空
        elif tiny_type == 1:
            content = "// Only comment\n"
        elif tiny_type == 2:
            content = "class X{}\n"
        elif tiny_type == 3:
            content = "@Component\nstruct Y{}\n"
        else:
            content = "export {}\n"
            
        file_path.write_text(content, encoding='utf-8')
        return [file_path]


if __name__ == "__main__":
    generator = SuperChaosProjectGenerator()
    generator.generate_chaos_on_steroids()

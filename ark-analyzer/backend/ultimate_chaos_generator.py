#!/usr/bin/env python3
"""
终极混乱场景生成器 - 第八轮深度压力测试
文件名: ultimate_chaos_generator.py
用途: 生成极其混乱、真实、高难度的ArkTS代码场景
遵循: 慢工出细活原理
"""

import os
import random
import string
from pathlib import Path
from typing import List, Dict, Tuple


class UltimateChaosGenerator:
    """
    终极混乱场景生成器 - 模拟真实开发中的各种混乱情况
    
    包括但不限于:
    - 超长行、极端缩进
    - 编码问题、混合字符
    - 深度嵌套、循环引用
    - 语法边缘情况
    - 大量注释和混合内容
    - 文件大小极端情况
    - 真实的错误代码场景
    """
    
    def __init__(self, output_dir: str = "/tmp/ultimate-chaos-project"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def generate_all_chaos_scenarios(self):
        """生成所有混乱场景"""
        scenarios = []
        
        print("=" * 100)
        print("🔧 开始生成终极混乱场景...")
        print("=" * 100)
        
        # 1. 超长行场景
        print("\n📁 生成超长行场景...")
        scenarios.extend(self._generate_extremely_long_lines())
        
        # 2. 深度嵌套场景
        print("📁 生成深度嵌套场景...")
        scenarios.extend(self._generate_deep_nesting())
        
        # 3. 编码混乱场景
        print("📁 生成编码混乱场景...")
        scenarios.extend(self._generate_encoding_chaos())
        
        # 4. 语法边缘情况
        print("📁 生成语法边缘情况...")
        scenarios.extend(self._generate_syntax_edge_cases())
        
        # 5. 大量注释场景
        print("📁 生成大量注释场景...")
        scenarios.extend(self._generate_massive_comments())
        
        # 6. 真实错误代码场景
        print("📁 生成真实错误代码场景...")
        scenarios.extend(self._generate_real_error_scenarios())
        
        # 7. 极小文件场景
        print("📁 生成极小文件场景...")
        scenarios.extend(self._generate_tiny_files())
        
        # 8. 极大文件场景
        print("📁 生成极大文件场景...")
        scenarios.extend(self._generate_huge_files())
        
        # 9. 混合内容场景
        print("📁 生成混合内容场景...")
        scenarios.extend(self._generate_mixed_content())
        
        # 10. 各种命名规则场景
        print("📁 生成各种命名规则场景...")
        scenarios.extend(self._generate_various_naming())
        
        print(f"\n✅ 生成完成！共 {len(scenarios)} 个混乱场景文件")
        return scenarios
        
    def _generate_extremely_long_lines(self) -> List[Path]:
        """生成超长行混乱场景"""
        scenarios = []
        
        # 场景1: 单个超超长行
        file1 = self.output_dir / "extremely-long-line.ets"
        long_line = "class VeryLongLine { " + " ".join([f"property{i}: number = {i};" for i in range(500)]) + " }"
        content1 = long_line + "\n"
        file1.write_text(content1, encoding='utf-8')
        scenarios.append(file1)
        
        # 场景2: 超长字符串字面量
        file2 = self.output_dir / "extremely-long-string.ets"
        long_string = 'x' * 50000  # 5万字符的字符串
        content2 = f"""class LongString {{
    myLongString: string = "{long_string}";
}}
"""
        file2.write_text(content2, encoding='utf-8')
        scenarios.append(file2)
        
        # 场景3: 超长函数签名
        file3 = self.output_dir / "extremely-long-signature.ets"
        many_params = ", ".join([f"param{i}: string" for i in range(100)])
        content3 = f"""class LongSignature {{
    myLongFunction({many_params}): void {{
        return;
    }}
}}
"""
        file3.write_text(content3, encoding='utf-8')
        scenarios.append(file3)
        
        return scenarios
        
    def _generate_deep_nesting(self) -> List[Path]:
        """生成深度嵌套场景"""
        scenarios = []
        
        # 场景1: 深嵌套类
        file1 = self.output_dir / "deep-nested-classes.ets"
        content1 = "class Level0 {"
        for i in range(1, 51):
            content1 += f" class Level{i} {{"
        content1 += " value: number = 42;"
        for i in range(50, -1, -1):
            content1 += " }"
        content1 += " }"
        file1.write_text(content1, encoding='utf-8')
        scenarios.append(file1)
        
        # 场景2: 深嵌套组件
        file2 = self.output_dir / "deep-nested-components.ets"
        content2 = "@Component\nstruct Level0 {\n"
        for i in range(1, 31):
            content2 += f"  @Component\n  struct Level{i} {{\n"
        content2 += "    build() { Text('Deep Nest'); }\n"
        for i in range(30, -1, -1):
            content2 += "  }\n"
        content2 += "}"
        file2.write_text(content2, encoding='utf-8')
        scenarios.append(file2)
        
        # 场景3: 深嵌套代码块
        file3 = self.output_dir / "deep-nested-blocks.ets"
        content3 = "class NestedBlocks {\n  method() {\n"
        for i in range(100):
            content3 += f"    if (true) {{\n"
        content3 += "      return 42;\n"
        for i in range(100):
            content3 += "    }\n"
        content3 += "  }\n}"
        file3.write_text(content3, encoding='utf-8')
        scenarios.append(file3)
        
        return scenarios
        
    def _generate_encoding_chaos(self) -> List[Path]:
        """生成编码混乱场景"""
        scenarios = []
        
        # 场景1: 混合语言文字
        file1 = self.output_dir / "mixed-languages.ets"
        content1 = """@Component
struct MixedLanguages {
    @State 中文变量: string = "你好";
    @State 日本語: string = "こんにちは";
    @State العربية: string = "مرحبا";
    @State emoji: string = "🎉🚀🎯";
    
    build() {
        Text(this.中文变量);
        Text(this.日本語);
        Text(this.العربية);
        Text(this.emoji);
    }
}

class РусскийКласс {
    方法₁₂₃() { return "俄语方法"; }
}
"""
        file1.write_text(content1, encoding='utf-8')
        scenarios.append(file1)
        
        # 场景2: 混合特殊字符
        file2 = self.output_dir / "special-chars.ets"
        content2 = """class SpecialChars {
    var1: string = "hello";
    var2: string = "world";
    'quoted-key': number = 42;
    "another-key": boolean = true;
}
"""
        file2.write_text(content2, encoding='utf-8')
        scenarios.append(file2)
        
        return scenarios
        
    def _generate_syntax_edge_cases(self) -> List[Path]:
        """生成语法边缘情况"""
        scenarios = []
        
        # 场景1: 空白字符大乱斗
        file1 = self.output_dir / "whitespace-chaos.ets"
        content1 = """class   WhitespaceChaos   {
  method1(  )  {  return  1;  }

  method2 (
     )
  {
    return
    2;
  }
}
"""
        file1.write_text(content1, encoding='utf-8')
        scenarios.append(file1)
        
        # 场景2: 混合大小写和风格
        file2 = self.output_dir / "mixed-casing.ets"
        content2 = """class mixedCasingClass {
  MYCONSTANT: number = 1;
  myVariable: string = "hello";
  MyMethod(): void {}
}

class AnotherClass {}
class ANOTHERCLASS {}
"""
        file2.write_text(content2, encoding='utf-8')
        scenarios.append(file2)
        
        # 场景3: 极端注释混合
        file3 = self.output_dir / "comment-edge-cases.ets"
        content3 = """// 单行注释
class Commented {
    // 另一个注释
    /* 多行
       注释
       结束啦 */
    method() { // 行内注释
        return /* 中间注释 */ 42;
    }
}
"""
        file3.write_text(content3, encoding='utf-8')
        scenarios.append(file3)
        
        return scenarios
        
    def _generate_massive_comments(self) -> List[Path]:
        """生成大量注释场景"""
        scenarios = []
        
        # 场景1: 几乎全是注释
        file1 = self.output_dir / "mostly-comments.ets"
        content1 = "/*"
        for i in range(1000):
            content1 += f"这是第 {i} 行注释。。。\n"
        content1 += "*/\n"
        content1 += "class MinimalCode { value: number = 42; }\n"
        file1.write_text(content1, encoding='utf-8')
        scenarios.append(file1)
        
        return scenarios
        
    def _generate_real_error_scenarios(self) -> List[Path]:
        """生成真实错误代码场景"""
        scenarios = []
        
        # 场景1: 不完整代码 (真实错误)
        file1 = self.output_dir / "incomplete-code.ets"
        content1 = """class Incomplete {
    method() {  // 没有闭合括号
        if (true) {
            // 这里有问题
            // 继续
"""
        file1.write_text(content1, encoding='utf-8')
        scenarios.append(file1)
        
        # 场景2: 真实的语法错误
        file2 = self.output_dir / "syntax-errors.ets"
        content2 = """class SyntaxErrors {
    method( // 缺少闭合
        return 1;
    }
    another-method() { // 不允许的命名
        return 2;
    }
}
"""
        file2.write_text(content2, encoding='utf-8')
        scenarios.append(file2)
        
        return scenarios
        
    def _generate_tiny_files(self) -> List[Path]:
        """生成极小文件场景"""
        scenarios = []
        
        # 场景1: 只有一个类
        file1 = self.output_dir / "tiny-class.ets"
        content1 = "class Tiny {}"
        file1.write_text(content1, encoding='utf-8')
        scenarios.append(file1)
        
        # 场景2: 只有组件
        file2 = self.output_dir / "tiny-component.ets"
        content2 = "@Component struct TinyComp { build(){} }"
        file2.write_text(content2, encoding='utf-8')
        scenarios.append(file2)
        
        # 场景3: 几乎为空
        file3 = self.output_dir / "almost-empty.ets"
        content3 = ""
        file3.write_text(content3, encoding='utf-8')
        scenarios.append(file3)
        
        return scenarios
        
    def _generate_huge_files(self) -> List[Path]:
        """生成极大文件场景"""
        scenarios = []
        
        # 场景1: 很多类
        file1 = self.output_dir / "many-classes.ets"
        content1 = ""
        for i in range(100):
            content1 += f"""class Class{i} {{
    property{i}: number = {i};
    method{i}() {{ return {i}; }}
}}
"""
        file1.write_text(content1, encoding='utf-8')
        scenarios.append(file1)
        
        return scenarios
        
    def _generate_mixed_content(self) -> List[Path]:
        """生成混合内容场景"""
        scenarios = []
        
        # 场景1: 混合类型和组件
        file1 = self.output_dir / "mixed-all.ets"
        content1 = """import { CommonUtil } from 'common';
import { Button } from 'ui';

@Observed
class MyModel {
    id: string;
}

@Component
@Entry
struct MixedComponent {
    @State value: string = "";
    @Link another: number;
    
    build() {
        Column() {
            Text(this.value);
            Button("Click")
                .onClick(() => {
                    this.handleClick();
                });
        }
    }
    
    handleClick() {
        console.log("Clicked!");
    }
}

class HelperService {
    static process(data: any): any {
        return data;
    }
}

export function standaloneFunction() {
    return "result";
}
"""
        file1.write_text(content1, encoding='utf-8')
        scenarios.append(file1)
        
        return scenarios
        
    def _generate_various_naming(self) -> List[Path]:
        """生成各种命名规则场景"""
        scenarios = []
        
        # 场景1: 各种合法标识符
        file1 = self.output_dir / "various-names.ets"
        content1 = """class NormalClass {}
class _UnderscoreStart {}
class ClassWithNumber123 {}
class $dollarStart {}

@Component
struct NormalComponent {}
struct _UnderscoreComponent {}
struct Component2 {}

class AllKinds {
    normalVar: number;
    _privateVar: string;
    $specialVar: boolean;
    var123: any;
    with_underscores: number;
    withDollar$: string;
}
"""
        file1.write_text(content1, encoding='utf-8')
        scenarios.append(file1)
        
        return scenarios


if __name__ == "__main__":
    generator = UltimateChaosGenerator()
    generator.generate_all_chaos_scenarios()
    print("\n💥 终极混乱场景已生成完成！")

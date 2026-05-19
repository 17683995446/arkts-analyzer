"""
大规模复杂测试项目生成器
文件名: create_complex_test_project.py
用途: 生成包含大量ArkTS文件的真实复杂项目，用于压力测试
"""
import os
import random
from pathlib import Path
from typing import List


class ComplexArkTSProjectGenerator:
    """复杂ArkTS项目生成器"""
    
    COMPONENT_NAMES = [
        "Header", "Footer", "Sidebar", "Navbar", "Card", "Button", "Input", 
        "Dropdown", "Modal", "Tabs", "Table", "Form", "Checkbox", "Radio",
        "Toggle", "Slider", "Progress", "Spinner", "Avatar", "Badge",
        "Pagination", "Breadcrumb", "Alert", "Tooltip", "Popover",
        "Accordion", "Carousel", "Calendar", "DatePicker", "TimePicker",
        "Chart", "Map", "VideoPlayer", "ImageGallery", "LoginForm",
        "RegistrationForm", "ProfileCard", "SearchBar", "Menu", "List",
        "Grid", "Tree", "Timeline", "Stepper", "Wizard", "Tag", "Chip"
    ]
    
    SERVICE_NAMES = [
        "AuthService", "UserService", "ApiService", "StorageService",
        "CacheService", "LoggerService", "AnalyticsService", "NotificationService",
        "WebSocketService", "FileService", "ImageService", "PaymentService",
        "CartService", "CheckoutService", "OrderService", "ProductService",
        "SearchService", "RecommendationService", "SocialService", "ChatService"
    ]
    
    MODEL_NAMES = [
        "User", "Product", "Order", "Cart", "Category", "Tag", "Comment",
        "Review", "Like", "Follow", "Message", "Notification", "Session",
        "Token", "Config", "Setting", "Log", "Audit", "Backup", "Report"
    ]
    
    UTILITY_NAMES = [
        "StringUtils", "DateUtils", "NumberUtils", "ValidationUtils",
        "FormatUtils", "ConversionUtils", "EncryptionUtils", "HashUtils",
        "StorageUtils", "NetworkUtils", "DeviceUtils", "ThemeUtils"
    ]
    
    DECORATORS = ["@Component", "@Observed", "@Entry"]
    STATE_DECORATORS = ["@State", "@Prop", "@Link", "@Provide", "@Consume"]
    
    def __init__(self, base_path: str, num_files: int = 100):
        self.base_path = Path(base_path)
        self.num_files = num_files
        
    def generate(self):
        """生成整个项目"""
        print(f"正在生成 {self.num_files} 个复杂ArkTS文件...")
        
        for i in range(self.num_files):
            self._generate_file(i)
        
        print("✓ 项目生成完成！")
    
    def _generate_file(self, index: int):
        """生成单个文件"""
        file_type = random.choice(["component", "service", "model", "utility", "page"])
        file_path = self._get_file_path(index, file_type)
        content = self._generate_content(index, file_type)
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
    
    def _get_file_path(self, index: int, file_type: str) -> Path:
        """获取文件路径"""
        name_suffix = f"_{index:03d}"
        
        if file_type == "component":
            name = random.choice(self.COMPONENT_NAMES) + name_suffix
            return self.base_path / "components" / f"{name}.ets"
        elif file_type == "service":
            name = random.choice(self.SERVICE_NAMES) + name_suffix
            return self.base_path / "services" / f"{name}.ets"
        elif file_type == "model":
            name = random.choice(self.MODEL_NAMES) + name_suffix
            return self.base_path / "models" / f"{name}.ets"
        elif file_type == "utility":
            name = random.choice(self.UTILITY_NAMES) + name_suffix
            return self.base_path / "utils" / f"{name}.ets"
        else:  # page
            name = f"Page{index:03d}"
            return self.base_path / "pages" / f"{name}.ets"
    
    def _generate_content(self, index: int, file_type: str) -> str:
        """生成文件内容"""
        if file_type == "component":
            return self._generate_component(index)
        elif file_type == "service":
            return self._generate_service(index)
        elif file_type == "model":
            return self._generate_model(index)
        elif file_type == "utility":
            return self._generate_utility(index)
        else:
            return self._generate_page(index)
    
    def _generate_component(self, index: int) -> str:
        """生成组件"""
        name = random.choice(self.COMPONENT_NAMES) + f"_{index:03d}"
        has_decorator = random.random() > 0.3
        decorator = "@Component" if has_decorator else ""
        
        num_properties = random.randint(1, 8)
        properties = []
        for i in range(num_properties):
            prop_type = random.choice(["string", "number", "boolean", "Object"])
            state_decorator = random.choice(self.STATE_DECORATORS) if random.random() > 0.3 else ""
            default = self._get_default_value(prop_type)
            properties.append(f"  {state_decorator} prop{i}: {prop_type} = {default}")
        
        num_methods = random.randint(0, 5)
        methods = []
        for i in range(num_methods):
            methods.append(self._generate_method(f"method{i}", random.randint(0, 3)))
        
        is_entry = random.random() > 0.7
        struct_decorator = "@Entry" if is_entry else ""
        
        build_content = self._generate_build_content(num_components=random.randint(1, 6))
        
        return f"""{struct_decorator}
{decorator}
struct {name} {{
{"".join([f"\n  {prop}" for prop in properties])}

{"".join([f"\n  {method}" for method in methods])}

  build() {{
{build_content}
  }}
}}
"""
    
    def _generate_service(self, index: int) -> str:
        """生成服务类"""
        name = random.choice(self.SERVICE_NAMES) + f"_{index:03d}"
        
        num_methods = random.randint(3, 10)
        methods = []
        for i in range(num_methods):
            is_async = random.random() > 0.5
            methods.append(self._generate_method(
                f"method{i}", 
                random.randint(0, 4),
                is_async=is_async
            ))
        
        return f"""export class {name} {{
  private static instance: {name}
  
  public static getInstance(): {name} {{
    if (!{name}.instance) {{
      {name}.instance = new {name}()
    }}
    return {name}.instance
  }}

{"".join([f"\n  {method}" for method in methods])}
}}
"""
    
    def _generate_model(self, index: int) -> str:
        """生成模型类"""
        name = random.choice(self.MODEL_NAMES) + f"_{index:03d}"
        num_fields = random.randint(3, 15)
        
        fields = []
        for i in range(num_fields):
            field_type = random.choice(["string", "number", "boolean", "Date", "string[]", "number[]"])
            default = self._get_default_value(field_type)
            fields.append(f"  public field{i}: {field_type} = {default}")
        
        return f"""export class {name} {{
{"".join([f"\n  {field}" for field in fields])}

  constructor(data?: Partial<{name}>) {{
    if (data) {{
      Object.assign(this, data)
    }}
  }}
  
  public toJSON(): Object {{
    return {{ ...this }}
  }}
}}
"""
    
    def _generate_utility(self, index: int) -> str:
        """生成工具类"""
        name = random.choice(self.UTILITY_NAMES) + f"_{index:03d}"
        num_functions = random.randint(2, 8)
        functions = []
        
        for i in range(num_functions):
            functions.append(self._generate_method(
                f"util{i}", 
                random.randint(1, 3),
                is_static=True
            ))
        
        return f"""export class {name} {{
{"".join([f"\n  {func}" for func in functions])}
}}
"""
    
    def _generate_page(self, index: int) -> str:
        """生成页面"""
        name = f"Page{index:03d}"
        build_content = self._generate_build_content(num_components=random.randint(3, 12))
        
        return f"""@Entry
@Component
struct {name} {{
  @State title: string = 'Page {index}'
  
  build() {{
{build_content}
  }}
}}
"""
    
    def _generate_method(self, name: str, num_params: int, is_async: bool = False, is_static: bool = False) -> str:
        """生成方法"""
        modifiers = []
        if is_static:
            modifiers.append("static")
        if is_async:
            modifiers.append("async")
        
        param_list = []
        for i in range(num_params):
            param_type = random.choice(["string", "number", "boolean", "Object"])
            param_list.append(f"arg{i}: {param_type}")
        
        return_type = random.choice(["void", "string", "number", "boolean", "Promise<void>", "Promise<string>", "Object"])
        
        body = self._generate_method_body()
        
        return f"""{(' '.join(modifiers) + ' ') if modifiers else ''}{name}({', '.join(param_list)}): {return_type} {{
{body}
  }}"""
    
    def _generate_method_body(self) -> str:
        """生成方法体"""
        body_length = random.randint(1, 10)
        lines = []
        
        for _ in range(body_length):
            line_type = random.choice(["var", "call", "return", "log", "if"])
            
            if line_type == "var":
                var_name = f"var{random.randint(0, 100)}"
                var_type = random.choice(["string", "number", "boolean"])
                default = self._get_default_value(var_type)
                lines.append(f"    let {var_name}: {var_type} = {default}")
            elif line_type == "call":
                lines.append(f"    console.log('debug')")
            elif line_type == "return":
                var_type = random.choice(["string", "number", "boolean"])
                lines.append(f"    return {self._get_default_value(var_type)}")
            elif line_type == "log":
                lines.append(f"    console.log('info')")
            else:  # if
                lines.append(f"    if (true) {{ }}")
        
        return "\n".join(lines)
    
    def _generate_build_content(self, num_components: int) -> str:
        """生成 build 方法内容"""
        components = ["Column()", "Row()", "Stack()", "Flex()", "List()"]
        elements = ["Text()", "Button()", "Image()", "Input()", "Divider()"]
        
        lines = ["    Column() {"]
        
        for _ in range(num_components):
            el = random.choice(elements)
            content = f"'{random.choice(['Hello', 'Test', 'Content', 'Item', 'Button'])}'"
            lines.append(f"      {el.replace('()', f'({content})')}")
        
        lines.append("    }")
        return "\n".join(lines)
    
    def _get_default_value(self, var_type: str) -> str:
        """获取默认值"""
        if var_type == "string":
            return f"'{random.choice(['test', 'hello', 'value', 'default', ''])}'"
        elif var_type == "number":
            return str(random.randint(0, 100))
        elif var_type == "boolean":
            return str(random.choice(["true", "false"]))
        elif var_type == "Date":
            return "new Date()"
        elif var_type.endswith("[]"):
            return "[]"
        else:
            return "{}"


if __name__ == "__main__":
    # 生成一个有200个文件的复杂项目！
    generator = ComplexArkTSProjectGenerator(
        base_path="/workspace/ark-analyzer/large-test-project",
        num_files=200
    )
    generator.generate()

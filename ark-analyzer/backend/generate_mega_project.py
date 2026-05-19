#!/usr/bin/env python3
"""
超大规模ArkTS测试项目生成器 - 用于终极压力测试
生成包含1000个文件的复杂真实ArkTS项目
"""
import os
import random
from pathlib import Path


class MegaArkTSProjectGenerator:
    """超大规模ArkTS项目生成器"""
    
    def __init__(self, output_dir: str = "/workspace/ark-analyzer/mega-test-project"):
        self.output_dir = Path(output_dir)
        self.categories = ["components", "pages", "services", "models", "utils", "api"]
        self.component_types = ["Button", "Card", "List", "Form", "Modal", "Dialog", "Tab", "Nav", 
                               "Input", "Select", "Checkbox", "Radio", "Slider", "Switch", "DatePicker",
                               "TimePicker", "Image", "Video", "Chart", "Map", "Table", "Grid", "Accordion"]
        self.service_names = ["Auth", "User", "Data", "Api", "Storage", "Network", "Cache", "Logger",
                             "Analytics", "Notification", "Theme", "I18n", "Config", "State"]
        self.model_names = ["User", "Product", "Order", "Cart", "Category", "Comment", "Review",
                           "Notification", "Session", "Token", "Log", "Config", "Setting", "Message",
                           "File", "Tag", "Like", "Follow", "Post", "Article", "Page"]
        self.utils_names = ["Date", "String", "Number", "Format", "Validation", "Hash", "Encryption",
                           "Storage", "Network", "Theme", "Color", "Size", "Unit", "Regex"]
        
    def generate(self, num_files: int = 1000):
        """生成超大规模测试项目"""
        print(f"🚀 开始生成超大规模ArkTS项目...")
        print(f"📦 目标文件数: {num_files}")
        print(f"📂 输出目录: {self.output_dir}")
        
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        for category in self.categories:
            category_dir = self.output_dir / category
            category_dir.mkdir(exist_ok=True)
            
        generated_count = 0
        files_per_category = num_files // len(self.categories)
        
        for category in self.categories:
            category_dir = self.output_dir / category
            count = files_per_category if category != self.categories[-1] else (num_files - generated_count)
            
            for i in range(count):
                file_content = self._generate_file(category, i)
                file_name = self._generate_filename(category, i)
                file_path = category_dir / file_name
                file_path.write_text(file_content, encoding="utf-8")
                generated_count += 1
                
                if generated_count % 100 == 0:
                    print(f"✅ 已生成 {generated_count}/{num_files} 个文件...")
        
        print(f"🎉 超大规模项目生成完成！共 {generated_count} 个文件！")
        return self.output_dir
        
    def _generate_filename(self, category: str, index: int) -> str:
        """生成文件名"""
        if category == "components":
            component_type = random.choice(self.component_types)
            return f"{component_type}_{index:03d}.ets"
        elif category == "pages":
            return f"Page_{index:03d}.ets"
        elif category == "services":
            service_name = random.choice(self.service_names)
            return f"{service_name}Service_{index:03d}.ets"
        elif category == "models":
            model_name = random.choice(self.model_names)
            return f"{model_name}_{index:03d}.ets"
        elif category == "utils":
            util_name = random.choice(self.utils_names)
            return f"{util_name}Utils_{index:03d}.ets"
        else:  # api
            return f"ApiModule_{index:03d}.ets"
            
    def _generate_file(self, category: str, index: int) -> str:
        """根据类别生成文件内容"""
        if category == "components":
            return self._generate_component(index)
        elif category == "pages":
            return self._generate_page(index)
        elif category == "services":
            return self._generate_service(index)
        elif category == "models":
            return self._generate_model(index)
        elif category == "utils":
            return self._generate_utils(index)
        else:
            return self._generate_api(index)
            
    def _generate_component(self, index: int) -> str:
        """生成组件文件"""
        component_type = random.choice(self.component_types)
        name = f"{component_type}_{index:03d}"
        
        return f"""@Component
@Entry
struct {name} {{
  @State title: string = 'Component {index}'
  @State count: number = 0
  @State isActive: boolean = false
  
  build() {{
    Column() {{
      Text(this.title)
        .fontSize(24)
        .fontWeight(FontWeight.Bold)
      
      Button('Click Me')
        .onClick(() => {{
          this.count++
          this.isActive = !this.isActive
        }})
      
      Text(`Count: ${{this.count}}`)
        .fontSize(18)
        .margin({{ top: 20 }})
      
      if (this.isActive) {{
        Text('Component is active!')
          .fontColor(Color.Green)
          .margin({{ top: 10 }})
      }}
    }}
    .width('100%')
    .padding(20)
  }}
  
  private increment() {{
    this.count++
  }}
  
  private reset() {{
    this.count = 0
  }}
}}
"""
        
    def _generate_page(self, index: int) -> str:
        """生成页面文件"""
        return f"""@Entry
@Component
struct Page_{index:03d} {{
  @State pageTitle: string = 'Page {index}'
  @State loading: boolean = false
  @State data: string[] = []
  
  aboutToAppear() {{
    this.loadData()
  }}
  
  build() {{
    Column() {{
      Text(this.pageTitle)
        .fontSize(28)
        .fontWeight(FontWeight.Bold)
        .margin({{ bottom: 20 }})
      
      if (this.loading) {{
        LoadingProgress()
          .width(50)
          .height(50)
      }} else {{
        List() {{
          ForEach(this.data, (item: string) => {{
            ListItem() {{
              Text(item)
                .fontSize(16)
                .padding(10)
            }}
          }})
        }}
        .width('100%')
        .height(300)
      }}
      
      Button('Refresh')
        .margin({{ top: 20 }})
        .onClick(() => {{
          this.loadData()
        }})
    }}
    .width('100%')
    .padding(20)
  }}
  
  async loadData() {{
    this.loading = true
    await this.simulateApiCall()
    this.data = ['Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5']
    this.loading = false
  }}
  
  simulateApiCall(): Promise<void> {{
    return new Promise((resolve) => {{
      setTimeout(() => {{
        resolve()
      }}, 500)
    }})
  }}
}}
"""
        
    def _generate_service(self, index: int) -> str:
        """生成服务文件"""
        service_name = random.choice(self.service_names)
        name = f"{service_name}Service_{index:03d}"
        
        return f"""export class {name} {{
  private static instance: {name}
  private config: object = {{}}
  
  static getInstance(): {name} {{
    if (!{name}.instance) {{
      {name}.instance = new {name}()
    }}
    return {name}.instance
  }}
  
  constructor() {{
    this.initialize()
  }}
  
  private initialize() {{
    console.log('{name} initialized')
    this.config = {{
      apiUrl: 'https://api.example.com',
      timeout: 5000
    }}
  }}
  
  async fetchData(endpoint: string): Promise<object> {{
    console.log(`Fetching from ${{endpoint}}`)
    return new Promise((resolve) => {{
      setTimeout(() => {{
        resolve({{ data: 'sample', timestamp: Date.now() }})
      }}, 100)
    }})
  }}
  
  saveData(key: string, value: any) {{
    console.log(`Saving ${{key}}`)
  }}
  
  loadData(key: string): any {{
    console.log(`Loading ${{key}}`)
    return null
  }}
  
  validate(input: any): boolean {{
    return input !== null && input !== undefined
  }}
  
  formatOutput(data: any): string {{
    return JSON.stringify(data)
  }}
  
  clearCache() {{
    console.log('Cache cleared')
  }}
}}
"""
        
    def _generate_model(self, index: int) -> str:
        """生成模型文件"""
        model_name = random.choice(self.model_names)
        
        return f"""export class {model_name}_{index:03d} {{
  id: string
  name: string
  createdAt: number
  updatedAt: number
  active: boolean
  
  constructor(data?: object) {{
    this.id = this.generateId()
    this.name = ''
    this.createdAt = Date.now()
    this.updatedAt = Date.now()
    this.active = true
    
    if (data) {{
      Object.assign(this, data)
    }}
  }}
  
  private generateId(): string {{
    return `id_${{Date.now()}}_${{Math.random().toString(36).substr(2, 9)}}`
  }}
  
  save() {{
    console.log(`Saving ${{this.constructor.name}}: ${{this.id}}`)
  }}
  
  update(data: object) {{
    Object.assign(this, data)
    this.updatedAt = Date.now()
    console.log(`Updated ${{this.id}}`)
  }}
  
  delete() {{
    console.log(`Deleting ${{this.id}}`)
  }}
  
  toJSON(): object {{
    return {{
      id: this.id,
      name: this.name,
      createdAt: this.createdAt,
      updatedAt: this.updatedAt,
      active: this.active
    }}
  }}
  
  static fromJSON(json: object): {model_name}_{index:03d} {{
    return new {model_name}_{index:03d}(json)
  }}
  
  clone(): {model_name}_{index:03d} {{
    return {model_name}_{index:03d}.fromJSON(this.toJSON())
  }}
}}
"""
        
    def _generate_utils(self, index: int) -> str:
        """生成工具文件"""
        util_name = random.choice(self.utils_names)
        name = f"{util_name}Utils_{index:03d}"
        
        return f"""export class {name} {{
  static format(input: any): string {{
    return String(input)
  }}
  
  static parse(input: string): any {{
    try {{
      return JSON.parse(input)
    }} catch (e) {{
      return input
    }}
  }}
  
  static validate(input: any): boolean {{
    return input !== null && input !== undefined && input !== ''
  }}
  
  static truncate(str: string, length: number = 50): string {{
    if (str.length <= length) {{
      return str
    }}
    return str.substring(0, length) + '...'
  }}
  
  static capitalize(str: string): string {{
    if (!str) return ''
    return str.charAt(0).toUpperCase() + str.slice(1)
  }}
  
  static isEmpty(value: any): boolean {{
    if (value === null || value === undefined) return true
    if (typeof value === 'string') return value.trim() === ''
    if (Array.isArray(value)) return value.length === 0
    if (typeof value === 'object') return Object.keys(value).length === 0
    return false
  }}
  
  static randomString(length: number = 10): string {{
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    let result = ''
    for (let i = 0; i < length; i++) {{
      result += chars.charAt(Math.floor(Math.random() * chars.length))
    }}
    return result
  }}
  
  static timestamp(): number {{
    return Date.now()
  }}
  
  static delay(ms: number): Promise<void> {{
    return new Promise(resolve => setTimeout(resolve, ms))
  }}
}}
"""
        
    def _generate_api(self, index: int) -> str:
        """生成API文件"""
        return f"""export class ApiModule_{index:03d} {{
  private baseUrl: string = 'https://api.example.com/v{index}'
  private headers: object = {{
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }}
  
  constructor(baseUrl?: string) {{
    if (baseUrl) {{
      this.baseUrl = baseUrl
    }}
  }}
  
  async get(endpoint: string, params?: object): Promise<any> {{
    console.log(`GET ${{this.baseUrl}}/${{endpoint}}`)
    return await this._request('GET', endpoint, params)
  }}
  
  async post(endpoint: string, data?: object): Promise<any> {{
    console.log(`POST ${{this.baseUrl}}/${{endpoint}}`)
    return await this._request('POST', endpoint, data)
  }}
  
  async put(endpoint: string, data?: object): Promise<any> {{
    console.log(`PUT ${{this.baseUrl}}/${{endpoint}}`)
    return await this._request('PUT', endpoint, data)
  }}
  
  async delete(endpoint: string): Promise<any> {{
    console.log(`DELETE ${{this.baseUrl}}/${{endpoint}}`)
    return await this._request('DELETE', endpoint)
  }}
  
  private async _request(method: string, endpoint: string, data?: any): Promise<any> {{
    return new Promise((resolve) => {{
      setTimeout(() => {{
        resolve({{
          success: true,
          data: {{ result: 'ok' }},
          timestamp: Date.now()
        }})
      }}, 50)
    }})
  }}
  
  setHeader(key: string, value: string) {{
    this.headers[key] = value
  }}
  
  getBaseUrl(): string {{
    return this.baseUrl
  }}
  
  setBaseUrl(url: string) {{
    this.baseUrl = url
  }}
}}
"""


if __name__ == "__main__":
    generator = MegaArkTSProjectGenerator()
    generator.generate(num_files=1000)

"""
LLM语义分析服务模块
文件名: semantic_analyzer_service.py
用途: 使用硅基流动API进行ArkTS代码的语义分析
"""
import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
import httpx

from config import SystemConfig

logger = logging.getLogger(__name__)


class SemanticAnalyzer:
    """
    LLM语义分析器 - 基于硅基流动API

    功能：
    1. 增强ArkTS代码的语义理解
    2. 识别隐式的类关系
    3. 推断方法调用意图
    4. 分析业务逻辑
    """

    def __init__(self, api_key: str, base_url: str = "https://api.siliconflow.cn/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = "Qwen/Qwen2.5-7B-Instruct"
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """获取HTTP客户端"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(60.0),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
        return self._client

    async def analyze_code_structure(self, code: str, file_path: str) -> Dict[str, Any]:
        """
        分析代码结构

        参数:
            code: ArkTS源代码
            file_path: 文件路径

        返回:
            增强后的实体关系信息
        """
        prompt = self._build_structure_prompt(code, file_path)

        try:
            response = await self._call_llm(prompt)
            return self._parse_structure_response(response)
        except Exception as e:
            logger.error(f"语义分析失败 {file_path}: {e}")
            return {"classes": [], "relations": [], "enhancements": []}

    async def analyze_relations(self, class_definitions: List[Dict]) -> List[Dict[str, Any]]:
        """
        分析类之间的关系

        参数:
            class_definitions: 类定义列表

        返回:
            推断出的关系列表
        """
        prompt = self._build_relation_prompt(class_definitions)

        try:
            response = await self._call_llm(prompt)
            return self._parse_relation_response(response)
        except Exception as e:
            logger.error(f"关系分析失败: {e}")
            return []

    async def suggest_improvements(self, code: str) -> List[str]:
        """
        建议代码改进

        参数:
            code: ArkTS源代码

        返回:
            改进建议列表
        """
        prompt = f"""分析以下ArkTS代码，提供代码质量改进建议：

```typescript
{code}
```

请提供：
1. 代码结构问题
2. 性能优化建议
3. 最佳实践建议
"""

        try:
            response = await self._call_llm(prompt)
            return self._parse_improvement_response(response)
        except Exception as e:
            logger.error(f"改进建议生成失败: {e}")
            return []

    async def _call_llm(self, prompt: str) -> str:
        """调用LLM API"""
        client = await self._get_client()

        payload = {
            "model": self.model_name,
            "messages": [
                {
                    "role": "system",
                    "content": """你是一个专业的ArkTS/HarmonyOS代码分析助手。
请用JSON格式返回分析结果，确保输出有效的JSON。
"""
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 2048
        }

        response = await client.post(
            f"{self.base_url}/chat/completions",
            json=payload
        )

        if response.status_code != 200:
            raise Exception(f"API调用失败: {response.status_code}")

        result = response.json()
        return result["choices"][0]["message"]["content"]

    def _build_structure_prompt(self, code: str, file_path: str) -> str:
        """构建结构分析提示词"""
        return f"""分析以下ArkTS文件，提取类结构和关系信息：

文件路径: {file_path}

代码:
```typescript
{code[:4000]}
```

请以JSON格式返回分析结果：
{{
  "classes": [
    {{
      "name": "类名",
      "purpose": "类的职责描述",
      "public_methods": ["方法列表"],
      "decorators": ["使用的装饰器"]
    }}
  ],
  "relations": [
    {{
      "type": "关系类型（extends|implements|uses|contains）",
      "from": "源类",
      "to": "目标类",
      "reason": "关系原因"
    }}
  ],
  "components": ["@Component装饰器组件列表"]
}}
"""

    def _build_relation_prompt(self, class_definitions: List[Dict]) -> str:
        """构建关系分析提示词"""
        classes_str = json.dumps(class_definitions[:20], indent=2, ensure_ascii=False)

        return f"""分析以下ArkTS类定义，推断它们之间的关系：

{classes_str}

请以JSON格式返回推断的关系：
{{
  "inferred_relations": [
    {{
      "from": "类A",
      "to": "类B",
      "relation_type": "关系类型",
      "confidence": 0.9,
      "reasoning": "推断原因"
    }}
  ]
}}
"""

    def _parse_structure_response(self, response: str) -> Dict[str, Any]:
        """解析结构分析响应"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            logger.warning("无法解析LLM返回的JSON")

        return {"classes": [], "relations": [], "enhancements": []}

    def _parse_relation_response(self, response: str) -> List[Dict[str, Any]]:
        """解析关系分析响应"""
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                return data.get("inferred_relations", [])
        except json.JSONDecodeError:
            logger.warning("无法解析LLM返回的关系JSON")

        return []

    def _parse_improvement_response(self, response: str) -> List[str]:
        """解析改进建议响应"""
        suggestions = []
        lines = response.split('\n')

        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('*') or line[0].isdigit()):
                cleaned = line.lstrip('-*0123456789. ) ')
                if cleaned:
                    suggestions.append(cleaned)

        return suggestions[:10]

    async def close(self):
        """关闭HTTP客户端"""
        if self._client:
            await self._client.aclose()
            self._client = None

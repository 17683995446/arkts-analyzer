"""
ArkAnalyzer配置管理模块
文件名: config.py
用途: 集中管理系统配置，支持环境变量和配置文件
"""
import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SystemConfig:
    """系统配置模型"""
    watch_path: str = field(default="", metadata={"description": "监控的代码目录路径"})
    api_key: str = field(default="", metadata={"description": "硅基流动API密钥"})
    base_url: str = field(default="https://api.siliconflow.cn/v1", metadata={"description": "LLM API地址"})
    model_name: str = field(default="Qwen/Qwen2.5-7B-Instruct", metadata={"description": "LLM模型名称"})
    debounce_seconds: float = field(default=1.0, metadata={"description": "防抖等待时间（秒）"})
    max_depth: int = field(default=10, metadata={"description": "调用链最大深度"})
    enable_llm_analysis: bool = field(default=True, metadata={"description": "是否启用LLM语义分析"})
    database_path: str = field(default="arkgraph.db", metadata={"description": "SQLite数据库路径"})
    
    @classmethod
    def load(cls) -> "SystemConfig":
        """从环境变量和配置文件加载配置"""
        config = cls()
        
        config.watch_path = os.getenv("ARK_WATCH_PATH", config.watch_path)
        config.api_key = os.getenv("SILICONFLOW_API_KEY", config.api_key)
        config.base_url = os.getenv("SILICONFLOW_BASE_URL", config.base_url)
        config.model_name = os.getenv("LLM_MODEL_NAME", config.model_name)
        
        config_file = Path("config.json")
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                file_config = json.load(f)
                for key, value in file_config.items():
                    if hasattr(config, key):
                        setattr(config, key, value)
        
        return config
    
    def save(self):
        """保存配置到文件"""
        config_file = Path("config.json")
        config_data = {
            "watch_path": self.watch_path,
            "api_key": self.api_key,
            "base_url": self.base_url,
            "model_name": self.model_name,
            "debounce_seconds": self.debounce_seconds,
            "max_depth": self.max_depth,
            "enable_llm_analysis": self.enable_llm_analysis,
            "database_path": self.database_path
        }
        
        with open(config_file, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)


class FileChangeEvent:
    """文件变更事件"""
    def __init__(
        self,
        file_path: str,
        event_type: str,
        timestamp: Optional[float] = None
    ):
        self.file_path = file_path
        self.event_type = event_type
        self.timestamp = timestamp or __import__("time").time()
    
    def __repr__(self):
        return f"FileChangeEvent(path={self.file_path}, type={self.event_type})"


class UpdateResult:
    """更新结果模型"""
    def __init__(
        self,
        success: bool,
        file_path: str,
        entities_updated: int = 0,
        duration_ms: float = 0.0,
        error_message: str = ""
    ):
        self.success = success
        self.file_path = file_path
        self.entities_updated = entities_updated
        self.duration_ms = duration_ms
        self.error_message = error_message
    
    def to_dict(self):
        return {
            "success": self.success,
            "file_path": self.file_path,
            "entities_updated": self.entities_updated,
            "duration_ms": self.duration_ms,
            "error_message": self.error_message
        }

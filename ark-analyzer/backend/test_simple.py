#!/usr/bin/env python3
"""
简单的模块加载测试
"""
import sys
from pathlib import Path

print("=== 模块导入测试 ===")
print()

# 添加路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 逐个测试导入
modules_to_test = [
    "config",
    "services.file_watcher_service",
    "services.arkts_parser_service",
    "database.connection",
    "services.synchronization_engine",
    "services.websocket_manager",
    "api.routes",
    "api.websocket_endpoint",
    "services.semantic_analyzer_service"
]

for module_name in modules_to_test:
    try:
        print(f"正在导入: {module_name:<40}", end="")
        __import__(module_name)
        print("✓ 成功")
    except Exception as e:
        print(f"✗ 失败: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

print()
print("=== 测试完成 ===")

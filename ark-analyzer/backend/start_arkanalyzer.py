#!/usr/bin/env python3
"""
ArkAnalyzer 启动脚本
文件名: start_arkanalyzer.py
用途: 启动完整的 ArkAnalyzer 系统
"""
import os
import sys
import logging
import asyncio
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ark_analyzer import app
from config import SystemConfig
from services.file_watcher_service import FileWatcherService
from services.synchronization_engine import SynchronizationEngine
from services.websocket_manager import WebSocketManager
from database.connection import DatabaseConnection
import uvicorn

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """主启动函数"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║          ArkAnalyzer - 百万行级ArkTS代码知识图谱分析系统         ║
║                    第一性原理 动态更新版                        ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # 加载配置
    config = SystemConfig()
    logger.info(f"启动配置加载:")
    logger.info(f"  - 监视目录: {config.watch_path}")
    logger.info(f"  - 数据库: {config.database_path}")
    logger.info(f"  - API密钥: {'已配置' if config.siliconflow_api_key else '未配置'}")
    
    # 确保目录存在
    Path(config.watch_path).mkdir(parents=True, exist_ok=True)
    Path(Path(config.database_path).parent).mkdir(parents=True, exist_ok=True)
    
    logger.info("\n启动服务...")
    
    # 启动服务器
    logger.info(f"启动 API 服务器于 http://{config.host}:{config.port}")
    
    config = uvicorn.Config(
        app,
        host=config.host,
        port=config.port,
        log_level="info",
        access_log=True
    )
    
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        logger.info("\n收到中断信号，正在关闭...")
    except Exception as e:
        logger.error(f"服务器错误: {e}")
    finally:
        logger.info("ArkAnalyzer 已停止")


if __name__ == "__main__":
    asyncio.run(main())

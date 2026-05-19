"""
ArkAnalyzer - 基于第一性原理的ArkTS知识图谱动态更新系统
文件名: ark_analyzer.py
用途: 主入口文件，协调所有模块
"""
import asyncio
import logging
from pathlib import Path
from typing import Optional
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database.connection import DatabaseConnection
from services.file_watcher_service import FileWatcherService
from services.synchronization_engine import SynchronizationEngine
from services.websocket_manager import WebSocketManager
from api.routes import router as api_router
from api.websocket_endpoint import websocket_endpoint
from config import SystemConfig

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("正在启动ArkAnalyzer系统...")
    
    db_connection = DatabaseConnection()
    await db_connection.initialize()
    app.state.db = db_connection
    
    app.state.websocket_manager = WebSocketManager()
    app.state.sync_engine = SynchronizationEngine(
        db_connection=db_connection,
        websocket_manager=app.state.websocket_manager
    )
    
    config = SystemConfig.load()
    if config.watch_path:
        app.state.file_watcher = FileWatcherService(
            sync_engine=app.state.sync_engine,
            watch_path=config.watch_path,
            debounce_seconds=config.debounce_seconds
        )
        app.state.file_watcher.start()
        logger.info(f"文件监控服务已启动，监控路径: {config.watch_path}")
    
    logger.info("ArkAnalyzer系统启动完成!")
    
    yield
    
    logger.info("正在关闭ArkAnalyzer系统...")
    if hasattr(app.state, 'file_watcher'):
        app.state.file_watcher.stop()
    if hasattr(app.state, 'db'):
        await app.state.db.close()
    logger.info("ArkAnalyzer系统已关闭")


app = FastAPI(
    title="ArkAnalyzer API",
    description="ArkTS知识图谱动态更新系统 API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
app.websocket_route("/ws/updates")(websocket_endpoint)


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "service": "ArkAnalyzer"}


def main():
    """主入口函数"""
    uvicorn.run(
        "ark_analyzer:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()

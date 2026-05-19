"""
ArkAnalyzer WebSocket管理器
文件名: websocket_manager.py
用途: 管理WebSocket连接，实现实时推送
"""
import asyncio
import json
import logging
from typing import Dict, Set, Optional
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    """WebSocket连接管理器"""
    
    def __init__(self):
        self._connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket):
        """接受新的WebSocket连接"""
        await websocket.accept()
        async with self._lock:
            self._connections.add(websocket)
        logger.info(f"WebSocket连接已建立，当前连接数: {len(self._connections)}")
    
    async def disconnect(self, websocket: WebSocket):
        """断开WebSocket连接"""
        async with self._lock:
            self._connections.discard(websocket)
        logger.info(f"WebSocket连接已断开，当前连接数: {len(self._connections)}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """发送个人消息"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"发送消息失败: {e}")
            await self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """广播消息到所有连接"""
        if not self._connections:
            return
        
        disconnected = set()
        
        async with self._lock:
            connections_snapshot = self._connections.copy()
        
        for connection in connections_snapshot:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"广播消息失败: {e}")
                disconnected.add(connection)
        
        for connection in disconnected:
            await self.disconnect(connection)
    
    async def send_update(
        self,
        update_type: str,
        data: dict,
        target: Optional[WebSocket] = None
    ):
        """发送更新消息"""
        message = {
            "type": update_type,
            "data": data
        }
        
        if target:
            await self.send_personal_message(message, target)
        else:
            await self.broadcast(message)
    
    @property
    def connection_count(self) -> int:
        """获取当前连接数"""
        return len(self._connections)

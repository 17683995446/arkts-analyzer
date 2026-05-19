"""
ArkAnalyzer WebSocket端点
文件名: websocket_endpoint.py
用途: 处理WebSocket连接和消息
"""
from fastapi import WebSocket, WebSocketDisconnect
from services.websocket_manager import WebSocketManager


async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket连接端点

    功能:
    1. 接受客户端连接
    2. 保持连接并处理消息
    3. 推送文件变更更新
    4. 推送同步状态
    """
    ws_manager: WebSocketManager = websocket.app.state.websocket_manager
    
    await ws_manager.connect(websocket)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "data": {
                "message": "已连接到ArkAnalyzer实时更新",
                "connection_id": id(websocket)
            }
        })
        
        while True:
            data = await websocket.receive_text()
            
            try:
                message = eval(data)
                
                if isinstance(message, dict):
                    msg_type = message.get("type")
                    
                    if msg_type == "ping":
                        await websocket.send_json({"type": "pong"})
                    elif msg_type == "request_sync":
                        sync_engine = websocket.app.state.sync_engine
                        config = websocket.app.state.db
                        await websocket.send_json({
                            "type": "sync_status",
                            "data": {"status": "syncing"}
                        })
            
            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": str(e)}
                })
    
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
    except Exception as e:
        await ws_manager.disconnect(websocket)

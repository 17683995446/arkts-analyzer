"""
ArkAnalyzer API路由模块
文件名: routes.py
用途: 定义RESTful API端点
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

router = APIRouter()


class ConfigUpdateRequest(BaseModel):
    """配置更新请求"""
    watch_path: Optional[str] = None
    api_key: Optional[str] = None
    debounce_seconds: Optional[float] = None
    enable_llm_analysis: Optional[bool] = None


class CallChainRequest(BaseModel):
    """调用链查询请求"""
    from_method_id: int
    to_method_id: int
    max_depth: int = 10


@router.get("/stats")
async def get_statistics(request: Request):
    """获取图谱统计信息"""
    db = request.app.state.db
    stats = await db.get_statistics()
    
    last_change = await db.fetchone(
        "SELECT created_at FROM change_logs ORDER BY created_at DESC LIMIT 1"
    )
    
    return {
        **stats,
        "last_sync_time": last_change['created_at'] if last_change else None,
        "sync_status": "idle"
    }


@router.get("/classes")
async def get_classes(
    request: Request,
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None
):
    """获取类列表"""
    db = request.app.state.db
    
    offset = (page - 1) * limit
    
    if search:
        classes = await db.fetchall(
            """
            SELECT c.*, f.path as file_path,
                   (SELECT COUNT(*) FROM methods WHERE class_id = c.id) as method_count
            FROM classes c
            JOIN files f ON c.file_id = f.id
            WHERE c.name LIKE ?
            ORDER BY c.name
            LIMIT ? OFFSET ?
            """,
            (f"%{search}%", limit, offset)
        )
        
        total = await db.fetchone(
            "SELECT COUNT(*) as count FROM classes WHERE name LIKE ?",
            (f"%{search}%",)
        )
    else:
        classes = await db.fetchall(
            """
            SELECT c.*, f.path as file_path,
                   (SELECT COUNT(*) FROM methods WHERE class_id = c.id) as method_count
            FROM classes c
            JOIN files f ON c.file_id = f.id
            ORDER BY c.name
            LIMIT ? OFFSET ?
            """,
            (limit, offset)
        )
        
        total = await db.fetchone("SELECT COUNT(*) as count FROM classes")
    
    return {
        "items": classes,
        "total": total['count'] if total else 0,
        "page": page,
        "limit": limit
    }


@router.get("/classes/{class_id}")
async def get_class_detail(request: Request, class_id: int):
    """获取类详情"""
    db = request.app.state.db
    
    class_info = await db.fetchone(
        """
        SELECT c.*, f.path as file_path
        FROM classes c
        JOIN files f ON c.file_id = f.id
        WHERE c.id = ?
        """,
        (class_id,)
    )
    
    if not class_info:
        raise HTTPException(status_code=404, detail="Class not found")
    
    methods = await db.fetchall(
        "SELECT * FROM methods WHERE class_id = ?",
        (class_id,)
    )
    
    extends = await db.fetchall(
        """
        SELECT c2.*
        FROM classes c1
        JOIN classes c2 ON c1.extends = c2.id
        WHERE c1.id = ?
        """,
        (class_id,)
    )
    
    called_by = await db.fetchall(
        """
        SELECT DISTINCT m.*
        FROM calls call
        JOIN methods m ON call.caller_id = m.id
        WHERE call.callee_id IN (SELECT id FROM methods WHERE class_id = ?)
        """,
        (class_id,)
    )
    
    calls = await db.fetchall(
        """
        SELECT DISTINCT m.*
        FROM calls call
        JOIN methods m ON call.callee_id = m.id
        WHERE call.caller_id IN (SELECT id FROM methods WHERE class_id = ?)
        """,
        (class_id,)
    )
    
    return {
        **class_info,
        "methods": methods,
        "extends": extends,
        "called_by": called_by,
        "calls": calls
    }


@router.get("/methods")
async def get_methods(
    request: Request,
    page: int = 1,
    limit: int = 50,
    search: Optional[str] = None,
    class_id: Optional[int] = None
):
    """获取方法列表"""
    db = request.app.state.db
    
    offset = (page - 1) * limit
    
    conditions = []
    params = []
    
    if search:
        conditions.append("m.name LIKE ?")
        params.append(f"%{search}%")
    
    if class_id:
        conditions.append("m.class_id = ?")
        params.append(class_id)
    
    where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
    
    methods = await db.fetchall(
        f"""
        SELECT m.*, c.name as class_name, f.path as file_path
        FROM methods m
        JOIN classes c ON m.class_id = c.id
        JOIN files f ON c.file_id = f.id
        {where_clause}
        ORDER BY m.name
        LIMIT ? OFFSET ?
        """,
        (*params, limit, offset)
    )
    
    return {
        "items": methods,
        "page": page,
        "limit": limit
    }


@router.get("/call-chain")
async def get_call_chain(
    request: Request,
    from_method_id: int,
    to_method_id: int,
    max_depth: int = 10
):
    """获取调用链路径"""
    db = request.app.state.db
    
    visited = set()
    paths = []
    
    async def dfs(current: int, target: int, path: List[int], depth: int):
        if depth > max_depth:
            return
        
        if current == target:
            paths.append(path.copy())
            return
        
        if current in visited:
            return
        
        visited.add(current)
        
        callees = await db.fetchall(
            "SELECT callee_id FROM calls WHERE caller_id = ?",
            (current,)
        )
        
        for callee in callees:
            if callee['callee_id'] not in path:
                path.append(callee['callee_id'])
                await dfs(callee['callee_id'], target, path, depth + 1)
                path.pop()
        
        visited.discard(current)
    
    await dfs(from_method_id, to_method_id, [from_method_id], 0)
    
    return {
        "paths": paths,
        "total_paths": len(paths),
        "depth": max_depth
    }


@router.get("/components")
async def get_components(request: Request):
    """获取组件列表"""
    db = request.app.state.db
    
    components = await db.fetchall(
        """
        SELECT c.*, f.path as file_path,
               (SELECT COUNT(*) FROM components WHERE parent_id = c.id) as child_count
        FROM classes c
        JOIN files f ON c.file_id = f.id
        WHERE c.flags & 1 = 1
        ORDER BY c.name
        """
    )
    
    return {"items": components}


@router.get("/component-tree")
async def get_component_tree(request: Request):
    """获取组件树"""
    db = request.app.state.db
    
    all_components = await db.fetchall(
        """
        SELECT * FROM classes WHERE flags & 1 = 1
        """
    )
    
    roots = []
    children_map = {}
    
    for comp in all_components:
        children_map[comp['id']] = []
    
    components_with_relations = await db.fetchall(
        """
        SELECT parent_id, child_id FROM components
        """
    )
    
    for parent_id, child_id in [(c['parent_id'], c['child_id']) for c in components_with_relations]:
        if parent_id in children_map:
            children_map[parent_id].append(child_id)
    
    def build_tree(component_id: int) -> dict:
        comp = next((c for c in all_components if c['id'] == component_id), None)
        if not comp:
            return None
        
        return {
            "id": comp['id'],
            "name": comp['name'],
            "children": [build_tree(child_id) for child_id in children_map.get(component_id, []) if build_tree(child_id)]
        }
    
    for comp in all_components:
        is_root = not any(c['child_id'] == comp['id'] for c in components_with_relations)
        if is_root:
            tree = build_tree(comp['id'])
            if tree:
                roots.append(tree)
    
    return {"tree": roots}


@router.get("/changes")
async def get_change_history(
    request: Request,
    limit: int = 20
):
    """获取变更历史"""
    db = request.app.state.db
    
    changes = await db.fetchall(
        """
        SELECT * FROM change_logs
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (limit,)
    )
    
    return {"items": changes}


@router.get("/search")
async def search_entities(
    request: Request,
    q: str,
    type: Optional[str] = None
):
    """搜索实体"""
    db = request.app.state.db
    results = []
    
    if type is None or type == "class":
        classes = await db.fetchall(
            """
            SELECT 'class' as type, c.id, c.name, c.file_id, f.path as file_path
            FROM classes c
            JOIN files f ON c.file_id = f.id
            WHERE c.name LIKE ?
            LIMIT 20
            """,
            (f"%{q}%",)
        )
        results.extend(classes)
    
    if type is None or type == "method":
        methods = await db.fetchall(
            """
            SELECT 'method' as type, m.id, m.name, m.class_id, f.path as file_path,
                   c.name as class_name
            FROM methods m
            JOIN classes c ON m.class_id = c.id
            JOIN files f ON c.file_id = f.id
            WHERE m.name LIKE ?
            LIMIT 20
            """,
            (f"%{q}%",)
        )
        results.extend(methods)
    
    return {"results": results}


@router.get("/graph/nodes")
async def get_graph_nodes(
    request: Request,
    type: str = "class"
):
    """获取图谱节点"""
    db = request.app.state.db
    
    if type == "class":
        nodes = await db.fetchall(
            """
            SELECT c.id, c.name, c.file_id, c.flags,
                   f.path as file_path,
                   'class' as node_type
            FROM classes c
            JOIN files f ON c.file_id = f.id
            """
        )
    else:
        nodes = await db.fetchall(
            """
            SELECT m.id, m.name, m.class_id,
                   c.name as class_name,
                   f.path as file_path,
                   'method' as node_type
            FROM methods m
            JOIN classes c ON m.class_id = c.id
            JOIN files f ON c.file_id = f.id
            """
        )
    
    return {"nodes": nodes}


@router.get("/graph/edges")
async def get_graph_edges(
    request: Request,
    type: str = "extends"
):
    """获取图谱边"""
    db = request.app.state.db
    
    if type == "extends":
        edges = await db.fetchall(
            "SELECT parent as source, child as target, 'extends' as relation FROM extends_relations"
        )
    elif type == "calls":
        edges = await db.fetchall(
            """
            SELECT caller_id as source, callee_id as target, 'calls' as relation
            FROM calls
            """
        )
    elif type == "components":
        edges = await db.fetchall(
            """
            SELECT parent_id as source, child_id as target, 'contains' as relation
            FROM components
            """
        )
    else:
        edges = []
    
    return {"edges": edges}


@router.put("/config")
async def update_config(
    request: Request,
    config: ConfigUpdateRequest
):
    """更新配置"""
    from config import SystemConfig
    
    current_config = SystemConfig.load()
    
    if config.watch_path is not None:
        current_config.watch_path = config.watch_path
    if config.api_key is not None:
        current_config.api_key = config.api_key
    if config.debounce_seconds is not None:
        current_config.debounce_seconds = config.debounce_seconds
    if config.enable_llm_analysis is not None:
        current_config.enable_llm_analysis = config.enable_llm_analysis
    
    current_config.save()
    
    return {"status": "success", "message": "Configuration updated"}

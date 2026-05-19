"""
ArkAnalyzer数据库连接管理模块
文件名: connection.py
用途: SQLite数据库连接池和事务管理
"""
import asyncio
import contextlib
import aiosqlite
from pathlib import Path
from typing import Optional, List, Dict, Any, AsyncIterator
import logging

from config import SystemConfig

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """SQLite数据库连接管理类"""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or "arkgraph.db"
        self._connection: Optional[aiosqlite.Connection] = None
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """初始化数据库，创建表结构"""
        async with self._lock:
            self._connection = await aiosqlite.connect(self.db_path)
            await self._connection.execute("PRAGMA foreign_keys = ON")
            await self._connection.execute("PRAGMA journal_mode = WAL")
            await self._create_tables()
            logger.info(f"数据库初始化完成: {self.db_path}")
    
    async def _create_tables(self):
        """创建数据库表结构"""
        await self._connection.executescript("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                path TEXT UNIQUE NOT NULL,
                hash BLOB NOT NULL,
                modified INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_files_path ON files(path);
            CREATE INDEX IF NOT EXISTS idx_files_hash ON files(hash);
            
            CREATE TABLE IF NOT EXISTS classes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                file_id INTEGER NOT NULL,
                flags INTEGER DEFAULT 0,
                line_number INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES files(id) ON DELETE CASCADE
            );
            
            CREATE INDEX IF NOT EXISTS idx_classes_file ON classes(file_id);
            CREATE INDEX IF NOT EXISTS idx_classes_name ON classes(name);
            
            CREATE TABLE IF NOT EXISTS methods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                class_id INTEGER NOT NULL,
                params TEXT,
                return_type TEXT,
                line_number INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE
            );
            
            CREATE INDEX IF NOT EXISTS idx_methods_class ON methods(class_id);
            CREATE INDEX IF NOT EXISTS idx_methods_name ON methods(name);
            
            CREATE TABLE IF NOT EXISTS calls (
                caller_id INTEGER NOT NULL,
                callee_id INTEGER NOT NULL,
                line_number INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (caller_id, callee_id),
                FOREIGN KEY (caller_id) REFERENCES methods(id) ON DELETE CASCADE,
                FOREIGN KEY (callee_id) REFERENCES methods(id) ON DELETE CASCADE
            );
            
            CREATE INDEX IF NOT EXISTS idx_calls_caller ON calls(caller_id);
            CREATE INDEX IF NOT EXISTS idx_calls_callee ON calls(callee_id);
            
            CREATE TABLE IF NOT EXISTS components (
                parent_id INTEGER NOT NULL,
                child_id INTEGER NOT NULL,
                PRIMARY KEY (parent_id, child_id),
                FOREIGN KEY (parent_id) REFERENCES classes(id) ON DELETE CASCADE,
                FOREIGN KEY (child_id) REFERENCES classes(id) ON DELETE CASCADE
            );
            
            CREATE INDEX IF NOT EXISTS idx_components_parent ON components(parent_id);
            CREATE INDEX IF NOT EXISTS idx_components_child ON components(child_id);
            
            CREATE TABLE IF NOT EXISTS change_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                change_type TEXT NOT NULL,
                file_hash_before BLOB,
                file_hash_after BLOB,
                entities_count INTEGER,
                duration_ms INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_change_logs_time ON change_logs(created_at DESC);
            
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await self._connection.commit()
    
    @property
    def connection(self) -> aiosqlite.Connection:
        """获取数据库连接"""
        if self._connection is None:
            raise RuntimeError("数据库未初始化，请先调用initialize()")
        return self._connection
    
    @contextlib.asynccontextmanager
    async def transaction(self):
        """事务上下文管理器 - 支持并发访问
        
        第一性原理：SQLite使用WAL模式支持并发读，但写操作需要串行化。
        使用asyncio.Lock确保同一时间只有一个写事务在执行。
        """
        async with self._lock:
            try:
                await self.connection.execute("BEGIN IMMEDIATE")
                yield self
                await self.connection.commit()
            except Exception:
                await self.connection.rollback()
                raise
    
    async def execute(self, sql: str, parameters: tuple = ()) -> aiosqlite.Cursor:
        """执行SQL语句"""
        return await self.connection.execute(sql, parameters)
    
    async def executemany(self, sql: str, parameters: List[tuple]) -> aiosqlite.Cursor:
        """批量执行SQL语句"""
        return await self.connection.executemany(sql, parameters)
    
    async def executescript(self, script: str):
        """执行SQL脚本"""
        await self.connection.executescript(script)
    
    async def commit(self):
        """提交事务"""
        await self.connection.commit()
    
    async def rollback(self):
        """回滚事务"""
        await self.connection.rollback()
    
    async def fetchone(self, sql: str, parameters: tuple = ()) -> Optional[Dict[str, Any]]:
        """查询单条记录"""
        cursor = await self.execute(sql, parameters)
        row = await cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return dict(zip(columns, row))
        return None
    
    async def fetchall(self, sql: str, parameters: tuple = ()) -> List[Dict[str, Any]]:
        """查询所有记录"""
        cursor = await self.execute(sql, parameters)
        rows = await cursor.fetchall()
        if rows:
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
        return []
    
    async def close(self):
        """关闭数据库连接"""
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("数据库连接已关闭")
    
    async def get_file_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """根据路径获取文件信息"""
        return await self.fetchone(
            "SELECT * FROM files WHERE path = ?",
            (file_path,)
        )
    
    async def get_file_hash(self, file_path: str) -> Optional[bytes]:
        """获取文件的哈希值"""
        result = await self.fetchone(
            "SELECT hash FROM files WHERE path = ?",
            (file_path,)
        )
        return result['hash'] if result else None
    
    async def get_classes_by_file(self, file_id: int) -> List[Dict[str, Any]]:
        """获取文件的所有类"""
        return await self.fetchall(
            "SELECT * FROM classes WHERE file_id = ?",
            (file_id,)
        )
    
    async def get_methods_by_class(self, class_id: int) -> List[Dict[str, Any]]:
        """获取类的所有方法"""
        return await self.fetchall(
            "SELECT * FROM methods WHERE class_id = ?",
            (class_id,)
        )
    
    async def get_statistics(self) -> Dict[str, int]:
        """获取图谱统计信息"""
        stats = {}
        
        result = await self.fetchone("SELECT COUNT(*) as count FROM files")
        stats['total_files'] = result['count'] if result else 0
        
        result = await self.fetchone("SELECT COUNT(*) as count FROM classes")
        stats['total_classes'] = result['count'] if result else 0
        
        result = await self.fetchone("SELECT COUNT(*) as count FROM methods")
        stats['total_methods'] = result['count'] if result else 0
        
        result = await self.fetchone("SELECT COUNT(*) as count FROM calls")
        stats['total_calls'] = result['count'] if result else 0
        
        result = await self.fetchone("SELECT COUNT(*) as count FROM components")
        stats['total_components'] = result['count'] if result else 0
        
        return stats
    
    async def get_all_classes(self) -> List[Dict[str, Any]]:
        """获取所有类"""
        return await self.fetchall("SELECT * FROM classes")
    
    async def get_all_files(self) -> List[Dict[str, Any]]:
        """获取所有文件"""
        return await self.fetchall("SELECT * FROM files")

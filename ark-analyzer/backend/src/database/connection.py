"""
ArkAnalyzer数据库连接管理模块
文件名: connection.py
用途: SQLite数据库连接池和事务管理
版本: v5.1 - 稳定版（无缓存，避免循环导入）
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
        logger.debug(f"[DB_INIT] 数据库初始化，路径: {self.db_path}")
    
    async def initialize(self):
        """初始化数据库，创建表结构"""
        logger.info(f"[DB_INITIALIZE_START] 开始初始化数据库: {self.db_path}")
        async with self._lock:
            logger.debug(f"[DB_CONNECT] 正在连接数据库...")
            self._connection = await aiosqlite.connect(self.db_path)
            logger.debug(f"[DB_CONNECT_OK] 数据库连接成功")
            
            logger.debug(f"[DB_PRAGMA_FK] 设置外键约束...")
            await self._connection.execute("PRAGMA foreign_keys = ON")
            logger.debug(f"[DB_PRAGMA_FK_OK] 外键约束设置完成")
            
            logger.debug(f"[DB_PRAGMA_WAL] 设置WAL模式...")
            await self._connection.execute("PRAGMA journal_mode = WAL")
            logger.debug(f"[DB_PRAGMA_WAL_OK] WAL模式设置完成")
            
            logger.debug(f"[DB_CREATE_TABLES] 正在创建表结构...")
            await self._create_tables()
            logger.debug(f"[DB_CREATE_TABLES_OK] 表结构创建完成")
            
        logger.info(f"[DB_INITIALIZE_COMPLETE] 数据库初始化完成: {self.db_path}")
    
    async def _create_tables(self):
        """创建数据库表结构"""
        logger.debug(f"[CREATE_TABLES_START] 开始创建表结构")
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
            
            CREATE TABLE IF NOT EXISTS extends_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent INTEGER NOT NULL,
                child INTEGER NOT NULL,
                FOREIGN KEY (parent) REFERENCES classes(id) ON DELETE CASCADE,
                FOREIGN KEY (child) REFERENCES classes(id) ON DELETE CASCADE
            );
            
            CREATE INDEX IF NOT EXISTS idx_extends_parent ON extends_relations(parent);
            CREATE INDEX IF NOT EXISTS idx_extends_child ON extends_relations(child);
            
            CREATE TABLE IF NOT EXISTS config (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        await self._connection.commit()
        logger.debug(f"[CREATE_TABLES_SCRIPT_OK] SQL脚本执行成功")
        logger.info(f"[CREATE_TABLES_COMPLETE] 表结构创建完成")
    
    @property
    def connection(self) -> aiosqlite.Connection:
        """获取数据库连接"""
        if self._connection is None:
            logger.error(f"[DB_CONNECTION_ERROR] 数据库未初始化，请先调用initialize()")
            raise RuntimeError("数据库未初始化，请先调用initialize()")
        logger.debug(f"[DB_CONNECTION_GET] 获取数据库连接")
        return self._connection
    
    @contextlib.asynccontextmanager
    async def transaction(self):
        """事务上下文管理器 - 支持并发访问
        
        第一性原理：SQLite使用WAL模式支持并发读，但写操作需要串行化。
        使用asyncio.Lock确保同一时间只有一个写事务在执行。
        """
        logger.debug(f"[TRANSACTION_ACQUIRE_LOCK] 尝试获取事务锁...")
        async with self._lock:
            logger.debug(f"[TRANSACTION_LOCK_ACQUIRED] 锁获取成功，开始事务")
            try:
                logger.debug(f"[TRANSACTION_BEGIN] 执行 BEGIN IMMEDIATE")
                await self.connection.execute("BEGIN IMMEDIATE")
                logger.debug(f"[TRANSACTION_BEGIN_OK] BEGIN IMMEDIATE 执行成功")
                yield self
                logger.debug(f"[TRANSACTION_COMMIT] 准备提交事务")
                await self.connection.commit()
                logger.debug(f"[TRANSACTION_COMMIT_OK] 事务提交成功")
            except Exception as e:
                logger.error(f"[TRANSACTION_ERROR] 事务执行异常: {e}")
                logger.debug(f"[TRANSACTION_ROLLBACK] 执行回滚")
                await self.connection.rollback()
                logger.debug(f"[TRANSACTION_ROLLBACK_OK] 回滚完成")
                raise
    
    async def execute(self, sql: str, parameters: tuple = ()) -> aiosqlite.Cursor:
        """执行SQL语句"""
        logger.debug(f"[EXECUTE_SQL] 执行SQL: {sql[:100]}... 参数: {parameters}")
        result = await self.connection.execute(sql, parameters)
        logger.debug(f"[EXECUTE_SQL_OK] SQL执行成功")
        return result
    
    async def executemany(self, sql: str, parameters: List[tuple]) -> aiosqlite.Cursor:
        """批量执行SQL语句"""
        logger.debug(f"[EXECUTE_MANY_SQL] 批量执行SQL: {sql[:100]}... 参数数量: {len(parameters)}")
        result = await self.connection.executemany(sql, parameters)
        logger.debug(f"[EXECUTE_MANY_SQL_OK] 批量SQL执行成功")
        return result
    
    async def executescript(self, script: str):
        """执行SQL脚本"""
        logger.debug(f"[EXECUTE_SCRIPT] 执行SQL脚本，长度: {len(script)}")
        await self.connection.executescript(script)
        logger.debug(f"[EXECUTE_SCRIPT_OK] SQL脚本执行成功")
    
    async def commit(self):
        """提交事务"""
        logger.debug(f"[COMMIT_START] 提交事务")
        await self.connection.commit()
        logger.debug(f"[COMMIT_OK] 事务提交成功")
    
    async def rollback(self):
        """回滚事务"""
        logger.debug(f"[ROLLBACK_START] 回滚事务")
        await self.connection.rollback()
        logger.debug(f"[ROLLBACK_OK] 事务回滚成功")
    
    async def fetchone(self, sql: str, parameters: tuple = ()) -> Optional[Dict[str, Any]]:
        """查询单条记录"""
        logger.debug(f"[FETCH_ONE_SQL] 查询单条记录: {sql[:100]}... 参数: {parameters}")
        cursor = await self.execute(sql, parameters)
        row = await cursor.fetchone()
        logger.debug(f"[FETCH_ONE_RESULT] 查询结果: {'有数据' if row else '无数据'}")
        if row:
            columns = [desc[0] for desc in cursor.description]
            result = dict(zip(columns, row))
            logger.debug(f"[FETCH_ONE_DATA] 返回数据: {result}")
            return result
        return None
    
    async def fetchall(self, sql: str, parameters: tuple = ()) -> List[Dict[str, Any]]:
        """查询所有记录"""
        logger.debug(f"[FETCH_ALL_SQL] 查询所有记录: {sql[:100]}... 参数: {parameters}")
        cursor = await self.execute(sql, parameters)
        rows = await cursor.fetchall()
        logger.debug(f"[FETCH_ALL_COUNT] 查询到 {len(rows)} 条记录")
        if rows:
            columns = [desc[0] for desc in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
            logger.debug(f"[FETCH_ALL_DATA] 返回 {len(results)} 条数据")
            return results
        return []
    
    async def close(self):
        """关闭数据库连接"""
        logger.debug(f"[CLOSE_START] 关闭数据库连接")
        if self._connection:
            await self._connection.close()
            self._connection = None
            logger.info("[CLOSE_OK] 数据库连接已关闭")
    
    async def get_file_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """根据路径获取文件信息"""
        logger.debug(f"[GET_FILE_BY_PATH] 查询文件: {file_path}")
        result = await self.fetchone(
            "SELECT * FROM files WHERE path = ?",
            (file_path,)
        )
        logger.debug(f"[GET_FILE_BY_PATH_RESULT] 文件查询{'成功' if result else '失败'}: {file_path}")
        return result
    
    async def get_file_hash(self, file_path: str) -> Optional[bytes]:
        """获取文件的哈希值"""
        logger.debug(f"[GET_FILE_HASH] 查询文件哈希: {file_path}")
        result = await self.fetchone(
            "SELECT hash FROM files WHERE path = ?",
            (file_path,)
        )
        hash_value = result['hash'] if result else None
        logger.debug(f"[GET_FILE_HASH_RESULT] 哈希查询{'成功' if hash_value else '失败'}: {file_path}")
        return hash_value
    
    async def get_classes_by_file(self, file_id: int) -> List[Dict[str, Any]]:
        """获取文件的所有类"""
        logger.debug(f"[GET_CLASSES_BY_FILE] 查询文件的类: file_id={file_id}")
        result = await self.fetchall(
            "SELECT * FROM classes WHERE file_id = ?",
            (file_id,)
        )
        logger.debug(f"[GET_CLASSES_BY_FILE_RESULT] 查询到 {len(result)} 个类")
        return result
    
    async def get_methods_by_class(self, class_id: int) -> List[Dict[str, Any]]:
        """获取类的所有方法"""
        logger.debug(f"[GET_METHODS_BY_CLASS] 查询类的方法: class_id={class_id}")
        result = await self.fetchall(
            "SELECT * FROM methods WHERE class_id = ?",
            (class_id,)
        )
        logger.debug(f"[GET_METHODS_BY_CLASS_RESULT] 查询到 {len(result)} 个方法")
        return result
    
    async def get_statistics(self) -> Dict[str, int]:
        """获取图谱统计信息"""
        logger.debug(f"[GET_STATS_START] 开始获取统计信息")
        stats = {}
        
        result = await self.fetchone("SELECT COUNT(*) as count FROM files")
        stats['total_files'] = result['count'] if result else 0
        logger.debug(f"[GET_STATS_FILES] 文件数: {stats['total_files']}")
        
        result = await self.fetchone("SELECT COUNT(*) as count FROM classes")
        stats['total_classes'] = result['count'] if result else 0
        logger.debug(f"[GET_STATS_CLASSES] 类数: {stats['total_classes']}")
        
        result = await self.fetchone("SELECT COUNT(*) as count FROM methods")
        stats['total_methods'] = result['count'] if result else 0
        logger.debug(f"[GET_STATS_METHODS] 方法数: {stats['total_methods']}")
        
        result = await self.fetchone("SELECT COUNT(*) as count FROM calls")
        stats['total_calls'] = result['count'] if result else 0
        logger.debug(f"[GET_STATS_CALLS] 调用数: {stats['total_calls']}")
        
        result = await self.fetchone("SELECT COUNT(*) as count FROM components")
        stats['total_components'] = result['count'] if result else 0
        logger.debug(f"[GET_STATS_COMPONENTS] 组件数: {stats['total_components']}")
        
        logger.info(f"[GET_STATS_COMPLETE] 统计信息获取完成: {stats}")
        return stats
    
    async def get_all_classes(self) -> List[Dict[str, Any]]:
        """获取所有类"""
        logger.debug(f"[GET_ALL_CLASSES_START] 获取所有类")
        result = await self.fetchall("SELECT * FROM classes")
        logger.debug(f"[GET_ALL_CLASSES_RESULT] 返回 {len(result)} 个类")
        return result
    
    async def get_all_files(self) -> List[Dict[str, Any]]:
        """获取所有文件"""
        logger.debug(f"[GET_ALL_FILES_START] 获取所有文件")
        result = await self.fetchall("SELECT * FROM files")
        logger.debug(f"[GET_ALL_FILES_RESULT] 返回 {len(result)} 个文件")
        return result

"""
ArkAnalyzer同步引擎模块
文件名: synchronization_engine.py
用途: 基于第一性原理实现增量同步，核心更新逻辑
版本: v5.0 - 增强日志版 - 修复事务内查询问题
"""
import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from database.connection import DatabaseConnection
from services.file_watcher_service import FileHashCalculator
from services.arkts_parser_service import ArkTSParser, ParsedFile
from services.websocket_manager import WebSocketManager
from config import FileChangeEvent, UpdateResult

logger = logging.getLogger(__name__)


@dataclass
class EntityCounter:
    """实体计数器"""
    classes: int = 0
    methods: int = 0
    calls: int = 0
    components: int = 0


class SynchronizationEngine:
    """
    同步引擎 - 基于第一性原理的核心设计

    第一性原理洞察：
    一个文件的变更只会影响该文件内部的所有实体和关系。
    因此，更新策略简化为：
    1. 删除该文件的旧数据
    2. 重新解析该文件
    3. 插入新数据

    不需要修改任何其他文件的数据！
    """

    def __init__(
        self,
        db_connection: DatabaseConnection,
        websocket_manager: WebSocketManager
    ):
        self.db = db_connection
        self.ws_manager = websocket_manager
        self.parser = ArkTSParser()
        self._running = False

    async def full_sync(self, watch_path: str) -> Dict[str, Any]:
        """全量同步 - 首次运行或恢复时使用"""
        logger.info(f"[FULL_SYNC_START] 开始全量同步，路径: {watch_path}")
        start_time = time.time()

        project_path = Path(watch_path)
        if not project_path.exists():
            logger.error(f"[FULL_SYNC_ERROR] 路径不存在: {watch_path}")
            raise ValueError(f"路径不存在: {watch_path}")
        logger.debug(f"[FULL_SYNC_PATH_OK] 路径验证通过: {watch_path}")

        ets_files = list(project_path.rglob("*.ets"))
        logger.info(f"[FULL_SYNC_FILES_FOUND] 发现 {len(ets_files)} 个 ArkTS 文件")

        processed = 0
        errors = []
        logger.info(f"[FULL_SYNC_PROCESSING] 开始处理 {len(ets_files)} 个文件...")

        for idx, file_path in enumerate(ets_files):
            try:
                logger.debug(f"[FULL_SYNC_FILE_{idx}] 处理文件 {file_path}")
                result = await self.update_single_file(str(file_path))
                if result.success:
                    processed += 1
                    logger.debug(f"[FULL_SYNC_FILE_SUCCESS_{idx}] 文件处理成功: {file_path}")
                else:
                    errors.append(result.to_dict())
                    logger.warning(f"[FULL_SYNC_FILE_ERROR_{idx}] 文件处理失败: {file_path}, error: {result.error_message}")
            except Exception as e:
                logger.error(f"[FULL_SYNC_FILE_EXCEPTION_{idx}] 处理文件异常 {file_path}: {e}")
                errors.append({
                    "file_path": str(file_path),
                    "error": str(e)
                })

        duration = time.time() - start_time
        logger.info(f"[FULL_SYNC_BROADCAST] 全量同步完成，准备广播: processed={processed}, total={len(ets_files)}, duration={duration:.2f}s")

        await self.ws_manager.broadcast({
            "type": "sync_complete",
            "data": {
                "total_files": len(ets_files),
                "processed": processed,
                "errors": len(errors),
                "duration_ms": int(duration * 1000)
            }
        })

        logger.info(f"[FULL_SYNC_COMPLETE] 全量同步完成: {processed}/{len(ets_files)} 文件，耗时 {duration:.2f}秒")

        return {
            "total_files": len(ets_files),
            "processed": processed,
            "errors": errors,
            "duration_ms": int(duration * 1000)
        }

    async def incremental_update(
        self,
        changes: Dict[str, str]
    ) -> List[UpdateResult]:
        """
        增量更新 - 处理多个文件变更

        参数:
            changes: 文件路径到变更类型的字典
                    {"path/to/file.ets": "modified", ...}

        返回:
            UpdateResult列表
        """
        logger.info(f"[INCREMENTAL_UPDATE_START] 开始增量更新，变更文件数: {len(changes)}")
        results = []

        for file_path, change_type in changes.items():
            logger.debug(f"[INCREMENTAL_UPDATE_FILE] 处理文件: {file_path}, 类型: {change_type}")
            try:
                result = await self.update_single_file(file_path, change_type)
                results.append(result)
                logger.debug(f"[INCREMENTAL_UPDATE_SUCCESS] 文件更新成功: {file_path}, 实体数: {result.entities_updated}")

                logger.debug(f"[INCREMENTAL_UPDATE_BROADCAST] 准备广播变更通知: {file_path}")
                await self.ws_manager.broadcast({
                    "type": "file_changed",
                    "data": result.to_dict()
                })
                logger.debug(f"[INCREMENTAL_UPDATE_BROADCAST_OK] 广播成功: {file_path}")

            except Exception as e:
                logger.error(f"[INCREMENTAL_UPDATE_ERROR] 增量更新失败 {file_path}: {e}")
                results.append(UpdateResult(
                    success=False,
                    file_path=file_path,
                    error_message=str(e)
                ))

        logger.info(f"[INCREMENTAL_UPDATE_COMPLETE] 增量更新完成，成功: {sum(1 for r in results if r.success)}/{len(results)}")
        return results

    async def update_single_file(
        self,
        file_path: str,
        change_type: str = "modified"
    ) -> UpdateResult:
        """
        更新单个文件 - 原子操作

        第一性原理实现：
        1. 计算新哈希（在事务外）
        2. 查询旧哈希（在事务外）
        3. BEGIN TRANSACTION（在事务内查询和插入）
        4. 删除旧数据（通过外键级联删除）
        5. 重新解析并插入新数据
        6. COMMIT TRANSACTION

        注意：所有数据库查询必须在事务开始前完成，避免嵌套事务问题。
        """
        logger.debug(f"[UPDATE_FILE_START] 开始更新文件: {file_path}, 类型: {change_type}")
        start_time = time.time()

        if change_type == "deleted":
            logger.debug(f"[UPDATE_FILE_DELETED] 检测到删除操作，调用 _delete_file_data")
            return await self._delete_file_data(file_path, start_time)

        if not Path(file_path).exists():
            logger.debug(f"[UPDATE_FILE_NOT_EXISTS] 文件不存在，调用 _delete_file_data: {file_path}")
            return await self._delete_file_data(file_path, start_time)
        logger.debug(f"[UPDATE_FILE_EXISTS] 文件存在验证通过: {file_path}")

        try:
            logger.debug(f"[UPDATE_FILE_HASH] 计算文件哈希: {file_path}")
            new_hash = await FileHashCalculator.calculate_md5_async(file_path)
            logger.debug(f"[UPDATE_FILE_HASH_NEW] 新哈希计算完成: {file_path}, hash={new_hash[:16]}...")

            logger.debug(f"[UPDATE_FILE_HASH_OLD] 查询旧哈希: {file_path}")
            old_hash = await self.db.get_file_hash(file_path)
            logger.debug(f"[UPDATE_FILE_HASH_COMPARE] 哈希比较: old={old_hash[:16] if old_hash else None}..., new={new_hash[:16]}...")

            if old_hash == new_hash:
                logger.debug(f"[UPDATE_FILE_SKIP] 文件未变化，跳过: {file_path}")
                return UpdateResult(
                    success=True,
                    file_path=file_path,
                    entities_updated=0,
                    duration_ms=int((time.time() - start_time) * 1000),
                    error_message=""
                )
            logger.debug(f"[UPDATE_FILE_CHANGED] 文件有变化，继续处理: {file_path}")

            logger.debug(f"[UPDATE_FILE_READ] 读取文件内容: {file_path}")
            content = await self._read_file_safe(file_path)
            logger.debug(f"[UPDATE_FILE_PARSE] 解析文件: {file_path}, 内容长度={len(content)}")
            parsed_file = self.parser.parse_file(file_path, content)
            logger.debug(f"[UPDATE_FILE_PARSED] 文件解析完成: {file_path}, classes={len(parsed_file.classes)}, functions={len(parsed_file.standalone_functions)}")

            logger.debug(f"[UPDATE_FILE_TRANSACTION] 开始数据库事务: {file_path}")
            async with self.db.transaction():
                logger.debug(f"[UPDATE_FILE_TRANSACTION_START] 事务已开始: {file_path}")
                existing_file = await self.db.get_file_by_path(file_path)
                logger.debug(f"[UPDATE_FILE_EXISTING_FILE] 查询现有文件: {file_path}, exists={existing_file is not None}")

                if existing_file:
                    logger.debug(f"[UPDATE_FILE_DELETE_REL] 删除文件关系: {file_path}, file_id={existing_file['id']}")
                    await self._delete_file_relationships(existing_file['id'])
                    logger.debug(f"[UPDATE_FILE_DELETE_REL_OK] 关系删除完成: {file_path}")

                logger.debug(f"[UPDATE_FILE_INSERT] 插入实体: {file_path}")
                entities = await self._insert_file_entities(file_path, new_hash, parsed_file)
                logger.debug(f"[UPDATE_FILE_INSERT_OK] 实体插入完成: {file_path}, classes={entities.classes}, methods={entities.methods}")

            logger.debug(f"[UPDATE_FILE_TRANSACTION_COMMIT] 事务已提交: {file_path}")

            logger.debug(f"[UPDATE_FILE_LOG] 记录变更日志: {file_path}")
            await self._log_change(file_path, change_type, entities, start_time)
            logger.debug(f"[UPDATE_FILE_LOG_OK] 变更日志记录完成: {file_path}")

            duration_ms = int((time.time() - start_time) * 1000)
            logger.info(f"[UPDATE_FILE_SUCCESS] 文件更新完成: {file_path}, 耗时 {duration_ms}ms, 实体数: {entities.classes + entities.methods}")

            return UpdateResult(
                success=True,
                file_path=file_path,
                entities_updated=entities.classes + entities.methods,
                duration_ms=duration_ms,
                error_message=""
            )

        except Exception as e:
            logger.error(f"[UPDATE_FILE_EXCEPTION] 更新文件异常 {file_path}: {e}")
            return UpdateResult(
                success=False,
                file_path=file_path,
                error_message=str(e)
            )

    async def _delete_file_data(
        self,
        file_path: str,
        start_time: float
    ) -> UpdateResult:
        """删除文件数据"""
        logger.debug(f"[DELETE_FILE_START] 开始删除文件数据: {file_path}")
        try:
            logger.debug(f"[DELETE_FILE_CHECK] 检查文件是否存在: {file_path}")
            existing_file = await self.db.get_file_by_path(file_path)
            logger.debug(f"[DELETE_FILE_CHECK_RESULT] 文件存在检查: {existing_file is not None}")

            if not existing_file:
                logger.debug(f"[DELETE_FILE_SKIP] 文件不存在，跳过删除: {file_path}")
                return UpdateResult(
                    success=True,
                    file_path=file_path,
                    entities_updated=0,
                    duration_ms=int((time.time() - start_time) * 1000)
                )

            logger.debug(f"[DELETE_FILE_TRANSACTION] 开始事务: {file_path}")
            async with self.db.transaction():
                logger.debug(f"[DELETE_FILE_EXECUTE] 执行删除: {file_path}, file_id={existing_file['id']}")
                await self.db.execute(
                    "DELETE FROM files WHERE path = ?",
                    (file_path,)
                )
                logger.debug(f"[DELETE_FILE_EXECUTE_OK] 删除成功: {file_path}")

            duration_ms = int((time.time() - start_time) * 1000)
            logger.debug(f"[DELETE_FILE_LOG] 记录删除日志: {file_path}")
            await self._log_change(file_path, "deleted", EntityCounter(), start_time)
            logger.debug(f"[DELETE_FILE_LOG_OK] 删除日志记录完成: {file_path}")

            logger.info(f"[DELETE_FILE_SUCCESS] 文件数据删除完成: {file_path}, 耗时 {duration_ms}ms")
            return UpdateResult(
                success=True,
                file_path=file_path,
                entities_updated=0,
                duration_ms=duration_ms
            )

        except Exception as e:
            logger.error(f"[DELETE_FILE_ERROR] 删除文件数据失败 {file_path}: {e}")
            return UpdateResult(
                success=False,
                file_path=file_path,
                error_message=str(e)
            )

    async def _delete_file_relationships(self, file_id: int):
        """删除文件的所有关联数据（通过外键级联）"""
        logger.debug(f"[DELETE_REL_START] 删除文件关联数据: file_id={file_id}")
        await self.db.execute(
            "DELETE FROM files WHERE id = ?",
            (file_id,)
        )
        logger.debug(f"[DELETE_REL_OK] 关联数据删除完成: file_id={file_id}")

    async def _insert_file_entities(
        self,
        file_path: str,
        file_hash: bytes,
        parsed_file: ParsedFile
    ) -> EntityCounter:
        """插入文件实体数据"""
        logger.debug(f"[INSERT_ENTITIES_START] 开始插入实体: {file_path}")
        counter = EntityCounter()

        logger.debug(f"[INSERT_FILE_RECORD] 插入文件记录: {file_path}")
        cursor = await self.db.execute(
            """
            INSERT INTO files (path, hash, modified)
            VALUES (?, ?, ?)
            """,
            (file_path, file_hash, int(time.time()))
        )
        file_id = cursor.lastrowid
        logger.debug(f"[INSERT_FILE_RECORD_OK] 文件记录插入成功: {file_path}, file_id={file_id}")

        logger.debug(f"[INSERT_CLASSES] 开始插入类: {file_path}, 类数量={len(parsed_file.classes)}")
        for idx, parsed_class in enumerate(parsed_file.classes):
            logger.debug(f"[INSERT_CLASS_{idx}] 插入类 {idx+1}/{len(parsed_file.classes)}: {parsed_class.name}")
            cursor = await self.db.execute(
                """
                INSERT INTO classes (name, file_id, flags, line_number)
                VALUES (?, ?, ?, ?)
                """,
                (
                    parsed_class.name,
                    file_id,
                    1 if parsed_class.is_component else 0,
                    parsed_class.line_number
                )
            )
            class_id = cursor.lastrowid
            counter.classes += 1
            logger.debug(f"[INSERT_CLASS_{idx}_OK] 类插入成功: {parsed_class.name}, class_id={class_id}")

            logger.debug(f"[INSERT_METHODS] 开始插入方法: {parsed_class.name}, 方法数量={len(parsed_class.methods)}")
            for midx, parsed_method in enumerate(parsed_class.methods):
                logger.debug(f"[INSERT_METHOD_{midx}] 插入方法 {midx+1}/{len(parsed_class.methods)}: {parsed_method.name}")
                cursor = await self.db.execute(
                    """
                    INSERT INTO methods (name, class_id, params, return_type, line_number)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        parsed_method.name,
                        class_id,
                        parsed_method.params,
                        parsed_method.return_type,
                        parsed_method.line_number
                    )
                )
                method_id = cursor.lastrowid
                counter.methods += 1
                logger.debug(f"[INSERT_METHOD_{midx}_OK] 方法插入成功: {parsed_method.name}, method_id={method_id}")

        logger.debug(f"[INSERT_FUNCTIONS] 开始插入独立函数: {file_path}, 函数数量={len(parsed_file.standalone_functions)}")
        for idx, func in enumerate(parsed_file.standalone_functions):
            logger.debug(f"[INSERT_FUNCTION_{idx}] 插入函数 {idx+1}/{len(parsed_file.standalone_functions)}: {func.name}")
            cursor = await self.db.execute(
                """
                INSERT INTO methods (name, class_id, params, return_type, line_number)
                VALUES (?, ?, ?, ?, ?)
                """,
                (func.name, file_id, func.params, func.return_type, func.line_number)
            )
            counter.methods += 1
            logger.debug(f"[INSERT_FUNCTION_{idx}_OK] 函数插入成功: {func.name}")

        logger.info(f"[INSERT_ENTITIES_COMPLETE] 实体插入完成: {file_path}, classes={counter.classes}, methods={counter.methods}")
        return counter

    async def _read_file_safe(self, file_path: str) -> str:
        """安全读取文件"""
        logger.debug(f"[READ_FILE_START] 开始读取文件: {file_path}")
        loop = asyncio.get_event_loop()
        content = await loop.run_in_executor(
            None,
            lambda: Path(file_path).read_text(encoding='utf-8')
        )
        logger.debug(f"[READ_FILE_OK] 文件读取完成: {file_path}, 长度={len(content)}")
        return content

    async def _log_change(
        self,
        file_path: str,
        change_type: str,
        entities: EntityCounter,
        start_time: float
    ):
        """记录变更日志"""
        logger.debug(f"[LOG_CHANGE_START] 开始记录变更日志: {file_path}, 类型={change_type}")
        duration_ms = int((time.time() - start_time) * 1000)
        entities_count = entities.classes + entities.methods
        logger.debug(f"[LOG_CHANGE_DATA] 变更数据: file_path={file_path}, type={change_type}, entities={entities_count}, duration={duration_ms}ms")

        async with self.db.transaction():
            logger.debug(f"[LOG_CHANGE_TRANSACTION] 事务已开始，准备插入日志")
            await self.db.execute(
                """
                INSERT INTO change_logs (file_path, change_type, entities_count, duration_ms)
                VALUES (?, ?, ?, ?)
                """,
                (
                    file_path,
                    change_type,
                    entities_count,
                    duration_ms
                )
            )
            logger.debug(f"[LOG_CHANGE_INSERT_OK] 变更日志插入成功: {file_path}")

        logger.debug(f"[LOG_CHANGE_COMPLETE] 变更日志记录完成: {file_path}")

"""
ArkAnalyzer同步引擎模块
文件名: synchronization_engine.py
用途: 基于第一性原理实现增量同步，核心更新逻辑
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
        logger.info(f"开始全量同步，路径: {watch_path}")
        start_time = time.time()

        project_path = Path(watch_path)
        if not project_path.exists():
            raise ValueError(f"路径不存在: {watch_path}")

        ets_files = list(project_path.rglob("*.ets"))
        logger.info(f"发现 {len(ets_files)} 个 ArkTS 文件")

        processed = 0
        errors = []

        for file_path in ets_files:
            try:
                result = await self.update_single_file(str(file_path))
                if result.success:
                    processed += 1
                else:
                    errors.append(result.to_dict())
            except Exception as e:
                logger.error(f"处理文件失败 {file_path}: {e}")
                errors.append({
                    "file_path": str(file_path),
                    "error": str(e)
                })

        duration = time.time() - start_time

        await self.ws_manager.broadcast({
            "type": "sync_complete",
            "data": {
                "total_files": len(ets_files),
                "processed": processed,
                "errors": len(errors),
                "duration_ms": int(duration * 1000)
            }
        })

        logger.info(f"全量同步完成: {processed}/{len(ets_files)} 文件，耗时 {duration:.2f}秒")

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
        results = []

        for file_path, change_type in changes.items():
            try:
                result = await self.update_single_file(file_path, change_type)
                results.append(result)

                await self.ws_manager.broadcast({
                    "type": "file_changed",
                    "data": result.to_dict()
                })

            except Exception as e:
                logger.error(f"增量更新失败 {file_path}: {e}")
                results.append(UpdateResult(
                    success=False,
                    file_path=file_path,
                    error_message=str(e)
                ))

        return results

    async def update_single_file(
        self,
        file_path: str,
        change_type: str = "modified"
    ) -> UpdateResult:
        """
        更新单个文件 - 原子操作

        第一性原理实现：
        1. BEGIN TRANSACTION
        2. 删除旧数据（通过外键级联删除）
        3. 重新解析并插入新数据
        4. COMMIT TRANSACTION

        步骤2和3之间可能出现短暂不一致，但这是可接受的。
        """
        start_time = time.time()

        if change_type == "deleted":
            return await self._delete_file_data(file_path, start_time)

        if not Path(file_path).exists():
            return await self._delete_file_data(file_path, start_time)

        try:
            new_hash = await FileHashCalculator.calculate_md5_async(file_path)
            old_hash = await self.db.get_file_hash(file_path)

            if old_hash == new_hash:
                logger.debug(f"文件未变化，跳过: {file_path}")
                return UpdateResult(
                    success=True,
                    file_path=file_path,
                    entities_updated=0,
                    duration_ms=int((time.time() - start_time) * 1000),
                    error_message=""
                )

            # 整个操作在单个事务中执行
            async with self.db.transaction():
                existing_file = await self.db.get_file_by_path(file_path)
                if existing_file:
                    await self._delete_file_relationships(existing_file['id'])

                content = await self._read_file_safe(file_path)
                parsed_file = self.parser.parse_file(file_path, content)

                entities = await self._insert_file_entities(file_path, new_hash, parsed_file)

            await self._log_change(file_path, change_type, entities, start_time)

            duration_ms = int((time.time() - start_time) * 1000)
            logger.info(f"文件更新完成: {file_path}, 耗时 {duration_ms}ms")

            return UpdateResult(
                success=True,
                file_path=file_path,
                entities_updated=entities.classes + entities.methods,
                duration_ms=duration_ms,
                error_message=""
            )

        except Exception as e:
            logger.error(f"更新文件失败 {file_path}: {e}")

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
        try:
            async with self.db.transaction():
                existing_file = await self.db.get_file_by_path(file_path)

                if existing_file:
                    await self.db.execute(
                        "DELETE FROM files WHERE path = ?",
                        (file_path,)
                    )

            duration_ms = int((time.time() - start_time) * 1000)

            await self._log_change(file_path, "deleted", EntityCounter(), start_time)

            return UpdateResult(
                success=True,
                file_path=file_path,
                entities_updated=0,
                duration_ms=duration_ms
            )

        except Exception as e:
            return UpdateResult(
                success=False,
                file_path=file_path,
                error_message=str(e)
            )

    async def _delete_file_relationships(self, file_id: int):
        """删除文件的所有关联数据（通过外键级联）"""
        await self.db.execute(
            "DELETE FROM files WHERE id = ?",
            (file_id,)
        )

    async def _insert_file_entities(
        self,
        file_path: str,
        file_hash: bytes,
        parsed_file: ParsedFile
    ) -> EntityCounter:
        """插入文件实体数据"""
        counter = EntityCounter()

        cursor = await self.db.execute(
            """
            INSERT INTO files (path, hash, modified)
            VALUES (?, ?, ?)
            """,
            (file_path, file_hash, int(time.time()))
        )
        file_id = cursor.lastrowid

        for parsed_class in parsed_file.classes:
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

            for parsed_method in parsed_class.methods:
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

        for func in parsed_file.standalone_functions:
            cursor = await self.db.execute(
                """
                INSERT INTO methods (name, class_id, params, return_type, line_number)
                VALUES (?, ?, ?, ?, ?)
                """,
                (func.name, file_id, func.params, func.return_type, func.line_number)
            )
            counter.methods += 1

        return counter

    async def _read_file_safe(self, file_path: str) -> str:
        """安全读取文件"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            lambda: Path(file_path).read_text(encoding='utf-8')
        )

    async def _log_change(
        self,
        file_path: str,
        change_type: str,
        entities: EntityCounter,
        start_time: float
    ):
        """记录变更日志"""
        duration_ms = int((time.time() - start_time) * 1000)

        async with self.db.transaction():
            await self.db.execute(
                """
                INSERT INTO change_logs (file_path, change_type, entities_count, duration_ms)
                VALUES (?, ?, ?, ?)
                """,
                (
                    file_path,
                    change_type,
                    entities.classes + entities.methods,
                    duration_ms
                )
            )

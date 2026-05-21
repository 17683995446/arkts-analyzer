#!/usr/bin/env python3
"""
第八轮 - 终极混乱与长时间稳定性深度压力测试
文件名: round8_ultimate_chaos_test.py
遵循: 慢工出细活原理
"""

import asyncio
import time
import sys
import random
import traceback
import os
from pathlib import Path
from typing import Dict, List, Any, Set
import logging

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.connection import DatabaseConnection
from services.synchronization_engine import SynchronizationEngine
from services.websocket_manager import WebSocketManager
from services.arkts_parser_service import ArkTSParser

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("round8-test")


class Round8UltimateChaosTester:
    """
    第八轮终极混乱与长时间稳定性深度压力测试
    遵循"慢工出细活"原则，深度覆盖各种混乱场景
    """
    
    def __init__(self, chaos_project_path: str, mega_project_path: str):
        self.chaos_path = Path(chaos_project_path)
        self.mega_path = Path(mega_project_path)
        self.db = None
        self.sync_engine = None
        self.parser = ArkTSParser()
        
        self.metrics = {
            "start_time": 0,
            "end_time": 0,
            "total_files_processed": 0,
            "total_operations": 0,
            "total_errors": 0,
            "errors_by_type": {},
            "failed_files": [],
            "defects_found": []
        }
        
    async def setup(self):
        """初始化测试环境"""
        logger.info("\n" + "=" * 100)
        logger.info("🔥 第八轮 - 终极混乱与长时间稳定性深度压力测试 🔥")
        logger.info("=" * 100)
        
        logger.info(f"📁 混乱项目: {self.chaos_path}")
        logger.info(f"📁 大型项目: {self.mega_path}")
        
        self.db = DatabaseConnection(":memory:")
        await self.db.initialize()
        self.ws_manager = WebSocketManager()
        self.sync_engine = SynchronizationEngine(self.db, self.ws_manager)
        
        self.metrics["start_time"] = time.time()
        logger.info("✅ 测试环境初始化完成\n")
        
    async def run_phase1_chaos_files_scan(self):
        """
        阶段1: 扫描并测试所有混乱场景文件
        目标: 发现解析器在各种混乱边缘情况下的问题
        """
        logger.info("=" * 100)
        logger.info("📋 阶段1: 混乱场景文件扫描测试")
        logger.info("=" * 100)
        
        chaos_files = list(self.chaos_path.rglob("*.ets"))
        logger.info(f"  发现 {len(chaos_files)} 个混乱场景文件")
        
        success_count = 0
        error_count = 0
        
        for idx, file_path in enumerate(chaos_files, 1):
            try:
                logger.info(f"  [{idx}/{len(chaos_files)}] 处理: {file_path.name}")
                
                # 先读取内容看一下
                content = file_path.read_text('utf-8')
                content_preview = content[:100] if len(content) > 100 else content
                logger.debug(f"  内容预览: {repr(content_preview)}")
                
                # 解析测试
                parsed = self.parser.parse_file(str(file_path), content)
                logger.info(f"  ✓ 解析: 发现 {len(parsed.classes)} 个类, {len(parsed.standalone_functions)} 个函数")
                
                # 同步测试
                result = await self.sync_engine.update_single_file(str(file_path))
                
                if result.success:
                    success_count += 1
                else:
                    error_count += 1
                    logger.error(f"  ✗ 同步失败: {result.error_message}")
                    self._record_defect("phase1_chaos_sync", str(file_path), result.error_message)
                    
            except Exception as e:
                error_count += 1
                error_str = str(e)
                logger.error(f"  ✗ 处理失败: {file_path.name} - {error_str}")
                self._record_defect("phase1_chaos_exception", str(file_path), error_str)
                self.metrics["failed_files"].append(str(file_path))
                
                # 记录堆栈
                self._record_error_type(str(type(e).__name__))
                
            self.metrics["total_files_processed"] += 1
            
        logger.info(f"\n📊 阶段1完成: 成功 {success_count}, 失败 {error_count}")
        
    async def run_phase2_long_running_stability(self):
        """
        阶段2: 长时间稳定性运行测试
        目标: 发现长时间运行中的内存泄漏、性能下降、状态混乱等问题
        """
        logger.info("\n" + "=" * 100)
        logger.info("📋 阶段2: 长时间稳定性运行测试 (60秒)")
        logger.info("=" * 100)
        
        # 获取所有可用文件
        all_files = []
        if self.mega_path.exists():
            all_files.extend(list(self.mega_path.rglob("*.ets")))
        if self.chaos_path.exists():
            all_files.extend(list(self.chaos_path.rglob("*.ets")))
            
        random.shuffle(all_files)
        logger.info(f"  使用 {len(all_files)} 个文件进行持续测试")
        
        start_time = time.time()
        duration = 60  # 运行60秒
        operations_count = 0
        errors_during = 0
        
        last_log_time = time.time()
        
        while time.time() - start_time < duration:
            if not all_files:
                await asyncio.sleep(0.01)
                continue
                
            # 随机选择并操作文件
            file_path = random.choice(all_files)
            
            try:
                # 随机选择操作
                operation = random.choice(['update', 'update', 'update', 'reparse', 'check'])
                
                if operation == 'update':
                    await self.sync_engine.update_single_file(str(file_path))
                elif operation == 'reparse':
                    content = file_path.read_text('utf-8')
                    self.parser.parse_file(str(file_path), content)
                    
                operations_count += 1
                
            except Exception as e:
                errors_during += 1
                self._record_defect("phase2_long_run", str(file_path), str(e))
                
            # 定期记录进度
            if time.time() - last_log_time > 5:
                elapsed = time.time() - start_time
                logger.info(f"  ⏱️ 已运行 {elapsed:.1f}秒, 操作数: {operations_count}, 错误: {errors_during}")
                last_log_time = time.time()
                
        total_time = time.time() - start_time
        logger.info(f"\n📊 阶段2完成: 持续运行 {total_time:.1f}秒, 总操作 {operations_count}, 错误 {errors_during}")
        
        self.metrics["total_operations"] += operations_count
        self.metrics["total_errors"] += errors_during
        
    async def run_phase3_concurrent_chaos(self):
        """
        阶段3: 极端并发与混乱操作
        目标: 发现高并发情况下的死锁、竞态条件、数据一致性问题
        """
        logger.info("\n" + "=" * 100)
        logger.info("📋 阶段3: 极端并发与混乱操作")
        logger.info("=" * 100)
        
        all_files = []
        if self.mega_path.exists():
            all_files.extend(list(self.mega_path.rglob("*.ets")))
        
        if not all_files:
            logger.warning("  没有足够的文件进行并发测试")
            return
            
        concurrency = 30  # 30个并发任务
        iterations = 20  # 每轮20次迭代
        
        logger.info(f"  并发数: {concurrency}, 迭代轮数: {iterations}")
        
        total_ops = 0
        total_errors = 0
        
        for batch in range(iterations):
            # 准备任务
            tasks = []
            for _ in range(concurrency):
                file_path = random.choice(all_files)
                tasks.append(self._concurrent_update(str(file_path)))
                
            # 同时执行
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 统计
            batch_ops = len(results)
            batch_errors = sum(1 for r in results if isinstance(r, Exception))
            
            total_ops += batch_ops
            total_errors += batch_errors
            
            if batch_errors > 0:
                for idx, r in enumerate(results):
                    if isinstance(r, Exception):
                        self._record_defect("phase3_concurrent", str(all_files[idx % len(all_files)]), str(r))
                        
            logger.info(f"  批次 {batch+1}/{iterations}: {batch_ops} 操作, {batch_errors} 错误")
            
        logger.info(f"\n📊 阶段3完成: 总操作 {total_ops}, 总错误 {total_errors}")
        
        self.metrics["total_operations"] += total_ops
        self.metrics["total_errors"] += total_errors
        
    async def _concurrent_update(self, file_path: str):
        """并发更新单个文件"""
        try:
            await self.sync_engine.update_single_file(file_path)
        except Exception as e:
            # 记录但继续
            logger.debug(f"并发更新异常 {file_path}: {e}")
            raise
            
    async def run_phase4_database_stress(self):
        """
        阶段4: 数据库操作压力测试
        目标: 发现数据库层的边界问题
        """
        logger.info("\n" + "=" * 100)
        logger.info("📋 阶段4: 数据库操作压力测试")
        logger.info("=" * 100)
        
        db_errors = 0
        
        # 测试各种数据库查询
        try:
            logger.info("  测试: 获取统计信息")
            stats = await self.db.get_statistics()
            logger.info(f"  ✓ 统计: {stats}")
        except Exception as e:
            db_errors += 1
            self._record_defect("phase4_db_stats", "", str(e))
            
        try:
            logger.info("  测试: 获取所有文件")
            files = await self.db.get_all_files()
            logger.info(f"  ✓ 文件列表: {len(files)} 个文件")
        except Exception as e:
            db_errors += 1
            self._record_defect("phase4_db_files", "", str(e))
            
        try:
            logger.info("  测试: 获取所有类")
            classes = await self.db.get_all_classes()
            logger.info(f"  ✓ 类列表: {len(classes)} 个类")
        except Exception as e:
            db_errors += 1
            self._record_defect("phase4_db_classes", "", str(e))
            
        logger.info(f"\n📊 阶段4完成: 数据库错误 {db_errors}")
        self.metrics["total_errors"] += db_errors
        
    async def print_complete_report(self):
        """打印完整的深度测试报告"""
        self.metrics["end_time"] = time.time()
        total_duration = self.metrics["end_time"] - self.metrics["start_time"]
        
        logger.info("\n" + "=" * 100)
        logger.info("📋 第八轮 - 终极混乱与深度压力测试 完整报告")
        logger.info("=" * 100)
        
        logger.info(f"\n⏱️  总耗时: {total_duration:.2f}秒")
        logger.info(f"📁 处理文件数: {self.metrics['total_files_processed']}")
        logger.info(f"🔧 总操作数: {self.metrics['total_operations']}")
        logger.info(f"❌ 总错误数: {self.metrics['total_errors']}")
        
        if self.metrics["defects_found"]:
            logger.warning(f"\n⚠️  发现 {len(self.metrics['defects_found'])} 个问题需要解决:")
            for i, defect in enumerate(self.metrics["defects_found"][:20], 1):
                logger.warning(f"\n  {i}. [{defect['phase']}]")
                logger.warning(f"     文件: {defect['file']}")
                logger.warning(f"     问题: {defect['error'][:150]}")
                
            if len(self.metrics["defects_found"]) > 20:
                logger.warning(f"\n  ... 还有 {len(self.metrics['defects_found']) - 20} 个问题")
        else:
            logger.info("\n🎉🎉🎉 完美！未发现任何问题！系统表现极其稳定！")
            
        logger.info("\n" + "=" * 100)
        
    def _record_defect(self, phase: str, file_path: str, error: str):
        """记录发现的问题"""
        self.metrics["defects_found"].append({
            "phase": phase,
            "file": file_path,
            "error": error,
            "time": time.time()
        })
        
    def _record_error_type(self, error_type: str):
        """记录错误类型统计"""
        if error_type not in self.metrics["errors_by_type"]:
            self.metrics["errors_by_type"][error_type] = 0
        self.metrics["errors_by_type"][error_type] += 1
        
    async def run_complete_test(self):
        """运行完整的第八轮终极测试"""
        await self.setup()
        await self.run_phase1_chaos_files_scan()
        await self.run_phase2_long_running_stability()
        await self.run_phase3_concurrent_chaos()
        await self.run_phase4_database_stress()
        await self.print_complete_report()
        
        if self.db:
            await self.db.close()
            
        return self.metrics


if __name__ == "__main__":
    chaos_path = "/tmp/ultimate-chaos-project"
    mega_path = "/workspace/ark-analyzer/mega-test-project"
    
    tester = Round8UltimateChaosTester(chaos_path, mega_path)
    results = asyncio.run(tester.run_complete_test())

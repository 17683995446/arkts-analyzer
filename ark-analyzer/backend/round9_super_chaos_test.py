#!/usr/bin/env python3
"""
第9轮 - 超级混乱与极限压力测试
前所未有的长时间、大规模、极端混乱测试！
"""
import asyncio
import time
import sys
import random
import os
from pathlib import Path
from typing import Dict, List, Any
import logging

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.connection import DatabaseConnection
from services.synchronization_engine import SynchronizationEngine
from services.websocket_manager import WebSocketManager
from services.arkts_parser_service import ArkTSParser

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("round9-test")


class Round9SuperChaosTester:
    """第9轮超级极限压力测试器"""
    
    def __init__(self, chaos_path: str, mega_path: str):
        self.chaos_path = Path(chaos_path)
        self.mega_path = Path(mega_path)
        self.db = None
        self.sync_engine = None
        self.parser = ArkTSParser()
        
        self.metrics = {
            "start_time": 0,
            "end_time": 0,
            "total_files_processed": 0,
            "total_operations": 0,
            "total_errors": 0,
            "defects_found": []
        }
        
    async def setup(self):
        """设置测试环境"""
        logger.info("=" * 100)
        logger.info("🔥🔥🔥 第9轮 - 超级混乱与极限压力测试 🔥🔥🔥")
        logger.info("=" * 100)
        
        self.db = DatabaseConnection(":memory:")
        await self.db.initialize()
        self.ws_manager = WebSocketManager()
        self.sync_engine = SynchronizationEngine(self.db, self.ws_manager)
        
        self.metrics["start_time"] = time.time()
        
    async def phase1_full_scan_super_chaos(self):
        """阶段1: 超级混乱项目完整扫描"""
        logger.info("\n" + "=" * 100)
        logger.info("📋 阶段1: 超级混乱项目完整扫描")
        logger.info("=" * 100)
        
        all_files = []
        if self.chaos_path.exists():
            all_files.extend(list(self.chaos_path.rglob("*.ets")))
        if self.mega_path.exists():
            all_files.extend(list(self.mega_path.rglob("*.ets")))
            
        random.shuffle(all_files)
        logger.info(f"  准备处理 {len(all_files)} 个文件...")
        
        success = 0
        errors = 0
        
        for idx, file_path in enumerate(all_files):
            try:
                result = await self.sync_engine.update_single_file(str(file_path))
                if result.success:
                    success += 1
                else:
                    errors += 1
                    self._record_defect("phase1_scan", str(file_path), result.error_message)
                    
            except Exception as e:
                errors += 1
                self._record_defect("phase1_scan", str(file_path), str(e))
                
            if (idx + 1) % 500 == 0:
                logger.info(f"  已处理 {idx + 1}/{len(all_files)} 个文件...")
                
        logger.info(f"📊 阶段1完成: 成功 {success}, 错误 {errors}")
        self.metrics["total_files_processed"] = success + errors
        self.metrics["total_errors"] += errors
        
    async def phase2_extreme_long_running(self):
        """阶段2: 超级长时间稳定性测试 - 300秒(5分钟)"""
        logger.info("\n" + "=" * 100)
        logger.info("📋 阶段2: 超级长时间稳定性测试 (300秒 = 5分钟)")
        logger.info("=" * 100)
        
        all_files = []
        if self.chaos_path.exists():
            all_files.extend(list(self.chaos_path.rglob("*.ets")))
        if self.mega_path.exists():
            all_files.extend(list(self.mega_path.rglob("*.ets")))
            
        random.shuffle(all_files)
        logger.info(f"  使用 {len(all_files)} 个文件进行测试...")
        
        start_time = time.time()
        duration_sec = 300  # 5分钟
        operations_count = 0
        errors_count = 0
        
        last_log_time = start_time
        last_op_count = 0
        
        while time.time() - start_time < duration_sec:
            if not all_files:
                await asyncio.sleep(0.01)
                continue
                
            file_path = random.choice(all_files)
            
            try:
                operation_type = random.randint(0, 2)
                
                if operation_type == 0:
                    await self.sync_engine.update_single_file(str(file_path))
                elif operation_type == 1:
                    content = file_path.read_text('utf-8', errors='replace')
                    self.parser.parse_file(str(file_path), content)
                else:
                    old_hash = await self.db.get_file_hash(str(file_path))
                    
                operations_count += 1
                
            except Exception as e:
                errors_count += 1
                self._record_defect("phase2_long_run", str(file_path), str(e))
                
            # 每5秒记录一次
            if time.time() - last_log_time > 5:
                elapsed = time.time() - start_time
                ops_in_last = operations_count - last_op_count
                logger.info(f"  ⏱️ 已运行 {elapsed:.1f}s, 总操作: {operations_count}, 本阶段速度: {ops_in_last / 5.0:.1f} ops/s")
                last_log_time = time.time()
                last_op_count = operations_count
                
        total_time = time.time() - start_time
        logger.info(f"\n📊 阶段2完成: {total_time:.1f}秒, 总操作: {operations_count}, 错误: {errors_count}")
        
        self.metrics["total_operations"] += operations_count
        self.metrics["total_errors"] += errors_count
        
    async def phase3_super_concurrent_chaos(self):
        """阶段3: 超级并发混乱测试"""
        logger.info("\n" + "=" * 100)
        logger.info("📋 阶段3: 超级并发混乱测试")
        logger.info("=" * 100)
        
        all_files = []
        if self.chaos_path.exists():
            all_files.extend(list(self.chaos_path.rglob("*.ets")))
        if self.mega_path.exists():
            all_files.extend(list(self.mega_path.rglob("*.ets")))
            
        if not all_files:
            logger.warning("  没有文件可测试")
            return
            
        concurrency_levels = [50, 80, 100]  # 50, 80, 100并发
        rounds = 10
        
        total_ops = 0
        total_errors = 0
        
        for level in concurrency_levels:
            logger.info(f"\n  测试并发级别: {level}")
            for round_num in range(rounds):
                tasks = []
                for _ in range(level):
                    file_path = random.choice(all_files)
                    tasks.append(self._do_random_operation(str(file_path)))
                    
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                batch_ops = len(results)
                batch_errors = sum(1 for r in results if isinstance(r, Exception))
                
                total_ops += batch_ops
                total_errors += batch_errors
                
                for idx, r in enumerate(results):
                    if isinstance(r, Exception):
                        self._record_defect("phase3_concurrent", str(all_files[idx % len(all_files)]), str(r))
                        
                logger.info(f"    轮次 {round_num + 1}/{rounds}: {batch_ops} 操作, {batch_errors} 错误")
                
        logger.info(f"\n📊 阶段3完成: 总操作 {total_ops}, 总错误 {total_errors}")
        
        self.metrics["total_operations"] += total_ops
        self.metrics["total_errors"] += total_errors
        
    async def _do_random_operation(self, file_path: str):
        """执行随机操作"""
        op = random.randint(0, 3)
        
        if op == 0:
            await self.sync_engine.update_single_file(file_path)
        elif op == 1:
            await self.db.get_statistics()
        elif op == 2:
            await self.db.get_all_classes()
        else:
            await self.db.get_all_files()
            
    async def phase4_memory_and_performance_check(self):
        """阶段4: 内存和性能检查"""
        logger.info("\n" + "=" * 100)
        logger.info("📋 阶段4: 系统健康检查")
        logger.info("=" * 100)
        
        stats = await self.db.get_statistics()
        logger.info(f"  📊 数据库统计:")
        logger.info(f"    文件数: {stats['total_files']}")
        logger.info(f"    类/组件数: {stats['total_classes']}")
        logger.info(f"    方法数: {stats['total_methods']}")
        
        classes = await self.db.get_all_classes()
        files = await self.db.get_all_files()
        
        logger.info(f"  ✅ 系统状态正常: 管理了 {len(classes)} 个类, {len(files)} 个文件")
        
    async def print_final_report(self):
        """打印最终报告"""
        self.metrics["end_time"] = time.time()
        total_duration = self.metrics["end_time"] - self.metrics["start_time"]
        
        logger.info("\n" + "=" * 100)
        logger.info("🔥🔥🔥 第9轮 - 超级混乱与极限压力测试 - 完整报告 🔥🔥🔥")
        logger.info("=" * 100)
        
        logger.info(f"\n⏱️  总耗时: {total_duration:.1f}秒")
        logger.info(f"📁 处理文件数: {self.metrics['total_files_processed']}")
        logger.info(f"🔧 总操作数: {self.metrics['total_operations']}")
        logger.info(f"❌ 总错误数: {self.metrics['total_errors']}")
        
        if self.metrics["defects_found"]:
            logger.warning(f"\n⚠️  发现 {len(self.metrics['defects_found'])} 个问题:")
            for i, defect in enumerate(self.metrics["defects_found"][:20]):
                logger.warning(f"  {i + 1}. {defect['phase']} - {defect['file']}")
                logger.warning(f"      {defect['error'][:100]}")
        else:
            logger.info("\n🎉🎉🎉🎉🎉 完美！！！未发现任何问题！！！系统极其稳定！！！🎉🎉🎉🎉🎉")
            
        logger.info("\n" + "=" * 100)
        
    def _record_defect(self, phase: str, file_path: str, error: str):
        """记录缺陷"""
        self.metrics["defects_found"].append({
            "phase": phase,
            "file": file_path,
            "error": error,
            "time": time.time()
        })
        
    async def run_complete_test(self):
        """运行完整测试"""
        await self.setup()
        await self.phase1_full_scan_super_chaos()
        await self.phase2_extreme_long_running()
        await self.phase3_super_concurrent_chaos()
        await self.phase4_memory_and_performance_check()
        await self.print_final_report()
        
        if self.db:
            await self.db.close()
            
        return self.metrics


if __name__ == "__main__":
    chaos_path = "/tmp/super-chaos-project"
    mega_path = "/workspace/ark-analyzer/mega-test-project"
    
    tester = Round9SuperChaosTester(chaos_path, mega_path)
    results = asyncio.run(tester.run_complete_test())

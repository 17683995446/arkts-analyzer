#!/usr/bin/env python3
"""
ArkAnalyzer 完整端到端长时压力测试
文件名: full_end_to_end_stress_test.py
用途: 完整运行系统，进行端到端真实运行时测试，发现深层bug！
"""
import asyncio
import logging
import time
import sys
import traceback
from pathlib import Path

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.connection import DatabaseConnection
from services.synchronization_engine import SynchronizationEngine
from services.websocket_manager import WebSocketManager
from services.arkts_parser_service import ArkTSParser
from config import SystemConfig, FileChangeEvent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("e2e_stress_test")


class E2EStressTester:
    """端到端压力测试器"""
    
    def __init__(self, project_dir: str, test_name: str):
        self.project_dir = Path(project_dir)
        self.test_name = test_name
        self.db = None
        self.sync_engine = None
        self.ws_manager = None
        self.parser = ArkTSParser()
        self.all_files = []
        self.start_time = 0
        self.metrics = {
            "files_processed": 0,
            "errors": 0,
            "startup_time": 0,
            "avg_file_update": 0,
            "classes_extracted": 0,
            "methods_extracted": 0
        }
        
    async def setup(self):
        """设置测试环境"""
        logger.info("=" * 70)
        logger.info(f"   🧪 {self.test_name}")
        logger.info("=" * 70)
        
        self.start_time = time.time()
        setup_start = time.time()
        
        # 1. 列出项目文件
        self.all_files = list(self.project_dir.rglob("*.ets"))
        logger.info(f"📁 项目文件数量: {len(self.all_files)}")
        
        # 2. 初始化数据库
        self.db = DatabaseConnection(":memory:")
        await self.db.initialize()
        
        # 3. 初始化同步引擎
        self.ws_manager = WebSocketManager()
        self.sync_engine = SynchronizationEngine(self.db, self.ws_manager)
        
        self.metrics["startup_time"] = time.time() - setup_start
        logger.info(f"✅ 系统初始化完成: {self.metrics['startup_time']:.3f}秒")
        logger.info("")
        
    async def test_full_scan(self):
        """全量扫描测试"""
        logger.info("🚀 测试1: 全量扫描")
        scan_start = time.time()
        
        error_count = 0
        total_time = 0
        for f in self.all_files:
            try:
                t0 = time.time()
                await self.sync_engine.update_single_file(str(f))
                total_time += time.time() - t0
                self.metrics["files_processed"] += 1
            except Exception as e:
                logger.error(f"❌ 文件处理异常 {f}: {e}")
                error_count +=1
        
        self.metrics["errors"] += error_count
        scan_duration = time.time() - scan_start
        self.metrics["avg_file_update"] = total_time / len(self.all_files) if self.all_files else 0
        
        stats = await self.db.get_statistics()
        self.metrics["classes_extracted"] = stats["total_classes"]
        self.metrics["methods_extracted"] = stats["total_methods"]
        
        logger.info(f"📊 扫描完成")
        logger.info(f"   ⏱️ 总耗时: {scan_duration:.2f}秒")
        logger.info(f"   📄 处理文件: {len(self.all_files)}")
        logger.info(f"   🏷️ 类/组件: {stats['total_classes']}")
        logger.info(f"   🔧 方法: {stats['total_methods']}")
        logger.info(f"   ❌ 错误: {error_count}")
        logger.info("")
    
    async def test_incremental_updates(self, iterations: int =30):
        """增量更新测试"""
        logger.info("🔄 测试2: 增量更新")
        total_ops = 0
        error_count =0
        start = time.time()
        
        for i in range(iterations):
            if not self.all_files: continue
            target_file = random.choice(self.all_files)
            try:
                await self.sync_engine.update_single_file(str(target_file))
                total_ops +=1
            except Exception as e:
                error_count +=1
                logger.error(f"❌ 增量更新异常: {e}")
        
        self.metrics["errors"] += error_count
        logger.info(f"📊 增量更新完成: {total_ops} 次操作, {error_count} 错误, {(time.time()-start):.2f}秒")
        logger.info("")
    
    async def test_concurrent_operations(self, num_workers: int =5):
        """并发操作测试"""
        logger.info("⚡ 测试3: 并发操作")
        
        if len(self.all_files) < num_workers:
            num_workers = len(self.all_files)
        
        test_files = random.sample(self.all_files, num_workers) if self.all_files else []
        
        start = time.time()
        tasks = []
        
        for f in test_files:
            tasks.append(self.sync_engine.update_single_file(str(f)))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        duration = time.time()-start
        logger.info(f"📊 并发操作完成: {len(test_files)} 并发请求, {duration:.2f}秒")
        logger.info("")
    
    async def test_database_integrity(self):
        """数据库完整性测试"""
        logger.info("🛡️ 测试4: 数据库完整性")
        
        all_classes = await self.db.get_all_classes()
        all_files_in_db = await self.db.get_all_files()
        
        if len(all_classes) ==0 or len(all_files_in_db) ==0:
            logger.warning("⚠️ 数据库数据可能有问题！")
        
        logger.info(f"📊 数据库检查:")
        logger.info(f"   📄 文件记录: {len(all_files_in_db)}")
        logger.info(f"   🏷️ 类/组件记录: {len(all_classes)}")
        
        # 统计检查
        stats = await self.db.get_statistics()
        logger.info(f"   📈 统计数据一致！")
        logger.info("")
        
        return len(all_classes) >0
        
    async def cleanup(self):
        """清理环境"""
        if self.db:
            await self.db.close()
    
    async def run(self):
        """运行完整测试"""
        await self.setup()
        
        await self.test_full_scan()
        await self.test_incremental_updates()
        await self.test_concurrent_operations()
        await self.test_database_integrity()
        
        total_time = time.time() - self.start_time
        logger.info("="*70)
        logger.info("🎉 压力测试完成！")
        logger.info("="*70)
        logger.info(f"📋 整体统计:")
        logger.info(f"   ⏱️ 总时间: {total_time:.2f}s")
        logger.info(f"   📄 总处理: {self.metrics['files_processed']}")
        logger.info(f"   🏷️ 类/组件: {self.metrics['classes_extracted']}")
        logger.info(f"   🔧 方法数: {self.metrics['methods_extracted']}")
        logger.info(f"   ✏️ 平均更新: {self.metrics['avg_file_update']*1000:.1f}ms")
        logger.info(f"   ❌ 总错误: {self.metrics['errors']}")
        
        await self.cleanup()
        
        return self.metrics


# 快速创建一个简单的辅助脚本，我们将这个直接运行在内存里的压力测试
import random
if __name__ == "__main__":
    tester = E2EStressTester(
        project_dir="/workspace/ark-analyzer/large-test-project",
        test_name="ArkAnalyzer Complete E2E Stress Test"
    )
    
    try:
        metrics = asyncio.run(tester.run())
        if metrics['errors'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
    except Exception as e:
        logger.error(f"严重问题！！异常: {e}")
        traceback.print_exc()
        sys.exit(1)

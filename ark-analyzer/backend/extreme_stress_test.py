#!/usr/bin/env python3
"""
极端压力测试 - 第四轮
文件名: extreme_stress_test.py
用途: 进行极端压力、长时间稳定性、超大项目测试
"""
import asyncio
import time
import logging
import sys
import random
import traceback
import os
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.connection import DatabaseConnection
from services.synchronization_engine import SynchronizationEngine
from services.websocket_manager import WebSocketManager
from services.arkts_parser_service import ArkTSParser
from utils.hash_util import HashCalculator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("extreme_stress_test")


class ExtremeStressTest:
    """极端压力测试"""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.db = None
        self.sync_engine = None
        self.parser = ArkTSParser()
        self.test_files = []
        self.metrics = {
            "start_time": 0,
            "end_time": 0,
            "total_operations": 0,
            "total_errors": 0,
            "total_files": 0,
            "max_memory_mb": 0,
            "defects": []
        }
        
    async def setup(self):
        """初始化测试环境"""
        logger.info("=" * 80)
        logger.info("          🔬 第四轮 - 极端压力与稳定性测试")
        logger.info("=" * 80)
        
        self.test_files = list(self.project_dir.rglob("*.ets"))
        self.metrics["total_files"] = len(self.test_files)
        logger.info(f"📁 测试文件数: {self.metrics['total_files']}")
        
        self.db = DatabaseConnection("/tmp/extreme_test_db.sqlite")
        await self.db.initialize()
        self.ws_manager = WebSocketManager()
        self.sync_engine = SynchronizationEngine(self.db, self.ws_manager)
        
        self.metrics["start_time"] = time.time()
        logger.info("✅ 系统初始化完成")
        
    async def test_1_full_scan(self):
        """测试1: 全量扫描所有文件"""
        logger.info("\n" + "="*80)
        logger.info("📋 测试 1: 全量扫描所有文件")
        logger.info("="*80)
        
        errors = 0
        start = time.time()
        
        for i, file_path in enumerate(self.test_files, 1):
            try:
                await self.sync_engine.update_single_file(str(file_path))
                if i % 50 == 0:
                    elapsed = time.time() - start
                    logger.info(f"  进度: {i}/{len(self.test_files)}, 耗时: {elapsed:.2f}s")
            except Exception as e:
                errors += 1
                self._record_defect("full_scan", str(file_path), str(e), "high")
        
        duration = time.time() - start
        stats = await self.db.get_statistics()
        
        logger.info(f"\n✅ 扫描完成: {duration:.2f}s, 错误: {errors}")
        logger.info(f"   统计: {stats}")
        
        self.metrics["total_operations"] += len(self.test_files)
        self.metrics["total_errors"] += errors
        
        return stats
        
    async def test_2_rapid_incremental_updates(self):
        """测试2: 快速增量更新（模拟真实开发修改）"""
        logger.info("\n" + "="*80)
        logger.info("📋 测试 2: 快速增量更新测试")
        logger.info("="*80)
        
        iterations = 1000  # 极端多的迭代
        errors = 0
        start = time.time()
        
        for i in range(iterations):
            if not self.test_files:
                continue
                
            file_path = random.choice(self.test_files)
            try:
                await self.sync_engine.update_single_file(str(file_path))
                
                if (i + 1) % 200 == 0:
                    elapsed = time.time() - start
                    speed = (i + 1) / elapsed
                    logger.info(f"  进度: {i+1}/{iterations}, 速度: {speed:.1f} op/s, 累计: {elapsed:.2f}s")
                    
            except Exception as e:
                errors += 1
                self._record_defect("incremental", str(file_path), str(e), "medium")
        
        duration = time.time() - start
        logger.info(f"\n✅ 增量更新完成: {duration:.2f}s, 操作: {iterations}, 错误: {errors}")
        logger.info(f"   平均: {(duration/iterations*1000):.2f}ms/op")
        
        self.metrics["total_operations"] += iterations
        self.metrics["total_errors"] += errors
        
    async def test_3_concurrent_bombardment(self):
        """测试3: 并发轰炸（极端并发）"""
        logger.info("\n" + "="*80)
        logger.info("📋 测试 3: 极端并发轰炸测试")
        logger.info("="*80)
        
        concurrency = 50  # 极端并发数
        batches = 20
        total_errors = 0
        total_ops = 0
        start = time.time()
        
        for batch in range(batches):
            # 随机选择文件
            batch_files = random.choices(self.test_files, k=concurrency) if self.test_files else []
            total_ops += len(batch_files)
            
            if not batch_files:
                continue
                
            tasks = []
            for file_path in batch_files:
                tasks.append(self.sync_engine.update_single_file(str(file_path)))
                
            # 并发执行
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            errors_in_batch = sum(1 for r in results if isinstance(r, Exception))
            total_errors += errors_in_batch
            
            if errors_in_batch > 0:
                for idx, r in enumerate(results):
                    if isinstance(r, Exception):
                        self._record_defect("concurrent_bomb", str(batch_files[idx]), str(r), "high")
            
            logger.info(f"  批次 {batch+1}/{batches}: 并发数 {len(batch_files)}, 错误: {errors_in_batch}")
        
        duration = time.time() - start
        logger.info(f"\n✅ 并发轰炸完成: {duration:.2f}s, 总操作: {total_ops}, 总错误: {total_errors}")
        
        self.metrics["total_operations"] += total_ops
        self.metrics["total_errors"] += total_errors
        
    async def test_4_long_duration_stability(self):
        """测试4: 长时间稳定性（持续运行）"""
        logger.info("\n" + "="*80)
        logger.info("📋 测试 4: 长时间稳定性测试")
        logger.info("="*80)
        
        duration_seconds = 30  # 30秒持续运行
        errors = 0
        start_time = time.time()
        operations = 0
        
        logger.info(f"   开始长时间运行测试，预计 {duration_seconds} 秒...")
        
        while time.time() - start_time < duration_seconds:
            if not self.test_files:
                await asyncio.sleep(0.1)
                continue
                
            file_path = random.choice(self.test_files)
            
            try:
                await self.sync_engine.update_single_file(str(file_path))
                operations += 1
            except Exception as e:
                errors += 1
                self._record_defect("stability", str(file_path), str(e), "critical")
            
            # 短暂休眠，避免过于密集
            await asyncio.sleep(0.01)
        
        actual_duration = time.time() - start_time
        logger.info(f"\n✅ 稳定性测试完成: 实际 {actual_duration:.2f}s, 操作: {operations}, 错误: {errors}")
        logger.info(f"   平均速度: {(operations/actual_duration):.2f} op/s")
        
        self.metrics["total_operations"] += operations
        self.metrics["total_errors"] += errors
        
    async def test_5_extreme_edge_cases(self):
        """测试5: 极端边缘情况"""
        logger.info("\n" + "="*80)
        logger.info("📋 测试 5: 极端边缘情况")
        logger.info("="*80)
        
        temp_dir = Path("/tmp/extreme_edge_cases")
        temp_dir.mkdir(exist_ok=True)
        
        edge_cases = self._generate_extreme_edge_cases(temp_dir)
        errors = 0
        
        for case_name, file_path in edge_cases.items():
            try:
                content = file_path.read_text(encoding="utf-8")
                parsed = self.parser.parse_file(str(file_path), content)
                logger.info(f"  ✓ {case_name}: 解析到 {len(parsed.classes)} 个类")
            except Exception as e:
                errors += 1
                self._record_defect("edge_case", str(file_path), str(e), "medium")
                logger.warning(f"  ✗ {case_name}: {e}")
        
        logger.info(f"\n✅ 边缘测试完成: 错误 {errors}")
        
        self.metrics["total_errors"] += errors
        
    def _generate_extreme_edge_cases(self, temp_dir: Path) -> Dict[str, Path]:
        """生成极端边缘案例"""
        edge_cases = {}
        
        # 1. 超大文件
        huge_content = "class HugeClass {\n"
        for i in range(500):
            huge_content += f"  method_{i}() {{ /* 这是一个很长很长的方法，用于测试性能 */ }}\n"
        huge_content += "}\n"
        huge_path = temp_dir / "huge_file.ets"
        huge_path.write_text(huge_content, encoding="utf-8")
        edge_cases["超大文件(500方法)"] = huge_path
        
        # 2. 超深嵌套
        deep_nesting = "class Level1 {\n"
        for i in range(2, 11):
            deep_nesting += f"  class Level{i} {{\n"
        deep_nesting += "    method() {}\n"
        for i in range(10, 1, -1):
            deep_nesting += "  }\n"
        deep_nesting += "}\n"
        deep_path = temp_dir / "deep_nesting.ets"
        deep_path.write_text(deep_nesting, encoding="utf-8")
        edge_cases["超深嵌套(10层)"] = deep_path
        
        # 3. 大量装饰器
        many_decorators = "@Component\n@Entry\n@ObservedV2\n"
        many_decorators += "@Builder\n@BuilderParam\n"
        many_decorators += "struct MultiDecorated {\n"
        many_decorators += "  @State @Prop @Link @Watch('change') value: string = ''\n"
        many_decorators += "  build() {}\n"
        many_decorators += "}\n"
        decor_path = temp_dir / "many_decorators.ets"
        decor_path.write_text(many_decorators, encoding="utf-8")
        edge_cases["大量装饰器"] = decor_path
        
        # 4. 混合UTF-8字符
        unicode_content = "class UnicodeClass {\n"
        unicode_content += "  中文方法() {}\n"
        unicode_content += "  emoji_🔧() {}\n"
        unicode_content += "  mixed_方法_123() {}\n"
        unicode_content += "}\n"
        unicode_path = temp_dir / "unicode.ets"
        unicode_path.write_text(unicode_content, encoding="utf-8")
        edge_cases["复杂UTF-8字符"] = unicode_path
        
        # 5. 超长方法名
        long_name = "class LongNames {\n"
        long_name += "  this_is_an_extremely_long_method_name_that_should_still_work_properly() {}\n"
        long_name += "}\n"
        long_path = temp_dir / "long_names.ets"
        long_path.write_text(long_name, encoding="utf-8")
        edge_cases["超长标识符"] = long_path
        
        return edge_cases
        
    def _record_defect(self, test_type: str, location: str, error: str, severity: str):
        """记录缺陷"""
        self.metrics["defects"].append({
            "test": test_type,
            "location": location,
            "error": error,
            "severity": severity,
            "timestamp": time.time()
        })
        
    async def print_summary(self):
        """打印测试总结"""
        self.metrics["end_time"] = time.time()
        total_time = self.metrics["end_time"] - self.metrics["start_time"]
        
        logger.info("\n" + "=" * 80)
        logger.info("                      📊 极端压力测试总结报告")
        logger.info("=" * 80)
        
        logger.info("\n⏱️  总运行时间: {:.2f}s".format(total_time))
        logger.info("📂 处理文件数: {}".format(self.metrics["total_files"]))
        logger.info("🔧 总操作数: {}".format(self.metrics["total_operations"]))
        logger.info("❌ 总错误数: {}".format(self.metrics["total_errors"]))
        logger.info("⚡ 平均操作: {:.2f}ms".format((total_time / max(self.metrics["total_operations"], 1)) * 1000))
        
        if self.metrics["defects"]:
            logger.warning("\n⚠️  发现 {} 个问题:".format(len(self.metrics["defects"])))
            for i, defect in enumerate(self.metrics["defects"][:10], 1):
                logger.warning(f"  {i}. [{defect['severity']}] {defect['test']}: {defect['location']}")
                logger.warning(f"     {defect['error']}")
        else:
            logger.info("\n🎉 **完美！未发现任何缺陷！**")
            
        logger.info("\n" + "=" * 80)
        
    async def run_all(self):
        """运行所有测试"""
        await self.setup()
        await self.test_1_full_scan()
        await self.test_2_rapid_incremental_updates()
        await self.test_3_concurrent_bombardment()
        await self.test_4_long_duration_stability()
        await self.test_5_extreme_edge_cases()
        await self.print_summary()
        if self.db:
            await self.db.close()
        

if __name__ == "__main__":
    project_dir = "/workspace/ark-analyzer/large-test-project"
    tester = ExtremeStressTest(project_dir)
    asyncio.run(tester.run_all())

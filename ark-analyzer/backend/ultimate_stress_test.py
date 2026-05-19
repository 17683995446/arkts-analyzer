#!/usr/bin/env python3
"""
第五轮终极压力测试 - 超大规模、超长时间、真实开发工作流
文件名: ultimate_stress_test.py
"""
import asyncio
import time
import logging
import sys
import random
import traceback
import gc
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
logger = logging.getLogger("ultimate_test")


class UltimateStressTest:
    """终极压力测试"""
    
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
            "defects": [],
            "phases": []
        }
        self.class_count = 0
        self.method_count = 0
        
    async def setup(self):
        """初始化测试环境"""
        logger.info("=" * 100)
        logger.info("       🎯 第五轮 - 终极压力测试（超大规模）")
        logger.info("=" * 100)
        
        self.test_files = list(self.project_dir.rglob("*.ets"))
        self.metrics["total_files"] = len(self.test_files)
        
        logger.info(f"📂 测试文件数: {self.metrics['total_files']}")
        logger.info(f"🗂️  项目目录: {self.project_dir}")
        
        self.db = DatabaseConnection("/tmp/ultimate_test_db.sqlite")
        await self.db.initialize()
        self.ws_manager = WebSocketManager()
        self.sync_engine = SynchronizationEngine(self.db, self.ws_manager)
        
        self.metrics["start_time"] = time.time()
        logger.info("✅ 系统初始化完成")
        
    async def test_1_mega_scan(self):
        """测试1 - 超大规模全量扫描（1000文件）"""
        logger.info("\n" + "=" * 100)
        logger.info("📋 测试 1 - 超大规模全量扫描（1000个文件）")
        logger.info("=" * 100)
        
        errors = 0
        start = time.time()
        
        for i, file_path in enumerate(self.test_files, 1):
            try:
                await self.sync_engine.update_single_file(str(file_path))
                
                if i % 100 == 0:
                    elapsed = time.time() - start
                    logger.info(f"   进度: {i}/{len(self.test_files)} 个文件，耗时: {elapsed:.2f}秒")
                    
            except Exception as e:
                errors += 1
                self._record_defect("mega_scan", str(file_path), str(e), "high")
        
        duration = time.time() - start
        stats = await self.db.get_statistics()
        self.class_count = stats.get("total_classes", 0)
        self.method_count = stats.get("total_methods", 0)
        
        logger.info(f"\n✅ 超大规模扫描完成: {duration:.2f}秒，错误: {errors}")
        logger.info(f"   解析结果: {self.class_count} 个类/struct，{self.method_count} 个方法")
        logger.info(f"   平均每个文件耗时: {(duration / len(self.test_files) * 1000):.2f}ms")
        
        self.metrics["total_operations"] += len(self.test_files)
        self.metrics["total_errors"] += errors
        self.metrics["phases"].append({"name": "超大规模扫描", "time": duration, "errors": errors})
        
        return stats
        
    async def test_2_rapid_updates(self):
        """测试2 - 超快速增量更新（5000次操作）"""
        logger.info("\n" + "=" * 100)
        logger.info("📋 测试 2 - 超快速增量更新（5000次操作）")
        logger.info("=" * 100)
        
        iterations = 5000
        errors = 0
        start = time.time()
        
        for i in range(iterations):
            if not self.test_files:
                continue
                
            file_path = random.choice(self.test_files)
            try:
                await self.sync_engine.update_single_file(str(file_path))
                
                if (i + 1) % 500 == 0:
                    elapsed = time.time() - start
                    speed = (i + 1) / elapsed
                    logger.info(f"   进度: {i+1}/{iterations}，速度: {speed:.1f} op/s，累计: {elapsed:.2f}秒")
                    
            except Exception as e:
                errors += 1
                self._record_defect("rapid_updates", str(file_path), str(e), "medium")
        
        duration = time.time() - start
        logger.info(f"\n✅ 超快速更新完成: {duration:.2f}秒，操作: {iterations}，错误: {errors}")
        logger.info(f"   平均操作耗时: {(duration / iterations * 1000):.2f}ms")
        
        self.metrics["total_operations"] += iterations
        self.metrics["total_errors"] += errors
        self.metrics["phases"].append({"name": "超快速更新", "time": duration, "errors": errors})
        
    async def test_3_extreme_concurrency(self):
        """测试3 - 极端并发（100并发 × 20批 = 2000次）"""
        logger.info("\n" + "=" * 100)
        logger.info("📋 测试 3 - 极端并发轰炸（100并发 × 20批 = 2000次）")
        logger.info("=" * 100)
        
        concurrency = 100
        batches = 20
        total_errors = 0
        total_ops = 0
        start = time.time()
        
        for batch_idx in range(batches):
            batch_files = random.choices(self.test_files, k=concurrency)
            total_ops += len(batch_files)
            
            if not batch_files:
                continue
                
            tasks = [self.sync_engine.update_single_file(str(f)) for f in batch_files]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            batch_errors = sum(1 for r in results if isinstance(r, Exception))
            total_errors += batch_errors
            
            if batch_errors > 0:
                for idx, r in enumerate(results):
                    if isinstance(r, Exception):
                        self._record_defect("extreme_concurrency", str(batch_files[idx]), str(r), "high")
            
            logger.info(f"   批次 {batch_idx+1}/{batches}: {len(batch_files)} 并发，错误: {batch_errors}")
        
        duration = time.time() - start
        logger.info(f"\n✅ 极端并发完成: {duration:.2f}秒，总操作: {total_ops}，总错误: {total_errors}")
        
        self.metrics["total_operations"] += total_ops
        self.metrics["total_errors"] += total_errors
        self.metrics["phases"].append({"name": "极端并发", "time": duration, "errors": total_errors})
        
    async def test_4_long_stability(self):
        """测试4 - 长时间稳定性（60秒）"""
        logger.info("\n" + "=" * 100)
        logger.info("📋 测试 4 - 长时间稳定性（60秒持续运行）")
        logger.info("=" * 100)
        
        duration_sec = 60
        errors = 0
        start_time = time.time()
        operations = 0
        
        logger.info(f"   开始持续运行测试，预计 {duration_sec} 秒...")
        
        while time.time() - start_time < duration_sec:
            if not self.test_files:
                await asyncio.sleep(0.01)
                continue
                
            file_path = random.choice(self.test_files)
            
            try:
                await self.sync_engine.update_single_file(str(file_path))
                operations += 1
                
                if operations % 500 == 0:
                    elapsed = time.time() - start_time
                    logger.info(f"   当前运行: {elapsed:.0f}/{duration_sec}秒，已完成 {operations} 次操作")
                    
            except Exception as e:
                errors += 1
                self._record_defect("long_stability", str(file_path), str(e), "critical")
            
            await asyncio.sleep(0.005)
        
        actual_duration = time.time() - start_time
        logger.info(f"\n✅ 稳定性测试完成: 实际 {actual_duration:.2f}秒，操作: {operations}，错误: {errors}")
        logger.info(f"   平均速度: {(operations / actual_duration):.2f} op/s")
        
        self.metrics["total_operations"] += operations
        self.metrics["total_errors"] += errors
        self.metrics["phases"].append({"name": "长时间稳定", "time": actual_duration, "errors": errors})
        
    async def test_5_edge_cases(self):
        """测试5 - 终极边缘情况"""
        logger.info("\n" + "=" * 100)
        logger.info("📋 测试 5 - 终极边缘情况")
        logger.info("=" * 100)
        
        temp_dir = Path("/tmp/ultimate_edge_cases")
        temp_dir.mkdir(exist_ok=True)
        
        edge_cases = self._generate_edge_cases(temp_dir)
        errors = 0
        
        for name, file_path in edge_cases.items():
            try:
                content = file_path.read_text(encoding="utf-8")
                parsed = self.parser.parse_file(str(file_path), content)
                logger.info(f"   ✓ {name}: {len(parsed.classes)} 个类")
            except Exception as e:
                errors += 1
                self._record_defect("edge_case", str(file_path), str(e), "medium")
                logger.warning(f"   ✗ {name}: {e}")
        
        logger.info(f"\n✅ 边缘测试完成: 错误 {errors}")
        self.metrics["total_errors"] += errors
        self.metrics["phases"].append({"name": "边缘情况", "time": 0, "errors": errors})
        
    def _generate_edge_cases(self, temp_dir: Path) -> Dict[str, Path]:
        """生成终极边缘案例"""
        cases = {}
        
        huge_content = "class MegaClass {\n"
        for i in range(1000):
            huge_content += f"  method{i}() {{}}\n"
        huge_content += "}\n"
        huge_path = temp_dir / "huge_1000_methods.ets"
        huge_path.write_text(huge_content, encoding="utf-8")
        cases["巨型类(1000方法)"] = huge_path
        
        nested_content = "class L1 {"
        for i in range(2, 21):
            nested_content += f"  class L{i} {{"
        nested_content += "    deepMethod() {}"
        for i in range(20, 0, -1):
            nested_content += "  }"
        nested_content += "}"
        nested_path = temp_dir / "deep_nested_20.ets"
        nested_path.write_text(nested_content, encoding="utf-8")
        cases["超深嵌套(20层)"] = nested_path
        
        unicode_content = """struct 测试组件 {
  @State 中文属性: string = '你好'
  build() { Text('测试') }
  emojiMethod🏆() {}
}
"""
        unicode_path = temp_dir / "unicode_chars.ets"
        unicode_path.write_text(unicode_content, encoding="utf-8")
        cases["复杂Unicode"] = unicode_path
        
        empty_path = temp_dir / "empty.ets"
        empty_path.write_text("", encoding="utf-8")
        cases["空文件"] = empty_path
        
        comment_content = """/* This is a
multi-line comment */
// Single line comment
class CommentedClass {
  method() {}
}
"""
        comment_path = temp_dir / "comments.ets"
        comment_path.write_text(comment_content, encoding="utf-8")
        cases["全注释文件"] = comment_path
        
        return cases
        
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
        total_duration = self.metrics["end_time"] - self.metrics["start_time"]
        
        logger.info("\n" + "=" * 100)
        logger.info("                    📊 第五轮终极压力测试总结报告")
        logger.info("=" * 100)
        
        logger.info(f"\n📈 总体统计:")
        logger.info(f"   总运行时间: {total_duration:.2f}秒")
        logger.info(f"   处理文件数: {self.metrics['total_files']}")
        logger.info(f"   总操作数: {self.metrics['total_operations']}")
        logger.info(f"   总错误数: {self.metrics['total_errors']}")
        logger.info(f"   平均操作: {(total_duration / max(self.metrics['total_operations'], 1) * 1000):.2f}ms")
        
        logger.info(f"\n📋 各阶段详细:")
        for phase in self.metrics["phases"]:
            logger.info(f"   - {phase['name']}: {phase.get('time', 0):.2f}秒，错误: {phase['errors']}")
        
        if self.metrics["defects"]:
            logger.warning(f"\n⚠️  发现 {len(self.metrics['defects'])} 个问题:")
            for i, defect in enumerate(self.metrics["defects"][:10], 1):
                logger.warning(f"   {i}. [{defect['severity']}] {defect['test']} - {defect.get('location', 'N/A')}")
                logger.warning(f"      {defect['error']}")
        else:
            logger.info("\n🎉🎉🎉 **完美！未发现任何缺陷！系统表现100%完美！**")
        
        logger.info("\n" + "=" * 100)
        
    async def run_all(self):
        """运行所有终极测试"""
        await self.setup()
        await self.test_1_mega_scan()
        await self.test_2_rapid_updates()
        await self.test_3_extreme_concurrency()
        await self.test_4_long_stability()
        await self.test_5_edge_cases()
        await self.print_summary()
        if self.db:
            await self.db.close()


if __name__ == "__main__":
    test_project = "/workspace/ark-analyzer/mega-test-project"
    tester = UltimateStressTest(test_project)
    asyncio.run(tester.run_all())

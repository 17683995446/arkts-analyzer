#!/usr/bin/env python3
"""
多轮并发压力测试 - 第三轮深度测试
文件名: multi_round_stress_test.py
用途: 进行多轮、复杂、真实的压力测试，发现深层缺陷！
"""
import asyncio
import time
import logging
import sys
import random
import traceback
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
logger = logging.getLogger("multi_stress_test")


class MultiRoundStressTest:
    """多轮压力测试"""
    
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.db = None
        self.sync_engine = None
        self.parser = ArkTSParser()
        self.test_files = []
        self.round_results = []
        self.total_metrics = {
            "total_operations": 0,
            "total_errors": 0,
            "total_time": 0,
            "peak_memory_mb": 0,
            "defects_found": []
        }
        
    async def setup(self):
        """初始化测试环境"""
        logger.info("=" * 70)
        logger.info("       🔬 第三轮深度压力测试 - 多轮并发")
        logger.info("=" * 70)
        
        self.test_files = list(self.project_dir.rglob("*.ets"))[:100]
        logger.info(f"📁 测试文件数: {len(self.test_files)}")
        
        self.db = DatabaseConnection(":memory:")
        await self.db.initialize()
        self.ws_manager = WebSocketManager()
        self.sync_engine = SynchronizationEngine(self.db, self.ws_manager)
        
        logger.info("✅ 系统初始化完成")
    
    async def round_1_full_scan(self):
        """第一轮: 全量扫描"""
        logger.info("\n" + "="*70)
        logger.info("📋 第一轮: 全量扫描测试")
        logger.info("="*70)
        
        start_time = time.time()
        errors = 0
        
        for f in self.test_files:
            try:
                await self.sync_engine.update_single_file(str(f))
            except Exception as e:
                errors += 1
                self.total_metrics["defects_found"].append({
                    "round": 1,
                    "type": "scan_error",
                    "file": str(f),
                    "error": str(e),
                    "severity": "high"
                })
        
        duration = time.time() - start_time
        stats = await self.db.get_statistics()
        
        result = {
            "round": 1,
            "name": "全量扫描",
            "duration": duration,
            "errors": errors,
            "files_processed": len(self.test_files),
            "classes": stats["total_classes"],
            "methods": stats["total_methods"]
        }
        
        self.round_results.append(result)
        self.total_metrics["total_operations"] += len(self.test_files)
        self.total_metrics["total_errors"] += errors
        self.total_metrics["total_time"] += duration
        
        logger.info(f"✅ 第一轮完成: {duration:.2f}s, {errors} 错误")
        return result
    
    async def round_2_incremental_updates(self):
        """第二轮: 增量更新"""
        logger.info("\n" + "="*70)
        logger.info("📋 第二轮: 增量更新测试")
        logger.info("="*70)
        
        start_time = time.time()
        iterations = 50
        errors = 0
        
        for i in range(iterations):
            if not self.test_files:
                break
            file = random.choice(self.test_files)
            try:
                await self.sync_engine.update_single_file(str(file))
            except Exception as e:
                errors += 1
                self.total_metrics["defects_found"].append({
                    "round": 2,
                    "type": "incremental_error",
                    "file": str(file),
                    "error": str(e),
                    "severity": "medium"
                })
        
        duration = time.time() - start_time
        result = {
            "round": 2,
            "name": "增量更新",
            "duration": duration,
            "errors": errors,
            "operations": iterations
        }
        
        self.round_results.append(result)
        self.total_metrics["total_operations"] += iterations
        self.total_metrics["total_errors"] += errors
        self.total_metrics["total_time"] += duration
        
        logger.info(f"✅ 第二轮完成: {duration:.2f}s, {errors} 错误")
        return result
    
    async def round_3_concurrent_operations(self):
        """第三轮: 并发操作"""
        logger.info("\n" + "="*70)
        logger.info("📋 第三轮: 并发操作测试")
        logger.info("="*70)
        
        test_sets = [
            self.test_files[:20],
            self.test_files[20:40],
            self.test_files[40:60]
        ]
        
        start_time = time.time()
        total_errors = 0
        
        for batch_idx, batch in enumerate(test_sets, 1):
            tasks = [self.sync_engine.update_single_file(str(f)) for f in batch]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            errors = sum(1 for r in results if isinstance(r, Exception))
            total_errors += errors
            
            if errors > 0:
                for r in results:
                    if isinstance(r, Exception):
                        self.total_metrics["defects_found"].append({
                            "round": 3,
                            "type": "concurrent_error",
                            "error": str(r),
                            "severity": "high"
                        })
            
            logger.info(f"  批次 {batch_idx}: {len(batch)} 并发, {errors} 错误")
        
        duration = time.time() - start_time
        result = {
            "round": 3,
            "name": "并发操作",
            "duration": duration,
            "errors": total_errors,
            "concurrent_batches": len(test_sets)
        }
        
        self.round_results.append(result)
        self.total_metrics["total_operations"] += sum(len(b) for b in test_sets)
        self.total_metrics["total_errors"] += total_errors
        self.total_metrics["total_time"] += duration
        
        logger.info(f"✅ 第三轮完成: {duration:.2f}s, {total_errors} 错误")
        return result
    
    async def round_4_database_integrity(self):
        """第四轮: 数据库完整性"""
        logger.info("\n" + "="*70)
        logger.info("📋 第四轮: 数据库完整性测试")
        logger.info("="*70)
        
        errors = 0
        
        try:
            stats = await self.db.get_statistics()
            logger.info(f"  统计信息: {stats}")
            
            classes = await self.db.get_all_classes()
            files = await self.db.get_all_files()
            
            logger.info(f"  类记录: {len(classes)}")
            logger.info(f"  文件记录: {len(files)}")
            
            if len(classes) == 0 or len(files) == 0:
                errors += 1
                self.total_metrics["defects_found"].append({
                    "round": 4,
                    "type": "integrity_error",
                    "error": "数据库为空",
                    "severity": "critical"
                })
            
        except Exception as e:
            errors += 1
            self.total_metrics["defects_found"].append({
                "round": 4,
                "type": "integrity_error",
                "error": str(e),
                "severity": "critical"
            })
        
        result = {
            "round": 4,
            "name": "数据库完整性",
            "duration": 0,
            "errors": errors
        }
        
        self.round_results.append(result)
        self.total_metrics["total_errors"] += errors
        
        logger.info(f"✅ 第四轮完成: {errors} 错误")
        return result
    
    async def round_5_hash_consistency(self):
        """第五轮: 哈希一致性测试"""
        logger.info("\n" + "="*70)
        logger.info("📋 第五轮: 哈希一致性测试")
        logger.info("="*70)
        
        errors = 0
        test_sample = self.test_files[:20] if self.test_files else []
        
        for f in test_sample:
            try:
                content = f.read_text(encoding="utf-8")
                hash1 = HashCalculator.calculate_md5(content)
                hash2 = HashCalculator.calculate_md5(content)
                
                if hash1 != hash2:
                    errors += 1
                    self.total_metrics["defects_found"].append({
                        "round": 5,
                        "type": "hash_inconsistency",
                        "file": str(f),
                        "error": "哈希结果不一致",
                        "severity": "low"
                    })
                    
            except Exception as e:
                errors += 1
                self.total_metrics["defects_found"].append({
                    "round": 5,
                    "type": "hash_error",
                    "file": str(f),
                    "error": str(e),
                    "severity": "medium"
                })
        
        result = {
            "round": 5,
            "name": "哈希一致性",
            "duration": 0,
            "errors": errors,
            "tested_files": len(test_sample)
        }
        
        self.round_results.append(result)
        self.total_metrics["total_errors"] += errors
        
        logger.info(f"✅ 第五轮完成: {errors} 错误")
        return result
    
    async def round_6_parser_edge_cases(self):
        """第六轮: 解析器边界情况"""
        logger.info("\n" + "="*70)
        logger.info("📋 第六轮: 解析器边界测试")
        logger.info("="*70)
        
        edge_cases = [
            ("empty.ets", ""),
            ("comments.ets", "// test\n/* block */"),
            ("spaces.ets", "   \n\n   \n"),
            ("unicode.ets", "struct 测试类 {\n  @State name: string = '中文'\n}"),
            ("special_chars.ets", "class Test$123 {\n  prop@name: number = 123\n}"),
            ("deep_nesting.ets", "class A { class B { class C { method1() {} } } }"),
        ]
        
        temp_dir = Path("/tmp/ark_edge_test")
        temp_dir.mkdir(exist_ok=True)
        
        errors = 0
        
        for filename, content in edge_cases:
            try:
                file_path = temp_dir / filename
                file_path.write_text(content, encoding="utf-8")
                parsed = self.parser.parse_file(str(file_path), content)
                logger.info(f"  ✓ {filename}: {len(parsed.classes)} classes")
            except Exception as e:
                errors += 1
                self.total_metrics["defects_found"].append({
                    "round": 6,
                    "type": "parser_edge_case",
                    "file": filename,
                    "error": str(e),
                    "severity": "medium"
                })
                logger.error(f"  ✗ {filename}: {e}")
        
        result = {
            "round": 6,
            "name": "解析器边界",
            "duration": 0,
            "errors": errors,
            "edge_cases": len(edge_cases)
        }
        
        self.round_results.append(result)
        self.total_metrics["total_errors"] += errors
        
        logger.info(f"✅ 第六轮完成: {errors} 错误")
        return result
    
    async def run_all_rounds(self):
        """运行所有测试轮次"""
        try:
            await self.setup()
            
            await self.round_1_full_scan()
            await self.round_2_incremental_updates()
            await self.round_3_concurrent_operations()
            await self.round_4_database_integrity()
            await self.round_5_hash_consistency()
            await self.round_6_parser_edge_cases()
            
            await self.print_summary()
            
        except Exception as e:
            logger.error(f"严重问题: {e}")
            traceback.print_exc()
        finally:
            if self.db:
                await self.db.close()
    
    async def print_summary(self):
        """打印测试总结"""
        logger.info("\n" + "=" * 70)
        logger.info("                    📊 测试总结报告")
        logger.info("=" * 70)
        
        logger.info("\n📋 各轮次结果:")
        for result in self.round_results:
            logger.info(f"  轮次 {result['round']}: {result['name']}")
            logger.info(f"    - 耗时: {result['duration']:.2f}s")
            logger.info(f"    - 错误: {result['errors']}")
        
        logger.info("\n📈 总体统计:")
        logger.info(f"  总操作数: {self.total_metrics['total_operations']}")
        logger.info(f"  总错误数: {self.total_metrics['total_errors']}")
        logger.info(f"  总耗时: {self.total_metrics['total_time']:.2f}s")
        logger.info(f"  平均操作耗时: {(self.total_metrics['total_time']/max(self.total_metrics['total_operations'], 1)*1000):.2f}ms")
        
        if self.total_metrics["defects_found"]:
            logger.warning(f"\n⚠️  发现 {len(self.total_metrics['defects_found'])} 个缺陷:")
            for i, defect in enumerate(self.total_metrics["defects_found"][:5], 1):
                logger.warning(f"  {i}. [{defect['severity']}] {defect['type']} - {defect.get('file', 'N/A')}")
                logger.warning(f"     错误: {defect['error']}")
        else:
            logger.info("\n✅ 未发现任何缺陷！")
        
        logger.info("\n" + "=" * 70)
        
        return self.total_metrics


if __name__ == "__main__":
    tester = MultiRoundStressTest("/workspace/ark-analyzer/large-test-project")
    asyncio.run(tester.run_all_rounds())

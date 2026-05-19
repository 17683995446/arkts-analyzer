#!/usr/bin/env python3
"""
ArkAnalyzer 真实压力测试脚本
文件名: stress_test.py
用途: 模拟真实开发场景，长时间运行系统，发现真实运行时缺陷
"""
import asyncio
import os
import random
import sys
import time
import logging
from pathlib import Path
from typing import List

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.connection import DatabaseConnection
from services.synchronization_engine import SynchronizationEngine
from services.websocket_manager import WebSocketManager
from services.arkts_parser_service import ArkTSParser
from utils.hash_util import HashCalculator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ArkAnalyzerStressTest:
    """ArkAnalyzer压力测试"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.db = None
        self.sync_engine = None
        self.ws_manager = None
        self.parser = ArkTSParser()
        self.files = []
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "defects_found": []
        }
    
    async def initialize(self):
        """初始化测试环境"""
        logger.info("=" * 70)
        logger.info("        ARKANALYZER 真实运行压力测试")
        logger.info("=" * 70)
        logger.info(f"  测试项目: {self.project_path}")
        logger.info("")
        
        # 1. 扫描所有文件
        self.files = list(self.project_path.rglob("*.ets"))
        logger.info(f"✓ 发现 {len(self.files)} 个 ArkTS 文件")
        
        # 2. 初始化数据库
        logger.info("初始化数据库...")
        self.db = DatabaseConnection(":memory:")
        await self.db.initialize()
        
        self.ws_manager = WebSocketManager()
        self.sync_engine = SynchronizationEngine(self.db, self.ws_manager)
        logger.info("✓ 数据库和同步引擎初始化完成")
        
        self.test_results["total_tests"] += 1
    
    async def run_full_scan_test(self):
        """测试 1: 完整项目扫描"""
        logger.info("")
        logger.info("测试 1: 完整项目扫描")
        logger.info("-" * 50)
        
        start_time = time.time()
        
        files_processed = 0
        errors = 0
        
        for file_path in self.files:
            try:
                await self.sync_engine.update_single_file(str(file_path))
                files_processed += 1
            except Exception as e:
                logger.error(f"文件处理失败: {file_path} - {e}")
                errors += 1
                self.test_results["defects_found"].append({
                    "test": "full_scan",
                    "file": str(file_path),
                    "error": str(e),
                    "severity": "high"
                })
        
        duration = time.time() - start_time
        
        # 获取统计信息
        stats = await self.db.get_statistics()
        
        logger.info(f"✓ 扫描完成！")
        logger.info(f"  - 处理文件数: {files_processed}")
        logger.info(f"  - 错误数: {errors}")
        logger.info(f"  - 耗时: {duration:.2f} 秒")
        logger.info(f"  - 解析的类: {stats['total_classes']}")
        logger.info(f"  - 解析的方法: {stats['total_methods']}")
        logger.info(f"  - 解析的组件: {stats['total_components']}")
        
        self.test_results["total_tests"] += 1
        if errors == 0 and stats["total_classes"] > 0:
            self.test_results["passed"] += 1
            logger.info("✓ 完整扫描测试通过！")
        else:
            self.test_results["failed"] += 1
            logger.warning("✗ 完整扫描测试有问题")
    
    async def run_single_file_update_test(self):
        """测试 2: 单个文件更新"""
        logger.info("")
        logger.info("测试 2: 单个文件更新")
        logger.info("-" * 50)
        
        # 随机选择一个文件
        if not self.files:
            logger.warning("没有可用的文件")
            return
        
        test_file = random.choice(self.files)
        logger.info(f"测试文件: {test_file}")
        
        start_time = time.time()
        
        try:
            await self.sync_engine.update_single_file(str(test_file))
            
            # 再次更新同一个文件（模拟真实场景）
            await self.sync_engine.update_single_file(str(test_file))
            
            duration = time.time() - start_time
            logger.info(f"✓ 单个文件更新成功！")
            logger.info(f"  - 耗时: {duration:.2f} 秒")
            
            self.test_results["total_tests"] += 1
            self.test_results["passed"] += 1
        except Exception as e:
            logger.error(f"单个文件更新失败: {e}")
            self.test_results["defects_found"].append({
                "test": "single_file_update",
                "file": str(test_file),
                "error": str(e),
                "severity": "medium"
            })
            self.test_results["total_tests"] += 1
            self.test_results["failed"] += 1
    
    async def run_batch_update_test(self):
        """测试 3: 批量更新"""
        logger.info("")
        logger.info("测试 3: 批量更新（10个文件）")
        logger.info("-" * 50)
        
        test_files = random.sample(self.files, min(10, len(self.files)))
        
        start_time = time.time()
        
        errors = 0
        for file_path in test_files:
            try:
                await self.sync_engine.update_single_file(str(file_path))
            except Exception as e:
                errors += 1
                logger.error(f"批量更新失败: {file_path} - {e}")
        
        duration = time.time() - start_time
        
        logger.info(f"✓ 批量更新测试完成！")
        logger.info(f"  - 处理文件: {len(test_files)}")
        logger.info(f"  - 错误数: {errors}")
        logger.info(f"  - 耗时: {duration:.2f} 秒")
        
        self.test_results["total_tests"] += 1
        if errors == 0:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
    
    async def run_concurrent_test(self):
        """测试 4: 并发操作"""
        logger.info("")
        logger.info("测试 4: 并发操作（模拟真实场景）")
        logger.info("-" * 50)
        
        test_files = random.sample(self.files, min(5, len(self.files)))
        
        start_time = time.time()
        
        tasks = []
        for file_path in test_files:
            tasks.append(self.sync_engine.update_single_file(str(file_path)))
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        duration = time.time() - start_time
        
        logger.info(f"✓ 并发操作测试完成！")
        logger.info(f"  - 耗时: {duration:.2f} 秒")
        
        self.test_results["total_tests"] += 1
        self.test_results["passed"] += 1
    
    async def run_parser_edge_case_test(self):
        """测试 5: 解析器边界情况"""
        logger.info("")
        logger.info("测试 5: 解析器边界情况")
        logger.info("-" * 50)
        
        edge_cases = [
            ("empty_file.ets", ""),
            ("only_comments.ets", "// This is a comment\n/* Block comment */"),
            ("only_struct.ets", "@Component\nstruct Test {}"),
            ("only_class.ets", "export class Test {}"),
        ]
        
        temp_dir = Path("/tmp/ark_test_edge")
        temp_dir.mkdir(exist_ok=True)
        
        errors = 0
        
        for filename, content in edge_cases:
            try:
                file_path = temp_dir / filename
                file_path.write_text(content, encoding="utf-8")
                
                # 解析文件
                parsed = self.parser.parse_file(str(file_path), content)
                logger.info(f"  ✓ {filename}: {len(parsed.classes)} classes")
                
            except Exception as e:
                logger.error(f"  ✗ {filename}: {e}")
                self.test_results["defects_found"].append({
                    "test": "edge_case",
                    "file": filename,
                    "error": str(e),
                    "severity": "medium"
                })
                errors += 1
        
        self.test_results["total_tests"] += 1
        if errors == 0:
            self.test_results["passed"] += 1
            logger.info("✓ 边界情况测试通过！")
        else:
            self.test_results["failed"] += 1
    
    async def run_database_query_test(self):
        """测试 6: 数据库查询"""
        logger.info("")
        logger.info("测试 6: 数据库查询")
        logger.info("-" * 50)
        
        queries_tested = 0
        errors = 0
        
        try:
            # 获取统计信息
            stats = await self.db.get_statistics()
            logger.info(f"  ✓ 统计查询: {stats}")
            queries_tested += 1
            
            # 获取类列表
            classes = await self.db.get_all_classes()
            logger.info(f"  ✓ 类列表查询: {len(classes)} 个类")
            queries_tested += 1
            
            # 获取所有文件
            files = await self.db.get_all_files()
            logger.info(f"  ✓ 文件列表查询: {len(files)} 个文件")
            queries_tested += 1
            
        except Exception as e:
            logger.error(f"查询失败: {e}")
            errors += 1
        
        self.test_results["total_tests"] += 1
        if errors == 0:
            self.test_results["passed"] += 1
            logger.info("✓ 数据库查询测试通过！")
        else:
            self.test_results["failed"] += 1
    
    async def run_hash_test(self):
        """测试 7: 哈希计算"""
        logger.info("")
        logger.info("测试 7: 哈希计算")
        logger.info("-" * 50)
        
        test_file = self.files[0] if self.files else None
        
        if test_file:
            try:
                content = test_file.read_text(encoding="utf-8")
                
                # 计算哈希
                hash1 = HashCalculator.calculate_md5(content)
                hash2 = HashCalculator.calculate_md5(content)
                logger.info(f"  ✓ 哈希计算: {len(hash1)} 字符")
                
                if hash1 == hash2:
                    logger.info(f"  ✓ 哈希一致性验证通过")
                else:
                    logger.error(f"  ✗ 哈希不一致")
                    self.test_results["defects_found"].append({
                        "test": "hash_consistency",
                        "file": str(test_file),
                        "error": "Hash is not consistent",
                        "severity": "low"
                    })
                
                self.test_results["total_tests"] += 1
                self.test_results["passed"] += 1
            except Exception as e:
                logger.error(f"哈希测试失败: {e}")
                self.test_results["failed"] += 1
                self.test_results["total_tests"] += 1
    
    async def cleanup(self):
        """清理测试环境"""
        if self.db:
            await self.db.close()
            logger.info("")
            logger.info("✓ 数据库连接已关闭")
    
    def print_results(self):
        """打印测试结果"""
        logger.info("")
        logger.info("=" * 70)
        logger.info("                    压力测试结果")
        logger.info("=" * 70)
        logger.info(f"  总测试数: {self.test_results['total_tests']}")
        logger.info(f"  通过: {self.test_results['passed']}")
        logger.info(f"  失败: {self.test_results['failed']}")
        
        if self.test_results["defects_found"]:
            logger.info("")
            logger.info(f"  发现的缺陷: {len(self.test_results['defects_found'])}")
            
            for i, defect in enumerate(self.test_results["defects_found"], 1):
                logger.info(f"  {i}. [{defect['severity']}] {defect['test']} - {defect.get('file', '')}")
                logger.info(f"     错误: {defect['error']}")
        else:
            logger.info("")
            logger.info("  ✓ 未发现任何缺陷！")
        
        logger.info("=" * 70)


async def main():
    """主函数"""
    # 使用我们创建的大规模测试项目
    project_path = "/workspace/ark-analyzer/large-test-project"
    
    tester = ArkAnalyzerStressTest(project_path)
    
    try:
        await tester.initialize()
        
        # 运行所有测试
        await tester.run_full_scan_test()
        await tester.run_single_file_update_test()
        await tester.run_batch_update_test()
        await tester.run_concurrent_test()
        await tester.run_parser_edge_case_test()
        await tester.run_database_query_test()
        await tester.run_hash_test()
        
        # 打印结果
        tester.print_results()
        
    except Exception as e:
        logger.error(f"压力测试异常: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await tester.cleanup()


if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
前后端完整集成测试 - 第七轮
遵循第一性原理：简单、高效、可靠
"""
import asyncio
import time
import sys
from pathlib import Path
import logging

sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.connection import DatabaseConnection
from services.synchronization_engine import SynchronizationEngine
from services.websocket_manager import WebSocketManager
from services.arkts_parser_service import ArkTSParser

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("integration_test")


class IntegrationTest:
    """前后端完整集成测试"""
    
    def __init__(self):
        self.db = None
        self.sync_engine = None
        self.parser = ArkTSParser()
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        
    async def setup(self):
        """初始化测试环境"""
        logger.info("=" * 100)
        logger.info("       🔬 第七轮 - 前后端完整集成测试")
        logger.info("=" * 100)
        
        self.db = DatabaseConnection(":memory:")
        await self.db.initialize()
        self.ws_manager = WebSocketManager()
        self.sync_engine = SynchronizationEngine(self.db, self.ws_manager)
        
        logger.info("✅ 集成测试环境初始化完成")
        
    async def test_database_api(self):
        """测试数据库API完整性"""
        logger.info("\n📋 测试 1: 数据库API完整性")
        
        tests_passed = 0
        tests_total = 0
        
        # 测试1: 获取所有类
        tests_total += 1
        try:
            classes = await self.db.get_all_classes()
            assert isinstance(classes, list), "get_all_classes应该返回列表"
            tests_passed += 1
            logger.info("   ✓ get_all_classes() API正常")
        except Exception as e:
            logger.error(f"   ✗ get_all_classes() 失败: {e}")
            self.results["errors"].append(f"get_all_classes: {e}")
        
        # 测试2: 获取所有文件
        tests_total += 1
        try:
            files = await self.db.get_all_files()
            assert isinstance(files, list), "get_all_files应该返回列表"
            tests_passed += 1
            logger.info("   ✓ get_all_files() API正常")
        except Exception as e:
            logger.error(f"   ✗ get_all_files() 失败: {e}")
            self.results["errors"].append(f"get_all_files: {e}")
        
        # 测试3: 获取统计信息
        tests_total += 1
        try:
            stats = await self.db.get_statistics()
            assert "total_files" in stats, "统计信息应包含total_files"
            assert "total_classes" in stats, "统计信息应包含total_classes"
            tests_passed += 1
            logger.info("   ✓ get_statistics() API正常")
        except Exception as e:
            logger.error(f"   ✗ get_statistics() 失败: {e}")
            self.results["errors"].append(f"get_statistics: {e}")
        
        # 测试4: 插入并查询类
        tests_total += 1
        try:
            await self.sync_engine.update_single_file("/tmp/test_class.ets")
            classes = await self.db.get_all_classes()
            assert len(classes) > 0, "应该至少有1个类"
            tests_passed += 1
            logger.info("   ✓ 插入并查询类正常")
        except Exception as e:
            logger.error(f"   ✗ 插入并查询类失败: {e}")
            self.results["errors"].append(f"insert_and_query: {e}")
        
        self.results["passed"] += tests_passed
        self.results["failed"] += (tests_total - tests_passed)
        
        logger.info(f"\n   数据库API测试: {tests_passed}/{tests_total} 通过")
        
    async def test_parser_api(self):
        """测试解析器API"""
        logger.info("\n📋 测试 2: 解析器API")
        
        tests_passed = 0
        tests_total = 0
        
        test_cases = [
            ("/tmp/component.ets", """@Component
struct MyComponent {
  @State value: string = 'test'
  build() { Text(this.value) }
}
"""),
            ("/tmp/class.ets", """class MyService {
  fetchData() { return 'data'; }
}
"""),
            ("/tmp/empty.ets", ""),
            ("/tmp/comments.ets", """// This is a comment
/* Block comment */
// Another comment
"""),
        ]
        
        for file_path, content in test_cases:
            tests_total += 1
            try:
                Path(file_path).write_text(content, encoding="utf-8")
                parsed = self.parser.parse_file(file_path, content)
                assert hasattr(parsed, "classes"), "解析结果应包含classes属性"
                tests_passed += 1
                logger.info(f"   ✓ 解析 {Path(file_path).name}: {len(parsed.classes)} 个类")
            except Exception as e:
                logger.error(f"   ✗ 解析 {Path(file_path).name} 失败: {e}")
                self.results["errors"].append(f"parse {file_path}: {e}")
        
        self.results["passed"] += tests_passed
        self.results["failed"] += (tests_total - tests_passed)
        
        logger.info(f"\n   解析器API测试: {tests_passed}/{tests_total} 通过")
        
    async def test_sync_engine(self):
        """测试同步引擎"""
        logger.info("\n📋 测试 3: 同步引擎")
        
        tests_passed = 0
        tests_total = 0
        
        test_files = [
            "/tmp/sync_test_1.ets",
            "/tmp/sync_test_2.ets",
            "/tmp/sync_test_3.ets",
        ]
        
        for test_file in test_files:
            tests_total += 1
            try:
                content = f"""@Component
struct TestStruct {{
  @State data: number = 123
  build() {{ Text('Test') }}
}}
"""
                Path(test_file).write_text(content, encoding="utf-8")
                await self.sync_engine.update_single_file(test_file)
                tests_passed += 1
                logger.info(f"   ✓ 同步 {Path(test_file).name} 成功")
            except Exception as e:
                logger.error(f"   ✗ 同步 {Path(test_file).name} 失败: {e}")
                self.results["errors"].append(f"sync {test_file}: {e}")
        
        self.results["passed"] += tests_passed
        self.results["failed"] += (tests_total - tests_passed)
        
        logger.info(f"\n   同步引擎测试: {tests_passed}/{tests_total} 通过")
        
    async def test_concurrent_operations(self):
        """测试并发操作"""
        logger.info("\n📋 测试 4: 并发操作")
        
        tests_passed = 0
        tests_total = 1
        
        try:
            tasks = []
            for i in range(50):
                file_path = f"/tmp/concurrent_test_{i}.ets"
                content = f"""class ConcurrentClass_{i} {{
  method{i}() {{ return {i}; }}
}}
"""
                Path(file_path).write_text(content, encoding="utf-8")
                tasks.append(self.sync_engine.update_single_file(file_path))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            errors = sum(1 for r in results if isinstance(r, Exception))
            
            if errors == 0:
                tests_passed = 1
                logger.info(f"   ✓ 50个并发操作全部成功")
            else:
                logger.warning(f"   ⚠️  50个并发操作中有 {errors} 个错误")
                
        except Exception as e:
            logger.error(f"   ✗ 并发操作测试失败: {e}")
            self.results["errors"].append(f"concurrent: {e}")
        
        self.results["passed"] += tests_passed
        self.results["failed"] += (tests_total - tests_passed)
        
        logger.info(f"\n   并发操作测试: {tests_passed}/{tests_total} 通过")
        
    async def test_edge_cases(self):
        """测试边界情况"""
        logger.info("\n📋 测试 5: 边界情况")
        
        tests_passed = 0
        tests_total = 0
        
        edge_cases = [
            ("空文件", "/tmp/empty.ets", ""),
            ("超长行", "/tmp/long_line.ets", "x" * 10000),
            ("特殊字符", "/tmp/special.ets", "class Test$123 { $prop: number = 123; }"),
            ("Unicode", "/tmp/unicode.ets", "class 中文类 { 中文方法() {} }"),
            ("嵌套类", "/tmp/nested.ets", "class A { class B { class C {} } }"),
        ]
        
        for name, file_path, content in edge_cases:
            tests_total += 1
            try:
                Path(file_path).write_text(content, encoding="utf-8")
                await self.sync_engine.update_single_file(file_path)
                tests_passed += 1
                logger.info(f"   ✓ {name} 处理成功")
            except Exception as e:
                logger.warning(f"   ⚠️  {name} 处理失败: {e}")
                self.results["errors"].append(f"edge_case {name}: {e}")
                # 边界情况失败不计入总数，因为这是测试边界
        
        self.results["passed"] += tests_passed
        self.results["failed"] += (tests_total - tests_passed)
        
        logger.info(f"\n   边界情况测试: {tests_passed}/{tests_total} 通过")
        
    async def print_summary(self):
        """打印测试总结"""
        total = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results["passed"] / total * 100) if total > 0 else 0
        
        logger.info("\n" + "=" * 100)
        logger.info("                    📊 第七轮集成测试总结报告")
        logger.info("=" * 100)
        
        logger.info(f"\n📈 测试结果:")
        logger.info(f"   通过: {self.results['passed']}")
        logger.info(f"   失败: {self.results['failed']}")
        logger.info(f"   通过率: {pass_rate:.1f}%")
        
        if self.results["errors"]:
            logger.warning(f"\n⚠️  发现 {len(self.results['errors'])} 个错误:")
            for i, error in enumerate(self.results["errors"][:10], 1):
                logger.warning(f"   {i}. {error}")
        
        if pass_rate >= 95:
            logger.info("\n🎉🎉🎉 **集成测试通过率 >= 95%，系统表现优秀！**")
        elif pass_rate >= 80:
            logger.info("\n✅ 集成测试通过率 >= 80%，系统可接受")
        else:
            logger.warning("\n⚠️  集成测试通过率 < 80%，需要优化")
        
        logger.info("\n" + "=" * 100)
        
    async def run_all_tests(self):
        """运行所有测试"""
        await self.setup()
        await self.test_database_api()
        await self.test_parser_api()
        await self.test_sync_engine()
        await self.test_concurrent_operations()
        await self.test_edge_cases()
        await self.print_summary()
        
        if self.db:
            await self.db.close()
            
        return self.results


if __name__ == "__main__":
    tester = IntegrationTest()
    results = asyncio.run(tester.run_all_tests())
    
    if results["failed"] > 0:
        sys.exit(1)

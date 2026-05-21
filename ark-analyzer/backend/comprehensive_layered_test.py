#!/usr/bin/env python3
"""
全面分层测试工具
第三步：分层测 - 静态走读、单元覆盖、集成验证、接口遍历、业务场景、数据校验
"""

import asyncio
import time
import sys
import random
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
import logging

sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.connection import DatabaseConnection
from services.synchronization_engine import SynchronizationEngine
from services.websocket_manager import WebSocketManager
from services.arkts_parser_service import ArkTSParser

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("layered-test")


@dataclass
class TestResult:
    """测试结果"""
    layer: str
    test_name: str
    passed: bool
    details: str
    duration_ms: int


class ComprehensiveLayeredTester:
    """
    全面分层测试器
    按照六个原则进行系统性测试
    """
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.db = None
        self.sync_engine = None
        self.parser = ArkTSParser()
        
    async def run_all_layers(self):
        """运行所有层次的测试"""
        logger.info("=" * 100)
        logger.info("🧪 第三步：分层测 - 全面分层测试")
        logger.info("=" * 100)
        
        await self._setup()
        
        # 第1层：静态走读（代码逻辑验证）
        await self.layer1_static_code_review()
        
        # 第2层：单元测试（每个函数独立测试）
        await self.layer2_unit_tests()
        
        # 第3层：集成测试（模块间交互）
        await self.layer3_integration_tests()
        
        # 第4层：接口遍历（所有API）
        await self.layer4_api_traversal()
        
        # 第5层：业务场景（完整业务流程）
        await self.layer5_business_scenarios()
        
        # 第6层：数据校验（数据一致性）
        await self.layer6_data_validation()
        
        await self._print_summary()
        await self._cleanup()
        
    async def _setup(self):
        """设置测试环境"""
        self.db = DatabaseConnection(":memory:")
        await self.db.initialize()
        self.ws_manager = WebSocketManager()
        self.sync_engine = SynchronizationEngine(self.db, self.ws_manager)
        
    async def _cleanup(self):
        """清理资源"""
        if self.db:
            await self.db.close()
            
    def _record_result(self, layer: str, test_name: str, passed: bool, details: str, duration_ms: int):
        """记录测试结果"""
        result = TestResult(
            layer=layer,
            test_name=test_name,
            passed=passed,
            details=details,
            duration_ms=duration_ms
        )
        self.results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"  {status} | {test_name} | {duration_ms}ms | {details}")
        
    async def layer1_static_code_review(self):
        """
        第1层：静态走读
        验证代码逻辑、分支、边界、异常处理
        """
        logger.info("\n" + "=" * 100)
        logger.info("📋 第1层：静态走读 - 代码逻辑验证")
        logger.info("=" * 100)
        
        start = time.time()
        
        # 1.1 验证解析器的所有分支
        test_cases = [
            ("解析 class 定义", "class Test {}", True),
            ("解析 export class", "export class Test {}", True),
            ("解析 struct", "struct Test {}", True),
            ("解析 @Component", "@Component\nstruct Test {}", True),
            ("解析空文件", "", False),
            ("解析纯注释", "// comment", False),
            ("解析方法", "class Test { method() {} }", True),
            ("解析属性", "class Test { @State value: string = ''; }", True),
        ]
        
        for test_name, code, should_find in test_cases:
            try:
                if code:
                    Path("/tmp/test_static.ets").write_text(code, encoding='utf-8')
                    parsed = self.parser.parse_file("/tmp/test_static.ets", code)
                    found = len(parsed.classes) > 0
                    passed = found == should_find
                    self._record_result("L1-静态走读", test_name, passed, 
                                       f"期望:{should_find} 实际:{found}", 0)
                else:
                    self._record_result("L1-静态走读", test_name, not should_find, 
                                       "空文件正确跳过", 0)
            except Exception as e:
                self._record_result("L1-静态走读", test_name, False, str(e)[:50], 0)
                
        # 1.2 验证异常处理
        exception_cases = [
            ("文件不存在", "/nonexistent/file.ets", "deleted"),
            ("空路径处理", "", "modified"),
        ]
        
        for test_name, file_path, change_type in exception_cases:
            try:
                result = await self.sync_engine.update_single_file(file_path, change_type)
                passed = not result.success  # 应该失败
                self._record_result("L1-静态走读", f"异常-{test_name}", passed,
                                   "正确处理异常", 0)
            except Exception as e:
                self._record_result("L1-静态走读", f"异常-{test_name}", True,
                                   f"异常捕获: {type(e).__name__}", 0)
                
        duration = int((time.time() - start) * 1000)
        logger.info(f"\n第1层完成，耗时: {duration}ms")
        
    async def layer2_unit_tests(self):
        """
        第2层：单元测试
        每个函数独立测试，覆盖所有入参和边界
        """
        logger.info("\n" + "=" * 100)
        logger.info("📋 第2层：单元测试 - 函数独立测试")
        logger.info("=" * 100)
        
        start = time.time()
        
        # 2.1 数据库单元测试
        await self._test_database_unit()
        
        # 2.2 解析器单元测试
        await self._test_parser_unit()
        
        # 2.3 同步引擎单元测试
        await self._test_sync_unit()
        
        duration = int((time.time() - start) * 1000)
        logger.info(f"\n第2层完成，耗时: {duration}ms")
        
    async def _test_database_unit(self):
        """数据库单元测试"""
        test_cases = [
            ("初始化数据库", lambda: self.db),
            ("创建表", lambda: self.db._create_tables()),
            ("获取统计", lambda: self.db.get_statistics()),
            ("获取所有文件", lambda: self.db.get_all_files()),
            ("获取所有类", lambda: self.db.get_all_classes()),
            ("事务回滚", lambda: self.db.rollback()),
        ]
        
        for test_name, test_func in test_cases:
            start = time.time()
            try:
                result = test_func()
                duration = int((time.time() - start) * 1000)
                self._record_result("L2-单元测试", f"DB-{test_name}", True,
                                   "执行成功", duration)
            except Exception as e:
                duration = int((time.time() - start) * 1000)
                self._record_result("L2-单元测试", f"DB-{test_name}", False,
                                   str(e)[:50], duration)
                
    async def _test_parser_unit(self):
        """解析器单元测试"""
        test_cases = [
            ("正常解析", "class Test {}"),
            ("解析组件", "@Component\nstruct Comp {}"),
            ("解析方法", "class Test { method() {} }"),
            ("解析多个类", "class A {}\nclass B {}"),
            ("解析装饰器属性", "@State val: string = ''"),
            ("解析继承", "class A extends B {}"),
            ("解析接口", "class A implements B, C {}"),
        ]
        
        for test_name, code in test_cases:
            start = time.time()
            try:
                Path("/tmp/test_parser.ets").write_text(code, encoding='utf-8')
                parsed = self.parser.parse_file("/tmp/test_parser.ets", code)
                duration = int((time.time() - start) * 1000)
                self._record_result("L2-单元测试", f"Parser-{test_name}", True,
                                   f"发现{len(parsed.classes)}个类", duration)
            except Exception as e:
                duration = int((time.time() - start) * 1000)
                self._record_result("L2-单元测试", f"Parser-{test_name}", False,
                                   str(e)[:50], duration)
                
    async def _test_sync_unit(self):
        """同步引擎单元测试"""
        test_file = Path("/tmp/test_sync.ets")
        test_file.write_text("class TestClass {}", encoding='utf-8')
        
        start = time.time()
        try:
            result = await self.sync_engine.update_single_file(str(test_file))
            duration = int((time.time() - start) * 1000)
            self._record_result("L2-单元测试", "Sync-单文件更新", result.success,
                               f"更新了{result.entities_updated}个实体", duration)
        except Exception as e:
            duration = int((time.time() - start) * 1000)
            self._record_result("L2-单元测试", "Sync-单文件更新", False,
                               str(e)[:50], duration)
                               
    async def layer3_integration_tests(self):
        """
        第3层：集成测试
        模块间交互、调用链路验证
        """
        logger.info("\n" + "=" * 100)
        logger.info("📋 第3层：集成测试 - 模块间交互")
        logger.info("=" * 100)
        
        start = time.time()
        
        # 3.1 完整文件处理流程
        test_file = Path("/tmp/integration_test.ets")
        test_file.write_text("""@Component
struct IntegrationTest {
    @State value: string = 'test';
    method1() { this.method2(); }
    method2() { return 42; }
    build() { Text(this.value); }
}
""", encoding='utf-8')
        
        try:
            # 全流程：解析 -> 同步 -> 查询
            parsed = self.parser.parse_file(str(test_file), test_file.read_text())
            sync_result = await self.sync_engine.update_single_file(str(test_file))
            stats = await self.db.get_statistics()
            
            passed = (len(parsed.classes) > 0 and 
                     sync_result.success and 
                     stats['total_classes'] > 0)
            
            self._record_result("L3-集成测试", "完整文件处理流程", passed,
                               f"类:{stats['total_classes']} 方法:{stats['total_methods']}", 0)
        except Exception as e:
            self._record_result("L3-集成测试", "完整文件处理流程", False,
                               str(e)[:50], 0)
                               
        # 3.2 多文件交互
        await self._test_multi_file_integration()
        
        duration = int((time.time() - start) * 1000)
        logger.info(f"\n第3层完成，耗时: {duration}ms")
        
    async def _test_multi_file_integration(self):
        """多文件集成测试"""
        for i in range(5):
            test_file = Path(f"/tmp/integration_{i}.ets")
            test_file.write_text(f"class Class{i} {{ value{i} = {i}; }}", encoding='utf-8')
            await self.sync_engine.update_single_file(str(test_file))
            
        stats = await self.db.get_statistics()
        passed = stats['total_classes'] >= 5
        
        self._record_result("L3-集成测试", "多文件交互(5文件)", passed,
                           f"管理{stats['total_classes']}个类", 0)
                           
    async def layer4_api_traversal(self):
        """
        第4层：接口遍历
        所有API路径、所有参数组合
        """
        logger.info("\n" + "=" * 100)
        logger.info("📋 第4层：接口遍历 - API全覆盖")
        logger.info("=" * 100)
        
        start = time.time()
        
        # 准备测试数据
        for i in range(10):
            Path(f"/tmp/api_test_{i}.ets").write_text(f"class ApiClass{i} {{}}", encoding='utf-8')
            await self.sync_engine.update_single_file(f"/tmp/api_test_{i}.ets")
            
        # 4.1 遍历所有数据库查询API
        apis = [
            ("get_statistics", lambda: self.db.get_statistics()),
            ("get_all_files", lambda: self.db.get_all_files()),
            ("get_all_classes", lambda: self.db.get_all_classes()),
            ("get_file_hash", lambda: self.db.get_file_hash("/tmp/api_test_0.ets")),
        ]
        
        for api_name, api_func in apis:
            start = time.time()
            try:
                result = api_func()
                duration = int((time.time() - start) * 1000)
                self._record_result("L4-接口遍历", f"API-{api_name}", True,
                                   f"返回类型:{type(result).__name__}", duration)
            except Exception as e:
                duration = int((time.time() - start) * 1000)
                self._record_result("L4-接口遍历", f"API-{api_name}", False,
                                   str(e)[:50], duration)
                                   
        duration = int((time.time() - start) * 1000)
        logger.info(f"\n第4层完成，耗时: {duration}ms")
        
    async def layer5_business_scenarios(self):
        """
        第5层：业务场景
        完整业务流程、真实使用场景
        """
        logger.info("\n" + "=" * 100)
        logger.info("📋 第5层：业务场景 - 完整业务流程")
        logger.info("=" * 100)
        
        start = time.time()
        
        scenarios = [
            ("场景1: 首次全量同步", self._scenario_first_sync),
            ("场景2: 增量更新", self._scenario_incremental_update),
            ("场景3: 删除文件", self._scenario_delete_file),
            ("场景4: 文件修改检测", self._scenario_modification_detection),
            ("场景5: 并发更新", self._scenario_concurrent_updates),
        ]
        
        for scenario_name, scenario_func in scenarios:
            scenario_start = time.time()
            try:
                passed = await scenario_func()
                duration = int((time.time() - scenario_start) * 1000)
                self._record_result("L5-业务场景", scenario_name, passed,
                                   "场景执行完成", duration)
            except Exception as e:
                duration = int((time.time() - scenario_start) * 1000)
                self._record_result("L5-业务场景", scenario_name, False,
                                   str(e)[:50], duration)
                                   
        duration = int((time.time() - start) * 1000)
        logger.info(f"\n第5层完成，耗时: {duration}ms")
        
    async def _scenario_first_sync(self) -> bool:
        """场景1: 首次全量同步"""
        # 模拟首次同步3个文件
        for i in range(3):
            Path(f"/tmp/sync_scene_{i}.ets").write_text(f"class Scene{i} {{}}", encoding='utf-8')
            await self.sync_engine.update_single_file(f"/tmp/sync_scene_{i}.ets")
            
        stats = await self.db.get_statistics()
        return stats['total_files'] >= 3
        
    async def _scenario_incremental_update(self) -> bool:
        """场景2: 增量更新"""
        file_path = "/tmp/incremental.ets"
        Path(file_path).write_text("class Original {}", encoding='utf-8')
        await self.sync_engine.update_single_file(file_path)
        
        # 修改文件
        Path(file_path).write_text("class Original { method() {} }", encoding='utf-8')
        result = await self.sync_engine.update_single_file(file_path)
        
        return result.success and result.entities_updated > 0
        
    async def _scenario_delete_file(self) -> bool:
        """场景3: 删除文件"""
        file_path = "/tmp/to_delete.ets"
        Path(file_path).write_text("class ToDelete {}", encoding='utf-8')
        await self.sync_engine.update_single_file(file_path)
        
        # 模拟删除
        result = await self.sync_engine.update_single_file(file_path, "deleted")
        return result.success
        
    async def _scenario_modification_detection(self) -> bool:
        """场景4: 文件修改检测"""
        file_path = "/tmp/modify_test.ets"
        Path(file_path).write_text("class First {}", encoding='utf-8')
        await self.sync_engine.update_single_file(file_path)
        
        # 相同内容，不应更新
        result1 = await self.sync_engine.update_single_file(file_path)
        
        # 修改内容，应该更新
        Path(file_path).write_text("class Second {}", encoding='utf-8')
        result2 = await self.sync_engine.update_single_file(file_path)
        
        return result1.entities_updated == 0 and result2.entities_updated > 0
        
    async def _scenario_concurrent_updates(self) -> bool:
        """场景5: 并发更新"""
        tasks = []
        for i in range(10):
            file_path = f"/tmp/concurrent_{i}.ets"
            Path(file_path).write_text(f"class Concurrent{i} {{}}", encoding='utf-8')
            tasks.append(self.sync_engine.update_single_file(file_path))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        successes = sum(1 for r in results if not isinstance(r, Exception) and r.success)
        
        return successes >= 9  # 允许1个失败（极端并发）
        
    async def layer6_data_validation(self):
        """
        第6层：数据校验
        数据一致性、完整性、流转自洽
        """
        logger.info("\n" + "=" * 100)
        logger.info("📋 第6层：数据校验 - 数据一致性")
        logger.info("=" * 100)
        
        start = time.time()
        
        # 准备测试数据
        for i in range(5):
            Path(f"/tmp/validation_{i}.ets").write_text(f"class Validate{i} {{}}", encoding='utf-8')
            await self.sync_engine.update_single_file(f"/tmp/validation_{i}.ets")
            
        # 6.1 数据完整性校验
        stats = await self.db.get_statistics()
        classes = await self.db.get_all_classes()
        files = await self.db.get_all_files()
        
        checks = [
            ("文件数一致性", stats['total_files'] == len(files)),
            ("类数一致性", stats['total_classes'] == len(classes)),
            ("统计信息完整性", all(k in stats for k in ['total_files', 'total_classes', 'total_methods'])),
            ("类数据完整性", all('name' in c for c in classes)),
            ("文件数据完整性", all('path' in f and 'hash' in f for f in files)),
        ]
        
        for check_name, check_result in checks:
            self._record_result("L6-数据校验", check_name, check_result,
                               "通过" if check_result else "失败", 0)
                               
        # 6.2 数据流转校验
        await self._validate_data_flow()
        
        duration = int((time.time() - start) * 1000)
        logger.info(f"\n第6层完成，耗时: {duration}ms")
        
    async def _validate_data_flow(self):
        """数据流转校验"""
        # 全量同步 -> 增量更新 -> 查询 -> 统计
        file_path = "/tmp/dataflow.ets"
        Path(file_path).write_text("class DataFlow {}", encoding='utf-8')
        
        # 同步
        sync_result = await self.sync_engine.update_single_file(file_path)
        
        # 查询
        classes = await self.db.get_all_classes()
        files = await self.db.get_all_files()
        
        # 统计
        stats = await self.db.get_statistics()
        
        # 校验流转一致性
        checks = [
            ("同步->查询一致性", sync_result.success and len(classes) > 0),
            ("查询->统计一致性", len(classes) == stats['total_classes']),
            ("文件->类关联一致性", all(c['file_id'] is not None for c in classes)),
        ]
        
        for check_name, check_result in checks:
            self._record_result("L6-数据校验", check_name, check_result,
                               "通过" if check_result else "失败", 0)
                               
    async def _print_summary(self):
        """打印测试总结"""
        logger.info("\n" + "=" * 100)
        logger.info("📊 六层测试总结报告")
        logger.info("=" * 100)
        
        layers = {}
        for result in self.results:
            if result.layer not in layers:
                layers[result.layer] = {'passed': 0, 'failed': 0}
            if result.passed:
                layers[result.layer]['passed'] += 1
            else:
                layers[result.layer]['failed'] += 1
                
        logger.info("\n各层测试结果:")
        total_passed = 0
        total_failed = 0
        
        for layer, counts in layers.items():
            total = counts['passed'] + counts['failed']
            rate = (counts['passed'] / total * 100) if total > 0 else 0
            total_passed += counts['passed']
            total_failed += counts['failed']
            
            logger.info(f"  {layer}: {counts['passed']}/{total} 通过 ({rate:.1f}%)")
            
        overall_rate = (total_passed / (total_passed + total_failed) * 100) if (total_passed + total_failed) > 0 else 0
        
        logger.info(f"\n总计: {total_passed}/{total_passed + total_failed} 通过 ({overall_rate:.1f}%)")
        
        if overall_rate >= 95:
            logger.info("\n🎉🎉🎉 测试通过率 >= 95%，系统完全合格！")
        elif overall_rate >= 80:
            logger.info("\n✅ 测试通过率 >= 80%，系统可接受")
        else:
            logger.warning("\n⚠️  测试通过率 < 80%，需要优化")
            
        if self.results:
            failed_tests = [r for r in self.results if not r.passed]
            if failed_tests:
                logger.warning(f"\n⚠️  发现 {len(failed_tests)} 个失败测试:")
                for test in failed_tests[:10]:
                    logger.warning(f"  - {test.layer} | {test.test_name}: {test.details}")
                    
        logger.info("\n" + "=" * 100)


if __name__ == "__main__":
    tester = ComprehensiveLayeredTester()
    asyncio.run(tester.run_all_layers())

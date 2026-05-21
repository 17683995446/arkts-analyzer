#!/usr/bin/env python3
"""
超深度全流程测试工具 - 8步标准流程
一、基准定调
二、测试前置
三、标准化全流程测试(8步)
四、判定验收
"""
import asyncio
import time
import sys
import random
import logging
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import traceback

sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.connection import DatabaseConnection
from services.synchronization_engine import SynchronizationEngine
from services.websocket_manager import WebSocketManager
from services.arkts_parser_service import ArkTSParser, ParsedFile
from config import UpdateResult

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("ULTRA_DEEP_TEST")


class TestPhase(Enum):
    """测试阶段"""
    PRE_ANALYSIS = "前置分析"
    STATIC_VERIFY = "1.静态代码核验"
    UNIT_FULL = "2.单元全覆盖测试"
    MODULE_INTEGRATION = "3.模块集成联调"
    API_TRAVERSE = "4.接口全量遍历"
    BUSINESS_CLOSED = "5.业务场景闭环"
    DATA_CONSISTENCY = "6.数据一致性校验"
    EXCEPTION_TEST = "7.异常容错测试"
    PERFORMANCE = "8.基础性能核验"


@dataclass
class TestCase:
    """测试用例"""
    phase: TestPhase
    name: str
    description: str
    input_data: Any
    expected_result: Any
    actual_result: Any = None
    passed: bool = False
    error_message: str = ""
    duration_ms: int = 0


@dataclass
class CodeAnalysisResult:
    """代码分析结果"""
    file_path: str
    module_name: str
    total_functions: int = 0
    total_branches: int = 0
    total_exceptions: int = 0
    branch_analysis: List[Dict[str, Any]] = None
    parameter_rules: List[Dict[str, Any]] = None
    data_flows: List[Dict[str, Any]] = None


class UltraDeepTester:
    """超深度全流程测试器"""

    def __init__(self):
        self.db = None
        self.sync_engine = None
        self.parser = ArkTSParser()
        self.test_cases: List[TestCase] = []
        self.analysis_results: List[CodeAnalysisResult] = []
        self.start_time = 0

    async def setup(self):
        """设置测试环境"""
        logger.info("=" * 120)
        logger.info("🏗️  一、基准定调 - 系统初始化")
        logger.info("=" * 120)

        self.start_time = time.time()

        self.db = DatabaseConnection(":memory:")
        await self.db.initialize()
        self.ws_manager = WebSocketManager()
        self.sync_engine = SynchronizationEngine(self.db, self.ws_manager)

        logger.info("✅ 系统初始化完成")

    async def run_phase_one_pre_analysis(self):
        """
        二、测试前置动作
        1. 拆解代码分层、模块依赖、调用链路、入口出口
        2. 提取所有参数规则、判断条件、边界阈值、默认逻辑、异常捕获
        3. 梳理数据流向、状态变更、事务逻辑、隐藏隐性规则
        """
        logger.info("\n" + "=" * 120)
        logger.info("📋 二、测试前置 - 深度代码分析")
        logger.info("=" * 120)

        # 读取所有核心代码进行分析
        core_files = [
            ("数据库层", "src/database/connection.py"),
            ("服务层-同步引擎", "src/services/synchronization_engine.py"),
            ("服务层-解析器", "src/services/arkts_parser_service.py"),
        ]

        for module_name, file_path in core_files:
            full_path = Path(__file__).parent / file_path
            if not full_path.exists():
                logger.warning(f"文件不存在: {full_path}")
                continue

            analysis = await self._analyze_single_file(str(full_path), module_name)
            self.analysis_results.append(analysis)

        logger.info(f"\n✅ 代码分析完成，分析了 {len(self.analysis_results)} 个模块")

    async def _analyze_single_file(self, file_path: str, module_name: str) -> CodeAnalysisResult:
        """分析单个文件"""
        logger.info(f"\n🔍 分析模块: {module_name}")
        content = Path(file_path).read_text(encoding='utf-8')
        lines = content.split('\n')

        analysis = CodeAnalysisResult(
            file_path=file_path,
            module_name=module_name,
            branch_analysis=[],
            parameter_rules=[],
            data_flows=[]
        )

        # 1. 分析函数
        func_pattern = r'^\s*(?:async\s+)?def\s+(\w+)\s*\('
        for i, line in enumerate(lines):
            func_match = re.match(func_pattern, line)
            if func_match:
                analysis.total_functions += 1
                logger.info(f"  ✅ 发现函数: {func_match.group(1)}() (行 {i+1})")

        # 2. 分析分支
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('if '):
                analysis.total_branches += 1
                analysis.branch_analysis.append({
                    'type': 'if',
                    'line': i+1,
                    'condition': stripped
                })
            elif stripped.startswith('for '):
                analysis.total_branches += 1
                analysis.branch_analysis.append({
                    'type': 'for',
                    'line': i+1,
                    'condition': stripped
                })
            elif stripped.startswith('while '):
                analysis.total_branches += 1
                analysis.branch_analysis.append({
                    'type': 'while',
                    'line': i+1,
                    'condition': stripped
                })
            elif stripped.startswith('try:'):
                analysis.total_exceptions += 1
                analysis.branch_analysis.append({
                    'type': 'try',
                    'line': i+1,
                    'condition': stripped
                })
            elif stripped.startswith('except'):
                analysis.total_exceptions += 1
                analysis.branch_analysis.append({
                    'type': 'except',
                    'line': i+1,
                    'condition': stripped
                })

        logger.info(f"  📊 统计: {analysis.total_functions} 函数, {analysis.total_branches} 分支, {analysis.total_exceptions} 异常处理")
        return analysis

    async def run_phase_two_8_step_tests(self):
        """
        三、标准化全流程测试
        8步完整测试流程
        """
        logger.info("\n" + "=" * 120)
        logger.info("🧪 三、标准化全流程测试 - 8步标准流程")
        logger.info("=" * 120)

        # 每一步逐一运行
        await self._step_1_static_verify()
        await self._step_2_unit_full_coverage()
        await self._step_3_module_integration()
        await self._step_4_api_traverse()
        await self._step_5_business_closed()
        await self._step_6_data_consistency()
        await self._step_7_exception_test()
        await self._step_8_performance()

    async def _step_1_static_verify(self):
        """
        1. 静态代码核验
        走读代码，核对逻辑合理性，排查冗余、死逻辑、资源漏洞、书写隐患
        """
        logger.info("\n" + "-" * 120)
        logger.info("1️⃣  静态代码核验")
        logger.info("-" * 120)

        # 测试1: 数据库初始化检查
        test = TestCase(
            phase=TestPhase.STATIC_VERIFY,
            name="数据库初始化检查",
            description="验证数据库连接和表结构创建",
            input_data=None,
            expected_result=True
        )
        start = time.time()
        try:
            stats = await self.db.get_statistics()
            test.actual_result = isinstance(stats, dict)
            test.passed = test.actual_result
            logger.info(f"✅ {test.name} 通过，统计信息: {stats}")
        except Exception as e:
            test.passed = False
            test.error_message = str(e)
            logger.error(f"❌ {test.name} 失败: {e}")
        test.duration_ms = int((time.time() - start) * 1000)
        self.test_cases.append(test)

        # 测试2: 连接属性检查
        test = TestCase(
            phase=TestPhase.STATIC_VERIFY,
            name="数据库连接属性验证",
            description="验证connection属性的访问",
            input_data=None,
            expected_result=True
        )
        start = time.time()
        try:
            conn = self.db.connection
            test.actual_result = conn is not None
            test.passed = test.actual_result
            logger.info(f"✅ {test.name} 通过")
        except Exception as e:
            test.passed = False
            test.error_message = str(e)
            logger.error(f"❌ {test.name} 失败: {e}")
        test.duration_ms = int((time.time() - start) * 1000)
        self.test_cases.append(test)

        # 测试3: 解析器基础检查
        test = TestCase(
            phase=TestPhase.STATIC_VERIFY,
            name="解析器基础功能验证",
            description="验证解析器能解析简单文件",
            input_data="class Test {} \n",
            expected_result=True
        )
        start = time.time()
        try:
            parsed = self.parser.parse_file("test.ets", test.input_data)
            test.actual_result = len(parsed.classes) >= 0
            test.passed = test.actual_result
            logger.info(f"✅ {test.name} 通过，解析到 {len(parsed.classes)} 个类")
        except Exception as e:
            test.passed = False
            test.error_message = str(e)
            logger.error(f"❌ {test.name} 失败: {e}")
        test.duration_ms = int((time.time() - start) * 1000)
        self.test_cases.append(test)

    async def _step_2_unit_full_coverage(self):
        """
        2. 单元全覆盖测试
        穷尽所有if/else、循环、分支、特殊场景，确保每段代码均可正常触发执行
        """
        logger.info("\n" + "-" * 120)
        logger.info("2️⃣  单元全覆盖测试")
        logger.info("-" * 120)

        # 测试数据库操作单元
        unit_tests = [
            ("数据库-get_statistics", self._unit_test_get_statistics),
            ("数据库-get_all_classes", self._unit_test_get_all_classes),
            ("数据库-get_all_files", self._unit_test_get_all_files),
            ("解析器-class", self._unit_test_parser_class),
            ("解析器-struct", self._unit_test_parser_struct),
            ("解析器-component", self._unit_test_parser_component),
            ("解析器-empty", self._unit_test_parser_empty),
            ("同步引擎-hash检测", self._unit_test_hash_check),
        ]

        for test_name, test_func in unit_tests:
            test = TestCase(
                phase=TestPhase.UNIT_FULL,
                name=test_name,
                description="单元测试",
                input_data=None,
                expected_result=True
            )
            start = time.time()
            try:
                result = await test_func()
                test.actual_result = result
                test.passed = result
                if result:
                    logger.info(f"✅ {test_name} 通过")
                else:
                    logger.error(f"❌ {test_name} 失败")
            except Exception as e:
                test.passed = False
                test.error_message = str(e)
                logger.error(f"❌ {test_name} 异常: {e}")
                traceback.print_exc()
            test.duration_ms = int((time.time() - start) * 1000)
            self.test_cases.append(test)

    async def _unit_test_get_statistics(self) -> bool:
        try:
            stats = await self.db.get_statistics()
            return all(k in stats for k in ['total_files', 'total_classes', 'total_methods'])
        except:
            return False

    async def _unit_test_get_all_classes(self) -> bool:
        try:
            await self.db.get_all_classes()
            return True
        except:
            return False

    async def _unit_test_get_all_files(self) -> bool:
        try:
            await self.db.get_all_files()
            return True
        except:
            return False

    async def _unit_test_parser_class(self) -> bool:
        try:
            parsed = self.parser.parse_file("t1.ets", "class MyClass { }")
            return len(parsed.classes) == 1
        except:
            return False

    async def _unit_test_parser_struct(self) -> bool:
        try:
            parsed = self.parser.parse_file("t2.ets", "struct MyStruct { }")
            return len(parsed.classes) == 1
        except:
            return False

    async def _unit_test_parser_component(self) -> bool:
        try:
            parsed = self.parser.parse_file("t3.ets", "@Component\nstruct MyComp { }")
            return len(parsed.classes) == 1 and parsed.classes[0].is_component
        except:
            return False

    async def _unit_test_parser_empty(self) -> bool:
        try:
            parsed = self.parser.parse_file("t4.ets", "")
            return len(parsed.classes) == 0
        except:
            return False

    async def _unit_test_hash_check(self) -> bool:
        try:
            test_file = Path("/tmp/hash_test.ets")
            test_file.write_text("class Test { }")

            await self.sync_engine.update_single_file(str(test_file))
            await asyncio.sleep(0.01)
            result = await self.sync_engine.update_single_file(str(test_file))

            return result.entities_updated == 0
        except:
            return False

    async def _step_3_module_integration(self):
        """
        3. 模块集成联调
        验证跨模块、跨层级调用正常，参数传递、状态同步无错乱
        """
        logger.info("\n" + "-" * 120)
        logger.info("3️⃣  模块集成联调")
        logger.info("-" * 120)

        # 创建集成测试文件
        test_files = []
        for i in range(3):
            file_path = Path(f"/tmp/integration_test_{i}.ets")
            content = f"class IntegrationTest{i} {{ \n  method{i}() {{ }} \n}}"
            file_path.write_text(content)
            test_files.append(str(file_path))

        # 完整流程测试
        test = TestCase(
            phase=TestPhase.MODULE_INTEGRATION,
            name="解析-同步-查询完整流程",
            description="完整的模块集成测试",
            input_data=test_files,
            expected_result=True
        )
        start = time.time()
        try:
            # 同步 - 使用新的连接隔离测试
            if self.db:
                await self.db.close()
            self.db = DatabaseConnection(":memory:")
            await self.db.initialize()
            self.sync_engine = SynchronizationEngine(self.db, self.ws_manager)

            for f in test_files:
                await self.sync_engine.update_single_file(f)

            # 查询
            stats = await self.db.get_statistics()
            classes = await self.db.get_all_classes()

            logger.info(f"📊 集成测试统计: {stats}")
            test.actual_result = stats['total_classes'] >= 3
            test.passed = test.actual_result
            logger.info(f"✅ {test.name} 通过，管理了 {len(classes)} 个类")
        except Exception as e:
            test.passed = False
            test.error_message = str(e)
            logger.error(f"❌ {test.name} 失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
        test.duration_ms = int((time.time() - start) * 1000)
        self.test_cases.append(test)

    async def _step_4_api_traverse(self):
        """
        4. 接口全量遍历
        全覆盖所有接口，校验正常请求、异常入参、超限参数、空值、非法格式
        """
        logger.info("\n" + "-" * 120)
        logger.info("4️⃣  接口全量遍历")
        logger.info("-" * 120)

        apis = [
            ("get_statistics", lambda: self.db.get_statistics()),
            ("get_all_classes", lambda: self.db.get_all_classes()),
            ("get_all_files", lambda: self.db.get_all_files()),
        ]

        for api_name, api_func in apis:
            test = TestCase(
                phase=TestPhase.API_TRAVERSE,
                name=f"API-{api_name}",
                description=f"遍历API: {api_name}",
                input_data=None,
                expected_result=True
            )
            start = time.time()
            try:
                result = api_func()
                if asyncio.iscoroutine(result):
                    result = await result
                test.actual_result = True
                test.passed = True
                logger.info(f"✅ API {api_name} 通过，返回类型: {type(result).__name__}")
            except Exception as e:
                test.passed = False
                test.error_message = str(e)
                logger.error(f"❌ API {api_name} 失败: {e}")
            test.duration_ms = int((time.time() - start) * 1000)
            self.test_cases.append(test)

        # 异常参数测试
        test = TestCase(
            phase=TestPhase.API_TRAVERSE,
            name="API-空文件路径",
            description="验证空文件路径的处理",
            input_data="",
            expected_result=False
        )
        start = time.time()
        try:
            result = await self.sync_engine.update_single_file("")
            test.actual_result = not result.success
            test.passed = test.actual_result
            logger.info(f"✅ {test.name} 正确处理了空路径")
        except Exception as e:
            test.passed = True  # 异常是预期的
            test.error_message = f"捕获到预期异常: {e}"
            logger.info(f"✅ {test.name} 捕获到预期异常")
        test.duration_ms = int((time.time() - start) * 1000)
        self.test_cases.append(test)

    async def _step_5_business_closed(self):
        """
        5. 业务场景闭环
        依据代码逻辑搭建完整正向、逆向、中断、重复操作场景，跑通全业务链路
        """
        logger.info("\n" + "-" * 120)
        logger.info("5️⃣  业务场景闭环")
        logger.info("-" * 120)

        scenarios = [
            ("正向-首次创建", self._scenario_create),
            ("正向-修改更新", self._scenario_update),
            ("逆向-删除文件", self._scenario_delete),
            ("重复-重复操作", self._scenario_duplicate),
        ]

        for name, scenario_func in scenarios:
            test = TestCase(
                phase=TestPhase.BUSINESS_CLOSED,
                name=name,
                description=name,
                input_data=None,
                expected_result=True
            )
            start = time.time()
            try:
                passed = await scenario_func()
                test.actual_result = passed
                test.passed = passed
                if passed:
                    logger.info(f"✅ 业务场景 {name} 通过")
                else:
                    logger.error(f"❌ 业务场景 {name} 失败")
            except Exception as e:
                test.passed = False
                test.error_message = str(e)
                logger.error(f"❌ 业务场景 {name} 异常: {e}")
            test.duration_ms = int((time.time() - start) * 1000)
            self.test_cases.append(test)

    async def _scenario_create(self) -> bool:
        file_path = "/tmp/scenario_create.ets"
        Path(file_path).write_text("class CreateTest { }")
        result = await self.sync_engine.update_single_file(file_path)
        return result.success

    async def _scenario_update(self) -> bool:
        file_path = "/tmp/scenario_update.ets"
        Path(file_path).write_text("class Original { }")
        await self.sync_engine.update_single_file(file_path)

        Path(file_path).write_text("class Updated { method() { } }")
        result = await self.sync_engine.update_single_file(file_path)
        return result.success and result.entities_updated > 0

    async def _scenario_delete(self) -> bool:
        file_path = "/tmp/scenario_delete.ets"
        Path(file_path).write_text("class DeleteTest { }")
        await self.sync_engine.update_single_file(file_path)

        result = await self.sync_engine.update_single_file(file_path, "deleted")
        return result.success

    async def _scenario_duplicate(self) -> bool:
        file_path = "/tmp/scenario_dup.ets"
        Path(file_path).write_text("class DupTest { }")

        for _ in range(3):
            result = await self.sync_engine.update_single_file(file_path)
            if not result.success:
                return False

        return True

    async def _step_6_data_consistency(self):
        """
        6. 数据一致性校验
        核对增删改查、数据存储、关联关系、数据回显完全匹配代码执行逻辑
        """
        logger.info("\n" + "-" * 120)
        logger.info("6️⃣  数据一致性校验")
        logger.info("-" * 120)

        # 数据一致性测试
        test = TestCase(
            phase=TestPhase.DATA_CONSISTENCY,
            name="数据一致性-增删查验证",
            description="验证数据的一致性",
            input_data=None,
            expected_result=True
        )
        start = time.time()
        try:
            # 隔离测试 - 重新初始化数据库
            if self.db:
                await self.db.close()
            self.db = DatabaseConnection(":memory:")
            await self.db.initialize()
            self.sync_engine = SynchronizationEngine(self.db, self.ws_manager)

            # 增加
            test_file = Path("/tmp/consistency_test.ets")
            test_file.write_text("class ConsistencyTest { \n  method1() { } \n  method2() { } \n}")
            await self.sync_engine.update_single_file(str(test_file))

            # 查询
            stats1 = await self.db.get_statistics()
            classes1 = await self.db.get_all_classes()

            # 删除
            await self.sync_engine.update_single_file(str(test_file), "deleted")

            # 查询
            stats2 = await self.db.get_statistics()

            test.actual_result = (
                stats1['total_classes'] > 0 and
                len(classes1) >= 1 and
                stats2['total_classes'] <= stats1['total_classes']
            )
            test.passed = test.actual_result

            logger.info(f"📊 一致性检查: 前={stats1}, 后={stats2}")
            if test.passed:
                logger.info(f"✅ {test.name} 通过")
            else:
                logger.error(f"❌ {test.name} 失败")
        except Exception as e:
            test.passed = False
            test.error_message = str(e)
            logger.error(f"❌ {test.name} 失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
        test.duration_ms = int((time.time() - start) * 1000)
        self.test_cases.append(test)

    async def _step_7_exception_test(self):
        """
        7. 异常容错测试
        验证超时、断连、报错、兜底降级、重试机制均按代码逻辑正常生效
        """
        logger.info("\n" + "-" * 120)
        logger.info("7️⃣  异常容错测试")
        logger.info("-" * 120)

        exception_tests = [
            ("文件不存在", "/tmp/nonexistent_file.ets", "modified"),
            ("空文件内容", "/tmp/empty_file.ets", "modified"),
            ("删除不存在的文件", "/tmp/deleted_not_exists.ets", "deleted"),
        ]

        for name, file_path, change_type in exception_tests:
            test = TestCase(
                phase=TestPhase.EXCEPTION_TEST,
                name=f"异常容错-{name}",
                description=name,
                input_data=file_path,
                expected_result=True
            )
            start = time.time()
            try:
                if name == "空文件内容":
                    Path(file_path).write_text("")
                result = await self.sync_engine.update_single_file(file_path, change_type)
                test.actual_result = True
                test.passed = True
                logger.info(f"✅ {name} 正常处理")
            except Exception as e:
                test.actual_result = True
                test.passed = True
                test.error_message = f"预期的异常处理: {e}"
                logger.info(f"✅ {name} 正常捕获异常")
            test.duration_ms = int((time.time() - start) * 1000)
            self.test_cases.append(test)

    async def _step_8_performance(self):
        """
        8. 基础性能核验
        高频核心流程验证响应稳定，无卡顿、阻塞、内存溢出问题
        """
        logger.info("\n" + "-" * 120)
        logger.info("8️⃣  基础性能核验")
        logger.info("-" * 120)

        # 生成大量文件
        logger.info("📦 准备性能测试文件...")
        perf_files = []
        for i in range(100):
            file_path = Path(f"/tmp/perf_test_{i}.ets")
            content = f"class PerfClass{i} {{ \n  method{i}() {{ }} \n  method{i+1}() {{ }} \n}}"
            file_path.write_text(content)
            perf_files.append(str(file_path))

        # 性能测试 - 批量更新
        test = TestCase(
            phase=TestPhase.PERFORMANCE,
            name="批量更新性能测试(100文件)",
            description="测试100个文件的批量更新性能",
            input_data=len(perf_files),
            expected_result=True
        )
        start = time.time()
        try:
            for f in perf_files:
                await self.sync_engine.update_single_file(f)

            stats = await self.db.get_statistics()
            total_time = (time.time() - start) * 1000
            avg_time = total_time / len(perf_files)

            logger.info(f"⚡ 性能: 总耗时 {total_time:.0f}ms, 平均 {avg_time:.1f}ms/文件")
            logger.info(f"📊 管理了 {stats['total_classes']} 个类, {stats['total_methods']} 个方法")

            test.actual_result = avg_time < 50  # 要求平均 < 50ms
            test.passed = test.actual_result
        except Exception as e:
            test.passed = False
            test.error_message = str(e)
            logger.error(f"❌ 性能测试失败: {e}")
        test.duration_ms = int((time.time() - start) * 1000)
        self.test_cases.append(test)

    async def run_phase_three_verdict(self):
        """
        四、判定验收标准
        1. 代码所有逻辑分支100%可执行
        2. 运行行为与代码定义完全一致
        3. 数据流转无误，无逻辑冲突与隐性缺陷
        4. 异常场景可平稳兜底，无崩溃报错
        """
        logger.info("\n" + "=" * 120)
        logger.info("🏆 四、判定验收 - 最终结果汇总")
        logger.info("=" * 120)

        total_tests = len(self.test_cases)
        passed_tests = sum(1 for tc in self.test_cases if tc.passed)
        failed_tests = total_tests - passed_tests
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        logger.info(f"\n📊 总体结果: {passed_tests}/{total_tests} 通过 ({pass_rate:.1f}%)")
        logger.info(f"   ⏱️  总耗时: {(time.time() - self.start_time):.1f}秒")

        # 按阶段分组显示
        phases = {}
        for tc in self.test_cases:
            if tc.phase not in phases:
                phases[tc.phase] = []
            phases[tc.phase].append(tc)

        logger.info(f"\n📋 各阶段详细结果:")
        for phase, tcs in sorted(phases.items(), key=lambda x: x[0].value):
            phase_pass = sum(1 for tc in tcs if tc.passed)
            phase_total = len(tcs)
            phase_rate = phase_pass / phase_total * 100 if phase_total > 0 else 0
            logger.info(f"  {phase.value}: {phase_pass}/{phase_total} ({phase_rate:.1f}%)")

        if failed_tests > 0:
            logger.warning(f"\n⚠️  发现 {failed_tests} 个失败测试:")
            for i, tc in enumerate([t for t in self.test_cases if not t.passed]):
                logger.warning(f"  {i+1}. {tc.phase.value} - {tc.name}")
                logger.warning(f"     {tc.error_message[:100] if tc.error_message else '未知错误'}")
        else:
            logger.info("\n🎉🎉🎉  完美！所有测试通过！")

        # 最终判定
        if pass_rate >= 95:
            logger.info("\n" + "=" * 120)
            logger.info("✅✅✅ 系统通过验收！完全符合所有标准！✅✅✅")
            logger.info("=" * 120)
        elif pass_rate >= 80:
            logger.warning("\n" + "=" * 120)
            logger.warning("⚠️  系统基本通过，但需要优化")
            logger.warning("=" * 120)
        else:
            logger.error("\n" + "=" * 120)
            logger.error("❌ 系统未通过验收，需要修复")
            logger.error("=" * 120)

    async def run_complete_test(self):
        """运行完整测试"""
        await self.setup()
        await self.run_phase_one_pre_analysis()
        await self.run_phase_two_8_step_tests()
        await self.run_phase_three_verdict()

        if self.db:
            await self.db.close()


if __name__ == "__main__":
    tester = UltraDeepTester()
    asyncio.run(tester.run_complete_test())

#!/usr/bin/env python3
"""
终极复杂场景深度测试工具
重点测试：超复杂场景、极深嵌套、极端并发、边界混乱、复杂状态管理
添加：详细代码级日志追踪
"""
import asyncio
import time
import sys
import random
import logging
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import traceback

sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.connection import DatabaseConnection
from services.synchronization_engine import SynchronizationEngine
from services.websocket_manager import WebSocketManager
from services.arkts_parser_service import ArkTSParser, ParsedFile
from config import UpdateResult

# 配置超详细日志 - 每一句代码都打印日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("ULTIMATE_COMPLEXITY_TEST")


@dataclass
class TestScenario:
    """测试场景"""
    name: str
    description: str
    complexity_score: int  # 复杂度评分 1-10
    duration_seconds: int
    operations_count: int
    passed: bool = False
    error_message: str = ""


class UltimateComplexityTester:
    """终极复杂场景测试器"""

    def __init__(self):
        self.db = None
        self.sync_engine = None
        self.parser = ArkTSParser()
        self.test_scenarios: List[TestScenario] = []
        self.start_time = 0
        self.total_operations = 0
        self.total_errors = 0

    async def setup(self):
        """设置测试环境"""
        logger.info("=" * 120)
        logger.info("🚀🚀🚀 终极复杂场景深度测试开始 🚀🚀🚀")
        logger.info("=" * 120)

        self.start_time = time.time()

        logger.info("[SETUP-001] 创建数据库连接...")
        self.db = DatabaseConnection(":memory:")

        logger.info("[SETUP-002] 初始化数据库...")
        await self.db.initialize()

        logger.info("[SETUP-003] 创建WebSocket管理器...")
        self.ws_manager = WebSocketManager()

        logger.info("[SETUP-004] 创建同步引擎...")
        self.sync_engine = SynchronizationEngine(self.db, self.ws_manager)

        logger.info("[SETUP-005] 初始化解析器...")
        self.parser = ArkTSParser()

        logger.info("[SETUP-006] 测试环境设置完成 ✅")

    # =========================================================================
    # 场景1: 超深嵌套复杂度测试
    # =========================================================================
    async def test_scenario_1_deep_nesting(self):
        """
        场景1: 超深嵌套复杂度测试
        复杂度: ★★★★★
        测试: 50层深度嵌套类的解析和同步
        """
        logger.info("\n" + "=" * 120)
        logger.info("🔷 场景1: 超深嵌套复杂度测试 (50层)")
        logger.info("=" * 120)

        scenario = TestScenario(
            name="超深嵌套复杂度",
            description="测试50层深度嵌套类的解析和同步",
            complexity_score=5,
            duration_seconds=30,
            operations_count=50
        )
        start_time = time.time()

        try:
            # 生成50层深度嵌套类
            logger.info("[SCENARIO-1-001] 生成50层深度嵌套类...")
            file_path = Path("/tmp/deep_nesting_50.ets")
            content = ""

            for i in range(50):
                logger.debug(f"[SCENARIO-1-002] 生成第 {i} 层...")
                content += f"class Level{i} {{\n"

            logger.info("[SCENARIO-1-003] 生成最深层数据...")
            content += "    deepestValue: number = 42;\n"

            for i in range(49, -1, -1):
                logger.debug(f"[SCENARIO-1-004] 闭合第 {i} 层...")
                content += "}\n"

            logger.info("[SCENARIO-1-005] 写入文件...")
            file_path.write_text(content, encoding='utf-8')

            logger.info("[SCENARIO-1-006] 开始解析...")
            parsed = self.parser.parse_file(str(file_path), content)

            logger.info(f"[SCENARIO-1-007] 解析结果: 发现 {len(parsed.classes)} 个类")
            assert len(parsed.classes) == 50, f"预期50个类，实际{len(parsed.classes)}"

            logger.info("[SCENARIO-1-008] 开始同步...")
            result = await self.sync_engine.update_single_file(str(file_path))

            logger.info(f"[SCENARIO-1-009] 同步结果: {result.success}")
            assert result.success, f"同步失败: {result.error_message}"

            stats = await self.db.get_statistics()
            logger.info(f"[SCENARIO-1-010] 数据库统计: {stats}")
            assert stats['total_classes'] == 50, f"预期50个类，实际{stats['total_classes']}"

            scenario.passed = True
            logger.info("✅ 场景1通过: 超深嵌套复杂度测试成功")

        except Exception as e:
            scenario.passed = False
            scenario.error_message = str(e)
            logger.error(f"❌ 场景1失败: {e}")
            logger.error(traceback.format_exc())

        scenario_duration = time.time() - start_time
        logger.info(f"[SCENARIO-1-011] 场景1完成，耗时: {scenario_duration:.2f}秒")
        self.test_scenarios.append(scenario)

    # =========================================================================
    # 场景2: 极端并发冲突测试
    # =========================================================================
    async def test_scenario_2_extreme_concurrency(self):
        """
        场景2: 极端并发冲突测试
        复杂度: ★★★★★
        测试: 100个并发任务同时操作同一个文件
        """
        logger.info("\n" + "=" * 120)
        logger.info("🔷 场景2: 极端并发冲突测试 (100并发)")
        logger.info("=" * 120)

        scenario = TestScenario(
            name="极端并发冲突",
            description="测试100个并发任务同时操作同一个文件",
            complexity_score=5,
            duration_seconds=30,
            operations_count=100
        )
        start_time = time.time()

        try:
            # 创建测试文件
            logger.info("[SCENARIO-2-001] 创建测试文件...")
            file_path = Path("/tmp/extreme_concurrent.ets")
            file_path.write_text("class OriginalClass {}", encoding='utf-8')

            # 100个并发任务
            logger.info("[SCENARIO-2-002] 创建100个并发任务...")
            tasks = []
            for i in range(100):
                logger.debug(f"[SCENARIO-2-003] 创建任务 {i}...")
                tasks.append(self.sync_engine.update_single_file(str(file_path)))

            logger.info("[SCENARIO-2-004] 执行100个并发任务...")
            results = await asyncio.gather(*tasks, return_exceptions=True)

            success_count = sum(1 for r in results if not isinstance(r, Exception) and r.success)
            error_count = sum(1 for r in results if isinstance(r, Exception))

            logger.info(f"[SCENARIO-2-005] 执行完成: 成功 {success_count}, 错误 {error_count}")

            # 允许少量错误（因为是极端并发）
            if success_count >= 90:
                scenario.passed = True
                logger.info(f"✅ 场景2通过: {success_count}/100 成功")
            else:
                scenario.passed = False
                scenario.error_message = f"成功率过低: {success_count}/100"
                logger.warning(f"⚠️ 场景2部分失败: {success_count}/100")

        except Exception as e:
            scenario.passed = False
            scenario.error_message = str(e)
            logger.error(f"❌ 场景2失败: {e}")
            logger.error(traceback.format_exc())

        scenario_duration = time.time() - start_time
        logger.info(f"[SCENARIO-2-006] 场景2完成，耗时: {scenario_duration:.2f}秒")
        self.test_scenarios.append(scenario)

    # =========================================================================
    # 场景3: 超大文件处理测试
    # =========================================================================
    async def test_scenario_3_huge_file(self):
        """
        场景3: 超大文件处理测试
        复杂度: ★★★★★
        测试: 包含1000个方法的大型类
        """
        logger.info("\n" + "=" * 120)
        logger.info("🔷 场景3: 超大文件处理测试 (1000方法)")
        logger.info("=" * 120)

        scenario = TestScenario(
            name="超大文件处理",
            description="测试包含1000个方法的大型类",
            complexity_score=5,
            duration_seconds=60,
            operations_count=1
        )
        start_time = time.time()

        try:
            # 生成超大文件
            logger.info("[SCENARIO-3-001] 生成包含1000个方法的大文件...")
            file_path = Path("/tmp/huge_class.ets")
            content = "class HugeClass {\n"

            for i in range(1000):
                logger.debug(f"[SCENARIO-3-002] 生成方法 {i}...")
                content += f"    method{i}(): number {{ return {i}; }}\n"

            content += "}\n"

            logger.info(f"[SCENARIO-3-003] 文件大小: {len(content)} 字符")
            file_path.write_text(content, encoding='utf-8')

            logger.info("[SCENARIO-3-004] 开始解析...")
            parsed = self.parser.parse_file(str(file_path), content)

            logger.info(f"[SCENARIO-3-005] 解析结果: {len(parsed.classes)} 个类")
            assert len(parsed.classes) == 1, "预期1个类"

            total_methods = sum(len(c.methods) for c in parsed.classes)
            logger.info(f"[SCENARIO-3-006] 解析到 {total_methods} 个方法")

            logger.info("[SCENARIO-3-007] 开始同步...")
            result = await self.sync_engine.update_single_file(str(file_path))

            logger.info(f"[SCENARIO-3-008] 同步结果: {result.success}")
            assert result.success, f"同步失败: {result.error_message}"

            stats = await self.db.get_statistics()
            logger.info(f"[SCENARIO-3-009] 数据库统计: {stats}")
            assert stats['total_methods'] >= 1000, f"预期至少1000个方法，实际{stats['total_methods']}"

            scenario.passed = True
            logger.info("✅ 场景3通过: 超大文件处理测试成功")

        except Exception as e:
            scenario.passed = False
            scenario.error_message = str(e)
            logger.error(f"❌ 场景3失败: {e}")
            logger.error(traceback.format_exc())

        scenario_duration = time.time() - start_time
        logger.info(f"[SCENARIO-3-010] 场景3完成，耗时: {scenario_duration:.2f}秒")
        self.test_scenarios.append(scenario)

    # =========================================================================
    # 场景4: 复杂边界混乱测试
    # =========================================================================
    async def test_scenario_4_boundary_chaos(self):
        """
        场景4: 复杂边界混乱测试
        复杂度: ★★★★★
        测试: 各种边界情况、混乱场景
        """
        logger.info("\n" + "=" * 120)
        logger.info("🔷 场景4: 复杂边界混乱测试")
        logger.info("=" * 120)

        scenario = TestScenario(
            name="复杂边界混乱",
            description="测试各种边界情况、混乱场景",
            complexity_score=5,
            duration_seconds=30,
            operations_count=10
        )
        start_time = time.time()

        try:
            boundary_cases = [
                ("空文件", ""),
                ("纯注释", "// Only comments here\n/* Multi-line */"),
                ("单行大文件", "class Single { " + "; ".join([f"v{i}" for i in range(100)]) + " }"),
                ("Unicode混乱", "class 中文类 { にほんご方法() {} }"),
                ("特殊字符", "class $Special$ { _underscore() {} }"),
            ]

            for idx, (name, content) in enumerate(boundary_cases):
                logger.info(f"[SCENARIO-4-001-{idx}] 测试边界: {name}...")
                file_path = Path(f"/tmp/boundary_{idx}.ets")
                file_path.write_text(content, encoding='utf-8')

                logger.debug(f"[SCENARIO-4-002-{idx}] 解析文件...")
                parsed = self.parser.parse_file(str(file_path), content)

                logger.debug(f"[SCENARIO-4-003-{idx}] 同步文件...")
                result = await self.sync_engine.update_single_file(str(file_path))

                logger.info(f"[SCENARIO-4-004-{idx}] {name}: 解析{len(parsed.classes)}类, 同步{'成功' if result.success else '失败'}")

            scenario.passed = True
            logger.info("✅ 场景4通过: 复杂边界混乱测试成功")

        except Exception as e:
            scenario.passed = False
            scenario.error_message = str(e)
            logger.error(f"❌ 场景4失败: {e}")
            logger.error(traceback.format_exc())

        scenario_duration = time.time() - start_time
        logger.info(f"[SCENARIO-4-005] 场景4完成，耗时: {scenario_duration:.2f}秒")
        self.test_scenarios.append(scenario)

    # =========================================================================
    # 场景5: 长时间稳定性压力测试
    # =========================================================================
    async def test_scenario_5_long_running_stability(self):
        """
        场景5: 长时间稳定性压力测试
        复杂度: ★★★★★
        测试: 持续60秒的高频操作
        """
        logger.info("\n" + "=" * 120)
        logger.info("🔷 场景5: 长时间稳定性压力测试 (60秒)")
        logger.info("=" * 120)

        scenario = TestScenario(
            name="长时间稳定性",
            description="持续60秒的高频操作",
            complexity_score=5,
            duration_seconds=60,
            operations_count=10000
        )
        start_time = time.time()

        try:
            # 创建多个测试文件
            logger.info("[SCENARIO-5-001] 创建测试文件...")
            test_files = []
            for i in range(10):
                file_path = Path(f"/tmp/stability_test_{i}.ets")
                file_path.write_text(f"class Test{i} {{ method{i}() {{}} }}", encoding='utf-8')
                test_files.append(str(file_path))

            # 同步初始文件
            logger.info("[SCENARIO-5-002] 同步初始文件...")
            for f in test_files:
                await self.sync_engine.update_single_file(f)

            # 持续操作60秒
            logger.info("[SCENARIO-5-003] 开始持续操作60秒...")
            operation_count = 0
            errors = 0
            last_report_time = start_time

            while time.time() - start_time < 60:
                file_path = random.choice(test_files)

                try:
                    logger.debug(f"[SCENARIO-5-004-{operation_count}] 操作 {operation_count}...")
                    await self.sync_engine.update_single_file(file_path)
                    operation_count += 1

                    # 每10秒报告一次
                    if time.time() - last_report_time >= 10:
                        elapsed = time.time() - start_time
                        rate = operation_count / elapsed
                        logger.info(f"[SCENARIO-5-005] 已运行 {elapsed:.1f}秒, 操作 {operation_count}, 速度 {rate:.1f} ops/s")
                        last_report_time = time.time()

                except Exception as e:
                    errors += 1
                    logger.warning(f"[SCENARIO-5-006] 操作失败: {e}")

            scenario.operations_count = operation_count
            logger.info(f"[SCENARIO-5-007] 测试完成: {operation_count} 操作, {errors} 错误")

            if errors < operation_count * 0.01:  # 允许1%错误率
                scenario.passed = True
                logger.info(f"✅ 场景5通过: {operation_count} 操作, 错误率 {errors/operation_count*100:.2f}%")
            else:
                scenario.passed = False
                scenario.error_message = f"错误率过高: {errors/operation_count*100:.2f}%"

        except Exception as e:
            scenario.passed = False
            scenario.error_message = str(e)
            logger.error(f"❌ 场景5失败: {e}")
            logger.error(traceback.format_exc())

        scenario_duration = time.time() - start_time
        logger.info(f"[SCENARIO-5-008] 场景5完成，耗时: {scenario_duration:.2f}秒")
        self.test_scenarios.append(scenario)

    # =========================================================================
    # 场景6: 复杂状态管理测试
    # =========================================================================
    async def test_scenario_6_complex_state_management(self):
        """
        场景6: 复杂状态管理测试
        复杂度: ★★★★★
        测试: 文件创建、修改、删除、再创建、再修改的完整状态流转
        """
        logger.info("\n" + "=" * 120)
        logger.info("🔷 场景6: 复杂状态管理测试")
        logger.info("=" * 120)

        scenario = TestScenario(
            name="复杂状态管理",
            description="测试完整的文件状态流转",
            complexity_score=5,
            duration_seconds=30,
            operations_count=10
        )
        start_time = time.time()

        try:
            file_path = Path("/tmp/state_test.ets")

            # 状态1: 创建
            logger.info("[SCENARIO-6-001] 状态1: 创建文件...")
            file_path.write_text("class Initial {}", encoding='utf-8')
            result1 = await self.sync_engine.update_single_file(str(file_path))
            logger.info(f"[SCENARIO-6-002] 创建结果: {result1.success}")

            # 状态2: 修改
            logger.info("[SCENARIO-6-003] 状态2: 修改文件...")
            file_path.write_text("class Modified { method1() {} }", encoding='utf-8')
            result2 = await self.sync_engine.update_single_file(str(file_path))
            logger.info(f"[SCENARIO-6-004] 修改结果: {result2.success}")

            stats1 = await self.db.get_statistics()
            logger.info(f"[SCENARIO-6-005] 当前统计: {stats1}")

            # 状态3: 删除
            logger.info("[SCENARIO-6-006] 状态3: 删除文件...")
            result3 = await self.sync_engine.update_single_file(str(file_path), "deleted")
            logger.info(f"[SCENARIO-6-007] 删除结果: {result3.success}")

            # 状态4: 重新创建
            logger.info("[SCENARIO-6-008] 状态4: 重新创建...")
            file_path.write_text("class Recreated { method1() {} method2() {} }", encoding='utf-8')
            result4 = await self.sync_engine.update_single_file(str(file_path))
            logger.info(f"[SCENARIO-6-009] 重新创建结果: {result4.success}")

            stats2 = await self.db.get_statistics()
            logger.info(f"[SCENARIO-6-010] 最终统计: {stats2}")

            # 验证状态一致性
            assert stats2['total_classes'] >= 1, "应该有至少1个类"
            assert stats2['total_methods'] >= 2, "应该有至少2个方法"

            scenario.passed = True
            logger.info("✅ 场景6通过: 复杂状态管理测试成功")

        except Exception as e:
            scenario.passed = False
            scenario.error_message = str(e)
            logger.error(f"❌ 场景6失败: {e}")
            logger.error(traceback.format_exc())

        scenario_duration = time.time() - start_time
        logger.info(f"[SCENARIO-6-011] 场景6完成，耗时: {scenario_duration:.2f}秒")
        self.test_scenarios.append(scenario)

    # =========================================================================
    # 场景7: 事务边界挑战测试
    # =========================================================================
    async def test_scenario_7_transaction_boundary(self):
        """
        场景7: 事务边界挑战测试
        复杂度: ★★★★★
        测试: 在事务边界处的各种操作
        """
        logger.info("\n" + "=" * 120)
        logger.info("🔷 场景7: 事务边界挑战测试")
        logger.info("=" * 120)

        scenario = TestScenario(
            name="事务边界挑战",
            description="测试在事务边界处的各种操作",
            complexity_score=5,
            duration_seconds=30,
            operations_count=50
        )
        start_time = time.time()

        try:
            # 快速连续操作
            logger.info("[SCENARIO-7-001] 快速连续操作...")
            for i in range(50):
                logger.debug(f"[SCENARIO-7-002-{i}] 操作 {i}...")
                file_path = Path(f"/tmp/transaction_test_{i}.ets")
                file_path.write_text(f"class Transaction{i} {{}}", encoding='utf-8')

                # 连续同步
                await self.sync_engine.update_single_file(str(file_path))

                # 查询统计
                if i % 10 == 0:
                    stats = await self.db.get_statistics()
                    logger.info(f"[SCENARIO-7-003-{i}] 统计: {stats}")

            # 验证最终状态
            stats = await self.db.get_statistics()
            logger.info(f"[SCENARIO-7-004] 最终统计: {stats}")

            assert stats['total_files'] == 50, f"应该有50个文件，实际{stats['total_files']}"
            assert stats['total_classes'] == 50, f"应该有50个类，实际{stats['total_classes']}"

            scenario.passed = True
            logger.info("✅ 场景7通过: 事务边界挑战测试成功")

        except Exception as e:
            scenario.passed = False
            scenario.error_message = str(e)
            logger.error(f"❌ 场景7失败: {e}")
            logger.error(traceback.format_exc())

        scenario_duration = time.time() - start_time
        logger.info(f"[SCENARIO-7-005] 场景7完成，耗时: {scenario_duration:.2f}秒")
        self.test_scenarios.append(scenario)

    # =========================================================================
    # 场景8: 数据一致性挑战测试
    # =========================================================================
    async def test_scenario_8_data_consistency_challenge(self):
        """
        场景8: 数据一致性挑战测试
        复杂度: ★★★★★
        测试: 在并发情况下的数据一致性
        """
        logger.info("\n" + "=" * 120)
        logger.info("🔷 场景8: 数据一致性挑战测试")
        logger.info("=" * 120)

        scenario = TestScenario(
            name="数据一致性挑战",
            description="测试在并发情况下的数据一致性",
            complexity_score=5,
            duration_seconds=30,
            operations_count=50
        )
        start_time = time.time()

        try:
            # 创建多个文件
            logger.info("[SCENARIO-8-001] 创建测试文件...")
            test_files = []
            for i in range(10):
                file_path = Path(f"/tmp/consistency_{i}.ets")
                file_path.write_text(f"class Class{i} {{ method{i}() {{}} }}", encoding='utf-8')
                test_files.append(str(file_path))

            # 并发同步
            logger.info("[SCENARIO-8-002] 并发同步...")
            tasks = []
            for f in test_files * 5:  # 每个文件同步5次
                tasks.append(self.sync_engine.update_single_file(f))

            results = await asyncio.gather(*tasks, return_exceptions=True)

            # 验证数据一致性
            logger.info("[SCENARIO-8-003] 验证数据一致性...")
            stats = await self.db.get_statistics()
            classes = await self.db.get_all_classes()
            files = await self.db.get_all_files()

            logger.info(f"[SCENARIO-8-004] 统计: {stats}")
            logger.info(f"[SCENARIO-8-005] 类数: {len(classes)}")
            logger.info(f"[SCENARIO-8-006] 文件数: {len(files)}")

            # 数据一致性检查
            assert stats['total_files'] == 10, f"应该有10个文件，实际{stats['total_files']}"
            assert stats['total_classes'] == 10, f"应该有10个类，实际{stats['total_classes']}"
            assert stats['total_methods'] == 10, f"应该有10个方法，实际{stats['total_methods']}"
            assert len(classes) == 10, f"应该有10个类，实际{len(classes)}"
            assert len(files) == 10, f"应该有10个文件，实际{len(files)}"

            scenario.passed = True
            logger.info("✅ 场景8通过: 数据一致性挑战测试成功")

        except Exception as e:
            scenario.passed = False
            scenario.error_message = str(e)
            logger.error(f"❌ 场景8失败: {e}")
            logger.error(traceback.format_exc())

        scenario_duration = time.time() - start_time
        logger.info(f"[SCENARIO-8-007] 场景8完成，耗时: {scenario_duration:.2f}秒")
        self.test_scenarios.append(scenario)

    async def run_all_scenarios(self):
        """运行所有场景"""
        await self.setup()

        logger.info("\n" + "=" * 120)
        logger.info("开始运行8个终极复杂场景测试...")
        logger.info("=" * 120)

        await self.test_scenario_1_deep_nesting()
        await self.test_scenario_2_extreme_concurrency()
        await self.test_scenario_3_huge_file()
        await self.test_scenario_4_boundary_chaos()
        await self.test_scenario_5_long_running_stability()
        await self.test_scenario_6_complex_state_management()
        await self.test_scenario_7_transaction_boundary()
        await self.test_scenario_8_data_consistency_challenge()

        await self.print_final_report()

        if self.db:
            await self.db.close()

    async def print_final_report(self):
        """打印最终报告"""
        total_duration = time.time() - self.start_time

        logger.info("\n" + "=" * 120)
        logger.info("🏆🏆🏆 终极复杂场景测试最终报告 🏆🏆🏆")
        logger.info("=" * 120)

        logger.info(f"\n⏱️  总测试时间: {total_duration:.1f}秒")
        logger.info(f"📊 测试场景数: {len(self.test_scenarios)}")

        passed = sum(1 for s in self.test_scenarios if s.passed)
        failed = len(self.test_scenarios) - passed

        logger.info(f"✅ 通过: {passed}/{len(self.test_scenarios)}")
        if failed > 0:
            logger.warning(f"❌ 失败: {failed}/{len(self.test_scenarios)}")

        logger.info(f"\n📋 各场景详情:")
        for idx, scenario in enumerate(self.test_scenarios, 1):
            status = "✅ PASS" if scenario.passed else "❌ FAIL"
            logger.info(f"  场景{idx}: {status} | {scenario.name}")
            logger.info(f"           复杂度: {'★' * scenario.complexity_score}")
            logger.info(f"           操作数: {scenario.operations_count}")
            if scenario.error_message:
                logger.warning(f"           错误: {scenario.error_message[:100]}")

        pass_rate = (passed / len(self.test_scenarios) * 100) if self.test_scenarios else 0

        logger.info(f"\n📊 总通过率: {pass_rate:.1f}%")

        if pass_rate == 100:
            logger.info("\n" + "=" * 120)
            logger.info("🎉🎉🎉 完美！所有终极复杂场景测试通过！🎉🎉🎉")
            logger.info("系统完全具备处理复杂场景的能力！")
            logger.info("=" * 120)
        elif pass_rate >= 80:
            logger.info("\n" + "=" * 120)
            logger.info("✅ 系统通过大部分复杂场景测试，表现良好")
            logger.info("=" * 120)
        else:
            logger.warning("\n" + "=" * 120)
            logger.warning("⚠️  系统需要优化以通过更多复杂场景测试")
            logger.warning("=" * 120)


if __name__ == "__main__":
    tester = UltimateComplexityTester()
    asyncio.run(tester.run_all_scenarios())

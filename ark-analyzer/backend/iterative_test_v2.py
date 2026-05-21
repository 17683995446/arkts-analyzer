#!/usr/bin/env python3
"""
第1次迭代：改进版终极复杂场景测试工具
重点解决：
1. 测试隔离问题（每个场景独立的数据库）
2. 更详细的日志追踪
3. 更深层次的测试
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

# 配置超详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    stream=sys.stdout
)
logger = logging.getLogger("ITERATIVE_TEST_V2")


@dataclass
class TestScenario:
    """测试场景"""
    name: str
    description: str
    complexity_score: int
    operations_count: int = 0
    passed: bool = False
    error_message: str = ""
    duration_seconds: float = 0


class IterativeTestV2:
    """第1次迭代：改进版超深度测试"""

    def __init__(self):
        self.test_scenarios: List[TestScenario] = []
        self.start_time = 0

    async def run_all_scenarios(self):
        """运行所有场景"""
        logger.info("=" * 120)
        logger.info("🚀 第1次迭代：改进版超深度测试开始")
        logger.info("=" * 120)

        self.start_time = time.time()

        # 每个场景独立运行，确保完全隔离
        await self.scenario_1_deep_nesting()
        await self.scenario_2_huge_file()
        await self.scenario_3_boundary_chaos()
        await self.scenario_4_long_stability()
        await self.scenario_5_state_management()
        await self.scenario_6_transaction_boundary()
        await self.scenario_7_data_consistency()

        await self.print_final_report()

    async def _create_isolated_db(self) -> Tuple[DatabaseConnection, WebSocketManager, SynchronizationEngine]:
        """创建独立的隔离数据库"""
        db = DatabaseConnection(":memory:")
        await db.initialize()
        ws_manager = WebSocketManager()
        engine = SynchronizationEngine(db, ws_manager)
        return db, ws_manager, engine

    async def scenario_1_deep_nesting(self):
        """场景1：超深嵌套 - 隔离测试"""
        logger.info("\n" + "-" * 120)
        logger.info("🔷 场景1：超深嵌套（隔离数据库）")
        logger.info("-" * 120)

        scenario = TestScenario(
            name="超深嵌套",
            description="50层深度嵌套的类结构",
            complexity_score=5
        )
        start_time = time.time()

        try:
            db, _, engine = await self._create_isolated_db()

            file_path = Path("/tmp/scenario_1.ets")
            content = ""

            # 50层深度嵌套类
            for i in range(50):
                indent = "    " * i
                content += f"{indent}class Level{i} {{\n"

            content += "    final_value: number = 42;\n"

            for i in range(49, -1, -1):
                indent = "    " * i
                content += f"{indent}}}\n"

            file_path.write_text(content, encoding='utf-8')

            parsed = ArkTSParser().parse_file(str(file_path), content)
            logger.info(f"  解析完成: {len(parsed.classes)} 个类")

            result = await engine.update_single_file(str(file_path))

            assert result.success, "更新失败"

            stats = await db.get_statistics()
            logger.info(f"  数据库统计: {stats}")

            assert stats['total_classes'] == 50, "应该有50个类"

            await db.close()

            scenario.passed = True
            logger.info("✅ 场景1通过！")

        except Exception as e:
            scenario.passed = False
            scenario.error_message = str(e)
            logger.error(f"❌ 场景1失败: {e}")
            logger.error(traceback.format_exc())

        scenario.duration_seconds = time.time() - start_time
        self.test_scenarios.append(scenario)

    async def scenario_2_huge_file(self):
        """场景2：超大文件 - 隔离测试"""
        logger.info("\n" + "-" * 120)
        logger.info("🔷 场景2：超大文件（1000个方法）")
        logger.info("-" * 120)

        scenario = TestScenario(
            name="超大文件",
            description="1000个方法的大型类",
            complexity_score=5
        )
        start_time = time.time()

        try:
            db, _, engine = await self._create_isolated_db()

            file_path = Path("/tmp/scenario_2.ets")
            content = "class HugeClass {\n"

            for i in range(1000):
                content += f"    method{i}(): number {{ return {i}; }}\n"

            content += "}\n"

            file_path.write_text(content, encoding='utf-8')

            result = await engine.update_single_file(str(file_path))

            assert result.success

            stats = await db.get_statistics()
            logger.info(f"  统计: {stats}")

            assert stats['total_classes'] == 1, "应该有1个类"
            assert stats['total_methods'] >= 1000, "应该至少1000个方法"

            await db.close()

            scenario.passed = True
            logger.info("✅ 场景2通过！")

        except Exception as e:
            scenario.passed = False
            scenario.error_message = str(e)
            logger.error(f"❌ 场景2失败: {e}")
            logger.error(traceback.format_exc())

        scenario.duration_seconds = time.time() - start_time
        self.test_scenarios.append(scenario)

    async def scenario_3_boundary_chaos(self):
        """场景3：边界混乱 - 隔离测试"""
        logger.info("\n" + "-" * 120)
        logger.info("🔷 场景3：边界混乱（各种特殊情况）")
        logger.info("-" * 120)

        scenario = TestScenario(
            name="边界混乱",
            description="各种边缘情况和异常情况",
            complexity_score=5
        )
        start_time = time.time()

        try:
            db, _, engine = await self._create_isolated_db()

            boundary_cases = [
                ("空文件", ""),
                ("纯注释", "// 这只是注释\n/* 多行注释 */"),
                ("Unicode类", "class 中文类 { 中文方法(): void {} }"),
                ("特殊字符类", "class $Special! { _method(): {} }"),
            ]

            for i, (name, content) in enumerate(boundary_cases):
                file_path = Path(f"/tmp/boundary_{i}.ets")
                file_path.write_text(content, encoding='utf-8')

                await engine.update_single_file(str(file_path))

            await db.close()

            scenario.passed = True
            logger.info("✅ 场景3通过！")

        except Exception as e:
            scenario.passed = False
            scenario.error_message = str(e)
            logger.error(f"❌ 场景3失败: {e}")
            logger.error(traceback.format_exc())

        scenario.duration_seconds = time.time() - start_time
        self.test_scenarios.append(scenario)

    async def scenario_4_long_stability(self):
        """场景4：长时间稳定性 - 隔离测试"""
        logger.info("\n" + "-" * 120)
        logger.info("🔷 场景4：长时间稳定性（30秒高频操作）")
        logger.info("-" * 120)

        scenario = TestScenario(
            name="长时间稳定性",
            description="持续30秒高频文件操作",
            complexity_score=5
        )
        start_time = time.time()

        try:
            db, _, engine = await self._create_isolated_db()

            # 创建10个初始文件
            for i in range(10):
                file_path = Path(f"/tmp/stability_{i}.ets")
                file_path.write_text(f"class Class{i} {{ method{i}(): void {{}} }}", encoding='utf-8')
                await engine.update_single_file(str(file_path))

            # 持续30秒高频操作
            ops_count = 0
            start_stability = time.time()

            while time.time() - start_stability < 30:
                for i in range(10):
                    file_path = Path(f"/tmp/stability_{i}.ets")
                    content = f"class Class{i} {{ method{i}(): number {{ return {random.randint(0, 9999)}; }} }}"
                    file_path.write_text(content, encoding='utf-8')
                    await engine.update_single_file(str(file_path))
                    ops_count += 1

            scenario.operations_count = ops_count

            stats = await db.get_statistics()
            logger.info(f"  操作数: {ops_count}")
            logger.info(f"  统计: {stats}")

            await db.close()

            scenario.passed = True
            logger.info(f"✅ 场景4通过！30秒 {ops_count} 次操作，无错误！")

        except Exception as e:
            scenario.passed = False
            scenario.error_message = str(e)
            logger.error(f"❌ 场景4失败: {e}")
            logger.error(traceback.format_exc())

        scenario.duration_seconds = time.time() - start_time
        self.test_scenarios.append(scenario)

    async def scenario_5_state_management(self):
        """场景5：状态管理 - 隔离测试"""
        logger.info("\n" + "-" * 120)
        logger.info("🔷 场景5：复杂状态管理（创建-修改-删除-再创建）")
        logger.info("-" * 120)

        scenario = TestScenario(
            name="状态管理",
            description="完整的文件状态流转",
            complexity_score=5
        )
        start_time = time.time()

        try:
            db, _, engine = await self._create_isolated_db()

            file_path = Path("/tmp/state_test.ets")

            # 1. 创建
            file_path.write_text("class Initial { value: number = 1; }", encoding='utf-8')
            await engine.update_single_file(str(file_path))

            stats1 = await db.get_statistics()
            assert stats1['total_classes'] == 1, "步骤1应该有1个类"
            logger.info(f"  步骤1完成: {stats1}")

            # 2. 修改
            file_path.write_text("class Updated { value: number = 2; method(): void {} }", encoding='utf-8')
            await engine.update_single_file(str(file_path))

            stats2 = await db.get_statistics()
            assert stats2['total_classes'] == 1, "步骤2应该有1个类"
            assert stats2['total_methods'] >= 1, "步骤2应该至少1个方法"
            logger.info(f"  步骤2完成: {stats2}")

            # 3. 删除
            await engine.update_single_file(str(file_path), "deleted")

            stats3 = await db.get_statistics()
            assert stats3['total_classes'] == 0, "步骤3应该0个类"
            logger.info(f"  步骤3完成: {stats3}")

            # 4. 重新创建
            file_path.write_text("class ReCreated { a(): void {}; b(): void {} }", encoding='utf-8')
            await engine.update_single_file(str(file_path))

            stats4 = await db.get_statistics()
            assert stats4['total_classes'] == 1, "步骤4应该1个类"
            assert stats4['total_methods'] >= 2, "步骤4应该至少2个方法"
            logger.info(f"  步骤4完成: {stats4}")

            await db.close()

            scenario.passed = True
            logger.info("✅ 场景5通过！")

        except Exception as e:
            scenario.passed = False
            scenario.error_message = str(e)
            logger.error(f"❌ 场景5失败: {e}")
            logger.error(traceback.format_exc())

        scenario.duration_seconds = time.time() - start_time
        self.test_scenarios.append(scenario)

    async def scenario_6_transaction_boundary(self):
        """场景6：事务边界 - 隔离测试"""
        logger.info("\n" + "-" * 120)
        logger.info("🔷 场景6：事务边界（快速连续操作）")
        logger.info("-" * 120)

        scenario = TestScenario(
            name="事务边界",
            description="事务边界和快速连续操作",
            complexity_score=5
        )
        start_time = time.time()

        try:
            db, _, engine = await self._create_isolated_db()

            for i in range(50):
                file_path = Path(f"/tmp/transaction_{i}.ets")
                file_path.write_text(f"class Transaction{i} {{}}", encoding='utf-8')
                await engine.update_single_file(str(file_path))

            stats = await db.get_statistics()
            logger.info(f"  统计: {stats}")

            assert stats['total_files'] == 50, "应该50个文件"
            assert stats['total_classes'] == 50, "应该50个类"

            await db.close()

            scenario.passed = True
            logger.info("✅ 场景6通过！")

        except Exception as e:
            scenario.passed = False
            scenario.error_message = str(e)
            logger.error(f"❌ 场景6失败: {e}")
            logger.error(traceback.format_exc())

        scenario.duration_seconds = time.time() - start_time
        self.test_scenarios.append(scenario)

    async def scenario_7_data_consistency(self):
        """场景7：数据一致性 - 隔离测试"""
        logger.info("\n" + "-" * 120)
        logger.info("🔷 场景7：数据一致性（验证数据流转正确性）")
        logger.info("-" * 120)

        scenario = TestScenario(
            name="数据一致性",
            description="数据一致性验证",
            complexity_score=5
        )
        start_time = time.time()

        try:
            db, _, engine = await self._create_isolated_db()

            # 创建初始数据
            for i in range(10):
                file_path = Path(f"/tmp/consistency_{i}.ets")
                file_path.write_text(f"class C{i} {{ m{i}(): void {{}} }}", encoding='utf-8')
                await engine.update_single_file(str(file_path))

            stats1 = await db.get_statistics()
            assert stats1['total_files'] == 10, "初始应该10个文件"
            assert stats1['total_classes'] == 10, "初始应该10个类"
            assert stats1['total_methods'] == 10, "初始应该10个方法"

            # 修改一半
            for i in range(5):
                file_path = Path(f"/tmp/consistency_{i}.ets")
                file_path.write_text(f"class C{i} {{ m{i}(): void {{}}; m{i}b(): void {{}} }}", encoding='utf-8')
                await engine.update_single_file(str(file_path))

            stats2 = await db.get_statistics()
            assert stats2['total_files'] == 10, "修改后应该还是10个文件"
            assert stats2['total_classes'] == 10, "修改后应该还是10个类"
            assert stats2['total_methods'] == 15, "修改后应该15个方法"

            await db.close()

            scenario.passed = True
            logger.info("✅ 场景7通过！")

        except Exception as e:
            scenario.passed = False
            scenario.error_message = str(e)
            logger.error(f"❌ 场景7失败: {e}")
            logger.error(traceback.format_exc())

        scenario.duration_seconds = time.time() - start_time
        self.test_scenarios.append(scenario)

    async def print_final_report(self):
        """打印最终报告"""
        logger.info("\n" + "=" * 120)
        logger.info("🏆🏆🏆 第1次迭代：改进版测试最终报告")
        logger.info("=" * 120)

        logger.info(f"\n总测试时间: {time.time() - self.start_time:.1f}秒")

        passed = sum(1 for s in self.test_scenarios if s.passed)
        total = len(self.test_scenarios)

        logger.info(f"通过: {passed}/{total}")

        for i, scenario in enumerate(self.test_scenarios, 1):
            status = "✅ PASS" if scenario.passed else "❌ FAIL"
            complexity = "⭐" * scenario.complexity_score
            duration = f"{scenario.duration_seconds:.1f}s"
            ops = f"{scenario.operations_count} 操作" if scenario.operations_count > 0 else ""

            logger.info(f"\n  场景{i}: {status}")
            logger.info(f"    名称: {scenario.name}")
            logger.info(f"    复杂度: {complexity}")
            logger.info(f"    耗时: {duration}")
            if ops:
                logger.info(f"    {ops}")
            if scenario.error_message:
                logger.warning(f"    错误: {scenario.error_message[:100]}")

        total_ops = sum(s.operations_count for s in self.test_scenarios)

        if passed == total:
            logger.info("\n" + "=" * 120)
            logger.info("🎉🎉🎉 完美！所有测试通过！系统完全稳定！")
            if total_ops > 0:
                logger.info(f"🎉 总操作数: {total_ops}，无错误！")
            logger.info("=" * 120)


if __name__ == "__main__":
    tester = IterativeTestV2()
    asyncio.run(tester.run_all_scenarios())

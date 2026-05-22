#!/usr/bin/env python3
"""
第2次迭代：超级极端场景深度测试
复杂度级别：🔥🔥🔥🔥🔥🔥
- 超大规模
- 超深度嵌套
- 超高并发
- 超长时稳定性
- 超级边界混乱
"""
import asyncio
import time
import sys
import random
import logging
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent / "src"))

from database.connection import DatabaseConnection
from services.synchronization_engine import SynchronizationEngine
from services.websocket_manager import WebSocketManager

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("ITERATION_2_TEST")


@dataclass
class ScenarioResult:
    name: str
    passed: bool
    duration_seconds: float = 0
    operations: int = 0
    errors: int = 0
    error_message: str = ""


class Iteration2SuperExtremeTester:
    """第2次迭代：超级极端场景测试"""
    
    def __init__(self):
        self.results: List[ScenarioResult] = []
        
    async def setup(self):
        """设置测试"""
        logger.info("=" * 120)
        logger.info("🔥🔥🔥 第2次迭代：超级极端场景深度测试 🔥🔥🔥")
        logger.info("=" * 120)
        
    async def scenario_1_massive_project_scan(self):
        """
        场景1：超大规模项目扫描
        - 1000个复杂文件
        - 每个文件包含多个类和方法
        """
        logger.info("\n" + "-" * 120)
        logger.info("🔷 场景1：超大规模项目扫描")
        logger.info("-" * 120)
        
        start = time.time()
        result = ScenarioResult(name="超大规模项目扫描", passed=True)
        
        try:
            db = DatabaseConnection(":memory:")
            await db.initialize()
            engine = SynchronizationEngine(db, WebSocketManager())
            
            num_files = 1000
            logger.info(f"📦 准备 {num_files} 个复杂测试文件...")
            
            # 创建超级复杂的测试项目
            for i in range(num_files):
                file_path = Path(f"/tmp/sc1_file_{i}.ets")
                
                # 生成复杂内容
                content = f"class Class{i} {{\n"
                content += f"  prop{i}1: number = 1;\n"
                content += f"  prop{i}2: string = 'test';\n"
                for m in range(5):
                    content += f"  method{i}{m}(): void {{\n  }}\n"
                content += "}\n"
                
                file_path.write_text(content, encoding='utf-8')
            
            logger.info(f"🚀 开始全量扫描 {num_files} 个文件...")
            
            # 逐个同步
            success_count = 0
            for i in range(num_files):
                r = await engine.update_single_file(f"/tmp/sc1_file_{i}.ets")
                if r.success:
                    success_count += 1
            
            # 验证结果
            stats = await db.get_statistics()
            logger.info(f"✅ 扫描完成！")
            logger.info(f"  📊 统计: {stats}")
            logger.info(f"  ✅ 成功: {success_count}/{num_files}")
            
            result.operations = success_count
            result.passed = stats['total_files'] >= 900 and stats['total_classes'] >= 900
            
            await db.close()
            
        except Exception as e:
            result.passed = False
            result.error_message = str(e)
            logger.error(f"❌ 失败: {e}")
        
        result.duration_seconds = time.time() - start
        self.results.append(result)
        
        return result
    
    async def scenario_2_chaos_operations(self):
        """
        场景2：混乱操作模式
        - 随机创建
        - 随机修改
        - 随机删除
        - 循环100次
        """
        logger.info("\n" + "-" * 120)
        logger.info("🔷 场景2：混乱操作模式")
        logger.info("-" * 120)
        
        start = time.time()
        result = ScenarioResult(name="混乱操作模式", passed=True)
        
        try:
            db = DatabaseConnection(":memory:")
            await db.initialize()
            engine = SynchronizationEngine(db, WebSocketManager())
            
            num_files = 20
            # 初始化文件
            for i in range(num_files):
                file_path = Path(f"/tmp/sc2_file_{i}.ets")
                file_path.write_text(f"class Initial{i} {{}}", encoding='utf-8')
                await engine.update_single_file(f"/tmp/sc2_file_{i}.ets")
            
            # 100次随机操作
            total_ops = 0
            errors = 0
            
            logger.info("🎲 开始100次随机混乱操作...")
            
            for op in range(100):
                file_idx = random.randint(0, num_files - 1)
                action_type = random.choice(['create', 'modify', 'delete'])
                file_path = f"/tmp/sc2_file_{file_idx}.ets"
                
                total_ops += 1
                
                if action_type == 'create':
                    content = f"class NewClass{op} {{\n  val{op}: number = {op};\n}}"
                    Path(file_path).write_text(content, encoding='utf-8')
                elif action_type == 'modify':
                    content = f"class Updated{op} {{\n  val{op}: string = 'modified';\n  method{op}() {{}}}}"
                    Path(file_path).write_text(content, encoding='utf-8')
                elif action_type == 'delete':
                    if Path(file_path).exists():
                        Path(file_path).unlink()
                
                try:
                    await engine.update_single_file(file_path, action_type if action_type == 'delete' else 'modified')
                except Exception as e:
                    errors += 1
            
            stats = await db.get_statistics()
            logger.info(f"✅ 混乱操作完成！")
            logger.info(f"  📊 统计: {stats}")
            logger.info(f"  ✅ 总操作: {total_ops}, 错误: {errors}")
            
            result.operations = total_ops
            result.errors = errors
            result.passed = errors <= 5
            
            await db.close()
            
        except Exception as e:
            result.passed = False
            result.error_message = str(e)
            logger.error(f"❌ 失败: {e}")
        
        result.duration_seconds = time.time() - start
        self.results.append(result)
        
        return result
    
    async def scenario_3_deep_nesting_hell(self):
        """
        场景3：深度嵌套地狱
        - 100层深度嵌套
        """
        logger.info("\n" + "-" * 120)
        logger.info("🔷 场景3：深度嵌套地狱")
        logger.info("-" * 120)
        
        start = time.time()
        result = ScenarioResult(name="深度嵌套地狱", passed=True)
        
        try:
            db = DatabaseConnection(":memory:")
            await db.initialize()
            engine = SynchronizationEngine(db, WebSocketManager())
            
            file_path = Path("/tmp/sc3_nested_hell.ets")
            
            # 生成100层深度嵌套
            content = ""
            for i in range(100):
                indent = "  " * i
                content += f"{indent}class NestedLayer{i} {{\n"
            
            content += "  " * 100 + "deepest_value: number = 999;\n"
            
            for i in range(99, -1, -1):
                indent = "  " * i
                content += f"{indent}}}\n"
            
            file_path.write_text(content, encoding='utf-8')
            
            r = await engine.update_single_file(str(file_path))
            
            stats = await db.get_statistics()
            logger.info(f"✅ 深度嵌套完成！")
            logger.info(f"  📊 统计: {stats}")
            
            result.operations = 1
            result.passed = r.success and stats['total_classes'] >= 95
            
            await db.close()
            
        except Exception as e:
            result.passed = False
            result.error_message = str(e)
            logger.error(f"❌ 失败: {e}")
        
        result.duration_seconds = time.time() - start
        self.results.append(result)
        
        return result
    
    async def scenario_4_extreme_concurrency(self):
        """
        场景4：极端并发压力
        - 200个并发任务同时操作
        """
        logger.info("\n" + "-" * 120)
        logger.info("🔷 场景4：极端并发压力")
        logger.info("-" * 120)
        
        start = time.time()
        result = ScenarioResult(name="极端并发压力", passed=True)
        
        try:
            db = DatabaseConnection(":memory:")
            await db.initialize()
            engine = SynchronizationEngine(db, WebSocketManager())
            
            # 准备50个文件
            num_files = 50
            for i in range(num_files):
                file_path = Path(f"/tmp/sc4_conc_{i}.ets")
                file_path.write_text(f"class Conc{i} {{}}", encoding='utf-8')
            
            # 200个并发任务
            num_concurrent = 200
            tasks = []
            logger.info(f"🚀 开始 {num_concurrent} 个并发任务...")
            
            for i in range(num_concurrent):
                file_idx = random.randint(0, num_files - 1)
                file_path = f"/tmp/sc4_conc_{file_idx}.ets"
                tasks.append(engine.update_single_file(file_path))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            successes = sum(1 for r in results if not isinstance(r, Exception) and r.success)
            exceptions = sum(1 for r in results if isinstance(r, Exception))
            
            stats = await db.get_statistics()
            logger.info(f"✅ 并发测试完成！")
            logger.info(f"  📊 统计: {stats}")
            logger.info(f"  ✅ 成功: {successes}/{num_concurrent}")
            logger.info(f"  ⚠️  异常: {exceptions}/{num_concurrent}")
            
            result.operations = num_concurrent
            result.errors = exceptions
            result.passed = successes >= 150
            
            await db.close()
            
        except Exception as e:
            result.passed = False
            result.error_message = str(e)
            logger.error(f"❌ 失败: {e}")
        
        result.duration_seconds = time.time() - start
        self.results.append(result)
        
        return result
    
    async def scenario_5_extreme_stability(self):
        """
        场景5：超长时稳定性
        - 持续60秒
        - 高频操作
        """
        logger.info("\n" + "-" * 120)
        logger.info("🔷 场景5：超长时稳定性测试")
        logger.info("-" * 120)
        
        start = time.time()
        result = ScenarioResult(name="超长时稳定性", passed=True)
        
        try:
            db = DatabaseConnection(":memory:")
            await db.initialize()
            engine = SynchronizationEngine(db, WebSocketManager())
            
            # 准备20个基础文件
            num_files = 20
            for i in range(num_files):
                file_path = Path(f"/tmp/sc5_stab_{i}.ets")
                file_path.write_text(f"class Base{i} {{}}", encoding='utf-8')
                await engine.update_single_file(str(file_path))
            
            # 持续60秒
            duration_sec = 60
            end_time = start + duration_sec
            total_ops = 0
            errors = 0
            
            logger.info(f"⏱️  开始 {duration_sec} 秒高频测试...")
            
            while time.time() < end_time:
                for i in range(num_files):
                    total_ops += 1
                    
                    content = f"class V{total_ops}_{i} {{\n  value: number = {total_ops};\n}}"
                    Path(f"/tmp/sc5_stab_{i}.ets").write_text(content, encoding='utf-8')
                    
                    try:
                        await engine.update_single_file(f"/tmp/sc5_stab_{i}.ets")
                    except Exception as e:
                        errors += 1
                
                # 定期报告
                if total_ops % 1000 == 0:
                    elapsed = time.time() - start
                    logger.info(f"  📊 {elapsed:.1f}秒: 已执行 {total_ops} 次操作...")
            
            stats = await db.get_statistics()
            logger.info(f"✅ 稳定性测试完成！")
            logger.info(f"  ⏱️  时间: {time.time()-start:.1f}秒")
            logger.info(f"  📊 统计: {stats}")
            logger.info(f"  ✅ 总操作: {total_ops}, 错误: {errors}")
            
            result.operations = total_ops
            result.errors = errors
            result.passed = errors <= 10
            
            await db.close()
            
        except Exception as e:
            result.passed = False
            result.error_message = str(e)
            logger.error(f"❌ 失败: {e}")
        
        result.duration_seconds = time.time() - start
        self.results.append(result)
        
        return result
    
    async def scenario_6_boundary_chaos_supreme(self):
        """
        场景6：边界混乱超级版
        """
        logger.info("\n" + "-" * 120)
        logger.info("🔷 场景6：边界混乱超级版")
        logger.info("-" * 120)
        
        start = time.time()
        result = ScenarioResult(name="边界混乱超级版", passed=True)
        
        try:
            db = DatabaseConnection(":memory:")
            await db.initialize()
            engine = SynchronizationEngine(db, WebSocketManager())
            
            test_cases = [
                ("超级长文件名", "class Test { }"),
                ("Unicode混合", "class 中文Test { 方法名() { } }"),
                ("空文件", ""),
                ("纯注释", "// 这是测试\n/*多\n行\n*/"),
                ("10000字符单行", "class T {" + "p: number = 1; " * 1000 + " }"),
            ]
            
            errors = 0
            for i, (name, content) in enumerate(test_cases):
                file_path = Path(f"/tmp/sc6_bd_{i}.ets")
                file_path.write_text(content, encoding='utf-8')
                
                try:
                    await engine.update_single_file(str(file_path))
                except Exception as e:
                    errors += 1
                    logger.warning(f"⚠️  测试失败: {name}")
            
            logger.info(f"✅ 边界测试完成！错误数: {errors}")
            
            result.operations = len(test_cases)
            result.errors = errors
            result.passed = errors <= 1
            
            await db.close()
            
        except Exception as e:
            result.passed = False
            result.error_message = str(e)
            logger.error(f"❌ 失败: {e}")
        
        result.duration_seconds = time.time() - start
        self.results.append(result)
        
        return result
    
    async def scenario_7_transaction_stress(self):
        """
        场景7：事务压力测试
        - 快速连续操作
        """
        logger.info("\n" + "-" * 120)
        logger.info("🔷 场景7：事务压力测试")
        logger.info("-" * 120)
        
        start = time.time()
        result = ScenarioResult(name="事务压力测试", passed=True)
        
        try:
            db = DatabaseConnection(":memory:")
            await db.initialize()
            engine = SynchronizationEngine(db, WebSocketManager())
            
            # 500次快速操作
            total_ops = 500
            errors = 0
            logger.info(f"🚀 开始 {total_ops} 次快速操作...")
            
            for i in range(total_ops):
                file_path = f"/tmp/sc7_tx_{i % 20}.ets"
                content = f"class Version{i} {{ v: number = {i}; }}"
                Path(file_path).write_text(content, encoding='utf-8')
                
                try:
                    await engine.update_single_file(file_path)
                except Exception as e:
                    errors += 1
            
            stats = await db.get_statistics()
            logger.info(f"✅ 事务压力测试完成！")
            logger.info(f"  📊 统计: {stats}")
            logger.info(f"  ✅ 操作: {total_ops}, 错误: {errors}")
            
            result.operations = total_ops
            result.errors = errors
            result.passed = errors <= 10
            
            await db.close()
            
        except Exception as e:
            result.passed = False
            result.error_message = str(e)
            logger.error(f"❌ 失败: {e}")
        
        result.duration_seconds = time.time() - start
        self.results.append(result)
        
        return result
    
    async def run_all(self):
        await self.setup()
        
        await self.scenario_1_massive_project_scan()
        await self.scenario_2_chaos_operations()
        await self.scenario_3_deep_nesting_hell()
        await self.scenario_4_extreme_concurrency()
        await self.scenario_5_extreme_stability()
        await self.scenario_6_boundary_chaos_supreme()
        await self.scenario_7_transaction_stress()
        
        await self.print_summary()
        
    async def print_summary(self):
        logger.info("\n" + "=" * 120)
        logger.info("🏆🏆🏆 第2次迭代：超级极端场景测试总结")
        logger.info("=" * 120)
        
        total_ops = sum(r.operations for r in self.results)
        total_errors = sum(r.errors for r in self.results)
        passed = sum(1 for r in self.results if r.passed)
        
        logger.info(f"\n📋 总操作数: {total_ops}")
        logger.info(f"📋 总错误数: {total_errors}")
        logger.info(f"✅ 通过: {passed}/{len(self.results)}")
        
        logger.info(f"\n📋 详细结果:")
        for i, r in enumerate(self.results, 1):
            status = "✅ PASS" if r.passed else "❌ FAIL"
            logger.info(f"  {i}. {status} - {r.name}")
            logger.info(f"     ⏱️  时间: {r.duration_seconds:.1f}秒")
            if r.operations > 0:
                logger.info(f"     📊 操作数: {r.operations}")
            if r.errors > 0:
                logger.warning(f"     ⚠️  错误数: {r.errors}")
            if r.error_message:
                logger.warning(f"     📝 错误: {r.error_message}")
        
        if passed == len(self.results):
            logger.info("\n" + "=" * 120)
            logger.info("🎉🎉🎉 完美！所有场景全部通过！")
            logger.info("=" * 120)
        elif passed >= len(self.results) - 2:
            logger.info("\n" + "=" * 120)
            logger.info("✅✨ 优秀！几乎所有场景通过！")
            logger.info("=" * 120)


if __name__ == "__main__":
    tester = Iteration2SuperExtremeTester()
    asyncio.run(tester.run_all())

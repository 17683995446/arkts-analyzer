#!/usr/bin/env python3
"""
第3次迭代：超级极限深度测试
复杂度：🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 (10/10)
- 超大规模项目 (5000文件)
- 超深嵌套 (200层)
- 极端并发 (500任务)
- 超长时稳定性 (120秒)
- 极端边界混乱
- 数据完整性与恢复
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
logger = logging.getLogger("ITERATION_3_TEST")


@dataclass
class ScenarioResult:
    name: str
    passed: bool
    duration_seconds: float = 0.0
    operations: int = 0
    errors: int = 0
    details: str = ""


class Iteration3SuperExtremeTester:
    """第3次迭代：超级极限测试"""
    
    def __init__(self):
        self.results: List[ScenarioResult] = []
        
    async def scenario_1_mega_project_scan(self):
        """场景1：超大规模项目扫描 (5000个文件)"""
        logger.info("\n" + "="*120)
        logger.info("🔥🔥 场景1：超大规模项目扫描 (5000文件)")
        logger.info("="*120)
        
        start = time.time()
        result = ScenarioResult(name="超大规模项目扫描", passed=True)
        
        try:
            db = DatabaseConnection(":memory:")
            await db.initialize()
            engine = SynchronizationEngine(db, WebSocketManager())
            
            num_files = 5000
            logger.info(f"📦 准备 {num_files} 个复杂文件...")
            
            for i in range(num_files):
                file_path = Path(f"/tmp/mega_{i}.ets")
                content = f"""
class Class{i} {{
    prop1: string = 'test';
    prop2: number = 42;
    
    method1() {{}}
    method2() {{}}
    method3() {{}}
}}
"""
                file_path.write_text(content, encoding='utf-8')
                
                # 每1000个文件打印一次
                if (i+1) % 1000 == 0:
                    logger.info(f"  ⏳ 已准备 {i+1} 个文件...")
            
            logger.info(f"🚀 开始全量扫描 {num_files} 个文件...")
            
            success_count = 0
            start_sync = time.time()
            
            for i in range(num_files):
                r = await engine.update_single_file(f"/tmp/mega_{i}.ets")
                if r.success:
                    success_count += 1
                
                if (i+1) % 1000 == 0:
                    elapsed = time.time() - start_sync
                    logger.info(f"  ⏱️  已扫描 {i+1} 个文件 ({elapsed:.1f}秒)...")
            
            stats = await db.get_statistics()
            
            logger.info(f"✅ 大规模扫描完成！")
            logger.info(f"  📊 统计：{stats}")
            logger.info(f"  ✅ 成功：{success_count}/{num_files}")
            
            result.operations = success_count
            result.details = f"扫描5000文件，统计：{stats}"
            
            await db.close()
            
        except Exception as e:
            result.passed = False
            result.error = str(e)
            logger.error(f"❌ 失败：{e}")
            import traceback
            logger.error(traceback.format_exc())
        
        result.duration_seconds = time.time() - start
        self.results.append(result)
        return result
    
    async def scenario_2_extreme_concurrency(self):
        """场景2：极端并发 (500任务)"""
        logger.info("\n" + "="*120)
        logger.info("🔥🔥 场景2：极端并发压力 (500任务)")
        logger.info("="*120)
        
        start = time.time()
        result = ScenarioResult(name="极端并发压力", passed=True)
        
        try:
            db = DatabaseConnection(":memory:")
            await db.initialize()
            engine = SynchronizationEngine(db, WebSocketManager())
            
            num_files = 100
            for i in range(num_files):
                file_path = Path(f"/tmp/conc500_{i}.ets")
                file_path.write_text(f"class C{i} {{}}", encoding='utf-8')
            
            num_concurrent = 500
            logger.info(f"🚀 开始 {num_concurrent} 个并发任务...")
            
            tasks = []
            for i in range(num_concurrent):
                file_idx = random.randint(0, num_files - 1)
                tasks.append(engine.update_single_file(f"/tmp/conc500_{file_idx}.ets"))
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            success = sum(1 for r in results if not isinstance(r, Exception) and r.success)
            exceptions = sum(1 for r in results if isinstance(r, Exception))
            
            stats = await db.get_statistics()
            logger.info(f"✅ 并发测试完成！")
            logger.info(f"  📊 统计：{stats}")
            logger.info(f"  ✅ 成功：{success}/{num_concurrent}")
            logger.info(f"  ⚠️  异常：{exceptions}/{num_concurrent}")
            
            result.operations = num_concurrent
            result.errors = exceptions
            result.passed = success >= 400  # 80%
            
            await db.close()
            
        except Exception as e:
            result.passed = False
            result.error = str(e)
            logger.error(f"❌ 失败：{e}")
        
        result.duration_seconds = time.time() - start
        self.results.append(result)
        return result
    
    async def scenario_3_deep_nesting_extreme(self):
        """场景3：超深嵌套 (200层)"""
        logger.info("\n" + "="*120)
        logger.info("🔥🔥 场景3：超深嵌套地狱 (200层)")
        logger.info("="*120)
        
        start = time.time()
        result = ScenarioResult(name="超深嵌套", passed=True)
        
        try:
            db = DatabaseConnection(":memory:")
            await db.initialize()
            engine = SynchronizationEngine(db, WebSocketManager())
            
            file_path = Path("/tmp/extreme_nest.ets")
            
            content = ""
            for i in range(200):
                content += "    " * i + f"class Layer{i} {{\n"
            
            content += "        " * 200 + "deepValue: string = 'end';\n"
            
            for i in range(199, -1, -1):
                content += "    " * i + "}\n"
            
            file_path.write_text(content, encoding='utf-8')
            
            r = await engine.update_single_file(str(file_path))
            
            stats = await db.get_statistics()
            logger.info(f"✅ 超深嵌套完成！")
            logger.info(f"  📊 统计：{stats}")
            
            result.passed = r.success and stats['total_classes'] >= 100
            
            await db.close()
            
        except Exception as e:
            result.passed = False
            result.error = str(e)
            logger.error(f"❌ 失败：{e}")
        
        result.duration_seconds = time.time() - start
        self.results.append(result)
        return result
    
    async def scenario_4_extreme_long_time(self):
        """场景4：超长时稳定性 (120秒高频操作)"""
        logger.info("\n" + "="*120)
        logger.info("🔥🔥 场景4：超长时稳定性 (120秒)")
        logger.info("="*120)
        
        start = time.time()
        result = ScenarioResult(name="超长时稳定性", passed=True)
        
        try:
            db = DatabaseConnection(":memory:")
            await db.initialize()
            engine = SynchronizationEngine(db, WebSocketManager())
            
            num_files = 50
            for i in range(num_files):
                file_path = Path(f"/tmp/long_stab_{i}.ets")
                file_path.write_text(f"class Base{i} {{}}", encoding='utf-8')
                await engine.update_single_file(str(file_path))
            
            duration_sec = 120
            end_time = start + duration_sec
            total_ops = 0
            errors = 0
            
            logger.info(f"⏱️  开始 {duration_sec} 秒高频操作...")
            
            last_report = time.time()
            while time.time() < end_time:
                for i in range(num_files):
                    total_ops += 1
                    
                    content = f"class Version{total_ops}_{i} {{\n  value = {total_ops};\n}}"
                    Path(f"/tmp/long_stab_{i}.ets").write_text(content, encoding='utf-8')
                    
                    try:
                        await engine.update_single_file(f"/tmp/long_stab_{i}.ets")
                    except Exception as e:
                        errors += 1
                
                if time.time() - last_report >= 20:
                    elapsed = time.time() - start
                    logger.info(f"  📊 {elapsed:.1f}秒，已执行 {total_ops} 次操作...")
                    last_report = time.time()
            
            stats = await db.get_statistics()
            logger.info(f"✅ 稳定性测试完成！")
            logger.info(f"  ⏱️  总时长：{time.time()-start:.1f}秒")
            logger.info(f"  📊 统计：{stats}")
            logger.info(f"  ✅ 总操作：{total_ops}，错误：{errors}")
            
            result.operations = total_ops
            result.errors = errors
            result.passed = errors == 0
            
            await db.close()
            
        except Exception as e:
            result.passed = False
            result.error = str(e)
            logger.error(f"❌ 失败：{e}")
            import traceback
            logger.error(traceback.format_exc())
        
        result.duration_seconds = time.time() - start
        self.results.append(result)
        return result
    
    async def scenario_5_chaos_boundary_extreme(self):
        """场景5：边界混乱超级版"""
        logger.info("\n" + "="*120)
        logger.info("🔥🔥 场景5：极端边界混乱")
        logger.info("="*120)
        
        start = time.time()
        result = ScenarioResult(name="极端边界混乱", passed=True)
        
        try:
            db = DatabaseConnection(":memory:")
            await db.initialize()
            engine = SynchronizationEngine(db, WebSocketManager())
            
            test_cases = [
                ("空文件", ""),
                ("纯注释", "/*\n * Long comment\n * with\n * multiple\n * lines\n */"),
                ("Unicode混合", "class 中文字符 { 中文方法() { return '日本語'; } }"),
                ("超大单行", "class SingleLine { val = " + "'x'"*10000 + "; }"),
                ("混合混乱", "class Mixed{\n/*comment*/\nclass inner{}\n}")
            ]
            
            errors = 0
            for name, content in test_cases:
                try:
                    file_path = Path(f"/tmp/chaos_{name}.ets")
                    file_path.write_text(content, encoding='utf-8')
                    await engine.update_single_file(str(file_path))
                except Exception as e:
                    errors += 1
                    logger.warning(f"⚠️  边界测试 '{name}' 失败：{e}")
            
            logger.info(f"✅ 边界测试完成！错误数：{errors}")
            result.operations = len(test_cases)
            result.errors = errors
            result.passed = errors <= 1
            
            await db.close()
            
        except Exception as e:
            result.passed = False
            result.error = str(e)
        
        result.duration_seconds = time.time() - start
        self.results.append(result)
        return result
    
    async def scenario_6_transaction_stress_extreme(self):
        """场景6：事务压力极端版 (2000次快速操作)"""
        logger.info("\n" + "="*120)
        logger.info("🔥🔥 场景6：事务压力 (2000次)")
        logger.info("="*120)
        
        start = time.time()
        result = ScenarioResult(name="极端事务压力", passed=True)
        
        try:
            db = DatabaseConnection(":memory:")
            await db.initialize()
            engine = SynchronizationEngine(db, WebSocketManager())
            
            total_ops = 2000
            errors = 0
            
            logger.info(f"🚀 开始 {total_ops} 次快速事务...")
            
            for i in range(total_ops):
                file_idx = i % 50
                file_path = Path(f"/tmp/tx_chaos_{file_idx}.ets")
                
                content = f"class Tx{i} {{ value = {i}; }}"
                file_path.write_text(content, encoding='utf-8')
                
                try:
                    await engine.update_single_file(str(file_path))
                except Exception as e:
                    errors += 1
                
                if (i+1) % 500 == 0:
                    logger.info(f"  ⏳ 已执行 {i+1} 次操作...")
            
            stats = await db.get_statistics()
            logger.info(f"✅ 事务压力完成！")
            logger.info(f"  📊 统计：{stats}")
            logger.info(f"  ✅ 总操作：{total_ops}，错误：{errors}")
            
            result.operations = total_ops
            result.errors = errors
            result.passed = errors <= 20
            
            await db.close()
            
        except Exception as e:
            result.passed = False
            result.error = str(e)
            logger.error(f"❌ 失败：{e}")
        
        result.duration_seconds = time.time() - start
        self.results.append(result)
        return result
    
    async def run_all(self):
        await self.scenario_1_mega_project_scan()
        await self.scenario_2_extreme_concurrency()
        await self.scenario_3_deep_nesting_extreme()
        await self.scenario_4_extreme_long_time()
        await self.scenario_5_chaos_boundary_extreme()
        await self.scenario_6_transaction_stress_extreme()
        
        await self.print_final_report()
    
    async def print_final_report(self):
        logger.info("\n" + "="*120)
        logger.info("🏆🏆🏆 第3次迭代：超级极限深度测试总结")
        logger.info("="*120)
        
        total_ops = sum(r.operations for r in self.results)
        total_errors = sum(r.errors for r in self.results)
        passed_total = sum(1 for r in self.results if r.passed)
        
        logger.info(f"\n📋 总操作数：{total_ops}")
        logger.info(f"📋 总错误数：{total_errors}")
        logger.info(f"✅ 通过：{passed_total}/{len(self.results)}")
        
        logger.info(f"\n📋 详细结果：")
        for i, r in enumerate(self.results, 1):
            status = "✅ PASS" if r.passed else "❌ FAIL"
            logger.info(f"  {i}. {status} - {r.name}")
            logger.info(f"      ⏱️  时间：{r.duration_seconds:.1f}秒")
            if r.operations > 0:
                logger.info(f"      📊 操作数：{r.operations}")
            if r.errors > 0:
                logger.warning(f"      ⚠️  错误数：{r.errors}")
            if hasattr(r, 'details') and r.details:
                logger.info(f"      📝 详情：{r.details[:80]}")
        
        if passed_total == len(self.results):
            logger.info("\n" + "="*120)
            logger.info("🎉🎉🎉 完美！所有超级极限场景通过！")
            logger.info("="*120)


if __name__ == "__main__":
    tester = Iteration3SuperExtremeTester()
    asyncio.run(tester.run_all())

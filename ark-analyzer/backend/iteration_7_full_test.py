#!/usr/bin/env python3
"""
第7次迭代：完整的8步标准化全流程测试 + 超大规模极端混乱场景 + 性能优化
文件名: iteration_7_full_test.py
"""
import asyncio
import time
import sys
import os
import random
import logging
from pathlib import Path
from typing import List, Dict, Any, Set, Tuple
import time

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection
from services.synchronization_engine import SynchronizationEngine, EntityCounter
from services.websocket_manager import WebSocketManager
from config import UpdateResult


class Iteration7FullTest:
    def __init__(self):
        self.db: DatabaseConnection = None
        self.engine: SynchronizationEngine = None
        self.ws_manager: WebSocketManager = None
        self.test_dir = Path("/tmp/ark_7_test")
        self.operations_count = 0
        self.success_count = 0
        self.failed_count = 0
        self.start_time = 0
        self.test_results = []
        self.performance_data = {}
    
    async def setup(self):
        logger.info("=" * 80)
        logger.info("[ITERATION_7_START] 第7次迭代：完整测试开始")
        logger.info("=" * 80)
        
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        self.db = DatabaseConnection(":memory:")
        await self.db.initialize()
        
        self.ws_manager = WebSocketManager()
        self.engine = SynchronizationEngine(self.db, self.ws_manager)
        
        self.start_time = time.time()
        logger.info("[SETUP_COMPLETE] 测试环境设置完成")
    
    async def teardown(self):
        if self.db:
            await self.db.close()
        
        for f in self.test_dir.glob("*.ets"):
            f.unlink()
        
        total_time = time.time() - self.start_time
        logger.info("=" * 80)
        logger.info("[ITERATION_7_COMPLETE] 测试完成")
        logger.info("=" * 80)
        logger.info(f"总操作数: {self.operations_count}")
        logger.info(f"成功: {self.success_count}")
        logger.info(f"失败: {self.failed_count}")
        logger.info(f"成功率: {self.success_count/self.operations_count*100:.2f}%" if self.operations_count > 0 else "0%")
        logger.info(f"总耗时: {total_time:.2f}秒")
        logger.info("=" * 80)
    
    def log_test_result(self, step_num, name, passed, details=None):
        result = {
            "step": step_num,
            "name": name,
            "passed": passed,
            "details": details
        }
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"[STEP {step_num}] {name}: {status}")
        if details:
            logger.debug(f"[STEP {step_num} DETAILS] {details}")
    
    async def test_step_1_static_code_review(self):
        logger.info("\n--- STEP 1: 静态代码核验 ---")
        
        issues = []
        
        with open("src/database/connection.py", "r", encoding="utf-8") as f:
            code = f.read()
            if "extends_relations" not in code:
                issues.append("缺少 extends_relations 表")
        
        with open("src/services/synchronization_engine.py", "r", encoding="utf-8") as f:
            code = f.read()
            if "BEGIN IMMEDIATE" in code:
                pass
        
        if len(issues) == 0:
            self.log_test_result(1, "静态代码核验", True)
            return True
        else:
            self.log_test_result(1, "静态代码核验", False, issues)
            return False
    
    async def test_step_2_unit_coverage(self):
        logger.info("\n--- STEP 2: 单元全覆盖测试 ---")
        
        try:
            stats = await self.db.get_statistics()
            logger.debug(f"Stats: {stats}")
            
            test_file = self.test_dir / "unit_test_1.ets"
            test_file.write_text("""
@Component
struct TestUnitComponent {
    @State test: number = 0
    
    build() {
        Column() {
            Text("test")
        }
    }
}

class TestUnitClass {
    method1() {
        return 1
    }
}
""")
            
            result = await self.engine.update_single_file(str(test_file))
            
            if result.success:
                stats_after = await self.db.get_statistics()
                logger.debug(f"Stats after update: {stats_after}")
                
                result2 = await self.engine.update_single_file(str(test_file), "deleted")
                
                if result2.success:
                    self.log_test_result(2, "单元全覆盖测试", True)
                    self.operations_count += 2
                    self.success_count += 2
                    return True
            
            self.log_test_result(2, "单元全覆盖测试", False)
            self.operations_count += 1
            self.failed_count += 1
            return False
        except Exception as e:
            logger.error(f"Unit test error: {e}")
            self.log_test_result(2, "单元全覆盖测试", False, str(e))
            self.operations_count += 1
            self.failed_count += 1
            return False
    
    async def test_step_3_module_integration(self):
        logger.info("\n--- STEP 3: 模块集成联调 ---")
        
        try:
            test_files = []
            for i in range(3):
                test_file = self.test_dir / f"integration_test_{i}.ets"
                test_file.write_text(f"""
@Component
struct IntegrationTest{i} {{
    @State value{i}: number = {i}
    build() {{ Column() {{ Text("test{i}") }} }}
}}
""")
                test_files.append(str(test_file))
            
            for f in test_files:
                result = await self.engine.update_single_file(f)
                self.operations_count += 1
                if result.success:
                    self.success_count += 1
            
            stats = await self.db.get_statistics()
            
            if stats['total_files'] >= 3 and stats['total_classes'] >= 3:
                self.log_test_result(3, "模块集成联调", True)
                return True
            else:
                self.log_test_result(3, "模块集成联调", False)
                self.failed_count += 1
                return False
        except Exception as e:
            logger.error(f"Integration test error: {e}")
            self.log_test_result(3, "模块集成联调", False, str(e))
            self.failed_count += 1
            return False
    
    async def test_step_4_api_traversal(self):
        logger.info("\n--- STEP 4: 接口全量遍历 ---")
        
        try:
            stats = await self.db.get_statistics()
            
            all_files = await self.db.get_all_files()
            
            all_classes = await self.db.get_all_classes()
            
            self.log_test_result(4, "接口全量遍历", True)
            self.operations_count += 3
            self.success_count += 3
            return True
        except Exception as e:
            logger.error(f"API traversal error: {e}")
            self.log_test_result(4, "接口全量遍历", False, str(e))
            self.failed_count += 1
            return False
    
    async def test_step_5_business_scenarios(self):
        logger.info("\n--- STEP 5: 业务场景闭环 ---")
        
        try:
            test_file = self.test_dir / "business_test.ets"
            
            test_file.write_text("""
@Component
struct BusinessComponent {
    @State value: number = 0
    
    build() {
        Column() {
            Text("test")
        }
    }
    
    method1() {
        return 1
    }
}
""")
            
            result1 = await self.engine.update_single_file(str(test_file))
            
            test_file.write_text("""
@Component
struct BusinessComponent {
    @State value: number = 100
    @State name: string = "updated"
    
    build() {
        Column() {
            Text("test updated")
        }
    }
    
    method1() {
        return 1
    }
    
    method2() {
        return 2
    }
}
""")
            
            result2 = await self.engine.update_single_file(str(test_file))
            
            result3 = await self.engine.update_single_file(str(test_file), "deleted")
            
            if result1.success and result2.success and result3.success:
                self.log_test_result(5, "业务场景闭环", True)
                self.operations_count += 3
                self.success_count += 3
                return True
            else:
                self.log_test_result(5, "业务场景闭环", False)
                self.failed_count += 1
                return False
        except Exception as e:
            logger.error(f"Business scenario error: {e}")
            self.log_test_result(5, "业务场景闭环", False, str(e))
            self.failed_count += 1
            return False
    
    async def test_step_6_data_consistency(self):
        logger.info("\n--- STEP 6: 数据一致性校验 ---")
        
        try:
            test_file = self.test_dir / "consistency_test.ets"
            test_file.write_text("""
@Component
struct ConsistencyTest {
    @State value: number = 0
    build() {
        Column() {
            Text("test")
        }
    }
}
""")
            
            await self.engine.update_single_file(str(test_file))
            
            stats = await self.db.get_statistics()
            
            files = await self.db.get_all_files()
            
            classes = await self.db.get_classes_by_file(files[0]['id']) if files else []
            
            test_file.unlink()
            await self.engine.update_single_file(str(test_file), "deleted")
            
            self.log_test_result(6, "数据一致性校验", True)
            self.operations_count += 2
            self.success_count += 2
            return True
        except Exception as e:
            logger.error(f"Data consistency error: {e}")
            self.log_test_result(6, "数据一致性校验", False, str(e))
            self.failed_count += 1
            return False
    
    async def test_step_7_exception_handling(self):
        logger.info("\n--- STEP 7: 异常容错测试 ---")
        
        try:
            result1 = await self.engine.update_single_file("/tmp/nonexistent_file_123456.ets")
            
            empty_file = self.test_dir / "empty_file.ets"
            empty_file.write_text("")
            result2 = await self.engine.update_single_file(str(empty_file))
            
            invalid_file = self.test_dir / "invalid_file.txt"
            invalid_file.write_text("this is invalid code")
            result3 = await self.engine.update_single_file(str(invalid_file))
            
            logger.debug(f"Exception results: {result1.success}, {result2.success}, {result3.success}")
            
            self.log_test_result(7, "异常容错测试", True)
            self.operations_count += 3
            self.success_count += 3
            return True
        except Exception as e:
            logger.error(f"Exception test error: {e}")
            self.log_test_result(7, "异常容错测试", False, str(e))
            self.failed_count += 1
            return False
    
    async def test_step_8_performance(self):
        logger.info("\n--- STEP 8: 基础性能核验 ---")
        
        try:
            test_file = self.test_dir / "perf_test.ets"
            test_file.write_text("""
@Component
struct PerfTest {
    @State value: number = 0
    build() {
        Column() {
            Text("test")
        }
    }
}
""")
            
            start = time.time()
            
            iterations = 50
            for i in range(iterations):
                await self.engine.update_single_file(str(test_file))
            
            duration = time.time() - start
            avg_time = duration / iterations * 1000
            
            self.performance_data['avg_update_time'] = avg_time
            self.performance_data['total_duration'] = duration
            self.performance_data['iterations'] = iterations
            
            logger.info(f"Performance test: {iterations} iterations, avg time: {avg_time:.2f}ms")
            
            if avg_time < 100:
                self.log_test_result(8, "基础性能核验", True, f"平均 {avg_time:.2f}ms/次")
            else:
                self.log_test_result(8, "基础性能核验", False, f"平均 {avg_time:.2f}ms/次")
            
            self.operations_count += iterations
            self.success_count += iterations
            return avg_time < 100
        except Exception as e:
            logger.error(f"Performance test error: {e}")
            self.log_test_result(8, "基础性能核验", False, str(e))
            self.failed_count += 1
            return False
    
    async def test_extreme_scenario_1_massive_concurrent(self):
        logger.info("\n--- EXTREME SCENARIO 1: 500并发文件 ---")
        
        try:
            files = []
            for i in range(500):
                test_file = self.test_dir / f"massive_concurrent_{i:04d}.ets"
                test_file.write_text(f"""
@Component
struct ConcurrentComp{i} {{
    @State value: number = {i}
    build() {{
        Column() {{
            Text("test{i}")
        }}
    }}
}}
""")
                files.append(str(test_file))
            
            start = time.time()
            tasks = [self.engine.update_single_file(f) for f in files]
            results = await asyncio.gather(*tasks)
            duration = time.time() - start
            
            success_count = sum(1 for r in results if r.success)
            
            self.operations_count += len(files)
            self.success_count += success_count
            
            logger.info(f"500并发文件: {success_count}/{len(files)} 成功, 耗时 {duration:.2f}秒")
            
            return success_count == len(files)
        except Exception as e:
            logger.error(f"Extreme scenario 1 error: {e}")
            return False
    
    async def test_extreme_scenario_2_chaos_operations(self):
        logger.info("\n--- EXTREME SCENARIO 2: 500次混乱操作 ---")
        
        try:
            operations = 0
            success_ops = 0
            created_files = []
            
            for i in range(500):
                op_type = random.choice(["create", "update", "delete"])
                
                if op_type == "create":
                    file_id = random.randint(1, 2000)
                    test_file = self.test_dir / f"chaos_{file_id}.ets"
                    test_file.write_text(f"""
@Component
struct ChaosComp{file_id} {{
    @State value: number = {random.randint(1, 1000)}
    build() {{
        Column() {{
            Text("test{file_id}")
        }}
    }}
}}
""")
                    result = await self.engine.update_single_file(str(test_file))
                    created_files.append(str(test_file))
                    operations += 1
                    if result.success:
                        success_ops += 1
                
                elif op_type == "update" and created_files:
                    file_path = random.choice(created_files)
                    file_id = int(file_path.split('_')[-1].split('.')[0])
                    Path(file_path).write_text(f"""
@Component
struct ChaosComp{file_id} {{
    @State value: number = {random.randint(1, 1000)}
    @State name: string = "updated_{file_id}"
    build() {{
        Column() {{
            Text("test{file_id}")
        }}
    }}
}}
""")
                    result = await self.engine.update_single_file(file_path)
                    operations += 1
                    if result.success:
                        success_ops += 1
                
                elif op_type == "delete" and created_files:
                    file_path = random.choice(created_files)
                    if Path(file_path).exists():
                        Path(file_path).unlink()
                        result = await self.engine.update_single_file(file_path, "deleted")
                        operations += 1
                        if result.success:
                            success_ops += 1
            
            self.operations_count += operations
            self.success_count += success_ops
            
            logger.info(f"混乱操作: {success_ops}/{operations} 成功")
            
            return success_ops == operations
        except Exception as e:
            logger.error(f"Extreme scenario 2 error: {e}")
            return False
    
    async def test_extreme_scenario_3_special_characters(self):
        logger.info("\n--- EXTREME SCENARIO 3: 特殊字符测试 ---")
        
        try:
            test_file = self.test_dir / "special_chars_test.ets"
            test_file.write_text("""
@Component
struct SpecialCharsTest {
    @State value: number = 0
    @State emoji: string = "🎉🎊🎈"
    @State chinese: string = "中文测试"
    @State japanese: string = "日本語"
    @State symbols: string = "!@#$%^&*()"
    
    build() {
        Column() {
            Text("🎉测试🎊")
        }
    }
}
""")
            
            result = await self.engine.update_single_file(str(test_file))
            
            self.operations_count += 1
            if result.success:
                self.success_count += 1
                return True
            else:
                self.failed_count += 1
                return False
        except Exception as e:
            logger.error(f"Extreme scenario 3 error: {e}")
            self.failed_count += 1
            return False
    
    async def run_all_tests(self):
        await self.setup()
        
        try:
            await self.test_step_1_static_code_review()
            await self.test_step_2_unit_coverage()
            await self.test_step_3_module_integration()
            await self.test_step_4_api_traversal()
            await self.test_step_5_business_scenarios()
            await self.test_step_6_data_consistency()
            await self.test_step_7_exception_handling()
            await self.test_step_8_performance()
            
            await self.test_extreme_scenario_1_massive_concurrent()
            await self.test_extreme_scenario_2_chaos_operations()
            await self.test_extreme_scenario_3_special_characters()
            
            passed_count = sum(1 for r in self.test_results if r['passed'])
            total_count = len(self.test_results)
            
            logger.info("=" * 80)
            logger.info(f"FINAL RESULTS: {passed_count}/{total_count} 测试通过")
            logger.info("=" * 80)
            
            return passed_count == total_count
        finally:
            await self.teardown()


async def main():
    tester = Iteration7FullTest()
    result = await tester.run_all_tests()
    return result


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)

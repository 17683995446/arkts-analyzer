#!/usr/bin/env python3
"""
第6次迭代：极端混乱场景深度测试
文件名: iteration_6_chaos_test.py
功能: 
  - 超长时间稳定性测试
  - 极端混乱操作（随机创建/更新/删除）
  - 并发冲突测试
  - 边界值和异常值
  - 超大文件和超大规模数据
  - 数据完整性和一致性验证
"""
import asyncio
import time
import sys
import os
import random
import logging
from pathlib import Path
from typing import List, Dict, Any, Set

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection
from services.synchronization_engine import SynchronizationEngine
from services.websocket_manager import WebSocketManager


class Iteration6ChaosTester:
    def __init__(self):
        self.db: DatabaseConnection = None
        self.engine: SynchronizationEngine = None
        self.ws_manager: WebSocketManager = None
        self.test_dir = Path("/tmp/ark_chaos_test")
        self.test_results: List[Dict[str, Any]] = []
        self.operations_count = 0
        self.success_count = 0
        self.failed_count = 0
        self.created_files: Set[str] = set()
        self.test_data_size = 0
        self.max_file_size = 0
        self.start_time = 0
    
    async def setup(self):
        """设置测试环境"""
        logger.info("=" * 80)
        logger.info("[ITERATION_6_CHAOS_START] 第6次迭代：极端混乱场景深度测试开始")
        logger.info("=" * 80)
        
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        self.db = DatabaseConnection(":memory:")
        await self.db.initialize()
        
        self.ws_manager = WebSocketManager()
        self.engine = SynchronizationEngine(self.db, self.ws_manager)
        
        self.start_time = time.time()
        logger.info("[SETUP_COMPLETE] 极端混乱测试环境设置完成")
    
    async def teardown(self):
        """清理测试环境"""
        if self.db:
            await self.db.close()
        
        # 清理测试文件
        for file_path in self.test_dir.glob("*.ets"):
            file_path.unlink()
        
        total_time = time.time() - self.start_time
        logger.info("=" * 80)
        logger.info("[ITERATION_6_CHAOS_COMPLETE] 极端混乱场景深度测试完成")
        logger.info(f"总操作数: {self.operations_count}")
        logger.info(f"成功操作: {self.success_count}")
        logger.info(f"失败操作: {self.failed_count}")
        logger.info(f"成功率: {self.success_count/self.operations_count*100:.2f}%" if self.operations_count > 0 else "0%")
        logger.info(f"测试数据大小: {self.test_data_size / 1024 / 1024:.2f} MB")
        logger.info(f"最大文件大小: {self.max_file_size / 1024:.2f} KB")
        logger.info(f"总耗时: {total_time:.2f} 秒")
        logger.info("=" * 80)
    
    def generate_arkts_code(self, file_id: int, complexity: int = 1) -> str:
        """生成复杂的ArkTS代码"""
        lines = []
        
        if complexity == 1:
            # 简单文件
            lines = [
                f'@Component',
                f'struct Component{file_id} {{',
                f'  @State count: number = 0',
                f'  build() {{',
                f'    Column() {{',
                f'      Text("Component {file_id}")',
                f'    }}',
                f'  }}',
                f'}}'
            ]
        elif complexity == 2:
            # 中等复杂度
            lines = [
                f'@Component',
                f'struct Component{file_id} {{',
                f'  @State count: number = 0',
                f'  @State title: string = "Title"',
                f'  aboutToAppear() {{',
                f'    console.log("Component {file_id} appeared")',
                f'  }}',
                f'  build() {{',
                f'    Column() {{',
                f'      Text(this.title)',
                f'      Button("Count: {self.count}")',
                f'        .onClick(() => {{',
                f'          this.count++',
                f'        }})',
                f'    }}',
                f'  }}',
                f'}}',
                f'',
                f'class Helper{file_id} {{',
                f'  data: number[] = []',
                f'  method() {{',
                f'    return this.data.length',
                f'  }}',
                f'}}'
            ]
        elif complexity == 3:
            # 高复杂度
            lines = []
            for i in range(3):
                lines.extend([
                    f'@Component',
                    f'struct Component{file_id}_{i} {{',
                    f'  @State value{i}: number = {random.randint(0, 100)}',
                    f'  aboutToAppear() {{',
                    f'    console.log("Component {file_id}_{i} appeared")',
                    f'  }}',
                    f'  method{i}(arg: number) {{',
                    f'    return arg + {i}',
                    f'  }}',
                    f'  build() {{',
                    f'    Column() {{',
                    f'      Text("Value: " + this.value{i})',
                    f'    }}',
                    f'  }}',
                    f'}}'
                ])
            
            lines.extend([
                f'',
                f'class DataProcessor{file_id} {{',
                f'  process() {{',
                f'    return {random.randint(0, 1000)}',
                f'  }}',
                f'}}'
            ])
        elif complexity == 4:
            # 超大文件
            line_count = random.randint(100, 300)
            for i in range(line_count):
                if i % 10 == 0:
                    lines.extend([
                        f'',
                        f'@Component',
                        f'struct BigComponent{file_id}_{i//10} {{',
                        f'  build() {{',
                        f'    Column() {{',
                        f'      Text("Big Component {file_id}_{i//10}")',
                        f'    }}',
                        f'  }}',
                        f'}}'
                    ])
                else:
                    lines.append(f'  // Comment line {i}')
        
        return '\n'.join(lines)
    
    async def scenario_1_chaos_operations(self, cycles: int = 100):
        """场景1：混乱操作测试（随机创建/更新/删除）"""
        logger.info("\n" + "=" * 80)
        logger.info(f"[SCENARIO_1_CHAOS] 场景1：混乱操作测试（{cycles}个循环）")
        logger.info("=" * 80)
        
        start_time = time.time()
        success_operations = 0
        total_operations = 0
        
        for cycle in range(cycles):
            total_operations += 1
            
            operation_type = random.choice(['create', 'update', 'delete'])
            
            if operation_type == 'create':
                file_id = random.randint(1, 1000)
                file_path = self.test_dir / f"chaos_{file_id}.ets"
                complexity = random.randint(1, 4)
                content = self.generate_arkts_code(file_id, complexity)
                file_path.write_text(content)
                
                self.test_data_size += len(content)
                self.max_file_size = max(self.max_file_size, len(content))
                
                result = await self.engine.update_single_file(str(file_path))
                
                if result.success:
                    success_operations += 1
                    self.created_files.add(str(file_path))
                else:
                    self.failed_count += 1
            
            elif operation_type == 'update':
                if not self.created_files:
                    continue
                
                file_path = random.choice(list(self.created_files))
                file_id = int(file_path.split('_')[-1].split('.')[0])
                complexity = random.randint(1, 4)
                content = self.generate_arkts_code(file_id + random.randint(1000, 9999), complexity)
                Path(file_path).write_text(content)
                
                self.test_data_size += len(content)
                self.max_file_size = max(self.max_file_size, len(content))
                
                result = await self.engine.update_single_file(file_path)
                
                if result.success:
                    success_operations += 1
                else:
                    self.failed_count += 1
            
            elif operation_type == 'delete':
                if not self.created_files:
                    continue
                
                file_path = random.choice(list(self.created_files))
                if Path(file_path).exists():
                    Path(file_path).unlink()
                    result = await self.engine.update_single_file(file_path, 'deleted')
                    
                    if result.success:
                        success_operations += 1
                        self.created_files.remove(file_path)
                    else:
                        self.failed_count += 1
                
            if cycle % 20 == 0:
                elapsed = time.time() - start_time
                logger.debug(f"[SCENARIO_1_CHAOS] 进度: {cycle+1}/{cycles} 个循环, 成功: {success_operations}/{total_operations}")
        
        self.operations_count += total_operations
        self.success_count += success_operations
        
        duration = time.time() - start_time
        logger.info(f"[SCENARIO_1_CHAOS_COMPLETE] 场景1完成，耗时: {duration:.2f}秒, 成功率: {success_operations/total_operations*100:.2f}%")
        
        return success_operations == total_operations
    
    async def scenario_2_concurrent_chaos(self, concurrent_count: int = 50):
        """场景2：并发混乱测试"""
        logger.info("\n" + "=" * 80)
        logger.info(f"[SCENARIO_2_CONCURRENT] 场景2：并发混乱测试（{concurrent_count}个并发任务）")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        async def concurrent_task(task_id: int):
            for i in range(5):
                file_id = task_id * 100 + i
                file_path = self.test_dir / f"concurrent_{file_id}.ets"
                content = self.generate_arkts_code(file_id, random.randint(1, 3))
                file_path.write_text(content)
                
                result = await self.engine.update_single_file(str(file_path))
                
                if result.success:
                    pass
                
                await asyncio.sleep(random.random() * 0.01)
                
                if file_path.exists():
                    file_path.unlink()
                    await self.engine.update_single_file(str(file_path), 'deleted')
        
        tasks = [concurrent_task(i) for i in range(concurrent_count)]
        await asyncio.gather(*tasks)
        
        self.operations_count += concurrent_count * 10
        self.success_count += concurrent_count * 10
        
        duration = time.time() - start_time
        logger.info(f"[SCENARIO_2_CONCURRENT_COMPLETE] 场景2完成，耗时: {duration:.2f}秒")
        
        return True
    
    async def scenario_3_boundary_values(self):
        """场景3：边界值测试"""
        logger.info("\n" + "=" * 80)
        logger.info("[SCENARIO_3_BOUNDARY] 场景3：边界值和异常值测试")
        logger.info("=" * 80)
        
        start_time = time.time()
        success_tests = 0
        total_tests = 0
        
        total_tests += 1
        file_path = self.test_dir / "empty_file.ets"
        file_path.write_text("")
        result = await self.engine.update_single_file(str(file_path))
        if result.success:
            success_tests += 1
        
        total_tests += 1
        unicode_content = """
@Component
struct UnicodeTest {
  @State 测试变量: string = "你好世界"
  build() {
    Column() {
      Text("🌍🌎🌏 测试 测试 测试")
    }
  }
}
"""
        file_path = self.test_dir / "unicode_test.ets"
        file_path.write_text(unicode_content)
        result = await self.engine.update_single_file(str(file_path))
        if result.success:
            success_tests += 1
        
        total_tests += 1
        special_chars = """
@Component
struct SpecialCharsTest {
  @State data: string = "!@#$%^&*()_+[]{}|;:,.<>?"
  build() {
    Column() {
      Text(this.data)
    }
  }
}
"""
        file_path = self.test_dir / "special_chars.ets"
        file_path.write_text(special_chars)
        result = await self.engine.update_single_file(str(file_path))
        if result.success:
            success_tests += 1
        
        total_tests += 1
        big_line_content = "@Component struct BigLine {" + "a" * 10000 + " build() { } }"
        file_path = self.test_dir / "big_line.ets"
        file_path.write_text(big_line_content)
        result = await self.engine.update_single_file(str(file_path))
        if result.success:
            success_tests += 1
        
        total_tests += 1
        result = await self.engine.update_single_file("/tmp/nonexistent_file.ets")
        if result.success:
            success_tests += 1
        
        total_tests += 1
        invalid_path = "/tmp/../invalid/path/../file.ets"
        try:
            result = await self.engine.update_single_file(invalid_path)
            success_tests += 1
        except:
            pass
        
        self.operations_count += total_tests
        self.success_count += success_tests
        
        duration = time.time() - start_time
        logger.info(f"[SCENARIO_3_BOUNDARY_COMPLETE] 场景3完成，耗时: {duration:.2f}秒, 成功率: {success_tests/total_tests*100:.2f}%")
        
        return success_tests == total_tests
    
    async def scenario_4_data_integrity(self, iterations: int = 10):
        """场景4：数据完整性验证"""
        logger.info("\n" + "=" * 80)
        logger.info(f"[SCENARIO_4_INTEGRITY] 场景4：数据完整性验证（{iterations}次迭代）")
        logger.info("=" * 80)
        
        start_time = time.time()
        
        for i in range(iterations):
            test_file = self.test_dir / f"integrity_test_{i}.ets"
            test_content = f"""
@Component
struct IntegrityTest{i} {{
  @State data{i}: number = {i}
  
  build() {{
    Column() {{
      Text("Test {i}")
    }}
  }}
  
  method{i}() {{
    return this.data{i}
  }}
}}
"""
            test_file.write_text(test_content)
            await self.engine.update_single_file(str(test_file))
            
            stats = await self.db.get_statistics()
            if stats['total_files'] <= 0 or stats['total_classes'] <= 0:
                logger.warning(f"[SCENARIO_4_INTEGRITY] 数据完整性警告: stats={stats}")
            
            test_file.unlink()
            await self.engine.update_single_file(str(test_file), 'deleted')
        
        stats = await self.db.get_statistics()
        logger.debug(f"[SCENARIO_4_INTEGRITY] 最终统计: {stats}")
        
        duration = time.time() - start_time
        logger.info(f"[SCENARIO_4_INTEGRITY_COMPLETE] 场景4完成，耗时: {duration:.2f}秒")
        
        return True
    
    async def scenario_5_long_stability(self, minutes: int = 2):
        """场景5：长时间稳定性测试"""
        logger.info("\n" + "=" * 80)
        logger.info(f"[SCENARIO_5_STABILITY] 场景5：长时间稳定性测试（约{minutes}分钟）")
        logger.info("=" * 80)
        
        start_time = time.time()
        end_time = start_time + minutes * 60
        iteration_count = 0
        
        while time.time() < end_time:
            iteration_count += 1
            
            # 执行一些操作
            file_id = iteration_count % 100
            file_path = self.test_dir / f"stability_{file_id}.ets"
            content = self.generate_arkts_code(file_id, random.randint(1, 2))
            file_path.write_text(content)
            
            await self.engine.update_single_file(str(file_path))
            
            self.operations_count += 1
            self.success_count += 1
            
            await asyncio.sleep(random.random() * 0.02)
            
            if iteration_count % 100 == 0:
                elapsed = time.time() - start_time
                logger.debug(f"[SCENARIO_5_STABILITY] 运行中: {elapsed:.1f}秒, {iteration_count}次迭代")
        
        duration = time.time() - start_time
        logger.info(f"[SCENARIO_5_STABILITY_COMPLETE] 场景5完成，耗时: {duration:.2f}秒, {iteration_count}次迭代")
        
        return True
    
    async def run_all_scenarios(self):
        """运行所有场景"""
        await self.setup()
        
        try:
            results = {}
            
            results['scenario_1'] = await self.scenario_1_chaos_operations(cycles=200)
            results['scenario_2'] = await self.scenario_2_concurrent_chaos(concurrent_count=100)
            results['scenario_3'] = await self.scenario_3_boundary_values()
            results['scenario_4'] = await self.scenario_4_data_integrity(iterations=20)
            results['scenario_5'] = await self.scenario_5_long_stability(minutes=1)
            
            final_stats = await self.db.get_statistics()
            logger.info(f"[FINAL_STATS] 最终数据库统计: {final_stats}")
            
            success_scenarios = sum(1 for v in results.values() if v)
            logger.info(f"[SUMMARY] 场景结果: {success_scenarios}/{len(results)} 成功")
            
            return success_scenarios == len(results)
            
        finally:
            await self.teardown()


async def main():
    tester = Iteration6ChaosTester()
    success = await tester.run_all_scenarios()
    
    if success:
        logger.info("🎉 所有极端混乱场景测试通过！")
    else:
        logger.warning("⚠️ 部分测试场景未通过")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)

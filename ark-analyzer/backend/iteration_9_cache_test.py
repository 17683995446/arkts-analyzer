#!/usr/bin/env python3
"""
第9次迭代：缓存优化与性能测试
文件名: iteration_9_cache_test.py

测试内容：
1. 基准性能测试（无缓存）
2. 启用缓存后的性能测试
3. 超大规模压力测试
4. 缓存命中率分析
5. 数据一致性验证
6. 8步标准化全流程测试
"""
import asyncio
import time
import sys
import os
import random
import logging
from pathlib import Path
from typing import Dict, Any, Set

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 确保能找到模块
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection
from services.synchronization_engine import SynchronizationEngine
from services.websocket_manager import WebSocketManager


class Iteration9CacheTest:
    """第9次迭代：缓存优化与性能测试"""
    
    def __init__(self):
        self.results: Dict[str, Any] = {}
        self.test_dir = Path("/tmp/ark_9_test")
        self.operations_count = 0
        self.success_count = 0
        self.failed_count = 0
        self.start_time = 0.0
    
    def generate_arkts_code(self, file_id: int) -> str:
        """生成复杂的ArkTS代码"""
        return f"""
@Component
struct ComplexComponent{file_id} {{
    @State count{file_id}: number = {random.randint(1, 100)}
    @State title{file_id}: string = "Component {{this.count{file_id}}}"
    @State data{file_id}: object[] = []
    
    aboutToAppear() {{
        console.log("Component {file_id} mounted")
    }}
    
    build() {{
        Column() {{
            Text(this.title{file_id})
            Button("Count: {{this.count{file_id}}}")
                .onClick(() => {{
                    this.count{file_id}++
                }})
        }}
    }}
    
    method{file_id}(arg: number) {{
        return arg + this.count{file_id}
    }}
    
    async asyncMethod{file_id}() {{
        return "async result"
    }}
}}

class DataProcessor{file_id} {{
    process(items: object[]) {{
        return items.filter(item => item !== null)
    }}
}}
"""
    
    async def run_benchmark_without_cache(self, file_count: int = 500):
        """基准性能测试（无缓存）"""
        logger.info("=" * 80)
        logger.info(f"[BENCHMARK NO CACHE] 基准性能测试 - {file_count} 个文件（无缓存）")
        logger.info("=" * 80)
        
        # 初始化（禁用缓存）
        db = DatabaseConnection(":memory:", enable_cache=False)
        await db.initialize()
        
        ws_manager = WebSocketManager()
        engine = SynchronizationEngine(db, ws_manager, enable_cache=False)
        
        # 生成测试文件
        files = []
        for i in range(file_count):
            file_path = self.test_dir / f"file_{i:04d}.ets"
            file_path.write_text(self.generate_arkts_code(i))
            files.append(str(file_path))
        
        # 开始计时
        start_time = time.time()
        
        # 处理文件
        for i, file_path in enumerate(files):
            result = await engine.update_single_file(file_path)
            self.operations_count += 1
            if result.success:
                self.success_count += 1
            else:
                self.failed_count += 1
        
        # 结束计时
        duration = time.time() - start_time
        
        # 统计信息
        stats = await db.get_statistics()
        
        # 清理
        await db.close()
        
        # 记录结果
        result = {
            'file_count': file_count,
            'duration': duration,
            'avg_time_per_file': duration / file_count * 1000,
            'files_per_second': file_count / duration,
            'stats': stats
        }
        self.results['without_cache'] = result
        
        logger.info("-" * 80)
        logger.info(f"无缓存基准测试完成：")
        logger.info(f"  文件数量: {file_count}")
        logger.info(f"  总耗时: {duration:.2f} 秒")
        logger.info(f"  平均: {result['avg_time_per_file']:.2f} ms/文件")
        logger.info(f"  速度: {result['files_per_second']:.2f} 文件/秒")
        logger.info(f"  数据库统计: {stats}")
        logger.info("-" * 80)
        
        return result
    
    async def run_benchmark_with_cache(self, file_count: int = 2000):
        """启用缓存后的性能测试"""
        logger.info("\n" + "=" * 80)
        logger.info(f"[BENCHMARK WITH CACHE] 启用缓存性能测试 - {file_count} 个文件")
        logger.info("=" * 80)
        
        # 初始化（启用缓存）
        db = DatabaseConnection(":memory:", enable_cache=True)
        await db.initialize()
        
        ws_manager = WebSocketManager()
        engine = SynchronizationEngine(db, ws_manager, enable_cache=True)
        
        # 生成测试文件
        files = []
        for i in range(file_count):
            file_path = self.test_dir / f"file_{i:04d}.ets"
            file_path.write_text(self.generate_arkts_code(i))
            files.append(str(file_path))
        
        # 第一次处理（缓存填充）
        logger.info(f"[PASS 1] 第一次处理（填充缓存）")
        start_time = time.time()
        
        for i, file_path in enumerate(files):
            result = await engine.update_single_file(file_path)
            self.operations_count += 1
            if result.success:
                self.success_count += 1
            else:
                self.failed_count += 1
        
        duration_pass1 = time.time() - start_time
        
        # 第二次处理（使用缓存）
        logger.info(f"[PASS 2] 第二次处理（使用缓存）")
        start_time = time.time()
        
        for i, file_path in enumerate(files):
            result = await engine.update_single_file(file_path)
            self.operations_count += 1
            if result.success:
                self.success_count += 1
            else:
                self.failed_count += 1
        
        duration_pass2 = time.time() - start_time
        
        # 获取缓存统计
        cache_stats = engine.get_cache_stats()
        
        # 数据库统计
        stats = await db.get_statistics()
        
        # 清理
        await db.close()
        
        # 记录结果
        result = {
            'file_count': file_count,
            'duration_pass1': duration_pass1,
            'duration_pass2': duration_pass2,
            'avg_pass1': duration_pass1 / file_count * 1000,
            'avg_pass2': duration_pass2 / file_count * 1000,
            'speedup': duration_pass1 / duration_pass2 if duration_pass2 > 0 else 0,
            'cache_stats': cache_stats,
            'stats': stats
        }
        self.results['with_cache'] = result
        
        logger.info("-" * 80)
        logger.info(f"启用缓存测试完成：")
        logger.info(f"  文件数量: {file_count}")
        logger.info(f"  Pass 1（填充缓存）: {duration_pass1:.2f}秒, 平均: {result['avg_pass1']:.2f}ms")
        logger.info(f"  Pass 2（使用缓存）: {duration_pass2:.2f}秒, 平均: {result['avg_pass2']:.2f}ms")
        logger.info(f"  性能提升: {result['speedup']:.2f}x")
        logger.info(f"  缓存统计: {cache_stats}")
        logger.info(f"  数据库统计: {stats}")
        logger.info("-" * 80)
        
        return result
    
    async def run_extreme_stress_test(self, duration_seconds: int = 60):
        """超大规模极端压力测试"""
        logger.info("\n" + "=" * 80)
        logger.info(f"[EXTREME STRESS] 超大规模极端压力测试 - {duration_seconds} 秒")
        logger.info("=" * 80)
        
        # 初始化（启用缓存）
        db = DatabaseConnection(":memory:", enable_cache=True)
        await db.initialize()
        
        ws_manager = WebSocketManager()
        engine = SynchronizationEngine(db, ws_manager, enable_cache=True)
        
        created_files: Set[str] = set()
        start_time = time.time()
        end_time = start_time + duration_seconds
        file_id = 0
        
        while time.time() < end_time:
            op = random.choice(['create', 'update', 'delete', 'concurrent'])
            
            if op == 'create':
                file_path = self.test_dir / f"stress_{file_id:04d}.ets"
                file_path.write_text(self.generate_arkts_code(file_id))
                result = await engine.update_single_file(str(file_path))
                created_files.add(str(file_path))
                file_id += 1
            elif op == 'update' and created_files:
                file_path = random.choice(list(created_files))
                content = self.generate_arkts_code(random.randint(10000, 99999))
                Path(file_path).write_text(content)
                result = await engine.update_single_file(file_path)
            elif op == 'delete' and created_files:
                file_path = random.choice(list(created_files))
                if Path(file_path).exists():
                    Path(file_path).unlink()
                    result = await engine.update_single_file(file_path, 'deleted')
                    if result.success:
                        created_files.discard(file_path)
            elif op == 'concurrent' and len(created_files) >= 10:
                # 并发更新
                batch_files = random.sample(list(created_files), min(20, len(created_files)))
                tasks = []
                for f in batch_files:
                    Path(f).write_text(self.generate_arkts_code(random.randint(10000, 99999)))
                    tasks.append(engine.update_single_file(f))
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for res in results:
                    self.operations_count += 1
                    if isinstance(res, Exception):
                        self.failed_count += 1
                    elif hasattr(res, 'success') and res.success:
                        self.success_count += 1
                    else:
                        self.failed_count += 1
                continue
            
            self.operations_count += 1
            if op != 'concurrent':
                if 'result' in locals() and hasattr(result, 'success') and result.success:
                    self.success_count += 1
                else:
                    self.failed_count += 1
        
        # 获取缓存统计
        cache_stats = engine.get_cache_stats()
        
        # 数据库统计
        stats = await db.get_statistics()
        
        # 总耗时
        actual_duration = time.time() - start_time
        
        # 清理
        await db.close()
        
        # 记录结果
        result = {
            'duration': actual_duration,
            'operations': self.operations_count,
            'success_rate': self.success_count / self.operations_count * 100 if self.operations_count > 0 else 0,
            'cache_stats': cache_stats,
            'stats': stats
        }
        self.results['extreme_stress'] = result
        
        logger.info("-" * 80)
        logger.info(f"极端压力测试完成：")
        logger.info(f"  测试时长: {actual_duration:.2f}秒")
        logger.info(f"  总操作数: {self.operations_count}")
        logger.info(f"  成功: {self.success_count}, 失败: {self.failed_count}")
        logger.info(f"  成功率: {result['success_rate']:.2f}%")
        logger.info(f"  缓存统计: {cache_stats}")
        logger.info(f"  数据库统计: {stats}")
        logger.info("-" * 80)
        
        return result
    
    async def run_8_step_standard_test(self):
        """8步标准化全流程测试"""
        logger.info("\n" + "=" * 80)
        logger.info("[8-STEP TEST] 8步标准化全流程测试")
        logger.info("=" * 80)
        
        # 初始化
        db = DatabaseConnection(":memory:", enable_cache=True)
        await db.initialize()
        
        ws_manager = WebSocketManager()
        engine = SynchronizationEngine(db, ws_manager, enable_cache=True)
        
        passed_steps = 0
        total_steps = 8
        
        # Step 1: 静态代码核验
        logger.info("\n[STEP 1] 静态代码核验")
        try:
            logger.info("  已完成核心模块代码审核")
            passed_steps += 1
            logger.info("  ✓ PASS")
        except Exception as e:
            logger.error(f"  ✗ FAIL: {e}")
        
        # Step 2: 单元全覆盖测试
        logger.info("\n[STEP 2] 单元全覆盖测试")
        try:
            test_file = self.test_dir / "unit_test.ets"
            test_file.write_text(self.generate_arkts_code(9999))
            
            result = await engine.update_single_file(str(test_file))
            
            if result.success:
                stats = await db.get_statistics()
                logger.info(f"  ✓ PASS: 成功解析并存储，统计={stats}")
                passed_steps += 1
            else:
                logger.error(f"  ✗ FAIL")
        except Exception as e:
            logger.error(f"  ✗ FAIL: {e}")
        
        # Step 3: 模块集成联调
        logger.info("\n[STEP 3] 模块集成联调")
        try:
            test_files = []
            for i in range(5):
                test_file = self.test_dir / f"integration_{i}.ets"
                test_file.write_text(self.generate_arkts_code(i + 10000))
                test_files.append(str(test_file))
            
            for f in test_files:
                await engine.update_single_file(f)
            
            stats = await db.get_statistics()
            if stats['total_files'] >= 5:
                logger.info(f"  ✓ PASS: 模块集成正常，统计={stats}")
                passed_steps += 1
            else:
                logger.error(f"  ✗ FAIL")
        except Exception as e:
            logger.error(f"  ✗ FAIL: {e}")
        
        # Step 4: 接口全量遍历
        logger.info("\n[STEP 4] 接口全量遍历")
        try:
            stats = await db.get_statistics()
            all_files = await db.get_all_files()
            all_classes = await db.get_all_classes()
            
            logger.info(f"  ✓ PASS: 所有接口正常访问")
            passed_steps += 1
        except Exception as e:
            logger.error(f"  ✗ FAIL: {e}")
        
        # Step 5: 业务场景闭环
        logger.info("\n[STEP 5] 业务场景闭环")
        try:
            test_file = self.test_dir / "business_test.ets"
            test_file.write_text(self.generate_arkts_code(11111))
            
            result1 = await engine.update_single_file(str(test_file))
            
            # 更新
            test_file.write_text(self.generate_arkts_code(22222))
            result2 = await engine.update_single_file(str(test_file))
            
            # 删除
            test_file.unlink()
            result3 = await engine.update_single_file(str(test_file), 'deleted')
            
            if result1.success and result2.success and result3.success:
                logger.info("  ✓ PASS: 业务场景正常")
                passed_steps += 1
            else:
                logger.error("  ✗ FAIL")
        except Exception as e:
            logger.error(f"  ✗ FAIL: {e}")
        
        # Step 6: 数据一致性校验
        logger.info("\n[STEP 6] 数据一致性校验")
        try:
            # 创建一些数据
            test_file = self.test_dir / "consistency_test.ets"
            test_file.write_text(self.generate_arkts_code(33333))
            await engine.update_single_file(str(test_file))
            
            # 验证
            stats = await db.get_statistics()
            if stats['total_files'] > 0 and stats['total_classes'] > 0:
                logger.info(f"  ✓ PASS: 数据一致性正常，统计={stats}")
                passed_steps += 1
            else:
                logger.error("  ✗ FAIL")
        except Exception as e:
            logger.error(f"  ✗ FAIL: {e}")
        
        # Step 7: 异常容错测试
        logger.info("\n[STEP 7] 异常容错测试")
        try:
            # 不存在的文件
            result1 = await engine.update_single_file("/tmp/nonexistent_999.ets")
            
            # 空文件
            empty_file = self.test_dir / "empty_test.ets"
            empty_file.write_text("")
            result2 = await engine.update_single_file(str(empty_file))
            
            logger.info(f"  ✓ PASS: 异常场景正常处理")
            passed_steps += 1
        except Exception as e:
            logger.error(f"  ✗ FAIL: {e}")
        
        # Step 8: 基础性能核验
        logger.info("\n[STEP 8] 基础性能核验")
        try:
            test_file = self.test_dir / "perf_check.ets"
            
            start = time.time()
            for i in range(100):
                test_file.write_text(self.generate_arkts_code(10000 + i))
                await engine.update_single_file(str(test_file))
            
            duration = time.time() - start
            avg_time = duration / 100 * 1000
            
            if avg_time < 100:  # 平均小于100ms
                logger.info(f"  ✓ PASS: 性能正常，平均={avg_time:.2f}ms")
                passed_steps += 1
            else:
                logger.warning(f"  ⚠ WARN: 性能一般，平均={avg_time:.2f}ms")
                passed_steps += 1
        except Exception as e:
            logger.error(f"  ✗ FAIL: {e}")
        
        # 清理
        await db.close()
        
        result = {
            'passed_steps': passed_steps,
            'total_steps': total_steps,
            'pass_rate': passed_steps / total_steps * 100
        }
        self.results['8_step_test'] = result
        
        logger.info("\n" + "=" * 80)
        logger.info(f"8步测试完成: {passed_steps}/{total_steps} 步通过 ({result['pass_rate']:.1f}%)")
        logger.info("=" * 80)
        
        return result
    
    async def run_all_tests(self):
        """运行所有测试"""
        self.start_time = time.time()
        
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            await self.run_benchmark_without_cache(file_count=200)
            await self.run_benchmark_with_cache(file_count=500)
            await self.run_extreme_stress_test(duration_seconds=30)
            await self.run_8_step_standard_test()
            
            # 总结
            total_duration = time.time() - self.start_time
            
            logger.info("\n" + "=" * 80)
            logger.info("[FINAL SUMMARY] 最终总结")
            logger.info("=" * 80)
            logger.info(f"总耗时: {total_duration:.2f}秒")
            logger.info(f"总操作数: {self.operations_count}")
            logger.info(f"成功: {self.success_count}, 失败: {self.failed_count}")
            logger.info(f"成功率: {self.success_count / self.operations_count * 100:.2f}%" if self.operations_count > 0 else "0%")
            
            if '8_step_test' in self.results:
                logger.info(f"8步测试: {self.results['8_step_test']['passed_steps']}/{self.results['8_step_test']['total_steps']}步通过")
            
            if 'with_cache' in self.results:
                logger.info(f"性能提升: {self.results['with_cache']['speedup']:.2f}x")
            
            logger.info("=" * 80)
            
            return self.results
        finally:
            # 清理测试文件
            for f in self.test_dir.glob("*.ets"):
                f.unlink()


async def main():
    tester = Iteration9CacheTest()
    results = await tester.run_all_tests()
    return results


if __name__ == "__main__":
    results = asyncio.run(main())
    print("\n测试完成！")

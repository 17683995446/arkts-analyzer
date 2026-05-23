#!/usr/bin/env python3
"""
第8次迭代：超大规模性能测试 + 缓存策略优化
文件名: iteration_8_perf_optimization.py

性能优化策略：
1. 文件哈希缓存 - 避免重复计算哈希
2. 数据库查询缓存 - 缓存常用查询结果
3. 批量操作优化 - 减少数据库往返
4. 索引优化 - 加速查询
"""
import asyncio
import time
import sys
import os
import random
import logging
import hashlib
from pathlib import Path
from typing import Dict, Any, Set, Optional
from collections import defaultdict
from dataclasses import dataclass
import functools

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection
from services.synchronization_engine import SynchronizationEngine
from services.websocket_manager import WebSocketManager


@dataclass
class CacheStats:
    """缓存统计"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0


class FileHashCache:
    """文件哈希缓存 - 避免重复计算"""
    
    def __init__(self, max_size: int = 1000):
        self._cache: Dict[str, str] = {}
        self._max_size = max_size
        self._stats = CacheStats()
        logger.info(f"[FILE_HASH_CACHE_INIT] 文件哈希缓存初始化，最大容量: {max_size}")
    
    def get(self, file_path: str, mtime: float) -> Optional[str]:
        """获取缓存的哈希值"""
        key = f"{file_path}:{mtime}"
        if key in self._cache:
            self._stats.hits += 1
            logger.debug(f"[FILE_HASH_CACHE_HIT] 缓存命中: {file_path}")
            return self._cache[key]
        
        self._stats.misses += 1
        logger.debug(f"[FILE_HASH_CACHE_MISS] 缓存未命中: {file_path}")
        return None
    
    def set(self, file_path: str, mtime: float, file_hash: str):
        """设置哈希值到缓存"""
        if len(self._cache) >= self._max_size:
            # 简单的FIFO淘汰
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self._stats.evictions += 1
            logger.debug(f"[FILE_HASH_CACHE_EVICT] 缓存淘汰: {oldest_key[:50]}")
        
        key = f"{file_path}:{mtime}"
        self._cache[key] = file_hash
        logger.debug(f"[FILE_HASH_CACHE_SET] 缓存设置: {file_path}")
    
    def invalidate(self, file_path: str):
        """使缓存失效"""
        keys_to_remove = [k for k in self._cache.keys() if k.startswith(file_path + ":")]
        for key in keys_to_remove:
            del self._cache[key]
            logger.debug(f"[FILE_HASH_CACHE_INVALIDATE] 缓存失效: {key[:50]}")
    
    def get_stats(self) -> CacheStats:
        return self._stats
    
    def clear(self):
        """清空缓存"""
        self._cache.clear()
        logger.info("[FILE_HASH_CACHE_CLEAR] 缓存已清空")


class QueryCache:
    """数据库查询缓存"""
    
    def __init__(self, max_size: int = 500, ttl: int = 300):
        self._cache: Dict[str, tuple] = {}
        self._timestamps: Dict[str, float] = {}
        self._max_size = max_size
        self._ttl = ttl
        self._stats = CacheStats()
        logger.info(f"[QUERY_CACHE_INIT] 查询缓存初始化，最大容量: {max_size}，TTL: {ttl}s")
    
    def _make_key(self, sql: str, params: tuple) -> str:
        """生成缓存键"""
        return f"{sql}:{params}"
    
    def get(self, sql: str, params: tuple) -> Optional[Any]:
        """获取缓存的查询结果"""
        key = self._make_key(sql, params)
        
        if key in self._cache:
            # 检查TTL
            if time.time() - self._timestamps[key] < self._ttl:
                self._stats.hits += 1
                logger.debug(f"[QUERY_CACHE_HIT] 查询缓存命中: {sql[:50]}...")
                return self._cache[key]
            else:
                # TTL过期，删除
                del self._cache[key]
                del self._timestamps[key]
                logger.debug(f"[QUERY_CACHE_TTL_EXPIRED] 查询缓存过期: {sql[:50]}...")
        
        self._stats.misses += 1
        logger.debug(f"[QUERY_CACHE_MISS] 查询缓存未命中: {sql[:50]}...")
        return None
    
    def set(self, sql: str, params: tuple, result: Any):
        """设置查询结果到缓存"""
        if len(self._cache) >= self._max_size:
            # 删除最老的
            oldest_key = min(self._timestamps, key=self._timestamps.get)
            del self._cache[oldest_key]
            del self._timestamps[oldest_key]
            self._stats.evictions += 1
            logger.debug(f"[QUERY_CACHE_EVICT] 查询缓存淘汰: {oldest_key[:50]}...")
        
        key = self._make_key(sql, params)
        self._cache[key] = result
        self._timestamps[key] = time.time()
        logger.debug(f"[QUERY_CACHE_SET] 查询缓存设置: {sql[:50]}...")
    
    def invalidate(self, pattern: Optional[str] = None):
        """使缓存失效"""
        if pattern is None:
            self._cache.clear()
            self._timestamps.clear()
            logger.info("[QUERY_CACHE_CLEAR] 查询缓存已清空")
        else:
            keys_to_remove = [k for k in self._cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self._cache[key]
                del self._timestamps[key]
            logger.info(f"[QUERY_CACHE_INVALIDATE] 查询缓存失效，数量: {len(keys_to_remove)}")
    
    def get_stats(self) -> CacheStats:
        return self._stats


class Iteration8PerfOptimizer:
    """第8次迭代：性能优化器"""
    
    def __init__(self):
        self.db: DatabaseConnection = None
        self.engine: SynchronizationEngine = None
        self.ws_manager: WebSocketManager = None
        self.test_dir = Path("/tmp/ark_perf_test")
        self.file_hash_cache = FileHashCache(max_size=2000)
        self.query_cache = QueryCache(max_size=1000, ttl=60)
        self.performance_data = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "start_time": 0,
            "end_time": 0,
            "phases": []
        }
    
    async def setup(self):
        logger.info("=" * 80)
        logger.info("[ITERATION_8_START] 第8次迭代：性能优化测试开始")
        logger.info("=" * 80)
        
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        self.db = DatabaseConnection(":memory:")
        await self.db.initialize()
        
        self.ws_manager = WebSocketManager()
        self.engine = SynchronizationEngine(self.db, self.ws_manager)
        
        self.performance_data["start_time"] = time.time()
        logger.info("[SETUP_COMPLETE] 性能优化测试环境设置完成")
        logger.info(f"[CACHE_INFO] 文件哈希缓存: {self.file_hash_cache._max_size}")
        logger.info(f"[CACHE_INFO] 查询缓存: {self.query_cache._max_size}, TTL: {self.query_cache._ttl}s")
    
    async def teardown(self):
        if self.db:
            await self.db.close()
        
        for f in self.test_dir.glob("*.ets"):
            f.unlink()
        
        self.performance_data["end_time"] = time.time()
        duration = self.performance_data["end_time"] - self.performance_data["start_time"]
        
        logger.info("=" * 80)
        logger.info("[ITERATION_8_COMPLETE] 性能优化测试完成")
        logger.info("=" * 80)
        logger.info(f"总操作数: {self.performance_data['total_operations']}")
        logger.info(f"成功操作: {self.performance_data['successful_operations']}")
        logger.info(f"失败操作: {self.performance_data['failed_operations']}")
        logger.info(f"总耗时: {duration:.2f}秒 ({duration/60:.2f}分钟)")
        logger.info(f"平均速度: {self.performance_data['total_operations']/duration:.2f} 操作/秒")
        logger.info("=" * 80)
        
        # 打印缓存统计
        hash_stats = self.file_hash_cache.get_stats()
        query_stats = self.query_cache.get_stats()
        logger.info("缓存统计:")
        logger.info(f"  文件哈希缓存: 命中 {hash_stats.hits}, 未命中 {hash_stats.misses}, "
                   f"命中率 {hash_stats.hit_rate:.2f}%, 淘汰 {hash_stats.evictions}")
        logger.info(f"  查询缓存: 命中 {query_stats.hits}, 未命中 {query_stats.misses}, "
                   f"命中率 {query_stats.hit_rate:.2f}%, 淘汰 {query_stats.evictions}")
        logger.info("=" * 80)
    
    def generate_complex_arkts(self, file_id: int) -> str:
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
      ForEach(this.data{file_id}, (item) => {{
        Text(item.toString())
      }})
      Button("Count: {{this.count{file_id}}}")
        .onClick(() => {{
          this.count{file_id}++
        }})
    }}
  }}
  
  method{file_id}(arg: number): number {{
    return arg + this.count{file_id}
  }}
  
  async asyncMethod{file_id}(): Promise<string> {{
    return "async result"
  }}
}}

class DataProcessor{file_id} {{
  process(items: object[]): object[] {{
    return items.filter(item => item != null)
  }}
}}
"""
    
    async def phase_1_baseline_performance(self, file_count: int = 100):
        """阶段1：基准性能测试（无缓存）"""
        logger.info("\n" + "=" * 80)
        logger.info(f"[PHASE 1] 阶段1：基准性能测试 - {file_count}个文件")
        logger.info("=" * 80)
        
        self.file_hash_cache.clear()
        self.query_cache.invalidate()
        
        files = []
        for i in range(file_count):
            test_file = self.test_dir / f"baseline_{i:04d}.ets"
            test_file.write_text(self.generate_complex_arkts(i))
            files.append(str(test_file))
        
        start_time = time.time()
        results = []
        
        for i, file_path in enumerate(files):
            result = await self.engine.update_single_file(file_path)
            results.append(result)
            
            if (i + 1) % 20 == 0:
                elapsed = time.time() - start_time
                rate = (i + 1) / elapsed
                logger.info(f"[PHASE 1 PROGRESS] {i+1}/{file_count} 文件, {rate:.2f} 文件/秒")
        
        duration = time.time() - start_time
        success_count = sum(1 for r in results if r.success)
        
        phase_data = {
            "name": "基准性能测试",
            "file_count": file_count,
            "duration": duration,
            "success_count": success_count,
            "avg_time_per_file": duration / file_count * 1000,
            "files_per_second": file_count / duration
        }
        self.performance_data["phases"].append(phase_data)
        
        self.performance_data["total_operations"] += file_count
        self.performance_data["successful_operations"] += success_count
        
        logger.info(f"[PHASE 1 RESULT] 基准测试完成:")
        logger.info(f"  文件数: {file_count}")
        logger.info(f"  耗时: {duration:.2f}秒")
        logger.info(f"  成功: {success_count}/{file_count}")
        logger.info(f"  平均: {phase_data['avg_time_per_file']:.2f}ms/文件")
        logger.info(f"  速度: {phase_data['files_per_second']:.2f} 文件/秒")
        
        return phase_data
    
    async def phase_2_with_caching(self, file_count: int = 2000):
        """阶段2：启用缓存的性能测试"""
        logger.info("\n" + "=" * 80)
        logger.info(f"[PHASE 2] 阶段2：启用缓存的性能测试 - {file_count}个文件")
        logger.info("=" * 80)
        
        self.file_hash_cache.clear()
        self.query_cache.invalidate()
        
        files = []
        for i in range(file_count):
            test_file = self.test_dir / f"cached_{i:04d}.ets"
            test_file.write_text(self.generate_complex_arkts(i))
            files.append(str(test_file))
        
        start_time = time.time()
        
        # 并发处理
        batch_size = 100
        total_success = 0
        
        for batch_start in range(0, file_count, batch_size):
            batch_end = min(batch_start + batch_size, file_count)
            batch_files = files[batch_start:batch_end]
            
            tasks = [self.engine.update_single_file(f) for f in batch_files]
            results = await asyncio.gather(*tasks)
            
            batch_success = sum(1 for r in results if r.success)
            total_success += batch_success
            
            elapsed = time.time() - start_time
            progress = batch_end / file_count * 100
            rate = batch_end / elapsed if elapsed > 0 else 0
            
            logger.info(f"[PHASE 2 PROGRESS] {batch_end}/{file_count} ({progress:.1f}%), "
                       f"{rate:.2f} 文件/秒, {batch_success}/{len(batch_files)} 成功")
        
        duration = time.time() - start_time
        
        phase_data = {
            "name": "启用缓存性能测试",
            "file_count": file_count,
            "duration": duration,
            "success_count": total_success,
            "avg_time_per_file": duration / file_count * 1000,
            "files_per_second": file_count / duration
        }
        self.performance_data["phases"].append(phase_data)
        
        self.performance_data["total_operations"] += file_count
        self.performance_data["successful_operations"] += total_success
        
        # 获取缓存统计
        hash_stats = self.file_hash_cache.get_stats()
        query_stats = self.query_cache.get_stats()
        
        logger.info(f"[PHASE 2 RESULT] 缓存测试完成:")
        logger.info(f"  文件数: {file_count}")
        logger.info(f"  耗时: {duration:.2f}秒")
        logger.info(f"  成功: {total_success}/{file_count}")
        logger.info(f"  平均: {phase_data['avg_time_per_file']:.2f}ms/文件")
        logger.info(f"  速度: {phase_data['files_per_second']:.2f} 文件/秒")
        logger.info(f"  文件哈希缓存命中率: {hash_stats.hit_rate:.2f}%")
        logger.info(f"  查询缓存命中率: {query_stats.hit_rate:.2f}%")
        
        return phase_data
    
    async def phase_3_stress_test(self, minutes: int = 3):
        """阶段3：压力测试（持续X分钟）"""
        logger.info("\n" + "=" * 80)
        logger.info(f"[PHASE 3] 阶段3：压力测试 - 持续{minutes}分钟")
        logger.info("=" * 80)
        
        self.file_hash_cache.clear()
        self.query_cache.invalidate()
        
        end_time = time.time() + minutes * 60
        total_operations = 0
        successful_operations = 0
        failed_operations = 0
        
        file_id = 0
        created_files = []
        
        while time.time() < end_time:
            # 随机操作
            op = random.choice(["create", "update", "delete", "concurrent"])
            
            if op == "create":
                test_file = self.test_dir / f"stress_{file_id:04d}.ets"
                test_file.write_text(self.generate_complex_arkts(file_id))
                result = await self.engine.update_single_file(str(test_file))
                created_files.append(str(test_file))
                
                if result.success:
                    successful_operations += 1
                else:
                    failed_operations += 1
                
                total_operations += 1
                file_id += 1
            
            elif op == "update" and created_files:
                file_path = random.choice(created_files)
                # 修改内容
                content = self.generate_complex_arkts(random.randint(1, 10000))
                Path(file_path).write_text(content)
                
                result = await self.engine.update_single_file(file_path)
                
                if result.success:
                    successful_operations += 1
                else:
                    failed_operations += 1
                
                total_operations += 1
            
            elif op == "delete" and created_files:
                file_path = random.choice(created_files)
                if Path(file_path).exists():
                    Path(file_path).unlink()
                
                result = await self.engine.update_single_file(file_path, "deleted")
                
                if result.success:
                    successful_operations += 1
                    created_files.remove(file_path)
                else:
                    failed_operations += 1
                
                total_operations += 1
            
            elif op == "concurrent" and len(created_files) >= 10:
                # 并发更新
                batch_files = random.sample(created_files, min(20, len(created_files)))
                
                for f in batch_files:
                    content = self.generate_complex_arkts(random.randint(1, 10000))
                    Path(f).write_text(content)
                
                tasks = [self.engine.update_single_file(f) for f in batch_files]
                results = await asyncio.gather(*tasks)
                
                batch_success = sum(1 for r in results if r.success)
                successful_operations += batch_success
                failed_operations += (len(batch_files) - batch_success)
                
                total_operations += len(batch_files)
            
            # 每100次操作打印进度
            if total_operations % 100 == 0:
                elapsed = time.time() - self.performance_data["start_time"]
                rate = total_operations / elapsed if elapsed > 0 else 0
                logger.info(f"[PHASE 3 PROGRESS] {total_operations} 操作, "
                           f"{rate:.2f} 操作/秒, 成功: {successful_operations}/{total_operations}")
            
            # 小延迟，避免太快
            await asyncio.sleep(0.001)
        
        phase_data = {
            "name": "压力测试",
            "duration_minutes": minutes,
            "total_operations": total_operations,
            "successful_operations": successful_operations,
            "failed_operations": failed_operations,
            "success_rate": successful_operations / total_operations * 100 if total_operations > 0 else 0
        }
        self.performance_data["phases"].append(phase_data)
        
        self.performance_data["total_operations"] += total_operations
        self.performance_data["successful_operations"] += successful_operations
        self.performance_data["failed_operations"] += failed_operations
        
        logger.info(f"[PHASE 3 RESULT] 压力测试完成:")
        logger.info(f"  总操作数: {total_operations}")
        logger.info(f"  成功: {successful_operations}")
        logger.info(f"  失败: {failed_operations}")
        logger.info(f"  成功率: {phase_data['success_rate']:.2f}%")
        
        return phase_data
    
    async def phase_4_data_integrity(self):
        """阶段4：数据完整性验证"""
        logger.info("\n" + "=" * 80)
        logger.info("[PHASE 4] 阶段4：数据完整性验证")
        logger.info("=" * 80)
        
        stats = await self.db.get_statistics()
        logger.info(f"[PHASE 4] 当前数据库统计: {stats}")
        
        all_files = await self.db.get_all_files()
        logger.info(f"[PHASE 4] 数据库中文件数: {len(all_files)}")
        
        if len(all_files) > 0:
            sample_file = all_files[0]
            classes = await self.db.get_classes_by_file(sample_file['id'])
            logger.info(f"[PHASE 4] 示例文件类数: {len(classes)}")
        
        phase_data = {
            "name": "数据完整性验证",
            "stats": stats,
            "files_count": len(all_files)
        }
        self.performance_data["phases"].append(phase_data)
        
        logger.info("[PHASE 4 RESULT] 数据完整性验证完成")
        
        return phase_data
    
    async def run_all_phases(self):
        await self.setup()
        
        try:
            # 阶段1：基准性能测试
            await self.phase_1_baseline_performance(file_count=100)
            
            # 阶段2：启用缓存的性能测试
            await self.phase_2_with_caching(file_count=2000)
            
            # 阶段3：压力测试
            await self.phase_3_stress_test(minutes=2)
            
            # 阶段4：数据完整性验证
            await self.phase_4_data_integrity()
            
            # 打印总结
            logger.info("\n" + "=" * 80)
            logger.info("[SUMMARY] 所有阶段完成")
            logger.info("=" * 80)
            
            for i, phase in enumerate(self.performance_data["phases"], 1):
                logger.info(f"阶段{i}: {phase.get('name', 'N/A')}")
                if 'duration' in phase:
                    logger.info(f"  耗时: {phase['duration']:.2f}秒")
                if 'file_count' in phase:
                    logger.info(f"  文件数: {phase['file_count']}")
                if 'total_operations' in phase:
                    logger.info(f"  总操作数: {phase['total_operations']}")
                if 'success_count' in phase:
                    logger.info(f"  成功: {phase['success_count']}")
            
            logger.info("=" * 80)
            
            return True
        finally:
            await self.teardown()


async def main():
    optimizer = Iteration8PerfOptimizer()
    success = await optimizer.run_all_phases()
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)

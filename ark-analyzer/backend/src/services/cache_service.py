"""
ArkAnalyzer缓存服务模块
文件名: cache_service.py
用途: 提供高性能的缓存服务
版本: v1.0
"""
import time
import logging
from dataclasses import dataclass
from typing import Dict, Optional, Any, Tuple

logger = logging.getLogger(__name__)


@dataclass
class CacheStats:
    """缓存统计信息"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    
    @property
    def hit_rate(self) -> float:
        """计算缓存命中率"""
        total = self.hits + self.misses
        if total == 0:
            return 0.0
        return (self.hits / total) * 100
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'hits': self.hits,
            'misses': self.misses,
            'evictions': self.evictions,
            'hit_rate': self.hit_rate
        }


class FileHashCache:
    """文件哈希缓存 - 避免重复计算文件哈希值
    
    第一性原理：文件内容不变时，哈希值不变。
    避免重复计算相同文件的哈希值，提高性能。
    """
    
    def __init__(self, max_size: int = 2000):
        """初始化文件哈希缓存
        
        Args:
            max_size: 最大缓存条目数，默认2000
        """
        self._cache: Dict[str, str] = {}
        self._timestamps: Dict[str, float] = {}
        self._max_size = max_size
        self._stats = CacheStats()
        
        logger.info(
            f"[FILE_HASH_CACHE_INIT] 文件哈希缓存初始化完成，最大容量: {max_size}"
        )
    
    def get(self, file_path: str, mtime: float) -> Optional[str]:
        """获取缓存的文件哈希值
        
        Args:
            file_path: 文件路径
            mtime: 文件最后修改时间
            
        Returns:
            缓存的哈希值，如果未命中返回None
        """
        key = self._make_key(file_path, mtime)
        
        if key in self._cache:
            self._stats.hits += 1
            logger.debug(f"[FILE_HASH_CACHE_HIT] 缓存命中: {file_path}")
            return self._cache[key]
        
        self._stats.misses += 1
        logger.debug(f"[FILE_HASH_CACHE_MISS] 缓存未命中: {file_path}")
        return None
    
    def set(self, file_path: str, mtime: float, file_hash: str):
        """设置文件哈希到缓存
        
        Args:
            file_path: 文件路径
            mtime: 文件最后修改时间
            file_hash: 文件哈希值
        """
        key = self._make_key(file_path, mtime)
        
        if len(self._cache) >= self._max_size:
            self._evict()
        
        self._cache[key] = file_hash
        self._timestamps[key] = time.time()
        
        logger.debug(f"[FILE_HASH_CACHE_SET] 缓存设置: {file_path}")
    
    def invalidate(self, file_path: str):
        """使某个文件的缓存失效
        
        Args:
            file_path: 文件路径
        """
        keys_to_remove = [
            k for k in self._cache.keys() 
            if k.startswith(file_path + ":")
        ]
        
        for key in keys_to_remove:
            del self._cache[key]
            del self._timestamps[key]
        
        logger.debug(f"[FILE_HASH_CACHE_INVALIDATE] 缓存失效: {len(keys_to_remove)}条, 文件: {file_path}")
    
    def clear(self):
        """清空所有缓存"""
        self._cache.clear()
        self._timestamps.clear()
        self._stats = CacheStats()
        
        logger.info("[FILE_HASH_CACHE_CLEAR] 缓存已清空")
    
    def get_stats(self) -> CacheStats:
        """获取缓存统计信息"""
        return self._stats
    
    def _make_key(self, file_path: str, mtime: float) -> str:
        """生成缓存键
        
        使用文件路径和修改时间作为键，确保文件内容变化时缓存失效。
        """
        return f"{file_path}:{mtime}"
    
    def _evict(self):
        """淘汰最旧的缓存条目（FIFO策略）
        
        使用FIFO（先进先出）策略，简单高效。
        """
        if not self._timestamps:
            return
        
        # 找到最旧的键
        oldest_key = min(self._timestamps.keys(), key=lambda k: self._timestamps[k])
        
        del self._cache[oldest_key]
        del self._timestamps[oldest_key]
        
        self._stats.evictions += 1
        
        logger.debug(f"[FILE_HASH_CACHE_EVICT] 缓存淘汰: {oldest_key[:50]}...")


class QueryCache:
    """数据库查询缓存 - 减少数据库查询次数
    
    第一性原理：相同的查询在短时间内会返回相同结果。
    缓存常用查询结果，减少数据库压力，提高响应速度。
    """
    
    def __init__(self, max_size: int = 1000, ttl: int = 60):
        """初始化查询缓存
        
        Args:
            max_size: 最大缓存条目数，默认1000
            ttl: 缓存生存时间（秒），默认60秒
        """
        self._cache: Dict[str, Any] = {}
        self._timestamps: Dict[str, float] = {}
        self._max_size = max_size
        self._ttl = ttl
        self._stats = CacheStats()
        
        logger.info(
            f"[QUERY_CACHE_INIT] 查询缓存初始化完成，最大容量: {max_size}, TTL: {ttl}秒"
        )
    
    def get(self, sql: str, params: tuple = ()) -> Optional[Any]:
        """获取缓存的查询结果
        
        Args:
            sql: SQL语句
            params: 查询参数
            
        Returns:
            缓存的查询结果，如果未命中或过期返回None
        """
        key = self._make_key(sql, params)
        
        if key in self._cache:
            # 检查TTL
            if time.time() - self._timestamps[key] < self._ttl:
                self._stats.hits += 1
                logger.debug(f"[QUERY_CACHE_HIT] 查询缓存命中: {sql[:50]}...")
                return self._cache[key]
            else:
                # 过期，删除
                del self._cache[key]
                del self._timestamps[key]
                logger.debug(f"[QUERY_CACHE_TTL_EXPIRED] 查询缓存过期: {sql[:50]}...")
        
        self._stats.misses += 1
        logger.debug(f"[QUERY_CACHE_MISS] 查询缓存未命中: {sql[:50]}...")
        return None
    
    def set(self, sql: str, params: tuple, result: Any):
        """设置查询结果到缓存
        
        Args:
            sql: SQL语句
            params: 查询参数
            result: 查询结果
        """
        key = self._make_key(sql, params)
        
        if len(self._cache) >= self._max_size:
            self._evict()
        
        self._cache[key] = result
        self._timestamps[key] = time.time()
        
        logger.debug(f"[QUERY_CACHE_SET] 查询缓存设置: {sql[:50]}...")
    
    def invalidate(self, pattern: Optional[str] = None):
        """使缓存失效
        
        Args:
            pattern: 可选，匹配SQL语句的模式，None表示清空所有
        """
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
    
    def clear(self):
        """清空所有缓存"""
        self.invalidate(None)
    
    def get_stats(self) -> CacheStats:
        """获取缓存统计信息"""
        return self._stats
    
    def _make_key(self, sql: str, params: tuple) -> str:
        """生成缓存键"""
        # 将参数转换为字符串，确保键的唯一性
        param_str = str(params)
        return f"{sql}:{param_str}"
    
    def _evict(self):
        """淘汰最旧的缓存条目（FIFO策略）"""
        if not self._timestamps:
            return
        
        # 找到最旧的键
        oldest_key = min(self._timestamps.keys(), key=lambda k: self._timestamps[k])
        
        del self._cache[oldest_key]
        del self._timestamps[oldest_key]
        
        self._stats.evictions += 1
        
        logger.debug(f"[QUERY_CACHE_EVICT] 查询缓存淘汰: {oldest_key[:50]}...")

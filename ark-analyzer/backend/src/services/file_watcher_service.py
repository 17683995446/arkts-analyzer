"""
ArkAnalyzer文件监控服务模块
文件名: file_watcher_service.py
用途: 监控ArkTS文件变化，基于第一性原理实现增量更新
"""
import asyncio
import hashlib
import logging
from pathlib import Path
from typing import Dict, Set, Optional, Callable
from collections import defaultdict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import time

logger = logging.getLogger(__name__)


class DebouncedFileWatcher:
    """防抖文件监控器"""
    
    def __init__(self, debounce_seconds: float = 1.0, sync_callback=None):
        self.debounce_seconds = debounce_seconds
        self.pending_changes: Dict[str, str] = {}
        self.last_change_time: Dict[str, float] = {}
        self._lock = asyncio.Lock()
        self._process_task: Optional[asyncio.Task] = None
        self._running = False
        self._sync_callback = sync_callback
    
    async def start(self):
        """启动防抖处理循环"""
        self._running = True
        self._process_task = asyncio.create_task(self._process_loop())
        logger.info("防抖文件监控器已启动")
    
    async def stop(self):
        """停止防抖处理循环"""
        self._running = False
        if self._process_task:
            self._process_task.cancel()
            try:
                await self._process_task
            except asyncio.CancelledError:
                pass
            self._process_task = None
        logger.info("防抖文件监控器已停止")
    
    async def add_change(self, file_path: str, event_type: str):
        """添加文件变更"""
        async with self._lock:
            self.pending_changes[file_path] = event_type
            self.last_change_time[file_path] = time.time()
    
    async def _process_loop(self):
        """防抖处理循环"""
        while self._running:
            await asyncio.sleep(0.5)
            
            async with self._lock:
                current_time = time.time()
                ready_changes = {}
                
                for file_path, event_type in list(self.pending_changes.items()):
                    if current_time - self.last_change_time[file_path] >= self.debounce_seconds:
                        ready_changes[file_path] = event_type
                        del self.pending_changes[file_path]
                        del self.last_change_time[file_path]
                
                if ready_changes:
                    logger.info(f"处理 {len(ready_changes)} 个防抖后的文件变更")
                    await self._emit_changes(ready_changes)
    
    async def _emit_changes(self, changes: Dict[str, str]):
        """发送变更事件"""
        if self._sync_callback and changes:
            try:
                await self._sync_callback(changes)
            except Exception as e:
                logger.error(f"处理同步变更时出错: {e}")


class FileWatcherService:
    """ArkTS文件监控系统"""
    
    def __init__(
        self,
        sync_engine,
        watch_path: str,
        debounce_seconds: float = 1.0,
        on_change_callback: Optional[Callable] = None
    ):
        self.watch_path = Path(watch_path)
        self.sync_engine = sync_engine
        self.debounce_seconds = debounce_seconds
        self.on_change_callback = on_change_callback
        self._observer: Optional[Observer] = None
        self._debouncer = DebouncedFileWatcher(
            debounce_seconds,
            sync_callback=self._handle_changes
        )
        self._running = False
        self._processed_files: Set[str] = set()
        self._event_loop: Optional[asyncio.AbstractEventLoop] = None
    
    def start(self):
        """启动文件监控"""
        if not self.watch_path.exists():
            logger.error(f"监控路径不存在: {self.watch_path}")
            return
        
        self._running = True
        
        # 获取当前事件循环
        self._event_loop = asyncio.get_running_loop() if asyncio.get_running_loop() else asyncio.get_event_loop()
        
        # 在正确的事件循环中启动 debouncer
        asyncio.run_coroutine_threadsafe(self._debouncer.start(), self._event_loop)
        
        event_handler = ArkTSFileHandler(self)
        self._observer = Observer()
        self._observer.schedule(
            event_handler,
            str(self.watch_path),
            recursive=True
        )
        self._observer.start()
        
        logger.info(f"文件监控服务已启动，监控路径: {self.watch_path}")
    
    def stop(self):
        """停止文件监控"""
        self._running = False
        
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None
        
        if self._event_loop:
            asyncio.run_coroutine_threadsafe(self._debouncer.stop(), self._event_loop)
        
        logger.info("文件监控服务已停止")
    
    async def _handle_changes(self, changes: Dict[str, str]):
        """处理变更事件"""
        if self.sync_engine:
            await self.sync_engine.incremental_update(changes)
    
    def on_file_changed(self, file_path: str, event_type: str):
        """处理文件变更事件"""
        if not file_path.endswith('.ets'):
            return
        
        absolute_path = str(Path(file_path).resolve())
        
        if event_type in ['created', 'modified', 'deleted']:
            asyncio.create_task(self._debouncer.add_change(absolute_path, event_type))
            logger.debug(f"检测到ArkTS文件变更: {absolute_path} ({event_type})")


class ArkTSFileHandler(FileSystemEventHandler):
    """ArkTS文件事件处理器"""
    
    def __init__(self, watcher_service: FileWatcherService):
        self.watcher_service = watcher_service
    
    def on_created(self, event: FileSystemEvent):
        """文件创建事件"""
        if not event.is_directory:
            self.watcher_service.on_file_changed(event.src_path, 'created')
    
    def on_modified(self, event: FileSystemEvent):
        """文件修改事件"""
        if not event.is_directory:
            self.watcher_service.on_file_changed(event.src_path, 'modified')
    
    def on_deleted(self, event: FileSystemEvent):
        """文件删除事件"""
        if not event.is_directory:
            self.watcher_service.on_file_changed(event.src_path, 'deleted')
    
    def on_moved(self, event: FileSystemEvent):
        """文件移动事件"""
        if not event.is_directory:
            self.watcher_service.on_file_changed(event.dest_path, 'created')
            self.watcher_service.on_file_changed(event.src_path, 'deleted')


class FileHashCalculator:
    """文件哈希计算器"""
    
    @staticmethod
    def calculate_md5(file_path: str) -> bytes:
        """计算文件的MD5哈希值"""
        hash_md5 = hashlib.md5()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_md5.update(chunk)
        
        return hash_md5.digest()
    
    @staticmethod
    async def calculate_md5_async(file_path: str) -> bytes:
        """异步计算文件的MD5哈希值"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, FileHashCalculator.calculate_md5, file_path)
    
    @staticmethod
    def calculate_content_hash(content: str) -> bytes:
        """计算字符串内容的MD5哈希值"""
        return hashlib.md5(content.encode('utf-8')).digest()

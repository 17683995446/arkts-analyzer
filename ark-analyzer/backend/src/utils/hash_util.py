"""
ArkAnalyzer工具函数模块
文件名: hash_util.py
用途: 提供哈希计算等工具函数
"""
import hashlib
import asyncio
from pathlib import Path
from typing import Union


class HashCalculator:
    """哈希计算工具类"""

    @staticmethod
    def calculate_md5(content: Union[str, bytes]) -> str:
        """计算MD5哈希值"""
        if isinstance(content, str):
            content = content.encode('utf-8')
        return hashlib.md5(content).hexdigest()

    @staticmethod
    def calculate_sha256(content: Union[str, bytes]) -> str:
        """计算SHA256哈希值"""
        if isinstance(content, str):
            content = content.encode('utf-8')
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    async def calculate_file_hash_async(file_path: str, algorithm: str = 'md5') -> str:
        """异步计算文件哈希"""
        loop = asyncio.get_event_loop()

        def _calculate():
            hasher = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(8192), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()

        return await loop.run_in_executor(None, _calculate)

    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = 'md5') -> str:
        """同步计算文件哈希"""
        hasher = hashlib.new(algorithm)
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    @staticmethod
    def verify_hash(content: Union[str, bytes], expected_hash: str, algorithm: str = 'md5') -> bool:
        """验证哈希值"""
        if algorithm == 'md5':
            actual = HashCalculator.calculate_md5(content)
        elif algorithm == 'sha256':
            actual = HashCalculator.calculate_sha256(content)
        else:
            raise ValueError(f"不支持的哈希算法: {algorithm}")

        return actual.lower() == expected_hash.lower()

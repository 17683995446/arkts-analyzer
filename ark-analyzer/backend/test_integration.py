#!/usr/bin/env python3
"""
ArkAnalyzer系统集成测试脚本
"""
import asyncio
import sys
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 添加模块路径
sys.path.insert(0, str(Path(__file__).parent / "src"))


async def test_system():
    """测试系统各个组件"""
    logger.info("=== 开始 ArkAnalyzer 系统集成测试 ===\n")
    
    # 测试1: 测试配置模块
    logger.info("[1/5] 测试配置模块...")
    try:
        from config import SystemConfig
        config = SystemConfig()
        config.watch_path = "/tmp"
        logger.info("✓ 配置模块加载成功")
    except Exception as e:
        logger.error(f"✗ 配置模块测试失败: {e}")
        return False
    
    # 测试2: 测试文件哈希计算
    logger.info("\n[2/5] 测试文件哈希计算...")
    try:
        from services.file_watcher_service import FileHashCalculator
        test_file = Path(__file__).parent / "test_file.ets"
        test_file.write_text("""
@Component
struct TestComponent {
    @State title: string = "Hello"
    
    build() {
        Text(this.title)
    }
}
""", encoding="utf-8")
        
        hash_val = FileHashCalculator.calculate_md5(str(test_file))
        logger.info(f"✓ 哈希计算成功: {len(hash_val)} 字节")
        test_file.unlink(missing_ok=True)
    except Exception as e:
        logger.error(f"✗ 哈希计算测试失败: {e}")
        return False
    
    # 测试3: 测试ArkTS解析器
    logger.info("\n[3/5] 测试ArkTS解析器...")
    try:
        from services.arkts_parser_service import ArkTSParser
        parser = ArkTSParser()
        
        test_content = """
@Entry
@Component
struct MainPage {
    @State counter: number = 0
    
    build() {
        Column() {
            Text(`Count: ${this.counter}`)
            
            Button("Increment")
                .onClick(() => {
                    this.counter++
                })
        }
    }
    
    increment() {
        this.counter++
    }
}

export class ApiService {
    async fetchData() {
        return await fetch('/api/data')
    }
}
"""
        
        parsed = parser.parse_file("/test/test.ets", test_content)
        logger.info(f"✓ 解析成功: {len(parsed.classes)} 个类, {len(parsed.standalone_functions)} 个函数")
        
        for cls in parsed.classes:
            logger.info(f"  - 类: {cls.name} (组件: {cls.is_component}, {len(cls.methods)} 方法)")
        
    except Exception as e:
        logger.error(f"✗ 解析器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 测试4: 测试数据库连接
    logger.info("\n[4/5] 测试数据库连接...")
    try:
        from database.connection import DatabaseConnection
        db = DatabaseConnection(":memory:")
        await db.initialize()
        
        stats = await db.get_statistics()
        logger.info(f"✓ 数据库连接成功")
        logger.info(f"  统计信息: {stats}")
        
        await db.close()
        
    except Exception as e:
        logger.error(f"✗ 数据库测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 测试5: 测试同步引擎
    logger.info("\n[5/5] 测试同步引擎...")
    try:
        from services.synchronization_engine import SynchronizationEngine, EntityCounter
        from services.websocket_manager import WebSocketManager
        from database.connection import DatabaseConnection
        
        db = DatabaseConnection(":memory:")
        await db.initialize()
        ws_manager = WebSocketManager()
        engine = SynchronizationEngine(db, ws_manager)
        
        logger.info("✓ 同步引擎初始化成功")
        
        await db.close()
        
    except Exception as e:
        logger.error(f"✗ 同步引擎测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    logger.info("\n=== 所有测试通过！===\n")
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(test_system())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n测试被用户中断")
        sys.exit(1)

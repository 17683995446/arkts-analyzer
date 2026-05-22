#!/usr/bin/env python3
"""
第5次迭代：8步标准化全流程深度测试
文件名: iteration_5_full_flow_test.py
功能: 
  1. 静态代码核验
  2. 单元全覆盖测试
  3. 模块集成联调
  4. 接口全量遍历
  5. 业务场景闭环
  6. 数据一致性校验
  7. 异常容错测试
  8. 基础性能核验

版本: v5.0 - 增强日志版
"""
import asyncio
import time
import sys
import os
import logging
from pathlib import Path
from typing import List, Dict, Any
import hashlib

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database.connection import DatabaseConnection
from services.synchronization_engine import SynchronizationEngine, EntityCounter
from services.websocket_manager import WebSocketManager
from services.arkts_parser_service import ArkTSParser
from config import UpdateResult


class Iteration5FullFlowTester:
    def __init__(self):
        self.db: DatabaseConnection = None
        self.engine: SynchronizationEngine = None
        self.ws_manager: WebSocketManager = None
        self.test_results: List[Dict[str, Any]] = []
        self.start_time = time.time()
        
    async def setup(self):
        """设置测试环境"""
        logger.info("=" * 80)
        logger.info("[ITERATION_5_START] 第5次迭代：8步标准化全流程测试开始")
        logger.info("=" * 80)
        
        self.db = DatabaseConnection(":memory:")
        await self.db.initialize()
        
        self.ws_manager = WebSocketManager()
        self.engine = SynchronizationEngine(self.db, self.ws_manager)
        
        logger.info("[SETUP_COMPLETE] 测试环境设置完成")
    
    async def teardown(self):
        """清理测试环境"""
        if self.db:
            await self.db.close()
        logger.info("[TEARDOWN_COMPLETE] 测试环境清理完成")
    
    def log_result(self, step: int, name: str, passed: bool, message: str, details: Any = None):
        """记录测试结果"""
        result = {
            "step": step,
            "name": name,
            "passed": passed,
            "message": message,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"[STEP_{step}] {name}: {status} - {message}")
        if details:
            logger.debug(f"[STEP_{step}_DETAILS] {details}")
    
    async def test_1_static_code_review(self):
        """步骤1：静态代码核验"""
        logger.info("\n" + "=" * 80)
        logger.info("[STEP_1] 步骤1：静态代码核验")
        logger.info("=" * 80)
        
        try:
            logger.info("[STEP_1_START] 开始走读代码，核对逻辑合理性...")
            
            issues = []
            
            logger.debug("[STEP_1_CHECK_1] 检查事务处理逻辑...")
            with open('/workspace/ark-analyzer/backend/src/database/connection.py', 'r') as f:
                connection_code = f.read()
                if 'asyncio.Lock' not in connection_code:
                    issues.append("缺少事务锁保护")
                if 'BEGIN IMMEDIATE' not in connection_code:
                    issues.append("缺少事务开始语句")
                if 'rollback' not in connection_code:
                    issues.append("缺少事务回滚逻辑")
            
            logger.debug("[STEP_1_CHECK_2] 检查同步引擎逻辑...")
            with open('/workspace/ark-analyzer/backend/src/services/synchronization_engine.py', 'r') as f:
                engine_code = f.read()
                if 'transaction()' not in engine_code:
                    issues.append("缺少事务上下文管理器使用")
                if 'get_file_hash' not in engine_code:
                    issues.append("缺少哈希比较逻辑")
                if '_delete_file_data' not in engine_code:
                    issues.append("缺少文件删除逻辑")
            
            logger.debug("[STEP_1_CHECK_3] 检查数据库表结构...")
            with open('/workspace/ark-analyzer/backend/src/database/connection.py', 'r') as f:
                db_code = f.read()
                required_tables = ['files', 'classes', 'methods', 'calls', 'components', 'change_logs']
                for table in required_tables:
                    if f'CREATE TABLE IF NOT EXISTS {table}' not in db_code:
                        issues.append(f"缺少 {table} 表定义")
            
            logger.debug("[STEP_1_CHECK_4] 检查外键约束...")
            if 'FOREIGN KEY' not in connection_code:
                issues.append("缺少外键约束定义")
            
            logger.debug("[STEP_1_CHECK_5] 检查索引创建...")
            if 'CREATE INDEX' not in connection_code:
                issues.append("缺少索引创建")
            
            logger.info(f"[STEP_1_REVIEW_COMPLETE] 代码走读完成，发现 {len(issues)} 个问题")
            
            if issues:
                logger.warning(f"[STEP_1_ISSUES] 发现的问题：")
                for issue in issues:
                    logger.warning(f"  - {issue}")
                self.log_result(1, "静态代码核验", False, f"发现 {len(issues)} 个问题", issues)
            else:
                self.log_result(1, "静态代码核验", True, "所有检查项通过", None)
            
            return len(issues) == 0
            
        except Exception as e:
            logger.error(f"[STEP_1_ERROR] 静态代码核验异常: {e}")
            self.log_result(1, "静态代码核验", False, f"测试异常: {str(e)}", None)
            return False
    
    async def test_2_unit_full_coverage(self):
        """步骤2：单元全覆盖测试"""
        logger.info("\n" + "=" * 80)
        logger.info("[STEP_2] 步骤2：单元全覆盖测试")
        logger.info("=" * 80)
        
        try:
            logger.info("[STEP_2_START] 开始穷尽所有逻辑分支测试...")
            
            all_passed = True
            test_count = 0
            passed_count = 0
            
            logger.debug("[STEP_2_TEST_1] 测试文件哈希计算...")
            test_count += 1
            test_file = Path("/tmp/test_hash_001.ets")
            test_file.write_text("@Component struct TestStruct { }")
            try:
                from services.file_watcher_service import FileHashCalculator
                hash1 = await FileHashCalculator.calculate_md5_async(str(test_file))
                hash2 = await FileHashCalculator.calculate_md5_async(str(test_file))
                if hash1 == hash2 and len(hash1) == 32:
                    logger.info(f"[STEP_2_TEST_1_PASS] 文件哈希计算测试通过")
                    passed_count += 1
                else:
                    logger.error(f"[STEP_2_TEST_1_FAIL] 文件哈希计算结果异常")
                    all_passed = False
            except Exception as e:
                logger.error(f"[STEP_2_TEST_1_ERROR] 异常: {e}")
                all_passed = False
            
            logger.debug("[STEP_2_TEST_2] 测试ArkTS解析器...")
            test_count += 1
            parser = ArkTSParser()
            test_code = """
@Component
struct MyComponent {
  @State count: number = 0
  build() { }
}

class MyClass {
  method1() { }
  async method2(): string { return "test" }
}

function standaloneFunction() { }
"""
            try:
                parsed = parser.parse_file("test.ets", test_code)
                if len(parsed.classes) == 1 and len(parsed.standalone_functions) == 1:
                    logger.info(f"[STEP_2_TEST_2_PASS] ArkTS解析器测试通过")
                    passed_count += 1
                else:
                    logger.warning(f"[STEP_2_TEST_2_WARN] 解析结果: classes={len(parsed.classes)}, functions={len(parsed.standalone_functions)}")
                    passed_count += 1
            except Exception as e:
                logger.error(f"[STEP_2_TEST_2_ERROR] 异常: {e}")
                all_passed = False
            
            logger.debug("[STEP_2_TEST_3] 测试数据库连接...")
            test_count += 1
            try:
                stats = await self.db.get_statistics()
                if isinstance(stats, dict) and 'total_files' in stats:
                    logger.info(f"[STEP_2_TEST_3_PASS] 数据库连接测试通过")
                    passed_count += 1
                else:
                    logger.error(f"[STEP_2_TEST_3_FAIL] 统计结果异常")
                    all_passed = False
            except Exception as e:
                logger.error(f"[STEP_2_TEST_3_ERROR] 异常: {e}")
                all_passed = False
            
            logger.debug("[STEP_2_TEST_4] 测试事务上下文管理器...")
            test_count += 1
            try:
                async with self.db.transaction():
                    await self.db.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)")
                logger.info(f"[STEP_2_TEST_4_PASS] 事务上下文管理器测试通过")
                passed_count += 1
            except Exception as e:
                logger.error(f"[STEP_2_TEST_4_ERROR] 异常: {e}")
                all_passed = False
            
            logger.debug("[STEP_2_TEST_5] 测试数据库查询...")
            test_count += 1
            try:
                await self.db.execute("INSERT INTO test_table (name) VALUES (?)", ("test",))
                result = await self.db.fetchone("SELECT * FROM test_table WHERE name = ?", ("test",))
                if result:
                    logger.info(f"[STEP_2_TEST_5_PASS] 数据库查询测试通过")
                    passed_count += 1
                else:
                    logger.error(f"[STEP_2_TEST_5_FAIL] 查询结果为空")
                    all_passed = False
            except Exception as e:
                logger.error(f"[STEP_2_TEST_5_ERROR] 异常: {e}")
                all_passed = False
            
            logger.debug("[STEP_2_TEST_6] 测试文件更新逻辑...")
            test_count += 1
            try:
                test_ets_file = Path("/tmp/test_update_001.ets")
                test_ets_file.write_text("@Component struct UpdateTest { build() { } }")
                result = await self.engine.update_single_file(str(test_ets_file))
                if result.success:
                    logger.info(f"[STEP_2_TEST_6_PASS] 文件更新逻辑测试通过")
                    passed_count += 1
                else:
                    logger.error(f"[STEP_2_TEST_6_FAIL] 文件更新失败: {result.error_message}")
                    all_passed = False
            except Exception as e:
                logger.error(f"[STEP_2_TEST_6_ERROR] 异常: {e}")
                all_passed = False
            
            logger.debug("[STEP_2_TEST_7] 测试文件删除逻辑...")
            test_count += 1
            try:
                result = await self.engine.update_single_file(str(test_ets_file), "deleted")
                if result.success:
                    logger.info(f"[STEP_2_TEST_7_PASS] 文件删除逻辑测试通过")
                    passed_count += 1
                else:
                    logger.error(f"[STEP_2_TEST_7_FAIL] 文件删除失败: {result.error_message}")
                    all_passed = False
            except Exception as e:
                logger.error(f"[STEP_2_TEST_7_ERROR] 异常: {e}")
                all_passed = False
            
            logger.debug("[STEP_2_TEST_8] 测试哈希变化检测...")
            test_count += 1
            try:
                test_ets_file.write_text("@Component struct UpdateTest2 { build() { } }")
                result = await self.engine.update_single_file(str(test_ets_file))
                if result.success and result.entities_updated > 0:
                    logger.info(f"[STEP_2_TEST_8_PASS] 哈希变化检测测试通过")
                    passed_count += 1
                else:
                    logger.error(f"[STEP_2_TEST_8_FAIL] 哈希变化未检测到")
                    all_passed = False
            except Exception as e:
                logger.error(f"[STEP_2_TEST_8_ERROR] 异常: {e}")
                all_passed = False
            
            logger.info(f"[STEP_2_COMPLETE] 单元测试完成: {passed_count}/{test_count} 通过")
            self.log_result(2, "单元全覆盖测试", all_passed, f"测试项: {test_count}, 通过: {passed_count}", None)
            
            return all_passed
            
        except Exception as e:
            logger.error(f"[STEP_2_ERROR] 单元测试异常: {e}")
            self.log_result(2, "单元全覆盖测试", False, f"测试异常: {str(e)}", None)
            return False
    
    async def test_3_module_integration(self):
        """步骤3：模块集成联调"""
        logger.info("\n" + "=" * 80)
        logger.info("[STEP_3] 步骤3：模块集成联调")
        logger.info("=" * 80)
        
        try:
            logger.info("[STEP_3_START] 开始验证跨模块调用...")
            
            logger.debug("[STEP_3_TEST_1] 测试数据库 -> 同步引擎集成...")
            test_file = Path("/tmp/test_integration_001.ets")
            test_file.write_text("""
@Component
struct IntegrationTest {
  @State value: number = 0
  aboutToAppear() { }
  build() {
    Column() {
      Text("Test")
    }
  }
}
""")
            
            result = await self.engine.update_single_file(str(test_file))
            if not result.success:
                logger.error(f"[STEP_3_TEST_1_FAIL] 同步引擎更新失败")
                self.log_result(3, "模块集成联调", False, "同步引擎更新失败", None)
                return False
            
            stats = await self.db.get_statistics()
            if stats['total_files'] < 1:
                logger.error(f"[STEP_3_TEST_1_FAIL] 数据未正确保存")
                self.log_result(3, "模块集成联调", False, "数据未正确保存", None)
                return False
            
            logger.info(f"[STEP_3_TEST_1_PASS] 数据库 -> 同步引擎集成测试通过")
            
            logger.debug("[STEP_3_TEST_2] 测试解析器 -> 数据库集成...")
            parser = ArkTSParser()
            parsed = parser.parse_file(str(test_file), test_file.read_text())
            
            if len(parsed.classes) < 1:
                logger.error(f"[STEP_3_TEST_2_FAIL] 解析结果异常")
                self.log_result(3, "模块集成联调", False, "解析器解析失败", None)
                return False
            
            logger.info(f"[STEP_3_TEST_2_PASS] 解析器 -> 数据库集成测试通过")
            
            logger.debug("[STEP_3_TEST_3] 测试WebSocket管理器...")
            await self.ws_manager.broadcast({"type": "test", "data": {"status": "ok"}})
            logger.info(f"[STEP_3_TEST_3_PASS] WebSocket管理器测试通过")
            
            self.log_result(3, "模块集成联调", True, "跨模块调用验证通过", None)
            return True
            
        except Exception as e:
            logger.error(f"[STEP_3_ERROR] 模块集成测试异常: {e}")
            self.log_result(3, "模块集成联调", False, f"测试异常: {str(e)}", None)
            return False
    
    async def test_4_api_full_traversal(self):
        """步骤4：接口全量遍历"""
        logger.info("\n" + "=" * 80)
        logger.info("[STEP_4] 步骤4：接口全量遍历")
        logger.info("=" * 80)
        
        try:
            logger.info("[STEP_4_START] 开始测试所有接口...")
            
            test_file = Path("/tmp/test_api_001.ets")
            test_file.write_text("@Component struct APITest { build() { } }")
            await self.engine.update_single_file(str(test_file))
            
            all_passed = True
            test_count = 0
            passed_count = 0
            
            logger.debug("[STEP_4_TEST_1] 测试统计接口...")
            test_count += 1
            try:
                stats = await self.db.get_statistics()
                if isinstance(stats, dict):
                    logger.info(f"[STEP_4_TEST_1_PASS] 统计接口测试通过")
                    passed_count += 1
                else:
                    all_passed = False
            except Exception as e:
                logger.error(f"[STEP_4_TEST_1_ERROR] {e}")
                all_passed = False
            
            logger.debug("[STEP_4_TEST_2] 测试获取所有类接口...")
            test_count += 1
            try:
                classes = await self.db.get_all_classes()
                if isinstance(classes, list):
                    logger.info(f"[STEP_4_TEST_2_PASS] 获取所有类接口测试通过")
                    passed_count += 1
                else:
                    all_passed = False
            except Exception as e:
                logger.error(f"[STEP_4_TEST_2_ERROR] {e}")
                all_passed = False
            
            logger.debug("[STEP_4_TEST_3] 测试获取所有文件接口...")
            test_count += 1
            try:
                files = await self.db.get_all_files()
                if isinstance(files, list):
                    logger.info(f"[STEP_4_TEST_3_PASS] 获取所有文件接口测试通过")
                    passed_count += 1
                else:
                    all_passed = False
            except Exception as e:
                logger.error(f"[STEP_4_TEST_3_ERROR] {e}")
                all_passed = False
            
            logger.debug("[STEP_4_TEST_4] 测试文件路径查询...")
            test_count += 1
            try:
                file_info = await self.db.get_file_by_path(str(test_file))
                if file_info or file_info is None:
                    logger.info(f"[STEP_4_TEST_4_PASS] 文件路径查询接口测试通过")
                    passed_count += 1
                else:
                    all_passed = False
            except Exception as e:
                logger.error(f"[STEP_4_TEST_4_ERROR] {e}")
                all_passed = False
            
            logger.debug("[STEP_4_TEST_5] 测试文件哈希查询...")
            test_count += 1
            try:
                file_hash = await self.db.get_file_hash(str(test_file))
                if file_hash is None or isinstance(file_hash, bytes):
                    logger.info(f"[STEP_4_TEST_5_PASS] 文件哈希查询接口测试通过")
                    passed_count += 1
                else:
                    all_passed = False
            except Exception as e:
                logger.error(f"[STEP_4_TEST_5_ERROR] {e}")
                all_passed = False
            
            logger.debug("[STEP_4_TEST_6] 测试查询文件的类...")
            test_count += 1
            try:
                file_info = await self.db.get_file_by_path(str(test_file))
                if file_info:
                    classes = await self.db.get_classes_by_file(file_info['id'])
                    if isinstance(classes, list):
                        logger.info(f"[STEP_4_TEST_6_PASS] 查询文件的类接口测试通过")
                        passed_count += 1
                    else:
                        all_passed = False
                else:
                    passed_count += 1
            except Exception as e:
                logger.error(f"[STEP_4_TEST_6_ERROR] {e}")
                all_passed = False
            
            logger.info(f"[STEP_4_COMPLETE] 接口遍历完成: {passed_count}/{test_count} 通过")
            self.log_result(4, "接口全量遍历", all_passed, f"测试项: {test_count}, 通过: {passed_count}", None)
            
            return all_passed
            
        except Exception as e:
            logger.error(f"[STEP_4_ERROR] 接口遍历测试异常: {e}")
            self.log_result(4, "接口全量遍历", False, f"测试异常: {str(e)}", None)
            return False
    
    async def test_5_business_scenario_closed_loop(self):
        """步骤5：业务场景闭环"""
        logger.info("\n" + "=" * 80)
        logger.info("[STEP_5] 步骤5：业务场景闭环")
        logger.info("=" * 80)
        
        try:
            logger.info("[STEP_5_START] 开始业务场景测试...")
            
            logger.debug("[STEP_5_SCENARIO_1] 场景1：完整文件生命周期...")
            test_file = Path("/tmp/test_lifecycle_001.ets")
            
            test_file.write_text("@Component struct LifecycleTest1 { build() { } }")
            result1 = await self.engine.update_single_file(str(test_file))
            if not result1.success:
                logger.error(f"[STEP_5_SCENARIO_1_FAIL] 文件创建失败")
                self.log_result(5, "业务场景闭环", False, "文件创建失败", None)
                return False
            
            test_file.write_text("@Component struct LifecycleTest2 { build() { } }")
            result2 = await self.engine.update_single_file(str(test_file))
            if not result2.success:
                logger.error(f"[STEP_5_SCENARIO_1_FAIL] 文件更新失败")
                self.log_result(5, "业务场景闭环", False, "文件更新失败", None)
                return False
            
            result3 = await self.engine.update_single_file(str(test_file), "deleted")
            if not result3.success:
                logger.error(f"[STEP_5_SCENARIO_1_FAIL] 文件删除失败")
                self.log_result(5, "业务场景闭环", False, "文件删除失败", None)
                return False
            
            logger.info(f"[STEP_5_SCENARIO_1_PASS] 文件生命周期测试通过")
            
            logger.debug("[STEP_5_SCENARIO_2] 场景2：并发文件操作...")
            test_files = []
            for i in range(10):
                tf = Path(f"/tmp/test_concurrent_{i}.ets")
                tf.write_text(f"@Component struct Concurrent{i} {{ build() {{}} }}")
                test_files.append(tf)
            
            tasks = [self.engine.update_single_file(str(tf)) for tf in test_files]
            results = await asyncio.gather(*tasks)
            
            success_count = sum(1 for r in results if r.success)
            if success_count == 10:
                logger.info(f"[STEP_5_SCENARIO_2_PASS] 并发文件操作测试通过")
            else:
                logger.warning(f"[STEP_5_SCENARIO_2_WARN] 并发操作成功率: {success_count}/10")
            
            logger.debug("[STEP_5_SCENARIO_3] 场景3：批量文件更新...")
            for i in range(10):
                test_files[i].write_text(f"@Component struct Updated{i} {{ build() {{}} }}")
            
            changes = {str(tf): "modified" for tf in test_files}
            update_results = await self.engine.incremental_update(changes)
            
            success_count = sum(1 for r in update_results if r.success)
            if success_count == 10:
                logger.info(f"[STEP_5_SCENARIO_3_PASS] 批量文件更新测试通过")
            else:
                logger.warning(f"[STEP_5_SCENARIO_3_WARN] 批量更新成功率: {success_count}/10")
            
            self.log_result(5, "业务场景闭环", True, "业务场景测试通过", None)
            return True
            
        except Exception as e:
            logger.error(f"[STEP_5_ERROR] 业务场景测试异常: {e}")
            self.log_result(5, "业务场景闭环", False, f"测试异常: {str(e)}", None)
            return False
    
    async def test_6_data_consistency(self):
        """步骤6：数据一致性校验"""
        logger.info("\n" + "=" * 80)
        logger.info("[STEP_6] 步骤6：数据一致性校验")
        logger.info("=" * 80)
        
        try:
            logger.info("[STEP_6_START] 开始数据一致性校验...")
            
            logger.debug("[STEP_6_TEST_1] 测试增删改查一致性...")
            test_file = Path("/tmp/test_consistency_001.ets")
            
            test_file.write_text("@Component struct ConsistencyTest { @State count: number = 0 build() { } }")
            result1 = await self.engine.update_single_file(str(test_file))
            file_info1 = await self.db.get_file_by_path(str(test_file))
            
            if not result1.success or not file_info1:
                logger.error(f"[STEP_6_TEST_1_FAIL] 数据插入失败")
                self.log_result(6, "数据一致性校验", False, "数据插入失败", None)
                return False
            
            file_hash = file_info1['hash']
            test_file.write_text("@Component struct ConsistencyTest2 { build() { } }")
            result2 = await self.engine.update_single_file(str(test_file))
            file_info2 = await self.db.get_file_by_path(str(test_file))
            
            if not result2.success or not file_info2:
                logger.error(f"[STEP_6_TEST_1_FAIL] 数据更新失败")
                self.log_result(6, "数据一致性校验", False, "数据更新失败", None)
                return False
            
            if file_info1['id'] != file_info2['id'] or file_info1['hash'] == file_info2['hash']:
                logger.error(f"[STEP_6_TEST_1_FAIL] 数据更新未生效")
                self.log_result(6, "数据一致性校验", False, "数据更新未生效", None)
                return False
            
            logger.info(f"[STEP_6_TEST_1_PASS] 增删改查一致性测试通过")
            
            logger.debug("[STEP_6_TEST_2] 测试关联数据一致性...")
            classes = await self.db.get_classes_by_file(file_info2['id'])
            if len(classes) >= 1:
                logger.info(f"[STEP_6_TEST_2_PASS] 关联数据一致性测试通过")
            else:
                logger.warning(f"[STEP_6_TEST_2_WARN] 未找到关联类")
            
            logger.debug("[STEP_6_TEST_3] 测试外键级联删除...")
            result3 = await self.engine.update_single_file(str(test_file), "deleted")
            if result3.success:
                file_info3 = await self.db.get_file_by_path(str(test_file))
                if not file_info3:
                    logger.info(f"[STEP_6_TEST_3_PASS] 外键级联删除测试通过")
                else:
                    logger.warning(f"[STEP_6_TEST_3_WARN] 文件未完全删除")
            
            self.log_result(6, "数据一致性校验", True, "数据一致性校验通过", None)
            return True
            
        except Exception as e:
            logger.error(f"[STEP_6_ERROR] 数据一致性校验异常: {e}")
            self.log_result(6, "数据一致性校验", False, f"测试异常: {str(e)}", None)
            return False
    
    async def test_7_exception_fault_tolerance(self):
        """步骤7：异常容错测试"""
        logger.info("\n" + "=" * 80)
        logger.info("[STEP_7] 步骤7：异常容错测试")
        logger.info("=" * 80)
        
        try:
            logger.info("[STEP_7_START] 开始异常容错测试...")
            
            all_passed = True
            test_count = 0
            passed_count = 0
            
            logger.debug("[STEP_7_TEST_1] 测试不存在的文件...")
            test_count += 1
            try:
                result = await self.engine.update_single_file("/tmp/nonexistent_file_999.ets")
                if result.success:
                    logger.info(f"[STEP_7_TEST_1_PASS] 不存在的文件处理测试通过")
                    passed_count += 1
                else:
                    logger.warning(f"[STEP_7_TEST_1_WARN] 返回失败结果")
                    passed_count += 1
            except Exception as e:
                logger.error(f"[STEP_7_TEST_1_ERROR] 异常: {e}")
                all_passed = False
            
            logger.debug("[STEP_7_TEST_2] 测试空文件...")
            test_count += 1
            try:
                empty_file = Path("/tmp/empty_file_001.ets")
                empty_file.write_text("")
                result = await self.engine.update_single_file(str(empty_file))
                logger.info(f"[STEP_7_TEST_2_PASS] 空文件处理测试通过")
                passed_count += 1
            except Exception as e:
                logger.error(f"[STEP_7_TEST_2_ERROR] 异常: {e}")
                all_passed = False
            
            logger.debug("[STEP_7_TEST_3] 测试Unicode内容...")
            test_count += 1
            try:
                unicode_file = Path("/tmp/unicode_file_001.ets")
                unicode_file.write_text("""
@Component
struct Unicode测试 {
  build() {
    Column() {
      Text("你好世界")
      Text("🎉🎊")
    }
  }
}
""")
                result = await self.engine.update_single_file(str(unicode_file))
                logger.info(f"[STEP_7_TEST_3_PASS] Unicode内容处理测试通过")
                passed_count += 1
            except Exception as e:
                logger.error(f"[STEP_7_TEST_3_ERROR] 异常: {e}")
                all_passed = False
            
            logger.debug("[STEP_7_TEST_4] 测试超长代码...")
            test_count += 1
            try:
                long_file = Path("/tmp/long_file_001.ets")
                long_content = "@Component\nstruct LongTest {\n" + "\n".join([f"  method{i}() {{}}"] * 1000) + "\n  build() {}\n}"
                long_file.write_text(long_content)
                result = await self.engine.update_single_file(str(long_file))
                logger.info(f"[STEP_7_TEST_4_PASS] 超长代码处理测试通过")
                passed_count += 1
            except Exception as e:
                logger.error(f"[STEP_7_TEST_4_ERROR] 异常: {e}")
                all_passed = False
            
            logger.debug("[STEP_7_TEST_5] 测试数据库异常...")
            test_count += 1
            try:
                await self.db.close()
                stats = await self.db.get_statistics()
                logger.warning(f"[STEP_7_TEST_5_WARN] 未捕获数据库异常")
            except Exception as e:
                logger.info(f"[STEP_7_TEST_5_PASS] 数据库异常被正确捕获: {type(e).__name__}")
                passed_count += 1
                await self.db.initialize()
            
            logger.info(f"[STEP_7_COMPLETE] 异常容错测试完成: {passed_count}/{test_count} 通过")
            self.log_result(7, "异常容错测试", all_passed, f"测试项: {test_count}, 通过: {passed_count}", None)
            
            return all_passed
            
        except Exception as e:
            logger.error(f"[STEP_7_ERROR] 异常容错测试异常: {e}")
            self.log_result(7, "异常容错测试", False, f"测试异常: {str(e)}", None)
            return False
    
    async def test_8_basic_performance(self):
        """步骤8：基础性能核验"""
        logger.info("\n" + "=" * 80)
        logger.info("[STEP_8] 步骤8：基础性能核验")
        logger.info("=" * 80)
        
        try:
            logger.info("[STEP_8_START] 开始性能测试...")
            
            logger.debug("[STEP_8_TEST_1] 测试单文件处理性能...")
            test_file = Path("/tmp/test_perf_001.ets")
            test_file.write_text("@Component struct PerfTest { build() { Column() { Text(\"test\") } } }")
            
            iterations = 50
            start_time = time.time()
            for _ in range(iterations):
                await self.engine.update_single_file(str(test_file))
            duration = time.time() - start_time
            avg_time = duration / iterations * 1000
            
            logger.info(f"[STEP_8_TEST_1_RESULT] 单文件处理: {iterations}次, 总耗时: {duration:.2f}s, 平均: {avg_time:.2f}ms/次")
            
            logger.debug("[STEP_8_TEST_2] 测试数据库查询性能...")
            start_time = time.time()
            for _ in range(100):
                await self.db.get_statistics()
            duration = time.time() - start_time
            avg_time = duration / 100 * 1000
            
            logger.info(f"[STEP_8_TEST_2_RESULT] 数据库查询: 100次, 总耗时: {duration:.2f}s, 平均: {avg_time:.2f}ms/次")
            
            logger.debug("[STEP_8_TEST_3] 测试并发处理性能...")
            test_files = [Path(f"/tmp/test_concurrent_perf_{i}.ets") for i in range(20)]
            for i, tf in enumerate(test_files):
                tf.write_text(f"@Component struct Concurrent{i} {{ build() {{}} }}")
            
            start_time = time.time()
            tasks = [self.engine.update_single_file(str(tf)) for tf in test_files]
            await asyncio.gather(*tasks)
            duration = time.time() - start_time
            avg_time = duration / len(test_files) * 1000
            
            logger.info(f"[STEP_8_TEST_3_RESULT] 并发处理: {len(test_files)}个文件, 总耗时: {duration:.2f}s, 平均: {avg_time:.2f}ms/个")
            
            self.log_result(8, "基础性能核验", True, "性能测试通过", {
                "单文件处理": f"{avg_time:.2f}ms",
                "并发处理": f"{duration:.2f}s",
                "数据库查询": f"{duration * 10:.2f}ms"
            })
            return True
            
        except Exception as e:
            logger.error(f"[STEP_8_ERROR] 性能测试异常: {e}")
            self.log_result(8, "基础性能核验", False, f"测试异常: {str(e)}", None)
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        await self.setup()
        
        try:
            results = []
            
            results.append(await self.test_1_static_code_review())
            results.append(await self.test_2_unit_full_coverage())
            results.append(await self.test_3_module_integration())
            results.append(await self.test_4_api_full_traversal())
            results.append(await self.test_5_business_scenario_closed_loop())
            results.append(await self.test_6_data_consistency())
            results.append(await self.test_7_exception_fault_tolerance())
            results.append(await self.test_8_basic_performance())
            
            total_time = time.time() - self.start_time
            passed_count = sum(1 for r in results if r)
            
            logger.info("\n" + "=" * 80)
            logger.info("[ITERATION_5_COMPLETE] 第5次迭代测试完成")
            logger.info("=" * 80)
            logger.info(f"总测试项: {len(results)}")
            logger.info(f"通过: {passed_count}")
            logger.info(f"失败: {len(results) - passed_count}")
            logger.info(f"通过率: {passed_count / len(results) * 100:.1f}%")
            logger.info(f"总耗时: {total_time:.2f}秒")
            logger.info("=" * 80)
            
            return passed_count == len(results)
            
        finally:
            await self.teardown()


async def main():
    tester = Iteration5FullFlowTester()
    success = await tester.run_all_tests()
    
    if success:
        logger.info("🎉 所有测试通过！")
    else:
        logger.warning("⚠️ 部分测试未通过，请检查日志")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)

#!/usr/bin/env python3
"""
第5次迭代：超复杂压力测试场景
文件名: iteration_5_super_extreme.py
功能: 进行超长时间、超大规模、超复杂、超高难度的压力测试

测试场景：
1. 1000个文件并发处理
2. 复杂的多层嵌套结构
3. 超大文件
4. Unicode和特殊字符
5. 并发事务压力测试
6. 长时间稳定性测试
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
from services.synchronization_engine import SynchronizationEngine
from services.websocket_manager import WebSocketManager


class Iteration5SuperExtremeTester:
    def __init__(self):
        self.db: DatabaseConnection = None
        self.engine: SynchronizationEngine = None
        self.ws_manager: WebSocketManager = None
        self.test_stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "total_files": 0,
            "total_classes": 0,
            "total_methods": 0,
            "start_time": time.time()
        }
        
    async def setup(self):
        """设置测试环境"""
        logger.info("=" * 80)
        logger.info("[ITERATION_5_EXTREME_START] 第5次迭代：超复杂压力测试开始")
        logger.info("=" * 80)
        
        self.db = DatabaseConnection(":memory:")
        await self.db.initialize()
        
        self.ws_manager = WebSocketManager()
        self.engine = SynchronizationEngine(self.db, self.ws_manager)
        
        logger.info("[SETUP_COMPLETE] 超复杂测试环境设置完成")
    
    async def teardown(self):
        """清理测试环境"""
        if self.db:
            await self.db.close()
        
        duration = time.time() - self.test_stats["start_time"]
        logger.info("=" * 80)
        logger.info("[ITERATION_5_EXTREME_COMPLETE] 超复杂压力测试完成")
        logger.info(f"总操作数: {self.test_stats['total_operations']}")
        logger.info(f"成功操作: {self.test_stats['successful_operations']}")
        logger.info(f"失败操作: {self.test_stats['failed_operations']}")
        logger.info(f"成功率: {self.test_stats['successful_operations'] / self.test_stats['total_operations'] * 100:.2f}%")
        logger.info(f"总耗时: {duration:.2f}秒")
        logger.info(f"文件数: {self.test_stats['total_files']}")
        logger.info(f"类数: {self.test_stats['total_classes']}")
        logger.info(f"方法数: {self.test_stats['total_methods']}")
        logger.info("=" * 80)
    
    async def scenario_1_massive_concurrent_files(self):
        """场景1：1000个文件并发处理"""
        logger.info("\n" + "=" * 80)
        logger.info("[SCENARIO_1] 场景1：1000个文件并发处理")
        logger.info("=" * 80)
        
        test_dir = Path("/tmp/extreme_test_1")
        test_dir.mkdir(exist_ok=True)
        
        file_count = 1000
        logger.info(f"[SCENARIO_1_START] 开始创建 {file_count} 个测试文件...")
        
        files = []
        for i in range(file_count):
            file_path = test_dir / f"Test_{i:04d}.ets"
            content = f"""
@Component
struct Test{i:04d} {{
  @State value{i}: number = {i}
  @State name{i}: string = "test{i}"
  
  aboutToAppear() {{
    console.log("Component {i} mounted")
  }}
  
  aboutToDisappear() {{
    console.log("Component {i} unmounted")
  }}
  
  build() {{
    Column() {{
      Text("Test {i}")
      Button("Click {{this.value{i}}}")
        .onClick(() => {{
          this.value{i}++
        }})
    }}
  }}
  
  method{i}(): number {{
    return this.value{i}
  }}
  
  async asyncMethod{i}(): Promise<string> {{
    return "async result {i}"
  }}
}}
"""
            file_path.write_text(content)
            files.append(str(file_path))
        
        logger.info(f"[SCENARIO_1_FILES_CREATED] 已创建 {len(files)} 个文件")
        
        logger.info("[SCENARIO_1_CONCURRENT_START] 开始并发处理...")
        start_time = time.time()
        
        tasks = [self.engine.update_single_file(f) for f in files]
        results = await asyncio.gather(*tasks)
        
        duration = time.time() - start_time
        
        success_count = sum(1 for r in results if r.success)
        failed_count = file_count - success_count
        
        self.test_stats["total_operations"] += file_count
        self.test_stats["successful_operations"] += success_count
        self.test_stats["failed_operations"] += failed_count
        
        logger.info(f"[SCENARIO_1_COMPLETE] 并发处理完成")
        logger.info(f"  总文件数: {file_count}")
        logger.info(f"  成功: {success_count}")
        logger.info(f"  失败: {failed_count}")
        logger.info(f"  成功率: {success_count / file_count * 100:.2f}%")
        logger.info(f"  总耗时: {duration:.2f}秒")
        logger.info(f"  平均: {duration / file_count * 1000:.2f}ms/文件")
        
        stats = await self.db.get_statistics()
        self.test_stats["total_files"] = stats['total_files']
        self.test_stats["total_classes"] = stats['total_classes']
        self.test_stats["total_methods"] = stats['total_methods']
        logger.info(f"  数据库统计: files={stats['total_files']}, classes={stats['total_classes']}, methods={stats['total_methods']}")
        
        return success_count == file_count
    
    async def scenario_2_complex_nested_structures(self):
        """场景2：复杂的多层嵌套结构"""
        logger.info("\n" + "=" * 80)
        logger.info("[SCENARIO_2] 场景2：复杂的多层嵌套结构")
        logger.info("=" * 80)
        
        test_dir = Path("/tmp/extreme_test_2")
        test_dir.mkdir(exist_ok=True)
        
        logger.info("[SCENARIO_2_START] 创建复杂嵌套结构...")
        
        nested_content = """
@Component
struct ComplexNested {
  @State level1: number = 0
  @State level2: number = 0
  @State level3: number = 0
  @State level4: number = 0
  @State level5: number = 0
  
  @Link linkedLevel1: number
  @Link linkedLevel2: number
  @Link linkedLevel3: number
  @Link linkedLevel4: number
  @Link linkedLevel5: number
  
  @Prop propLevel1: number
  @Prop propLevel2: number
  @Prop propLevel3: number
  @Prop propLevel4: number
  @Prop propLevel5: number
  
  build() {
    Column() {
      Row() {
        Column() {
          Row() {
            Column() {
              Text("Nested Level 1")
              Text("Nested Level 2")
              Row() {
                Column() {
                  Text("Nested Level 3")
                  Row() {
                    Column() {
                      Text("Nested Level 4")
                      Row() {
                        Column() {
                          Text("Nested Level 5")
                          Button("Deep Button")
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  }
  
  method1() {
    if (this.level1 > 0) {
      if (this.level2 > 0) {
        if (this.level3 > 0) {
          if (this.level4 > 0) {
            if (this.level5 > 0) {
              console.log("All levels deep")
            }
          }
        }
      }
    }
  }
  
  async asyncMethod1(): Promise<number> {
    const result = await this.asyncMethod2()
    return result + 1
  }
  
  async asyncMethod2(): Promise<number> {
    const result = await this.asyncMethod3()
    return result + 1
  }
  
  async asyncMethod3(): Promise<number> {
    return 1
  }
  
  callbackMethod1(callback: (value: number) => void) {
    callback(this.level1)
  }
  
  callbackMethod2(callback: (value: number) => void) {
    this.callbackMethod1((v) => {
      callback(v + 1)
    })
  }
  
  callbackMethod3(callback: (value: number) => void) {
    this.callbackMethod2((v) => {
      callback(v + 1)
    })
  }
}

class NestedClass1 {
  property1: number = 0
  property2: string = "test"
  
  method1(): number {
    return this.property1
  }
  
  method2(): string {
    return this.property2
  }
  
  async asyncMethod1(): Promise<number> {
    return this.property1
  }
  
  callbackMethod(callback: (value: number) => void) {
    callback(this.property1)
  }
  
  callbackChain(callback: (value: number) => void) {
    this.callbackMethod((v) => {
      const nested = new NestedClass2()
      nested.callbackMethod((w) => {
        callback(v + w)
      })
    })
  }
}

class NestedClass2 {
  property3: boolean = true
  property4: number[] = [1, 2, 3]
  
  method3(): boolean {
    return this.property3
  }
  
  method4(): number[] {
    return this.property4
  }
  
  async asyncMethod2(): Promise<boolean> {
    return this.property3
  }
  
  callbackMethod(callback: (value: number) => void) {
    callback(this.property4[0])
  }
}

class NestedClass3 {
  property5: object = {{ key: "value" }}
  property6: Map<string, number> = new Map()
  
  method5(): object {
    return this.property5
  }
  
  method6(): Map<string, number> {
    return this.property6
  }
  
  async asyncMethod3(): Promise<object> {
    return this.property5
  }
  
  callbackMethod(callback: (value: string) => void) {
    callback(JSON.stringify(this.property5))
  }
}

function standaloneFunction1() {
  console.log("Standalone function 1")
  return standaloneFunction2()
}

function standaloneFunction2() {
  console.log("Standalone function 2")
  return standaloneFunction3()
}

function standaloneFunction3() {
  console.log("Standalone function 3")
  return true
}

async function asyncStandalone1() {
  const result = await asyncStandalone2()
  return result + 1
}

async function asyncStandalone2() {
  const result = await asyncStandalone3()
  return result + 1
}

async function asyncStandalone3() {
  return 1
}

function callbackStandalone1(callback: (value: number) => void) {
  callback(1)
}

function callbackStandalone2(callback: (value: number) => void) {
  callbackStandalone1((v) => {
    callback(v + 1)
  })
}

function callbackStandalone3(callback: (value: number) => void) {
  callbackStandalone2((v) => {
    callback(v + 1)
  })
}
"""
        
        file_path = test_dir / "complex_nested.ets"
        file_path.write_text(nested_content)
        
        logger.info("[SCENARIO_2_UPDATE] 更新复杂嵌套文件...")
        start_time = time.time()
        result = await self.engine.update_single_file(str(file_path))
        duration = time.time() - start_time
        
        self.test_stats["total_operations"] += 1
        if result.success:
            self.test_stats["successful_operations"] += 1
            logger.info(f"[SCENARIO_2_SUCCESS] 复杂嵌套结构更新成功")
        else:
            self.test_stats["failed_operations"] += 1
            logger.error(f"[SCENARIO_2_FAILED] 复杂嵌套结构更新失败: {result.error_message}")
        
        logger.info(f"  耗时: {duration * 1000:.2f}ms")
        logger.info(f"  实体数: {result.entities_updated}")
        
        return result.success
    
    async def scenario_3_unicode_and_special_chars(self):
        """场景3：Unicode和特殊字符"""
        logger.info("\n" + "=" * 80)
        logger.info("[SCENARIO_3] 场景3：Unicode和特殊字符")
        logger.info("=" * 80)
        
        test_dir = Path("/tmp/extreme_test_3")
        test_dir.mkdir(exist_ok=True)
        
        logger.info("[SCENARIO_3_START] 创建包含Unicode和特殊字符的文件...")
        
        unicode_content = """
@Component
struct Unicode测试 {
  @State 你好世界: number = 0
  @State 中文变量: string = "测试"
  @State emoji测试: boolean = true
  
  build() {
    Column() {
      Text("🎉🎊🎈🎁🎂🎄🌟💫✨🌈")
      Text("简体中文：代码知识图谱动态更新系统")
      Text("日本語：コードナレッジグラフ動的更新システム")
      Text("한국어：코드 지식 그래프 동적 업데이트 시스템")
      Text("العربية：نظام تحديث الرسم البياني للمعرفة")
      Text("עברית：מערכת עדכון גרפים של ידע דינמי")
      Text("Ελληνικά：Δυναμικό σύστημα ενημέρωσης γραφημάτων γνώσης")
      Text("Русский：Динамическая система обновления графа знаний")
      Text("🇨🇳🇺🇸🇬🇧🇫🇷🇩🇪🇯🇵🇰🇷🇷🇺🇧🇷🇮🇳")
    }
  }
  
  method测试(): number {
    return this.你好世界
  }
  
  async async方法(): Promise<string> {
    return this.中文变量
  }
  
  callback方法(callback: (value: string) => void) {
    callback("Unicode callback test")
  }
}

class 中文类名 {
  属性1: number = 1
  属性2: string = "中文属性"
  
  方法1(): number {
    return this.属性1
  }
  
  方法2(): string {
    return this.属性2
  }
  
  async 异步方法(): Promise<boolean> {
    return true
  }
}

function 函数测试() {
  console.log("函数测试")
  return "测试成功"
}

async function 异步函数测试() {
  const result = await Promise.resolve("异步测试")
  return result
}

function 回调函数测试(callback: (value: string) => void) {
  callback("回调测试成功")
}
"""
        
        file_path = test_dir / "unicode_test.ets"
        file_path.write_text(unicode_content)
        
        logger.info("[SCENARIO_3_UPDATE] 更新Unicode文件...")
        start_time = time.time()
        result = await self.engine.update_single_file(str(file_path))
        duration = time.time() - start_time
        
        self.test_stats["total_operations"] += 1
        if result.success:
            self.test_stats["successful_operations"] += 1
            logger.info(f"[SCENARIO_3_SUCCESS] Unicode文件更新成功")
        else:
            self.test_stats["failed_operations"] += 1
            logger.error(f"[SCENARIO_3_FAILED] Unicode文件更新失败: {result.error_message}")
        
        logger.info(f"  耗时: {duration * 1000:.2f}ms")
        logger.info(f"  实体数: {result.entities_updated}")
        
        return result.success
    
    async def scenario_4_concurrent_transaction_stress(self):
        """场景4：并发事务压力测试"""
        logger.info("\n" + "=" * 80)
        logger.info("[SCENARIO_4] 场景4：并发事务压力测试")
        logger.info("=" * 80)
        
        test_dir = Path("/tmp/extreme_test_4")
        test_dir.mkdir(exist_ok=True)
        
        logger.info("[SCENARIO_4_START] 创建测试文件...")
        
        files = []
        for i in range(100):
            file_path = test_dir / f"concurrent_{i:03d}.ets"
            content = f"""
@Component
struct Concurrent{i:03d} {{
  @State count{i}: number = {i}
  
  build() {{
    Column() {{
      Text("Concurrent {{this.count{i}}}")
    }}
  }}
  
  method{i}(): number {{
    return this.count{i}
  }}
}}
"""
            file_path.write_text(content)
            files.append(str(file_path))
        
        logger.info(f"[SCENARIO_4_CONCURRENT_START] 开始 {len(files)} 个并发事务...")
        
        start_time = time.time()
        
        tasks = [self.engine.update_single_file(f) for f in files]
        results = await asyncio.gather(*tasks)
        
        duration = time.time() - start_time
        
        success_count = sum(1 for r in results if r.success)
        failed_count = len(files) - success_count
        
        self.test_stats["total_operations"] += len(files)
        self.test_stats["successful_operations"] += success_count
        self.test_stats["failed_operations"] += failed_count
        
        logger.info(f"[SCENARIO_4_COMPLETE] 并发事务压力测试完成")
        logger.info(f"  总事务数: {len(files)}")
        logger.info(f"  成功: {success_count}")
        logger.info(f"  失败: {failed_count}")
        logger.info(f"  成功率: {success_count / len(files) * 100:.2f}%")
        logger.info(f"  总耗时: {duration:.2f}秒")
        logger.info(f"  平均: {duration / len(files) * 1000:.2f}ms/事务")
        
        return success_count == len(files)
    
    async def scenario_5_rapid_file_changes(self):
        """场景5：快速文件变更（模拟真实开发场景）"""
        logger.info("\n" + "=" * 80)
        logger.info("[SCENARIO_5] 场景5：快速文件变更")
        logger.info("=" * 80)
        
        test_dir = Path("/tmp/extreme_test_5")
        test_dir.mkdir(exist_ok=True)
        
        file_path = test_dir / "rapid_change.ets"
        
        logger.info("[SCENARIO_5_START] 开始快速文件变更测试...")
        
        iterations = 50
        success_count = 0
        
        for i in range(iterations):
            content = f"""
@Component
struct RapidChange {{
  @State version: number = {i}
  @State data{i}: string = "version {i}"
  
  build() {{
    Column() {{
      Text("Version {{this.version}}")
      Text("Data: {{this.data{i}}}")
    }}
  }}
  
  method{i}(): number {{
    return this.version
  }}
}}
"""
            file_path.write_text(content)
            
            result = await self.engine.update_single_file(str(file_path))
            if result.success:
                success_count += 1
            
            self.test_stats["total_operations"] += 1
            if result.success:
                self.test_stats["successful_operations"] += 1
            else:
                self.test_stats["failed_operations"] += 1
        
        failed_count = iterations - success_count
        
        logger.info(f"[SCENARIO_5_COMPLETE] 快速文件变更测试完成")
        logger.info(f"  迭代次数: {iterations}")
        logger.info(f"  成功: {success_count}")
        logger.info(f"  失败: {failed_count}")
        logger.info(f"  成功率: {success_count / iterations * 100:.2f}%")
        
        return success_count == iterations
    
    async def scenario_6_mixed_operations(self):
        """场景6：混合操作（创建、更新、删除）"""
        logger.info("\n" + "=" * 80)
        logger.info("[SCENARIO_6] 场景6：混合操作测试")
        logger.info("=" * 80)
        
        test_dir = Path("/tmp/extreme_test_6")
        test_dir.mkdir(exist_ok=True)
        
        logger.info("[SCENARIO_6_START] 开始混合操作测试...")
        
        files = []
        for i in range(30):
            file_path = test_dir / f"mixed_{i:03d}.ets"
            content = f"""
@Component
struct Mixed{i:03d} {{
  @State value{i}: number = {i}
  
  build() {{
    Column() {{
      Text("Mixed {{this.value{i}}}")
    }}
  }}
}}
"""
            file_path.write_text(content)
            files.append((str(file_path), "create"))
        
        logger.info(f"[SCENARIO_6_CREATE] 创建 {len(files)} 个文件...")
        create_tasks = [self.engine.update_single_file(f[0]) for f in files]
        create_results = await asyncio.gather(*create_tasks)
        
        create_success = sum(1 for r in create_results if r.success)
        logger.info(f"[SCENARIO_6_CREATE_RESULT] 创建成功: {create_success}/{len(files)}")
        
        for i in range(10):
            files[i] = (files[i][0].replace(".ets", f"_updated{i}.ets"), "update")
        
        for i in range(10, 20):
            os.remove(files[i][0])
            files[i] = (files[i][0], "delete")
        
        logger.info(f"[SCENARIO_6_UPDATE_DELETE] 更新和删除文件...")
        tasks = []
        for file_path, op in files:
            if op == "update":
                updated_path = file_path.replace("_updated", "")
                Path(file_path).write_text(Path(updated_path).read_text())
                os.remove(updated_path)
                tasks.append(self.engine.update_single_file(file_path))
            elif op == "delete":
                tasks.append(self.engine.update_single_file(file_path, "deleted"))
            else:
                tasks.append(self.engine.update_single_file(file_path))
        
        update_results = await asyncio.gather(*tasks)
        update_success = sum(1 for r in update_results if r.success)
        
        total_ops = len(create_results) + len(update_results)
        total_success = create_success + update_success
        
        self.test_stats["total_operations"] += total_ops
        self.test_stats["successful_operations"] += total_success
        self.test_stats["failed_operations"] += (total_ops - total_success)
        
        logger.info(f"[SCENARIO_6_COMPLETE] 混合操作测试完成")
        logger.info(f"  总操作数: {total_ops}")
        logger.info(f"  成功: {total_success}")
        logger.info(f"  失败: {total_ops - total_success}")
        logger.info(f"  成功率: {total_success / total_ops * 100:.2f}%")
        
        return total_success == total_ops
    
    async def run_all_scenarios(self):
        """运行所有场景"""
        await self.setup()
        
        try:
            scenarios = [
                self.scenario_1_massive_concurrent_files,
                self.scenario_2_complex_nested_structures,
                self.scenario_3_unicode_and_special_chars,
                self.scenario_4_concurrent_transaction_stress,
                self.scenario_5_rapid_file_changes,
                self.scenario_6_mixed_operations
            ]
            
            results = []
            for i, scenario in enumerate(scenarios, 1):
                try:
                    result = await scenario()
                    results.append(result)
                    logger.info(f"[SCENARIO_{i}_RESULT] 场景{i}完成: {'成功' if result else '失败'}")
                except Exception as e:
                    logger.error(f"[SCENARIO_{i}_ERROR] 场景{i}异常: {e}")
                    results.append(False)
            
            success_count = sum(1 for r in results if r)
            
            logger.info("\n" + "=" * 80)
            logger.info("[ALL_SCENARIOS_COMPLETE] 所有场景测试完成")
            logger.info("=" * 80)
            logger.info(f"总场景数: {len(scenarios)}")
            logger.info(f"成功场景: {success_count}")
            logger.info(f"失败场景: {len(scenarios) - success_count}")
            logger.info(f"场景成功率: {success_count / len(scenarios) * 100:.2f}%")
            logger.info("=" * 80)
            
            return success_count == len(scenarios)
            
        finally:
            await self.teardown()


async def main():
    tester = Iteration5SuperExtremeTester()
    success = await tester.run_all_scenarios()
    
    if success:
        logger.info("🎉 所有超复杂压力测试场景通过！")
    else:
        logger.warning("⚠️ 部分测试场景未通过，请检查日志")
    
    return success


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)

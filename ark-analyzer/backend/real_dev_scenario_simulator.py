#!/usr/bin/env python3
"""
真实开发场景模拟器
文件名: real_dev_scenario_simulator.py
用途: 模拟真实开发人员不断修改 ArkTS 项目文件，用于发现系统真实运行时问题！
"""
import asyncio
import random
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor
import shutil

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("dev_scen_sim")


class RealDevScenarioSimulator:
    """真实开发场景模拟器"""
    
    def __init__(self, project_dir: str, num_operations: int = 50):
        self.project_dir = Path(project_dir)
        self.num_operations = num_operations
        self.all_files = list(self.project_dir.rglob("*.ets"))
        self.operation_stats = {"modified": 0, "added": 0, "deleted": 0, "renamed": 0}
        self.running = True
    
    def _random_modify_file(self, file_path: Path):
        """随机修改文件内容"""
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            if not lines:
                return
            
            # 随机修改操作
            choice = random.choice(["add_comment", "modify_class", "add_method", "delete_random"])
            
            if choice == "add_comment":
                insert_pos = random.randint(0, len(lines))
                lines.insert(insert_pos, "// Auto-generated dev comment: " + str(time.time()))
            
            elif choice == "modify_class":
                for i, line in enumerate(lines):
                    if "class" in line or "struct" in line:
                        if "class" in line:
                            lines[i] = line.replace("class", "class Modified")
                        break
            
            elif choice == "add_method":
                new_method = f"""
    randomMethod{int(random.randint(1, 100000)): string {{
        return "result";
    }}
""".strip()
                insert_pos = random.randint(0, len(lines))
                lines.insert(insert_pos, new_method)
            
            file_path.write_text("\n".join(lines), encoding="utf-8")
            return True
        except Exception as e:
            logger.error(f"文件修改失败: {e}")
            return False
    
    def _random_add_file(self):
        """随机添加新文件"""
        try:
            filename = f"NewDevFile{random.randint(1, 10000)}.ets"
            components = ["pages", "components", "services", "models", "utils"]
            target_dir = self.project_dir / random.choice(components)
            target_dir.mkdir(exist_ok=True)
            new_file = target_dir / filename
            
            content = f"""@Component
struct {filename.split(".ets", "")} {{
    @State count: number = 0
    
    build() {{
        Column() {{
            Text("New File")
        }}
    }}
    
    increment() {{
        this.count++;
    }}
}}"""
            new_file.write_text(content, encoding="utf-8")
            self.all_files.append(new_file)
            return new_file
        except Exception as e:
            logger.error(f"添加文件失败: {e}")
            return None
    
    def _random_delete_file(self):
        """随机删除文件"""
        if not self.all_files:
            return None
        
        try:
            file = random.choice(self.all_files)
            file.unlink(missing_ok=True)
            self.all_files.remove(file)
            return file
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return None
    
    async def simulate_real_dev_workflow(self):
        """模拟真实开发流程"""
        logger.info(f"🎯 开始真实开发场景模拟")
        logger.info(f"📁 项目目录: {self.project_dir}")
        logger.info(f"📋 计划操作: {self.num_operations}次")
        logger.info("-" * 70)
        
        start_time = time.time()
        
        for i in range(self.num_operations):
            if not self.running:
                break
            
            operation = random.choices(
                ["modify", "add", "delete"],
                weights=[0.7, 0.2, 0.1]  # 修改70%，添加20%，删除10%
            )[0]
            
            file_processed = None
            
            if operation == "modify":
                if self.all_files:
                    target_file = random.choice(self.all_files)
                    logger.info(f"[{i+1}/{self.num_operations}] 📝 修改文件: {target_file.name}")
                    self._random_modify_file(target_file)
                    self.operation_stats["modified"] += 1
                    file_processed = target_file
                    
            elif operation == "add":
                logger.info(f"[{i+1}/{self.num_operations}] ➕ 新建文件")
                new_file = self._random_add_file()
                if new_file:
                    self.operation_stats["added"] += 1
                    file_processed = new_file
                    
            elif operation == "delete":
                logger.info(f"[{i+1}/{self.num_operations}] ❌ 删除文件")
                deleted = self._random_delete_file()
                if deleted:
                    self.operation_stats["deleted"] += 1
                    file_processed = deleted
            
            # 模拟真实的开发间隔
            await asyncio.sleep(random.uniform(0.05, 0.2))
        
        duration = time.time() - start_time
        
        logger.info("-" * 70)
        logger.info(f"✅ 开发模拟完成！")
        logger.info(f"📊 操作统计:")
        logger.info(f"   ✏️ 修改: {self.operation_stats['modified']}")
        logger.info(f"   ➕ 新增: {self.operation_stats['added']}")
        logger.info(f"   ❌ 删除: {self.operation_stats['deleted']}")
        logger.info(f"⏱️ 总耗时: {duration:.2f}秒")
        logger.info("-" * 70)
        
        return self.operation_stats


if __name__ == "__main__":
    simulator = RealDevScenarioSimulator(
        project_dir="/workspace/ark-analyzer/large-test-project",
        num_operations=100
    )
    
    asyncio.run(simulator.simulate_real_dev_workflow())

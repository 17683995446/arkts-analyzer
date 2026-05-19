#!/usr/bin/env python3
"""
ArkAnalyzer 前端集成测试脚本
测试前端是否可以正常构建
"""
import sys
import os
import subprocess
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("frontend-test")

def test_frontend():
    frontend_dir = Path("/workspace/ark-analyzer/frontend")
    logger.info("=" *70)
    logger.info("   🎨 ArkAnalyzer 前端集成测试")
    logger.info("=" *70)
    logger.info(f"📂 前端目录: {frontend_dir}")
    
    if not frontend_dir.exists():
        logger.error("❌ 前端目录不存在！")
        return False
    
    # 检查package.json
    pkg_json = frontend_dir / "package.json"
    if not pkg_json.exists():
        logger.error("❌ package.json 不存在！")
        return False
    
    logger.info("✅ 前端项目结构正常")
    
    # 尝试安装依赖
    logger.info("")
    logger.info("📦 检查是否已安装依赖...")
    node_modules = frontend_dir / "node_modules"
    
    if not node_modules.exists():
        logger.info("📦 安装依赖 (npm install)...")
        try:
            process = subprocess.Popen(
                ["npm", "install"],
                cwd=str(frontend_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                logger.info("✅ 依赖安装成功！")
            else:
                logger.error(f"❌ 依赖安装失败！错误: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 安装依赖异常: {e}")
            return False
    else:
        logger.info("✅ node_modules 已存在，跳过安装")
    
    # 尝试构建
    logger.info("")
    logger.info("🏗️  测试前端构建...")
    
    try:
        process = subprocess.Popen(
            ["npm", "run", "build"],
            cwd=str(frontend_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        
        if process.returncode ==0:
            logger.info("✅ 前端构建成功！")
            dist_dir = frontend_dir / "dist"
            if dist_dir.exists():
                file_count = len(list(dist_dir.rglob("*")))
                logger.info(f"📦 构建输出: {file_count} 个文件")
                
            return True
        else:
            logger.error(f"❌ 前端构建失败！")
            logger.error(f"stderr: {stderr}")
            logger.error(f"stdout: {stdout}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 构建异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    result = test_frontend()
    if result:
        logger.info("")
        logger.info("🎉🎉🎉 前端测试完全通过！！")
        return 0
    else:
        logger.error("")
        logger.error("❌ 前端测试失败！")
        return 1
        
if __name__ == "__main__":
    sys.exit(main())

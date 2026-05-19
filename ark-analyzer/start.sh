#!/bin/bash

# ArkAnalyzer 启动脚本

echo "========================================="
echo "  ArkAnalyzer - ArkTS知识图谱动态更新系统"
echo "========================================="
echo ""

# 设置工作目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查Python版本
python3 --version || {
    echo "错误: 需要Python 3.10或更高版本"
    exit 1
}

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建Python虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装后端依赖
echo "安装后端依赖..."
pip install -r requirements.txt

echo ""
echo "========================================="
echo "  后端服务已准备就绪"
echo "========================================="
echo ""
echo "启动后端服务:"
echo "  cd backend/src"
echo "  python ark_analyzer.py"
echo ""
echo "或者使用uvicorn:"
echo "  uvicorn src.ark_analyzer:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "前端开发服务器:"
echo "  cd frontend"
echo "  npm install"
echo "  npm run dev"
echo ""

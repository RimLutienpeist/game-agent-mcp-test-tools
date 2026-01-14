#!/bin/bash
# 测试运行器启动脚本 - 自动使用虚拟环境

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 进入项目根目录（test 的父目录）
cd "$SCRIPT_DIR/.."

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "❌ 错误：虚拟环境不存在"
    echo "请先运行：python3 -m venv venv && venv/bin/pip install -e ."
    exit 1
fi

# 使用虚拟环境的 Python 运行测试
venv/bin/python3 test/scripts/test_stage_runner.py "$@"

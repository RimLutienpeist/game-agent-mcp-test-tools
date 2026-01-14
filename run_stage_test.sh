#!/bin/bash
# 测试运行器启动脚本 - 自动使用虚拟环境

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 进入项目根目录（test 的父目录）
cd "$SCRIPT_DIR/.."

# 检查是否在虚拟环境中（venv 或 conda）
if [ -d "venv" ]; then
    # 如果 venv 存在，使用 venv
    venv/bin/python3 test/scripts/test_stage_runner.py "$@"
else
    # 否则使用当前环境的 Python（适用于 conda）
    python3 test/scripts/test_stage_runner.py "$@"
fi

#!/usr/bin/env python3
"""
简单的图像生成测试脚本
直接调用 _generate_game_asset_internal 函数
"""

import sys
import os
import asyncio
from pathlib import Path

# 获取脚本所在目录并切换到项目根目录
script_dir = Path(__file__).parent
project_root = script_dir.parent
os.chdir(project_root)

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(project_root))

# 设置环境变量（禁用背景移除）
os.environ['AUTO_REMOVE_BACKGROUND'] = 'false'

# 导入函数
from mcp_server import _generate_game_asset_internal

# 工作空间路径
workspace = 'test/temp_workspace/yeild-test'

print(f"工作空间: {workspace}")
print(f"开始生成图像...")
print("=" * 60)

# 调用函数生成图像（使用 asyncio.run 因为它是 async 函数）
result = asyncio.run(_generate_game_asset_internal(workspace, max_concurrent=2))

print("=" * 60)
print("\n生成结果:")
print(result)

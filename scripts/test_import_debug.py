#!/usr/bin/env python3
import sys
import importlib
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Step 1: Starting import...", flush=True)
sys.stdout.flush()

print("Step 2: About to import mcp_server module", flush=True)
sys.stdout.flush()

module = importlib.import_module("mcp_server")

print("Step 3: Module imported successfully!", flush=True)
sys.stdout.flush()

print("Step 4: Getting function...", flush=True)
func = getattr(module, "_generate_game_asset_internal")

print(f"Step 5: Function retrieved: {func}", flush=True)
print("SUCCESS!")

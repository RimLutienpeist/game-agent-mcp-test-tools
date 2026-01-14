# 🚀 运行测试指南

## 快速开始

### 使用 run_stage_test.sh（推荐）

这个脚本会自动使用虚拟环境，无需手动激活：

```bash
# 分阶段测试（禁用抠图）

# 步骤1: 生成 game.md（可自定义游戏创意）
./run_stage_test.sh -w generate-game-contents -s stage1 --workspace tile-test \
  --user-input "请帮我生成一个森林冰火人游戏，火人和冰人分别用上下左右和wasd控制"

# 步骤2: 生成 tasks.json
./run_stage_test.sh -w generate-game-contents -s stage2 --workspace yeild-test

# 步骤3: 生成 assets.md
./run_stage_test.sh -w generate-game-contents -s stage3 --workspace thumb-test-bommer

# 步骤4: 生成图像（禁用抠图）
AUTO_REMOVE_BACKGROUND=false ./run_stage_test.sh -w generate-game-contents -s stage4 --workspace my_test

cd /home/leke/playground/game-agent/qwen-code/setting_tools/.qwen/mcp-servers/game-helper-python && 
venv/bin/python3 test_generate_images.py
```

**注意**：

- 🆕 使用 `--user-input` 或 `-u` 参数可以自定义游戏创意
- 如果不提供，将使用配置文件中的默认示例

```bash

# 步骤1: 生成 game.md（可自定义游戏创意）
./run_stage_test.sh -w generate-game-contents -s stage1 --workspace thumb-test-bommer \
  --user-input "我想玩一个跑酷游戏"
  
# 步骤2: 生成 tasks.json
./run_stage_test.sh -w generate-game-contents -s stage2 --workspace thumb-test-bommer

# 步骤4: 生成图像（禁用抠图）
```



---

## 完整命令格式

```bash
# 基础格式
./run_stage_test.sh -w <workflow> -s <stage> --workspace <name>

# 禁用抠图
AUTO_REMOVE_BACKGROUND=false ./run_stage_test.sh -w <workflow> -s <stage> --workspace <name>

# 查看详细日志
./run_stage_test.sh -w <workflow> -s <stage> --workspace <name> -v
```

---

## 常见问题

### Q: 如何查看生成的文件？

```bash
# 查看工作空间
ls -lh test/temp_workspace/my_test/

# 查看 game.md
cat test/temp_workspace/my_test/doc/game.md

# 查看 tasks.json
cat test/temp_workspace/my_test/public/tasks.json
```

### Q: 如何清理工作空间？

```bash
# 删除特定工作空间
rm -rf test/temp_workspace/my_test

# 清理所有
rm -rf test/temp_workspace/*
```

### Q: 如何同时测试多个阶段？

```bash
# 一次性测试前3个阶段
./run_stage_test.sh -w generate-game-contents -s stage1,stage2,stage3 --workspace my_test
```

### Q: 为什么要用 `./run_stage_test.sh` 而不是 `python3 test/scripts/test_stage_runner.py`？

**原因：**
- `run_stage_test.sh` 自动使用虚拟环境中的 Python
- 虚拟环境中已安装所有必需的依赖（mcp, pyyaml等）
- 无需手动激活虚拟环境

---

## 文件结构

```
test/temp_workspace/my_test/
├── doc/
│   ├── game.md          # stage1 生成
│   └── assets.md        # stage3 生成
└── public/
    ├── tasks.json       # stage2 生成
    └── assets/          # stage4 生成
        ├── asset1.png
        └── _originals/
```

---

## 详细文档

- 📖 [快速开始指南](WORKSPACE_TESTING_QUICKSTART.md)
- 📖 [自定义用户输入指南](test/docs/CUSTOM_USER_INPUT.md) 🆕
- 📖 [工作空间复用指南](test/docs/WORKSPACE_GUIDE.md)
- 📖 [跳过图像抠图指南](test/docs/SKIP_BACKGROUND_REMOVAL.md)
- 📖 [测试系统完整文档](test/README.md)

---

## 注意事项

1. **必须在项目根目录运行**
   ```bash
   cd /path/to/game-helper-python
   ./run_stage_test.sh ...
   ```

2. **禁用抠图时的命令**
   ```bash
   AUTO_REMOVE_BACKGROUND=false ./run_stage_test.sh -w generate-game-contents -s stage4 --workspace my_test
   ```

3. **查看帮助**
   ```bash
   ./run_stage_test.sh --help
   ```

祝测试顺利！🎉

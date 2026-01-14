# 🚀 分阶段测试快速开始指南

## 核心改进

现在测试框架支持 `--workspace` 参数，允许你在多次测试中**复用同一个工作空间**，真正实现分阶段测试！

## 快速开始

### 你的需求：分步执行测试

```bash
# 进入项目根目录
cd /home/leke/playground/game-agent/qwen-code/setting_tools/.qwen/mcp-servers/game-helper-python

# 第1步：生成 game.md
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage1 \
  --workspace my_test

# 第2步：生成 tasks.json（复用同一工作空间）
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage2 \
  --workspace my_test

# 第3步：生成 assets.md
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage3 \
  --workspace my_test

# 第4步：生成图像（禁用抠图，不需要下载 rembg 模型）
AUTO_REMOVE_BACKGROUND=false python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage4 \
  --workspace my_test

# ✋ 停止，不执行 stage5

# 注意：如果想启用抠图（需要下载 rembg 模型），去掉 AUTO_REMOVE_BACKGROUND=false
```

## 核心原理

### 之前（没有 --workspace）

```bash
# 第1次运行
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage1
# 创建: test/temp_workspace/generate-game-contents_20260108_150230/

# 第2次运行
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage2
# 创建: test/temp_workspace/generate-game-contents_20260108_150245/
# ❌ 找不到 game.md（在不同的工作空间！）
```

### 现在（使用 --workspace）

```bash
# 第1次运行
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage1 --workspace my_test
# 创建: test/temp_workspace/my_test/

# 第2次运行
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage2 --workspace my_test
# 复用: test/temp_workspace/my_test/
# ✅ 找到 game.md（在同一个工作空间！）
```

## 生成的文件结构

```
test/temp_workspace/my_test/
├── doc/
│   ├── game.md          # stage1 生成
│   └── assets.md        # stage3 生成
└── public/
    ├── tasks.json       # stage2 生成
    └── assets/          # stage4 生成
        ├── asset1.png
        ├── asset2.png
        └── _originals/
```

## 快速演示脚本

运行自动化演示：

```bash
./test/scripts/demo_workspace_test.sh
```

这个脚本会自动执行前3个阶段，并展示结果。

## 查看生成的文件

```bash
# 查看工作空间
ls -lh test/temp_workspace/my_test/

# 查看 game.md
cat test/temp_workspace/my_test/doc/game.md

# 查看 tasks.json
cat test/temp_workspace/my_test/public/tasks.json

# 查看 assets.md
cat test/temp_workspace/my_test/doc/assets.md
```

## 清理工作空间

```bash
# 删除特定工作空间
rm -rf test/temp_workspace/my_test

# 清理所有测试工作空间
rm -rf test/temp_workspace/*
```

## 高级用法

### 测试多个阶段（仍复用工作空间）

```bash
# 一次性测试前3个阶段（快速，不生成图像）
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage1,stage2,stage3 \
  --workspace my_test
```

### 重新测试失败的阶段

```bash
# 假设 stage3 失败，修改后重新运行
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage3 \
  --workspace my_test
```

### 详细日志模式

```bash
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage1 \
  --workspace my_test \
  -v
```

## 完整文档

- 📖 [工作空间复用完整指南](test/docs/WORKSPACE_GUIDE.md)
- 📖 [跳过图像抠图指南](test/docs/SKIP_BACKGROUND_REMOVAL.md) 🆕
- 📖 [测试系统完整文档](test/README.md)
- 📖 [快速入门](test/docs/QUICKSTART.md)

## 帮助命令

```bash
python3 test/scripts/test_stage_runner.py --help
```

输出：
```
  --workspace WORKSPACE
                        指定工作空间名称（用于复用已有工作空间，例如: my_test）
```

## 注意事项

1. **工作空间名称建议**
   - 使用简洁的名称：`my_test`、`test_001`、`debug`
   - 避免空格和特殊字符
   - 使用小写字母和下划线

2. **阶段执行顺序**
   - 必须按照依赖顺序执行：stage1 → stage2 → stage3 → stage4
   - 跳过某个阶段会导致后续阶段失败

3. **调试技巧**
   - 使用 `-v` 查看详细日志
   - 保留工作空间便于检查中间结果
   - 失败后可以重新运行单个阶段

祝测试顺利！🎉

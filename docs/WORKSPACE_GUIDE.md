# 工作空间复用指南

## 功能说明

现在测试框架支持**指定工作空间名称**，允许你在多次测试中复用同一个工作空间。这样可以实现真正的分阶段测试。

## 使用方法

### 基本用法

使用 `--workspace` 参数指定工作空间名称：

```bash
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage1 --workspace my_test
```

### 完整的分阶段测试流程

#### 步骤1: 生成 game.md

```bash
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage1 \
  --workspace my_test
```

**输出：**
- ✓ 创建工作空间: `test/temp_workspace/my_test/`
- ✓ 生成文件: `test/temp_workspace/my_test/doc/game.md`

---

#### 步骤2: 生成 tasks.json

```bash
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage2 \
  --workspace my_test
```

**输出：**
- ✓ 使用已存在的工作空间: `test/temp_workspace/my_test/`
- ✓ 读取: `test/temp_workspace/my_test/doc/game.md`
- ✓ 生成文件: `test/temp_workspace/my_test/public/tasks.json`

---

#### 步骤3: 生成 assets.md

```bash
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage3 \
  --workspace my_test
```

**输出：**
- ✓ 使用已存在的工作空间: `test/temp_workspace/my_test/`
- ✓ 读取: `test/temp_workspace/my_test/public/tasks.json`
- ✓ 生成文件: `test/temp_workspace/my_test/doc/assets.md`

---

#### 步骤4: 生成游戏素材图像

```bash
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage4 \
  --workspace my_test
```

**输出：**
- ✓ 使用已存在的工作空间: `test/temp_workspace/my_test/`
- ✓ 读取: `test/temp_workspace/my_test/public/tasks.json`
- ✓ 生成图像: `test/temp_workspace/my_test/public/assets/*.png`

---

## 工作空间结构

使用自定义工作空间后，目录结构如下：

```
test/temp_workspace/my_test/
├── doc/
│   ├── game.md          # 步骤1生成
│   └── assets.md        # 步骤3生成
└── public/
    ├── tasks.json       # 步骤2生成
    └── assets/          # 步骤4生成
        ├── asset1.png
        ├── asset2.png
        └── _originals/  # 高质量原图
```

## 高级用法

### 1. 跳过某些阶段

如果你已经有了 `game.md`，可以直接从步骤2开始：

```bash
# 先手动创建工作空间并复制 game.md
mkdir -p test/temp_workspace/my_test/doc
cp /path/to/game.md test/temp_workspace/my_test/doc/

# 从步骤2开始
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage2 --workspace my_test
```

### 2. 重新测试某个阶段

如果某个阶段失败，可以修改后重新运行：

```bash
# 重新运行步骤3
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage3 --workspace my_test
```

### 3. 测试多个阶段（仍使用同一工作空间）

```bash
# 一次性测试步骤2和3
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage2,stage3 \
  --workspace my_test
```

### 4. 查看工作空间内容

```bash
# 查看工作空间结构
tree test/temp_workspace/my_test/

# 查看生成的 game.md
cat test/temp_workspace/my_test/doc/game.md

# 查看生成的 tasks.json
cat test/temp_workspace/my_test/public/tasks.json

# 查看生成的图像
ls -lh test/temp_workspace/my_test/public/assets/
```

## 对比：有无 --workspace 参数

### 不使用 --workspace（默认行为）

```bash
# 第1次运行
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage1
# 创建: test/temp_workspace/generate-game-contents_20260108_150230/

# 第2次运行
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage2
# 创建: test/temp_workspace/generate-game-contents_20260108_150245/
# ❌ 找不到 game.md（在不同的工作空间！）
```

### 使用 --workspace（复用工作空间）

```bash
# 第1次运行
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage1 --workspace my_test
# 创建: test/temp_workspace/my_test/

# 第2次运行
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage2 --workspace my_test
# 复用: test/temp_workspace/my_test/
# ✓ 找到 game.md（在同一个工作空间！）
```

## 注意事项

1. **工作空间名称规范**
   - 使用简单的名称，如：`my_test`、`tank_game`、`test_001`
   - 避免使用空格和特殊字符
   - 推荐使用小写字母和下划线

2. **工作空间位置**
   - 默认位置：`test/temp_workspace/`
   - 可在配置文件中修改：`config/stage_test_config.yaml`

3. **清理工作空间**
   ```bash
   # 删除特定工作空间
   rm -rf test/temp_workspace/my_test

   # 清理所有测试工作空间
   rm -rf test/temp_workspace/*
   ```

4. **调试技巧**
   - 使用 `-v` 参数查看详细日志：
     ```bash
     python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage1 --workspace my_test -v
     ```
   - 保留工作空间便于检查结果（配置文件中 `cleanup_after_test: false`）

## 实际示例

### 示例1: 快速测试前3个阶段（文档生成）

```bash
# 一次性测试
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage1,stage2,stage3 \
  --workspace quick_test
```

### 示例2: 分步调试图像生成

```bash
# 步骤1-3：先生成文档
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage1,stage2,stage3 \
  --workspace debug_images

# 检查 tasks.json
cat test/temp_workspace/debug_images/public/tasks.json

# 步骤4：单独测试图像生成
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage4 \
  --workspace debug_images \
  -v
```

### 示例3: 使用真实API测试

```bash
# 警告：会调用真实API，消耗token！
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage1 \
  --workspace real_api_test \
  --no-mock
```

## 常见问题

### Q1: 如何查看可用的工作空间？

```bash
ls -lh test/temp_workspace/
```

### Q2: 工作空间名称冲突怎么办？

如果工作空间已存在，框架会复用它。如果想要全新的工作空间，使用不同的名称或删除旧的：

```bash
rm -rf test/temp_workspace/my_test
```

### Q3: 如何在多次测试中保持工作空间？

配置文件中设置：
```yaml
global:
  cleanup_after_test: false  # 不自动清理
```

### Q4: 测试失败后如何重试？

直接重新运行失败的阶段（使用相同的 `--workspace` 参数）：

```bash
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage3 \
  --workspace my_test
```

## 总结

使用 `--workspace` 参数后，你可以：

✅ 真正的分阶段测试（每次只测试一个阶段）
✅ 复用已有的测试数据（不重复生成）
✅ 灵活调试（失败后重试单个阶段）
✅ 手动检查中间结果（查看生成的文件）
✅ 节省时间（跳过已完成的阶段）

祝测试顺利！🎉

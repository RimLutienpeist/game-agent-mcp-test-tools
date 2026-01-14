# 🖼️ 如何测试图像生成

## 📋 准备工作

你需要一个 `tasks.json` 文件，格式如下：

```json
[
  {
    "name": "image1.png",
    "description": "图像描述...",
    "size": "1024x1024",
    "is_background": false,
    "needs_generation": true
  }
]
```

## 🚀 方法1: 使用快速测试脚本（最简单）

### 步骤1: 准备测试环境

```bash
# 创建测试工作空间
mkdir -p test/temp_workspace/my_test/public

# 复制你的 tasks.json
cp tasks.json test/temp_workspace/my_test/public/
```

### 步骤2: 运行测试

```bash
# 使用快速测试脚本
python test_image_generation.py test/temp_workspace/my_test
```

### 步骤3: 查看结果

```bash
# 生成的图像在这里
ls -lh test/temp_workspace/my_test/public/assets/

# 查看原图（高质量版本）
ls -lh test/temp_workspace/my_test/public/assets/_originals/
```

---

## 🔧 方法2: 使用分阶段测试系统

### 步骤1: 准备完整的工作空间

```bash
# 创建完整结构
mkdir -p test/temp_workspace/full_test/public
mkdir -p test/temp_workspace/full_test/doc

# 复制 tasks.json
cp tasks.json test/temp_workspace/full_test/public/
```

### 步骤2: 只测试图像生成阶段

```bash
# 测试 generate-game-asset 工作流的图像生成部分
python test/scripts/test_stage_runner.py \
  --workflow generate-game-asset \
  --stage stage3,stage4,stage5
```

### 步骤3: 查看详细报告

测试完成后会显示：
- ✅ 成功数量
- ❌ 失败数量
- ⏱️ 总耗时
- 📊 每张图像的详细信息

---

## 🎯 方法3: 直接调用Python函数

创建一个测试脚本 `my_test.py`:

```python
from mcp_server import _generate_game_asset_internal

# 调用图像生成
workspace_dir = "test/temp_workspace/my_test"
result = _generate_game_asset_internal(workspace_dir, max_concurrent=3)

# 打印结果
print(result)
```

运行：
```bash
python my_test.py
```

---

## 📁 目录结构要求

测试前，你的工作空间应该是这样的：

```
test/temp_workspace/my_test/
└── public/
    └── tasks.json          # 你的任务文件
```

测试后，会生成：

```
test/temp_workspace/my_test/
└── public/
    ├── tasks.json          # 原始任务文件（尺寸会被更新）
    └── assets/             # 生成的图像
        ├── image1.png      # 处理后的图像（背景已移除、已缩放）
        ├── image2.png
        └── _originals/     # 高质量原图
            ├── image1.png
            └── image2.png
```

---

## ⚙️ 配置选项

### 调整并发数量

```python
# 默认并发5个，可以调整
result = _generate_game_asset_internal(workspace_dir, max_concurrent=3)
```

### 关闭Mock模式（使用真实API）

编辑 `test/config/stage_test_config.yaml`:
```yaml
mock:
  enabled: false  # 改为 false 使用真实API
```

⚠️ **警告**: 使用真实API会产生费用！

---

## 🔍 验证生成结果

### 检查图像数量

```bash
# 统计生成的图像
ls test/temp_workspace/my_test/public/assets/*.png | wc -l

# 对比 tasks.json 中的任务数
cat test/temp_workspace/my_test/public/tasks.json | jq '. | length'
```

### 检查图像尺寸

```bash
# 安装 imagemagick（如果没有）
# sudo apt-get install imagemagick

# 查看图像信息
identify test/temp_workspace/my_test/public/assets/*.png
```

### 检查是否有透明通道

```python
from PIL import Image

img = Image.open("test/temp_workspace/my_test/public/assets/image1.png")
print(f"模式: {img.mode}")  # 应该是 'RGBA'
print(f"尺寸: {img.size}")
```

---

## 📊 示例输出

成功的输出应该类似：

```
============================================================
开始阶段: generate-game-asset -> stage3
============================================================
📥 准备输入...
⚙️  执行: generate_images_async...
✓ 函数执行完成

Batch generation complete!

Statistics:
  • Success: 5
  • Failed: 0
  • Total time: 45.3s
  • Average time: 9.1s/image
  • Speedup: 3.2x (vs serial)
  • Save location: /path/to/assets/

✅ Generated assets:
  • image1.png [1024x1024] (8.5s) [BG removed: 245,678 pixels]
  • image2.png [512x512] (7.2s) [BG removed: 61,234 pixels]
  ...
```

---

## ❓ 常见问题

### Q1: 提示 "tasks.json 不存在"

**解决**: 确保文件路径正确
```bash
# 检查文件是否存在
ls test/temp_workspace/my_test/public/tasks.json
```

### Q2: 生成的图像数量不对

**解决**: 检查 `needs_generation` 字段
```bash
# 只有 needs_generation=true 的任务才会生成
cat tasks.json | jq '.[] | select(.needs_generation == true)'
```

### Q3: API调用失败

**检查**:
1. 网络连接是否正常
2. API密钥是否有效
3. 是否达到API限额

**临时方案**: 使用Mock模式测试逻辑

### Q4: 背景没有移除

**原因**: `is_background: true` 的图像不会移除背景

**解决**: 检查 tasks.json 中的 `is_background` 字段

---

## 💡 快速测试命令总结

```bash
# 方法1: 快速测试脚本
mkdir -p test/temp_workspace/my_test/public
cp tasks.json test/temp_workspace/my_test/public/
python test_image_generation.py test/temp_workspace/my_test

# 方法2: 分阶段测试
python test/scripts/test_stage_runner.py -w generate-game-asset -s stage3,stage4,stage5

# 查看结果
ls -lh test/temp_workspace/*/public/assets/
```

---

## 🎉 完成！

现在你可以开始测试图像生成了！

建议从**方法1**开始，最简单快速。

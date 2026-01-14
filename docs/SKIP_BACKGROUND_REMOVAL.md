# 跳过图像抠图（背景移除）指南

## 问题说明

**stage4（图像生成）默认会进行两个步骤：**

1. ✅ **调用API生成图像** - 只需要API密钥，无需下载模型
2. ⚠️ **自动抠图（背景移除）** - 需要下载 rembg 模型（约200-400MB）

如果你不想下载抠图模型，可以通过环境变量禁用抠图功能。

---

## 解决方案

### 方法1: 临时禁用（推荐用于测试）

在运行测试命令前设置环境变量：

```bash
# Linux/Mac
export AUTO_REMOVE_BACKGROUND=false

# 然后运行测试
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage4 --workspace my_test
```

或者一行命令：

```bash
# Linux/Mac
AUTO_REMOVE_BACKGROUND=false python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage4 --workspace my_test

# Windows PowerShell
$env:AUTO_REMOVE_BACKGROUND="false"; python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage4 --workspace my_test

# Windows CMD
set AUTO_REMOVE_BACKGROUND=false && python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage4 --workspace my_test
```

### 方法2: 永久禁用（添加到 .env 文件）

在项目根目录创建或编辑 `.env` 文件：

```bash
# .env 文件
AUTO_REMOVE_BACKGROUND=false
```

然后正常运行测试即可：

```bash
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage4 --workspace my_test
```

---

## 完整的分阶段测试示例（禁用抠图）

```bash
# 在项目根目录执行

# 步骤1: 生成 game.md
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage1 --workspace my_test

# 步骤2: 生成 tasks.json
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage2 --workspace my_test

# 步骤3: 生成 assets.md
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage3 --workspace my_test

# 步骤4: 生成图像（禁用抠图）
AUTO_REMOVE_BACKGROUND=false python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage4 --workspace my_test
```

---

## 效果对比

### 启用抠图（默认）

```
✓ 生成图像: asset1.png
✓ 抠图处理: asset1.png (移除了 12,345 像素)
✓ 保存原图: _originals/asset1.png
```

**优点：** 生成透明背景PNG，适合游戏开发
**缺点：** 需要下载rembg模型（约200-400MB）

### 禁用抠图

```
✓ 生成图像: asset1.png
⚠ 跳过抠图（AUTO_REMOVE_BACKGROUND=false）
✓ 保存原图: _originals/asset1.png
```

**优点：** 无需下载模型，节省时间和空间
**缺点：** 图像带有白色背景，需要后续手动处理

---

## 如何验证抠图是否被禁用

查看日志输出：

```bash
# 启用抠图时的日志
自动移除背景: 开启
正在初始化 rembg session...

# 禁用抠图时的日志
自动移除背景: 关闭
跳过背景移除（AUTO_REMOVE_BACKGROUND=false）
```

---

## 如果遇到 rembg 模型下载问题

如果你在测试时看到以下错误：

```
正在初始化 rembg session...
Downloading model from https://...
Error: Connection timeout
```

说明抠图功能被启用了，但模型下载失败。解决方案：

1. **临时禁用抠图**（使用上面的方法）
2. 或者等待模型下载完成（首次需要几分钟）

---

## 常见问题

### Q1: 禁用抠图后，生成的图像有背景吗？

**A:** 是的，生成的图像会保留API返回的原始背景（通常是白色或纯色背景）。

### Q2: 能否后续再手动抠图？

**A:** 可以。原始图像会保存在 `public/assets/_originals/` 目录，你可以稍后使用其他工具处理。

### Q3: 如何重新启用抠图？

**A:** 删除环境变量或设置为 `true`：

```bash
export AUTO_REMOVE_BACKGROUND=true
# 或
unset AUTO_REMOVE_BACKGROUND
```

### Q4: 测试时如何同时禁用API调用和抠图？

**A:** 测试框架默认使用 Mock API（不会真正调用图像生成API）。如果需要测试真实API但禁用抠图：

```bash
AUTO_REMOVE_BACKGROUND=false python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage4 \
  --workspace my_test \
  --no-mock
```

---

## 总结

**对于你的需求（不想下载rembg模型）：**

✅ **推荐方案：** 使用环境变量临时禁用抠图

```bash
# 一行命令解决
AUTO_REMOVE_BACKGROUND=false python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage4 --workspace my_test
```

这样：
- ✅ 仍然会调用API生成图像
- ✅ 跳过抠图处理（不需要下载模型）
- ✅ 保存原始图像到 `_originals/` 目录
- ✅ 测试可以正常完成

祝测试顺利！🎉

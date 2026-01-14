# 🚀 分阶段测试快速入门

## 5分钟快速上手

### 步骤1: 查看测试系统结构

```bash
ls -la
```

你会看到以下关键文件：
- ✅ `stage_test_config.yaml` - 配置文件
- ✅ `test_stage_runner.py` - 测试脚本
- ✅ `stage_validators.py` - 验证器
- ✅ `README_STAGE_TEST.md` - 完整文档

### 步骤2: 运行第一个测试

```bash
# 测试阶段1：游戏设计生成
python test_stage_runner.py --workflow generate-game-contents --stage stage1
```

**你会看到：**
```
============================================================
开始阶段: generate-game-contents -> stage1
============================================================
📥 准备输入...
⚙️  执行: text_generation_function.generate_game_design...
✓ 函数执行完成
✓ 输出已保存: tests/temp_workspace/.../doc/game.md
🔍 验证输出...
  ✓ file_exists 验证通过
  ✓ file_not_empty 验证通过
✅ 阶段完成: stage1 (15.32s)
```

### 步骤3: 查看生成的文件

```bash
# 查找最新的测试工作空间
ls -t tests/temp_workspace/

# 查看生成的game.md
cat tests/temp_workspace/generate-game-contents_*/doc/game.md
```

### 步骤4: 测试多个阶段

```bash
# 测试前3个阶段（跳过图像生成，速度快）
python test_stage_runner.py --workflow generate-game-contents --stage stage1,stage2,stage3
```

**结果：**
- ✅ `doc/game.md` - 游戏设计文档
- ✅ `public/tasks.json` - 素材任务清单
- ✅ `doc/assets.md` - 素材使用说明

### 步骤5: 运行演示脚本

```bash
./demo_stage_test.sh
```

这会自动运行几个示例测试并展示结果。

## 📋 常用命令速查

### 测试单个阶段
```bash
# 只测试游戏设计生成
python test_stage_runner.py -w generate-game-contents -s stage1

# 只测试素材清单生成
python test_stage_runner.py -w generate-game-contents -s stage2
```

### 测试阶段范围
```bash
# 从stage2开始测试到结束
python test_stage_runner.py -w generate-game-contents --from-stage stage2

# 测试前3个阶段
python test_stage_runner.py -w generate-game-contents -s stage1,stage2,stage3
```

### 测试完整工作流
```bash
# 测试所有阶段
python test_stage_runner.py -w generate-game-contents

# 测试另一个工作流
python test_stage_runner.py -w generate-game-asset
```

### 使用预设场景
```bash
# 快速测试（跳过图像生成）
python test_stage_runner.py --scenario quick

# 完整测试
python test_stage_runner.py --scenario full
```

## 🎯 典型使用场景

### 场景1: 调试stage2的JSON生成问题

```bash
# 1. 单独测试stage2
python test_stage_runner.py -w generate-game-contents -s stage2 -v

# 2. 查看生成的JSON
cat tests/temp_workspace/generate-game-contents_*/public/tasks.json | python -m json.tool

# 3. 如果有问题，检查验证规则
grep -A 10 "stage2:" stage_test_config.yaml
```

### 场景2: 验证完整流程（不包括图像生成）

```bash
# 测试除了stage4外的所有阶段
python test_stage_runner.py -w generate-game-contents -s stage1,stage2,stage3,stage5
```

### 场景3: 只测试图像生成管道

```bash
# 1. 准备测试数据
mkdir -p tests/temp_workspace/test_image_gen/public
cp tests/fixtures/sample_tasks.json tests/temp_workspace/test_image_gen/public/

# 2. 测试图像生成
python test_stage_runner.py -w generate-game-asset -s stage1,stage2,stage3,stage4
```

## 📊 理解测试输出

### 成功的测试
```
✅ stage1: 游戏设计生成 (15.32s)
✅ stage2: 素材清单生成 (12.45s)
✅ stage3: 素材文档生成 (10.23s)

总计: 3 个阶段
成功: 3 个
失败: 0 个
成功率: 100.0%
```

### 失败的测试
```
❌ stage2: 素材清单生成 (2.15s)
   错误: tasks.json 不是有效的JSON格式

总计: 2 个阶段
成功: 1 个
失败: 1 个
成功率: 50.0%
```

## 🔧 配置调整

### 关闭测试后清理（便于调试）

编辑 `stage_test_config.yaml`:
```yaml
global:
  cleanup_after_test: false  # 改为 false
```

### 调整超时时间

```yaml
stages:
  stage1:
    timeout: 60  # 增加到60秒
```

### 禁用某个验证

```yaml
validation:
  # - check: "contains_keywords"  # 注释掉不需要的验证
  - check: "file_exists"
```

## ❓ 遇到问题？

### 问题1: 找不到模块

```bash
# 确保在正确的目录
cd /path/to/game-helper-python

# 检查Python路径
python -c "import sys; print('\n'.join(sys.path))"
```

### 问题2: 配置文件错误

```bash
# 验证YAML格式
python -c "import yaml; yaml.safe_load(open('stage_test_config.yaml'))"
```

### 问题3: 工作空间找不到

```bash
# 检查是否创建
ls -la tests/temp_workspace/

# 手动创建
mkdir -p tests/temp_workspace
```

## 📚 下一步

- 阅读完整文档: `cat README_STAGE_TEST.md`
- 查看配置示例: `cat stage_test_config.yaml`
- 了解验证器: `cat stage_validators.py`
- 运行演示: `./demo_stage_test.sh`

## 💡 提示

1. **从简单开始**: 先测试单个阶段，熟悉后再测试完整流程
2. **保留工作空间**: 设置 `cleanup_after_test: false` 便于调试
3. **使用verbose模式**: 遇到问题时加上 `-v` 参数查看详细日志
4. **逐步验证**: 每个阶段完成后手动检查输出文件

祝测试顺利！🎉

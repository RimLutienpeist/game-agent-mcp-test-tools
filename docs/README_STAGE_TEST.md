# MCP工具分阶段测试指南

## 📚 概述

这是一套完整的分阶段测试系统，允许你独立测试MCP工具的每个阶段，快速定位问题。

## 🗂️ 文件说明

```
game-helper-python/
├── stage_test_config.yaml       # 阶段测试配置文件（定义所有阶段的输入输出和验证规则）
├── test_stage_runner.py         # 分阶段测试运行器（主测试脚本）
├── stage_validators.py          # 验证器模块（提供各种验证检查函数）
├── tests/
│   └── fixtures/                # 测试夹具和示例数据
│       ├── sample_user_input.txt    # 示例游戏创意输入
│       └── sample_tasks.json        # 示例素材任务列表
└── tests/temp_workspace/        # 测试工作空间（自动创建）
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install pyyaml pillow
```

### 2. 测试单个阶段

```bash
# 只测试阶段1：游戏设计生成
python test_stage_runner.py --workflow generate-game-contents --stage stage1

# 只测试阶段2：素材清单生成
python test_stage_runner.py --workflow generate-game-contents --stage stage2
```

### 3. 测试多个阶段

```bash
# 测试阶段1、2、3
python test_stage_runner.py --workflow generate-game-contents --stage stage1,stage2,stage3
```

### 4. 从某阶段开始测试

```bash
# 从阶段2开始测试到结束
python test_stage_runner.py --workflow generate-game-contents --from-stage stage2
```

### 5. 测试完整工作流

```bash
# 测试完整的 generate-game-contents 工作流
python test_stage_runner.py --workflow generate-game-contents

# 测试 generate-game-asset 工作流
python test_stage_runner.py --workflow generate-game-asset
```

### 6. 使用预设场景

```bash
# 快速测试（跳过图像生成）
python test_stage_runner.py --scenario quick

# 完整测试
python test_stage_runner.py --scenario full
```

## 📋 工作流和阶段说明

### 工作流1: `generate-game-contents` (完整游戏生成)

| 阶段 | 名称 | 说明 | 输入 | 输出 |
|------|------|------|------|------|
| **stage1** | 游戏设计生成 | 根据用户创意生成游戏设计文档 | 用户文本输入 | `doc/game.md` |
| **stage2** | 素材清单生成 | 生成JSON格式的素材任务列表 | `doc/game.md` | `public/tasks.json` |
| **stage3** | 素材文档生成 | 生成素材使用说明 | `public/tasks.json` | `doc/assets.md` |
| **stage4** | 素材图像生成 | 批量生成游戏素材图像 | `public/tasks.json` | `public/assets/*.png` |
| **stage5** | TODO列表生成 | 生成实现步骤TODO列表 | `doc/game.md` + `doc/assets.md` | `../todos.json` |

### 工作流2: `generate-game-asset` (批量素材生成)

| 阶段 | 名称 | 说明 |
|------|------|------|
| **stage1** | 任务加载与过滤 | 从tasks.json读取并过滤需要生成的任务 |
| **stage2** | 依赖分析与分批 | 使用拓扑排序处理yield_from依赖 |
| **stage3** | 并发图像生成 | 异步并发调用API生成图像 |
| **stage4** | 图像后处理 | 背景移除、图像缩放、保存原图 |
| **stage5** | 元数据更新 | 更新tasks.json中的实际尺寸信息 |

### 工作流3: `add-game-asset` (单个素材添加)

| 阶段 | 名称 | 说明 |
|------|------|------|
| **stage1** | 素材元数据生成 | 使用LLM生成素材的完整元数据 |
| **stage2** | 任务添加 | 将新素材添加到tasks.json |
| **stage3** | 图像生成 | 生成单个素材图像 |
| **stage4** | 文档更新 | 追加素材说明到assets.md |

## 🔍 验证规则

每个阶段都有详细的验证规则，包括：

### 文件验证
- ✅ `file_exists` - 文件是否存在
- ✅ `file_not_empty` - 文件非空
- ✅ `min_size` - 文件最小大小

### JSON验证
- ✅ `valid_json` - JSON格式正确
- ✅ `is_array` - 是数组格式
- ✅ `array_not_empty` - 数组非空
- ✅ `items_have_fields` - 数组元素包含必填字段
- ✅ `size_format_valid` - 尺寸格式正确（如 1024x1024）

### 内容验证
- ✅ `contains_keywords` - 包含关键词
- ✅ `asset_count_matches` - 素材数量匹配

### 图像验证
- ✅ `directory_exists` - 目录存在
- ✅ `image_count_matches` - 图像数量匹配
- ✅ `images_valid` - 图像格式正确
- ✅ `images_size_correct` - 图像尺寸正确（允许容差）
- ✅ `originals_saved` - 原图已保存

## 📊 测试输出示例

```
============================================================
开始阶段: generate-game-contents -> stage1
============================================================
📥 准备输入...
⚙️  执行: text_generation_function.generate_game_design...
✓ 函数执行完成
✓ 输出已保存: /path/to/workspace/doc/game.md
🔍 验证输出...
  ✓ file_exists 验证通过
  ✓ file_not_empty 验证通过
  ✓ contains_keywords 验证通过
  ✓ min_size 验证通过
✅ 阶段完成: stage1 (15.32s)

============================================================
测试总结
============================================================
✅ stage1: 游戏设计生成 (15.32s)
✅ stage2: 素材清单生成 (12.45s)
✅ stage3: 素材文档生成 (10.23s)

总计: 3 个阶段
成功: 3 个
失败: 0 个
成功率: 100.0%

💾 工作空间保留: tests/temp_workspace/generate-game-contents_20260107_153045
```

## ⚙️ 配置说明

### 全局配置 (`stage_test_config.yaml`)

```yaml
global:
  workspace_base: "tests/temp_workspace"  # 测试工作空间基础路径
  cleanup_after_test: false               # 测试后是否清理（建议false便于调试）
  stop_on_error: true                     # 某阶段失败是否停止
  verbose: true                           # 详细输出
```

### Mock配置

```yaml
mock:
  enabled: true                           # 启用Mock（避免调用真实API）
  llm_responses: "tests/fixtures/mock_responses/"
  api_delay: 0.5                          # 模拟API延迟
```

## 🎯 使用场景

### 场景1: 调试某个阶段的问题

```bash
# 假设stage3出现问题，单独测试这个阶段
python test_stage_runner.py --workflow generate-game-contents --stage stage3 -v

# 检查输出文件
cat tests/temp_workspace/generate-game-contents_*/doc/assets.md
```

### 场景2: 验证前3个阶段的逻辑（跳过耗时的图像生成）

```bash
python test_stage_runner.py --workflow generate-game-contents --stage stage1,stage2,stage3
```

### 场景3: 只测试图像生成管道

```bash
# 先手动准备好 tasks.json，然后测试stage4
cp tests/fixtures/sample_tasks.json tests/temp_workspace/test_dir/public/
python test_stage_runner.py --workflow generate-game-contents --stage stage4
```

### 场景4: 测试依赖关系处理

```bash
# 只测试 generate-game-asset 的前2个阶段（任务加载和依赖分析）
python test_stage_runner.py --workflow generate-game-asset --stage stage1,stage2
```

## 🐛 调试技巧

### 1. 保留工作空间

```yaml
# 在 stage_test_config.yaml 中设置
global:
  cleanup_after_test: false
```

测试后可以手动检查生成的文件：
```bash
ls -la tests/temp_workspace/generate-game-contents_*/
```

### 2. 查看详细日志

```bash
python test_stage_runner.py --workflow generate-game-contents --verbose
```

### 3. 单独验证某个输出

```python
from stage_validators import get_validator

validator = get_validator("tests/temp_workspace/your_test_dir")
result = validator.validate_valid_json("public/tasks.json")
print(f"JSON有效: {result}")
```

### 4. 查看阶段配置

```bash
# 查看某个阶段的详细配置
cat stage_test_config.yaml | grep -A 20 "stage2:"
```

## 📝 添加新的验证规则

在 `stage_validators.py` 中添加新方法：

```python
def validate_custom_check(self, file_path: str, param: Any) -> bool:
    """自定义验证逻辑"""
    try:
        # 你的验证代码
        return True
    except:
        return False
```

在 `stage_test_config.yaml` 中使用：

```yaml
validation:
  - check: "custom_check"
    param: "some_value"
    message: "自定义验证失败"
```

## ❓ 常见问题

### Q1: 测试时会调用真实API吗？

A: 默认不会，配置中 `mock.enabled: true` 表示使用Mock模式。如果要测试真实API，使用 `--no-mock` 参数（谨慎使用，会产生费用）。

### Q2: 测试失败后如何查看详细错误？

A: 使用 `--verbose` 参数查看完整堆栈跟踪，同时检查保留的工作空间中的文件。

### Q3: 可以跳过某些验证吗？

A: 可以，在配置文件中设置 `can_skip: true`，或者注释掉不需要的验证规则。

### Q4: 如何添加自己的测试场景？

A: 在 `stage_test_config.yaml` 的 `test_scenarios` 部分添加：

```yaml
test_scenarios:
  my_scenario:
    workflows: ["generate-game-contents"]
    stages: ["stage1", "stage2"]
    mock: true
```

然后运行：
```bash
python test_stage_runner.py --scenario my_scenario
```

## 🔗 相关文件

- `mcp_server.py` - MCP工具主文件
- `image_generation_function.py` - 图像生成模块
- `image_generation_function_async.py` - 异步并发图像生成
- `text_generation_function.py` - LLM调用函数

## 📄 许可

与主项目保持一致

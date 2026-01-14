# MCP工具分阶段测试系统

## 📁 目录结构

```
test/
├── config/                          # 配置文件
│   ├── stage_test_config.yaml      # 阶段测试配置（所有工作流和阶段定义）
│   ├── test_config.yaml            # 通用测试配置
│   └── pytest.ini                  # Pytest设置
├── scripts/                         # 测试脚本
│   ├── test_stage_runner.py        # 主测试运行器
│   ├── stage_validators.py         # 验证器模块
│   └── demo_stage_test.sh          # 演示脚本
├── docs/                            # 文档
│   ├── README_STAGE_TEST.md        # 完整文档
│   ├── QUICKSTART.md               # 快速入门
│   └── IMPLEMENTATION_SUMMARY.md   # 实现总结
├── fixtures/                        # 测试夹具
│   ├── sample_user_input.txt       # 示例输入
│   └── sample_tasks.json           # 示例任务
└── temp_workspace/                  # 测试工作空间（自动创建）
```

## 🚀 快速开始

### 方式1: 使用相对路径（推荐）

```bash
# 在项目根目录运行
cd /path/to/game-helper-python

# 测试单个阶段
python test/scripts/test_stage_runner.py -w generate-game-contents -s stage1

# 测试多个阶段
python test/scripts/test_stage_runner.py -w generate-game-contents -s stage1,stage2,stage3

# 运行演示
./test/scripts/demo_stage_test.sh
```

### 方式2: 从test目录运行

```bash
cd test/scripts

# 测试（使用默认配置路径）
python test_stage_runner.py -w generate-game-contents -s stage1

# 指定配置文件
python test_stage_runner.py -w generate-game-contents -s stage1 -c ../config/stage_test_config.yaml
```

## 📚 文档

- **快速入门**: [docs/QUICKSTART.md](docs/QUICKSTART.md)
- **工作空间复用指南**: [docs/WORKSPACE_GUIDE.md](docs/WORKSPACE_GUIDE.md) 🆕
- **完整文档**: [docs/README_STAGE_TEST.md](docs/README_STAGE_TEST.md)
- **实现总结**: [docs/IMPLEMENTATION_SUMMARY.md](docs/IMPLEMENTATION_SUMMARY.md)

## 🎯 常用命令

### 基础测试

```bash
# 从项目根目录运行（推荐）
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage1
python3 test/scripts/test_stage_runner.py -w generate-game-contents --from-stage stage2
python3 test/scripts/test_stage_runner.py --scenario quick

# 运行演示
./test/scripts/demo_stage_test.sh

# 查看帮助
python3 test/scripts/test_stage_runner.py --help
```

### 🆕 工作空间复用（分阶段测试）

```bash
# 步骤1: 生成 game.md
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage1 --workspace my_test

# 步骤2: 生成 tasks.json（复用同一工作空间）
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage2 --workspace my_test

# 步骤3: 生成 assets.md
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage3 --workspace my_test

# 步骤4: 生成图像
python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage4 --workspace my_test

# 运行工作空间演示脚本
./test/scripts/demo_workspace_test.sh
```

详细说明请查看: [docs/WORKSPACE_GUIDE.md](docs/WORKSPACE_GUIDE.md)

## 📋 支持的工作流

1. **generate-game-contents** - 完整游戏生成（5个阶段）
2. **generate-game-asset** - 批量素材生成（5个阶段）
3. **add-game-asset** - 单个素材添加（4个阶段）

## 🔧 配置文件

### 主配置文件
- `config/stage_test_config.yaml` - 所有工作流和阶段的定义

### 关键配置项

```yaml
global:
  workspace_base: "test/temp_workspace"   # 测试工作空间
  cleanup_after_test: false               # 是否清理测试文件
  stop_on_error: true                     # 错误时是否停止
```

## 📊 测试覆盖

- ✅ 3个工作流
- ✅ 14个阶段
- ✅ 20+ 种验证类型
- ✅ Mock API支持
- ✅ 工作空间复用（分阶段测试） 🆕

## 💡 提示

1. **首次使用**: 阅读 `docs/QUICKSTART.md`
2. **详细文档**: 阅读 `docs/README_STAGE_TEST.md`
3. **调试模式**: 使用 `-v` 参数查看详细日志
4. **保留工作空间**: 设置 `cleanup_after_test: false` 便于调试

## ❓ 遇到问题？

1. 确保在项目根目录运行命令
2. 检查Python路径是否正确
3. 查看 `docs/README_STAGE_TEST.md` 的常见问题部分
4. 使用 `-v` 参数查看详细错误信息

## 📞 帮助

```bash
python test/scripts/test_stage_runner.py --help
```

祝测试顺利！🎉

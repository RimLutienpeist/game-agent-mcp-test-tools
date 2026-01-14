#!/bin/bash
# 演示工作空间复用功能的测试脚本

set -e  # 遇到错误立即退出

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 工作空间名称
WORKSPACE_NAME="demo_test"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}分阶段测试演示（使用工作空间复用）${NC}"
echo -e "${BLUE}========================================${NC}\n"

# 进入项目根目录
cd "$(dirname "$0")/../.."

echo -e "${YELLOW}工作空间名称: ${WORKSPACE_NAME}${NC}\n"

# 步骤1: 生成 game.md
echo -e "${GREEN}[步骤 1/4] 生成游戏设计文档 (game.md)...${NC}"
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage1 \
  --workspace "$WORKSPACE_NAME"

echo -e "\n${BLUE}✓ game.md 已生成${NC}"
echo -e "位置: test/temp_workspace/$WORKSPACE_NAME/doc/game.md\n"
sleep 1

# 步骤2: 生成 tasks.json
echo -e "${GREEN}[步骤 2/4] 生成素材任务清单 (tasks.json)...${NC}"
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage2 \
  --workspace "$WORKSPACE_NAME"

echo -e "\n${BLUE}✓ tasks.json 已生成${NC}"
echo -e "位置: test/temp_workspace/$WORKSPACE_NAME/public/tasks.json\n"
sleep 1

# 步骤3: 生成 assets.md
echo -e "${GREEN}[步骤 3/4] 生成素材使用说明 (assets.md)...${NC}"
python3 test/scripts/test_stage_runner.py \
  -w generate-game-contents \
  -s stage3 \
  --workspace "$WORKSPACE_NAME"

echo -e "\n${BLUE}✓ assets.md 已生成${NC}"
echo -e "位置: test/temp_workspace/$WORKSPACE_NAME/doc/assets.md\n"
sleep 1

# 步骤4: 生成图像（可选，注释掉以节省时间）
echo -e "${YELLOW}[步骤 4/4] 跳过图像生成（耗时较长）${NC}"
echo -e "${YELLOW}如需测试图像生成，运行以下命令：${NC}"
echo -e "python3 test/scripts/test_stage_runner.py -w generate-game-contents -s stage4 --workspace $WORKSPACE_NAME\n"

# 显示工作空间内容
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}测试完成！工作空间内容：${NC}"
echo -e "${BLUE}========================================${NC}\n"

if command -v tree &> /dev/null; then
    tree -L 3 "test/temp_workspace/$WORKSPACE_NAME"
else
    find "test/temp_workspace/$WORKSPACE_NAME" -type f
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}查看生成的文件：${NC}"
echo -e "${GREEN}========================================${NC}\n"

echo -e "${YELLOW}1. 游戏设计文档：${NC}"
echo -e "   cat test/temp_workspace/$WORKSPACE_NAME/doc/game.md\n"

echo -e "${YELLOW}2. 素材任务清单：${NC}"
echo -e "   cat test/temp_workspace/$WORKSPACE_NAME/public/tasks.json\n"

echo -e "${YELLOW}3. 素材使用说明：${NC}"
echo -e "   cat test/temp_workspace/$WORKSPACE_NAME/doc/assets.md\n"

echo -e "${YELLOW}4. 清理工作空间：${NC}"
echo -e "   rm -rf test/temp_workspace/$WORKSPACE_NAME\n"

echo -e "${GREEN}测试成功完成！🎉${NC}"

#!/bin/bash
# 分阶段测试演示脚本

# 切换到项目根目录
cd "$(dirname "$0")/../.."

echo "========================================="
echo "MCP工具分阶段测试演示"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 显示帮助信息
echo -e "${BLUE}1. 显示帮助信息${NC}"
python test/scripts/test_stage_runner.py --help
echo ""
read -p "按Enter继续..."
echo ""

# 2. 测试单个阶段
echo -e "${BLUE}2. 测试单个阶段 (stage1: 游戏设计生成)${NC}"
echo "命令: python test/scripts/test_stage_runner.py --workflow generate-game-contents --stage stage1"
python test/scripts/test_stage_runner.py --workflow generate-game-contents --stage stage1
echo ""
read -p "按Enter继续..."
echo ""

# 3. 测试多个阶段
echo -e "${BLUE}3. 测试多个阶段 (stage1, stage2, stage3)${NC}"
echo "命令: python test/scripts/test_stage_runner.py --workflow generate-game-contents --stage stage1,stage2,stage3"
python test/scripts/test_stage_runner.py --workflow generate-game-contents --stage stage1,stage2,stage3
echo ""
read -p "按Enter继续..."
echo ""

# 4. 查看生成的文件
echo -e "${BLUE}4. 查看生成的文件${NC}"
LATEST_WORKSPACE=$(ls -td tests/temp_workspace/generate-game-contents_* 2>/dev/null | head -1)
if [ -n "$LATEST_WORKSPACE" ]; then
    echo "工作空间: $LATEST_WORKSPACE"
    echo ""
    echo "目录结构:"
    tree -L 3 "$LATEST_WORKSPACE" 2>/dev/null || find "$LATEST_WORKSPACE" -maxdepth 3 -print
    echo ""

    if [ -f "$LATEST_WORKSPACE/doc/game.md" ]; then
        echo -e "${GREEN}✓ game.md 已生成${NC}"
        echo "前10行预览:"
        head -10 "$LATEST_WORKSPACE/doc/game.md"
    fi
    echo ""

    if [ -f "$LATEST_WORKSPACE/public/tasks.json" ]; then
        echo -e "${GREEN}✓ tasks.json 已生成${NC}"
        echo "内容预览:"
        cat "$LATEST_WORKSPACE/public/tasks.json" | python -m json.tool 2>/dev/null || cat "$LATEST_WORKSPACE/public/tasks.json"
    fi
else
    echo -e "${YELLOW}未找到工作空间，请先运行测试${NC}"
fi
echo ""

echo -e "${GREEN}演示完成！${NC}"
echo ""
echo "更多用法:"
echo "  - 测试完整工作流: python test/scripts/test_stage_runner.py --workflow generate-game-contents"
echo "  - 从stage2开始测试: python test/scripts/test_stage_runner.py --workflow generate-game-contents --from-stage stage2"
echo "  - 使用快速场景: python test/scripts/test_stage_runner.py --scenario quick"
echo "  - 详细模式: python test/scripts/test_stage_runner.py --workflow generate-game-contents --verbose"
echo ""
echo "查看完整文档: cat test/docs/README_STAGE_TEST.md"

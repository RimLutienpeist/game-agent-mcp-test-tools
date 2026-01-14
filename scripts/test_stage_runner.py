#!/usr/bin/env python3
"""
分阶段测试运行器
Stage-by-Stage Test Runner

用法示例:
  # 测试完整工作流
  python test_stage_runner.py --workflow generate-game-contents

  # 只测试单个阶段
  python test_stage_runner.py --workflow generate-game-contents --stage stage1

  # 测试多个阶段
  python test_stage_runner.py --workflow generate-game-contents --stage stage1,stage2,stage3

  # 从某个阶段开始测试到结束
  python test_stage_runner.py --workflow generate-game-contents --from-stage stage2

  # 使用预设场景
  python test_stage_runner.py --scenario quick

  # 使用真实API（谨慎！）
  python test_stage_runner.py --workflow generate-game-contents --no-mock
"""

import os
import sys
import json
import yaml
import argparse
import logging
import shutil
import asyncio
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import importlib.util

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


class StageTestRunner:
    """分阶段测试运行器"""

    def __init__(self, config_path: str = None, user_input: str = None):
        """初始化测试运行器

        Args:
            config_path: 配置文件路径
            user_input: 自定义用户输入（用于 stage1）
        """
        # 默认配置文件路径（相对于脚本所在目录）
        if config_path is None:
            script_dir = Path(__file__).parent.parent
            config_path = script_dir / "config" / "stage_test_config.yaml"
        self.config_path = str(config_path)
        self.config = self._load_config()
        self.workspace_dir = None
        self.results = []
        self.current_workflow = None
        self.context = {}  # 存储阶段间传递的数据
        self.user_input = user_input  # 自定义用户输入

    def _load_config(self) -> Dict:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.info(f"✓ 已加载配置文件: {self.config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"✗ 配置文件不存在: {self.config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"✗ 配置文件格式错误: {e}")
            sys.exit(1)

    def _setup_workspace(self, workflow_name: str, custom_workspace: str = None) -> str:
        """创建测试工作空间

        Args:
            workflow_name: 工作流名称
            custom_workspace: 自定义工作空间名称（可选）

        Returns:
            工作空间路径
        """
        base_dir = Path(self.config['global']['workspace_base'])

        if custom_workspace:
            # 使用自定义工作空间名称
            workspace = base_dir / custom_workspace
            if workspace.exists():
                logger.info(f"✓ 使用已存在的工作空间: {workspace}")
            else:
                logger.info(f"✓ 创建新的工作空间: {workspace}")
        else:
            # 使用默认的带时间戳的工作空间
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            workspace = base_dir / f"{workflow_name}_{timestamp}"
            logger.info(f"✓ 创建新的工作空间: {workspace}")

        # 创建必要的目录
        workspace.mkdir(parents=True, exist_ok=True)
        (workspace / "doc").mkdir(exist_ok=True)
        (workspace / "public").mkdir(exist_ok=True)
        (workspace / "public" / "assets").mkdir(exist_ok=True)

        return str(workspace)

    def _cleanup_workspace(self):
        """清理测试工作空间"""
        if self.workspace_dir and self.config['global'].get('cleanup_after_test', False):
            try:
                shutil.rmtree(self.workspace_dir)
                logger.info(f"✓ 工作空间已清理: {self.workspace_dir}")
            except Exception as e:
                logger.warning(f"⚠ 清理工作空间失败: {e}")

    def _import_function(self, function_path: str):
        """动态导入函数"""
        try:
            # 解析函数路径，例如 "text_generation_function.generate_game_design"
            if '.' in function_path:
                module_name, func_name = function_path.rsplit('.', 1)
            else:
                # 如果是内部函数，从 mcp_server 导入
                module_name = "mcp_server"
                func_name = function_path

            # 导入模块
            module = importlib.import_module(module_name)
            func = getattr(module, func_name)
            return func
        except (ImportError, AttributeError) as e:
            logger.error(f"✗ 无法导入函数 {function_path}: {e}")
            return None

    def _prepare_input(self, stage_config: Dict, workflow_name: str) -> Any:
        """准备阶段输入"""
        input_config = stage_config.get('input', {})
        input_type = input_config.get('type')

        if input_type == 'text':
            # 从命令行、配置或fixture读取文本输入
            source = input_config.get('source')
            if source == 'user_input':
                # 优先使用命令行提供的用户输入
                if self.user_input:
                    logger.info(f"使用自定义用户输入: {self.user_input[:50]}...")
                    return self.user_input
                # 否则使用配置文件中的示例
                example = input_config.get('example', "测试游戏")
                logger.info(f"使用示例输入: {example[:50]}...")
                return example
            else:
                # 从context读取
                return self.context.get(source)

        elif input_type == 'file':
            # 读取文件内容
            file_path = Path(self.workspace_dir) / input_config.get('source')
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning(f"⚠ 输入文件不存在: {file_path}")
                return None

        elif input_type == 'files':
            # 读取多个文件
            contents = {}
            for source in input_config.get('sources', []):
                file_path = Path(self.workspace_dir) / source
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        contents[source] = f.read()
            return contents

        elif input_type == 'directory':
            # 返回目录路径
            return self.workspace_dir

        elif input_type == 'memory':
            # 从context读取内存数据
            source = input_config.get('source')
            return self.context.get(source)

        return None

    def _validate_output(self, stage_config: Dict, stage_name: str) -> bool:
        """验证阶段输出"""
        output_config = stage_config.get('output', {})
        validations = output_config.get('validation', [])

        all_passed = True

        for validation in validations:
            check_type = validation.get('check')
            result = self._run_validation_check(check_type, validation, output_config)

            if not result:
                all_passed = False
                message = validation.get('message', f'{check_type} 验证失败')
                logger.error(f"  ✗ {message}")
            else:
                logger.info(f"  ✓ {check_type} 验证通过")

        # 验证通过后，输出统计信息
        if all_passed:
            self._print_stats(stage_config, stage_name)

        return all_passed

    def _run_validation_check(self, check_type: str, validation: Dict, output_config: Dict) -> bool:
        """运行单个验证检查"""
        try:
            if check_type == 'file_exists':
                file_path = Path(self.workspace_dir) / output_config.get('path')
                return file_path.exists()

            elif check_type == 'file_not_empty':
                file_path = Path(self.workspace_dir) / output_config.get('path')
                return file_path.exists() and file_path.stat().st_size > 0

            elif check_type == 'valid_json':
                files = validation.get('files', [output_config.get('path')])
                for file_rel_path in files:
                    file_path = Path(self.workspace_dir) / file_rel_path
                    if not file_path.exists():
                        return False
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            json.load(f)
                    except json.JSONDecodeError:
                        return False
                return True

            elif check_type == 'is_array':
                file_path = Path(self.workspace_dir) / output_config.get('path')
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return isinstance(data, list)

            elif check_type == 'array_not_empty':
                file_path = Path(self.workspace_dir) / output_config.get('path')
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return isinstance(data, list) and len(data) > 0

            elif check_type == 'items_have_fields':
                file_path = Path(self.workspace_dir) / output_config.get('path')
                required_fields = validation.get('required_fields', [])
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if not isinstance(data, list):
                    return False
                for item in data:
                    if not all(field in item for field in required_fields):
                        return False
                return True

            elif check_type == 'contains_keywords':
                file_path = Path(self.workspace_dir) / output_config.get('path')
                keywords = validation.get('keywords', [])
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return any(keyword in content for keyword in keywords)

            elif check_type == 'min_size':
                file_path = Path(self.workspace_dir) / output_config.get('path')
                min_size = validation.get('value', 0)
                return file_path.stat().st_size >= min_size

            elif check_type == 'directory_exists':
                dir_path = Path(self.workspace_dir) / output_config.get('path')
                return dir_path.exists() and dir_path.is_dir()

            elif check_type == 'image_count_matches':
                assets_dir = Path(self.workspace_dir) / output_config.get('path')
                tasks_file = Path(self.workspace_dir) / validation.get('reference')

                if not tasks_file.exists():
                    return False

                with open(tasks_file, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)

                expected_count = len(tasks) if isinstance(tasks, list) else 0
                actual_count = len(list(assets_dir.glob('*.png')))

                # 排除 _originals 目录
                actual_count -= len(list((assets_dir / '_originals').glob('*.png'))) if (assets_dir / '_originals').exists() else 0

                return actual_count == expected_count

            elif check_type == 'size_format_valid':
                file_path = Path(self.workspace_dir) / output_config.get('path')
                pattern = validation.get('pattern')
                import re
                with open(file_path, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
                for task in tasks:
                    size = task.get('size', '')
                    if not re.match(pattern, size):
                        return False
                return True

            # 其他验证类型可以继续添加...
            else:
                logger.warning(f"⚠ 未知的验证类型: {check_type}")
                return True  # 未知的验证默认通过

        except Exception as e:
            logger.error(f"  ✗ 验证检查异常 ({check_type}): {e}")
            return False

    def _print_stats(self, stage_config: Dict, stage_name: str):
        """打印阶段统计信息"""
        try:
            from stage_validators import StageValidator
            validator = StageValidator(self.workspace_dir)

            output_config = stage_config.get('output', {})
            output_type = output_config.get('type')

            logger.info(f"\n📊 统计信息:")

            if output_type == 'file':
                file_path = output_config.get('path')
                file_format = output_config.get('format', '')

                # Markdown 文件统计
                if file_format == 'markdown':
                    stats = validator.get_file_stats(file_path)
                    if stats:
                        logger.info(f"  - 文件大小: {stats['file_size_bytes']} 字节 ({stats['file_size_kb']} KB)")
                        logger.info(f"  - 字符数: {stats['char_count']}")
                        logger.info(f"  - 行数: {stats['line_count']}")

                # JSON 文件统计
                elif file_format == 'json':
                    stats = validator.get_json_stats(file_path)
                    if stats:
                        logger.info(f"  - 文件大小: {stats['file_size_bytes']} 字节 ({stats['file_size_kb']} KB)")
                        if 'item_count' in stats:
                            logger.info(f"  - 图像任务数: {stats['item_count']}")

            # 图像目录统计
            elif output_type == 'directory':
                assets_dir = output_config.get('path')
                # 查找 validation 中的 reference 文件
                validations = output_config.get('validation', [])
                reference_file = None
                for v in validations:
                    if v.get('check') == 'image_count_matches':
                        reference_file = v.get('reference')
                        break

                stats = validator.get_image_stats(assets_dir, reference_file)
                if stats:
                    logger.info(f"  - 成功生成图像: {stats['generated_count']}")
                    if 'success_rate' in stats:
                        logger.info(f"  - 生成进度: {stats['success_rate']}")
                    logger.info(f"  - 总大小: {stats['total_size_kb']} KB ({stats['total_size_mb']} MB)")

        except Exception as e:
            # 统计信息打印失败不影响测试结果
            logger.debug(f"统计信息打印失败: {e}")

    def run_stage(self, workflow_name: str, stage_name: str) -> Dict:
        """运行单个阶段"""
        logger.info(f"\n{'='*60}")
        logger.info(f"开始阶段: {workflow_name} -> {stage_name}")
        logger.info(f"{'='*60}")

        workflow_config = self.config['workflows'].get(workflow_name)
        if not workflow_config:
            logger.error(f"✗ 未找到工作流: {workflow_name}")
            return {"success": False, "error": "工作流不存在"}

        stage_config = workflow_config['stages'].get(stage_name)
        if not stage_config:
            logger.error(f"✗ 未找到阶段: {stage_name}")
            return {"success": False, "error": "阶段不存在"}

        stage_result = {
            "stage": stage_name,
            "name": stage_config.get('name'),
            "start_time": datetime.now(),
            "success": False,
            "error": None
        }

        try:
            # 1. 准备输入
            logger.info(f"📥 准备输入...")
            input_data = self._prepare_input(stage_config, workflow_name)

            # 2. 执行函数
            logger.info(f"⚙️  执行: {stage_config.get('function')}...")
            func = self._import_function(stage_config.get('function'))

            if not func:
                stage_result['error'] = "函数导入失败"
                return stage_result

            # 根据函数类型调用
            # 这里需要根据实际函数签名调整
            if stage_config.get('function') == '_generate_game_asset_internal':
                result = func(self.workspace_dir)
            elif stage_config.get('function') in ['text_generation_function.generate_game_design',
                                                    'text_generation_function.generate_assets_json',
                                                    'text_generation_function.generate_assets_doc']:
                # 检查函数是否是协程函数
                if inspect.iscoroutinefunction(func):
                    result = asyncio.run(func(input_data))
                else:
                    result = func(input_data)
            else:
                # 通用调用
                if inspect.iscoroutinefunction(func):
                    result = asyncio.run(func(input_data))
                else:
                    result = func(input_data)

            logger.info(f"✓ 函数执行完成")

            # 3. 保存输出
            output_config = stage_config.get('output', {})
            if output_config.get('type') == 'file':
                output_path = Path(self.workspace_dir) / output_config.get('path')
                output_path.parent.mkdir(parents=True, exist_ok=True)

                # 如果结果是ToolResult格式
                if isinstance(result, dict) and 'content' in result:
                    content = result['content'][0]['text']
                else:
                    content = result

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logger.info(f"✓ 输出已保存: {output_path}")

            elif output_config.get('type') == 'files':
                for path in output_config.get('paths', []):
                    # 这里需要根据实际情况处理多文件输出
                    pass

            elif output_config.get('type') == 'memory':
                # 保存到context供后续阶段使用
                var_name = output_config.get('variable')
                self.context[var_name] = result
                logger.info(f"✓ 结果已保存到内存: {var_name}")

            # 4. 验证输出
            logger.info(f"🔍 验证输出...")
            validation_passed = self._validate_output(stage_config, stage_name)

            stage_result['success'] = validation_passed
            stage_result['end_time'] = datetime.now()
            stage_result['duration'] = (stage_result['end_time'] - stage_result['start_time']).total_seconds()

            if validation_passed:
                logger.info(f"✅ 阶段完成: {stage_name} ({stage_result['duration']:.2f}s)")
            else:
                logger.error(f"❌ 阶段失败: {stage_name}")

        except Exception as e:
            import traceback
            stage_result['error'] = str(e)
            stage_result['traceback'] = traceback.format_exc()
            stage_result['end_time'] = datetime.now()
            logger.error(f"❌ 阶段异常: {e}")
            logger.debug(traceback.format_exc())

        return stage_result

    def run_workflow(self, workflow_name: str, stages: Optional[List[str]] = None,
                     from_stage: Optional[str] = None, workspace: Optional[str] = None) -> List[Dict]:
        """运行完整工作流或指定阶段

        Args:
            workflow_name: 工作流名称
            stages: 要运行的阶段列表
            from_stage: 起始阶段
            workspace: 自定义工作空间名称（可选）

        Returns:
            测试结果列表
        """
        logger.info(f"\n{'#'*60}")
        logger.info(f"# 开始测试工作流: {workflow_name}")
        logger.info(f"{'#'*60}\n")

        # 设置工作空间
        self.workspace_dir = self._setup_workspace(workflow_name, custom_workspace=workspace)
        self.current_workflow = workflow_name

        workflow_config = self.config['workflows'].get(workflow_name)
        if not workflow_config:
            logger.error(f"✗ 工作流不存在: {workflow_name}")
            return []

        # 确定要运行的阶段
        all_stages = list(workflow_config['stages'].keys())

        if stages:
            # 用户指定了阶段列表
            stages_to_run = stages
        elif from_stage:
            # 从指定阶段开始运行到结束
            if from_stage in all_stages:
                start_idx = all_stages.index(from_stage)
                stages_to_run = all_stages[start_idx:]
            else:
                logger.error(f"✗ 起始阶段不存在: {from_stage}")
                return []
        else:
            # 运行所有阶段
            stages_to_run = all_stages

        logger.info(f"将运行以下阶段: {', '.join(stages_to_run)}\n")

        # 逐个运行阶段
        results = []
        for stage_name in stages_to_run:
            result = self.run_stage(workflow_name, stage_name)
            results.append(result)

            # 如果阶段失败且配置了停止，则中断
            if not result['success'] and self.config['global'].get('stop_on_error', True):
                logger.warning(f"⚠ 阶段失败，停止后续阶段")
                break

        # 打印总结
        self._print_summary(results)

        # 清理工作空间（可选）
        if not self.config['global'].get('cleanup_after_test', False):
            logger.info(f"\n💾 工作空间保留: {self.workspace_dir}")

        return results

    def _print_summary(self, results: List[Dict]):
        """打印测试总结"""
        logger.info(f"\n{'='*60}")
        logger.info(f"测试总结")
        logger.info(f"{'='*60}")

        total = len(results)
        success = sum(1 for r in results if r['success'])
        failed = total - success

        for result in results:
            status = "✅" if result['success'] else "❌"
            duration = result.get('duration', 0)
            logger.info(f"{status} {result['stage']}: {result['name']} ({duration:.2f}s)")
            if result.get('error'):
                logger.info(f"   错误: {result['error']}")

        logger.info(f"\n总计: {total} 个阶段")
        logger.info(f"成功: {success} 个")
        logger.info(f"失败: {failed} 个")
        logger.info(f"成功率: {success/total*100:.1f}%")

    def run_scenario(self, scenario_name: str):
        """运行预设测试场景"""
        logger.info(f"\n🎬 运行测试场景: {scenario_name}")

        scenario_config = self.config['test_scenarios'].get(scenario_name)
        if not scenario_config:
            logger.error(f"✗ 场景不存在: {scenario_name}")
            return

        workflows = scenario_config.get('workflows', [])
        stages = scenario_config.get('stages')

        for workflow in workflows:
            if stages == 'all':
                self.run_workflow(workflow)
            else:
                self.run_workflow(workflow, stages=stages)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='MCP工具分阶段测试运行器')

    parser.add_argument('--workflow', '-w', type=str,
                        help='要测试的工作流名称 (generate-game-contents, generate-game-asset, add-game-asset)')
    parser.add_argument('--stage', '-s', type=str,
                        help='要测试的阶段，多个阶段用逗号分隔 (例如: stage1,stage2)')
    parser.add_argument('--from-stage', '-f', type=str,
                        help='从指定阶段开始测试到结束')
    parser.add_argument('--workspace', type=str, default=None,
                        help='指定工作空间名称（用于复用已有工作空间，例如: my_test）')
    parser.add_argument('--user-input', '-u', type=str, default=None,
                        help='自定义用户输入（用于 stage1 游戏创意）')
    parser.add_argument('--scenario', type=str,
                        help='使用预设测试场景 (quick, full, real_api)')
    parser.add_argument('--config', '-c', type=str, default=None,
                        help='配置文件路径（默认: test/config/stage_test_config.yaml）')
    parser.add_argument('--no-mock', action='store_true',
                        help='使用真实API（谨慎使用！）')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='详细输出')

    args = parser.parse_args()

    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # 创建运行器
    runner = StageTestRunner(config_path=args.config, user_input=args.user_input)

    # 运行测试
    if args.scenario:
        runner.run_scenario(args.scenario)
    elif args.workflow:
        stages = args.stage.split(',') if args.stage else None
        runner.run_workflow(args.workflow, stages=stages, from_stage=args.from_stage, workspace=args.workspace)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()

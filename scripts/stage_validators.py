"""
阶段验证器模块
Stage Validators Module

提供各种验证检查函数，用于验证每个阶段的输出
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List
from PIL import Image


class StageValidator:
    """阶段验证器基类"""

    def __init__(self, workspace_dir: str):
        self.workspace_dir = Path(workspace_dir)

    def validate_file_exists(self, file_path: str) -> bool:
        """验证文件是否存在"""
        full_path = self.workspace_dir / file_path
        return full_path.exists()

    def validate_file_not_empty(self, file_path: str) -> bool:
        """验证文件非空"""
        full_path = self.workspace_dir / file_path
        return full_path.exists() and full_path.stat().st_size > 0

    def get_file_stats(self, file_path: str) -> Dict[str, Any]:
        """获取文件统计信息（大小、字符数等）"""
        try:
            full_path = self.workspace_dir / file_path
            if not full_path.exists():
                return {}

            file_size = full_path.stat().st_size

            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
                char_count = len(content)
                line_count = content.count('\n') + 1

            return {
                'file_size_bytes': file_size,
                'file_size_kb': round(file_size / 1024, 2),
                'char_count': char_count,
                'line_count': line_count
            }
        except:
            return {}

    def validate_valid_json(self, file_path: str) -> bool:
        """验证JSON格式"""
        try:
            full_path = self.workspace_dir / file_path
            with open(full_path, 'r', encoding='utf-8') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, FileNotFoundError):
            return False

    def get_json_stats(self, file_path: str) -> Dict[str, Any]:
        """获取JSON文件统计信息（项目数量等）"""
        try:
            full_path = self.workspace_dir / file_path
            if not full_path.exists():
                return {}

            file_size = full_path.stat().st_size

            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            stats = {
                'file_size_bytes': file_size,
                'file_size_kb': round(file_size / 1024, 2),
            }

            if isinstance(data, list):
                stats['item_count'] = len(data)
                # 如果是图像任务列表，统计图像信息
                if data and isinstance(data[0], dict) and 'name' in data[0]:
                    stats['image_tasks'] = len(data)
            elif isinstance(data, dict):
                stats['key_count'] = len(data.keys())

            return stats
        except:
            return {}

    def validate_is_array(self, file_path: str) -> bool:
        """验证JSON是数组"""
        try:
            full_path = self.workspace_dir / file_path
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return isinstance(data, list)
        except:
            return False

    def validate_array_not_empty(self, file_path: str) -> bool:
        """验证数组非空"""
        try:
            full_path = self.workspace_dir / file_path
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return isinstance(data, list) and len(data) > 0
        except:
            return False

    def validate_items_have_fields(self, file_path: str, required_fields: List[str]) -> bool:
        """验证数组中的每个元素都包含必填字段"""
        try:
            full_path = self.workspace_dir / file_path
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, list):
                return False

            for item in data:
                if not all(field in item for field in required_fields):
                    return False

            return True
        except:
            return False

    def validate_contains_keywords(self, file_path: str, keywords: List[str]) -> bool:
        """验证文件包含关键词"""
        try:
            full_path = self.workspace_dir / file_path
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return any(keyword in content for keyword in keywords)
        except:
            return False

    def validate_min_size(self, file_path: str, min_bytes: int) -> bool:
        """验证文件最小大小"""
        try:
            full_path = self.workspace_dir / file_path
            return full_path.stat().st_size >= min_bytes
        except:
            return False

    def validate_size_format(self, file_path: str, pattern: str = r'^\d+x\d+$') -> bool:
        """验证尺寸格式（如 1024x1024）"""
        try:
            full_path = self.workspace_dir / file_path
            with open(full_path, 'r', encoding='utf-8') as f:
                tasks = json.load(f)

            for task in tasks:
                size = task.get('size', '')
                if not re.match(pattern, size):
                    return False

            return True
        except:
            return False

    def validate_directory_exists(self, dir_path: str) -> bool:
        """验证目录存在"""
        full_path = self.workspace_dir / dir_path
        return full_path.exists() and full_path.is_dir()

    def validate_image_count_matches(self, assets_dir: str, reference_file: str) -> bool:
        """验证生成的图像数量与任务数匹配"""
        try:
            assets_path = self.workspace_dir / assets_dir
            tasks_path = self.workspace_dir / reference_file

            if not tasks_path.exists():
                return False

            with open(tasks_path, 'r', encoding='utf-8') as f:
                tasks = json.load(f)

            expected_count = len(tasks) if isinstance(tasks, list) else 0

            # 统计PNG文件数量（排除 _originals 目录）
            png_files = list(assets_path.glob('*.png'))
            originals_dir = assets_path / '_originals'
            if originals_dir.exists():
                originals_count = len(list(originals_dir.glob('*.png')))
            else:
                originals_count = 0

            actual_count = len(png_files) - originals_count

            return actual_count == expected_count

        except:
            return False

    def get_image_stats(self, assets_dir: str, reference_file: str = None) -> Dict[str, Any]:
        """获取图像生成统计信息"""
        try:
            assets_path = self.workspace_dir / assets_dir

            if not assets_path.exists():
                return {}

            # 统计PNG文件数量（排除 _originals 目录）
            png_files = [f for f in assets_path.glob('*.png') if '_originals' not in str(f)]
            actual_count = len(png_files)

            stats = {
                'generated_count': actual_count,
            }

            # 如果提供了参考文件，计算期望数量
            if reference_file:
                tasks_path = self.workspace_dir / reference_file
                if tasks_path.exists():
                    with open(tasks_path, 'r', encoding='utf-8') as f:
                        tasks = json.load(f)
                    expected_count = len(tasks) if isinstance(tasks, list) else 0
                    stats['expected_count'] = expected_count
                    stats['success_rate'] = f"{actual_count}/{expected_count}"

            # 统计总文件大小
            total_size = sum(f.stat().st_size for f in png_files)
            stats['total_size_kb'] = round(total_size / 1024, 2)
            stats['total_size_mb'] = round(total_size / (1024 * 1024), 2)

            return stats
        except:
            return {}

    def validate_images_valid(self, assets_dir: str, allowed_formats: List[str] = ['PNG']) -> bool:
        """验证所有图像文件格式正确"""
        try:
            assets_path = self.workspace_dir / assets_dir
            image_files = list(assets_path.glob('*.png'))

            for img_file in image_files:
                # 跳过 _originals 目录
                if '_originals' in str(img_file):
                    continue

                try:
                    with Image.open(img_file) as img:
                        if img.format not in allowed_formats:
                            return False
                except:
                    return False

            return len(image_files) > 0

        except:
            return False

    def validate_images_size_correct(self, assets_dir: str, reference_file: str, tolerance: int = 10) -> bool:
        """验证图像尺寸正确（允许容差）"""
        try:
            assets_path = self.workspace_dir / assets_dir
            tasks_path = self.workspace_dir / reference_file

            with open(tasks_path, 'r', encoding='utf-8') as f:
                tasks = json.load(f)

            for task in tasks:
                img_name = task.get('name')
                expected_size = task.get('size', '')

                if not expected_size or 'x' not in expected_size:
                    continue

                expected_w, expected_h = map(int, expected_size.split('x'))
                img_path = assets_path / img_name

                if not img_path.exists():
                    return False

                with Image.open(img_path) as img:
                    actual_w, actual_h = img.size

                    # 检查是否在容差范围内
                    if abs(actual_w - expected_w) > tolerance or abs(actual_h - expected_h) > tolerance:
                        return False

            return True

        except:
            return False

    def validate_originals_saved(self, originals_dir: str) -> bool:
        """验证原图已保存"""
        full_path = self.workspace_dir / originals_dir
        if not full_path.exists():
            return False

        # 检查是否有PNG文件
        png_files = list(full_path.glob('*.png'))
        return len(png_files) > 0

    def validate_asset_count_matches(self, assets_doc: str, reference_file: str) -> bool:
        """验证assets.md中的素材数量与tasks.json匹配"""
        try:
            doc_path = self.workspace_dir / assets_doc
            tasks_path = self.workspace_dir / reference_file

            with open(tasks_path, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
            expected_count = len(tasks)

            with open(doc_path, 'r', encoding='utf-8') as f:
                doc_content = f.read()

            # 统计 "####" 标题数量（每个素材一个四级标题）
            actual_count = doc_content.count('####')

            return actual_count >= expected_count

        except:
            return False

    def validate_todos_structure(self, todos_file: str) -> bool:
        """验证TODO文件结构"""
        try:
            full_path = self.workspace_dir / todos_file
            with open(full_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 支持两种格式: {todos: [...]} 或 [...]
            if isinstance(data, dict):
                return 'todos' in data and isinstance(data['todos'], list)
            elif isinstance(data, list):
                return True

            return False

        except:
            return False

    def validate_has_test_step(self, todos_file: str, keyword: str = 'playwright') -> bool:
        """验证TODO列表包含测试步骤"""
        try:
            full_path = self.workspace_dir / todos_file
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read().lower()

            return keyword.lower() in content

        except:
            return False


def get_validator(workspace_dir: str) -> StageValidator:
    """获取验证器实例"""
    return StageValidator(workspace_dir)

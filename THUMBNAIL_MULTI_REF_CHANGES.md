# Thumbnail 多图参考功能实现说明

## 概述

实现了让 Thumbnail 在最后生成，并支持使用多张已生成的代表性素材作为参考图进行图生图。

---

## 核心改动

### 1. **Prompt 改动** (`prompt.py`)

#### 变更点
- **位置调整**: Thumbnail 从第一个素材改为最后一个素材
- **引用方式**: 使用 `__MULTI__:` 格式支持多图参考

#### 新的 Thumbnail 规范

```json
{
  "name": "thumbnail.png",
  "description": "缩略图的详细描述...",
  "size": "1376×768",
  "yield_from": "__MULTI__:asset1.png,asset2.png,asset3.png",
  "is_background": true
}
```

**字段说明**:
- `yield_from`: 使用 `__MULTI__:` 前缀 + 逗号分隔的文件名
- LLM 会自动选择 3-5 个最具代表性的素材作为参考
- 这些素材将作为视觉参考传递给图像生成模型

---

### 2. **图像生成函数改动** (`image_generation_function_async.py`)

#### 改动位置: 第 680-773 行

添加了对 `__MULTI__:` 格式的解析和处理：

```python
if yield_from.startswith("__MULTI__:"):
    # 解析多个参考图
    ref_images_str = yield_from.replace("__MULTI__:", "")
    ref_image_names = [name.strip() for name in ref_images_str.split(",")]

    # 构建 parts 数组
    parts = [{"text": prompt}]
    for ref_name in ref_image_names:
        # 读取每张参考图并编码为 base64
        parts.append({
            "inline_data": {"mime_type": "image/png", "data": ref_image_b64}
        })

    # 调用 API
    gemini_data = {
        "contents": [{"parts": parts}],
        ...
    }
```

**特性**:
- ✅ 支持多张参考图（3-5 张推荐）
- ✅ 自动跳过不存在的文件
- ✅ 降级处理：如果所有参考图都不存在，使用纯文本生成
- ✅ 详细日志：显示实际使用的参考图数量和名称

---

### 3. **依赖分析改动** (`image_generation_function_async.py`)

#### 改动位置: 第 258-294 行

扩展了依赖关系分析，支持 `__MULTI__:` 格式：

```python
elif yield_from.startswith("__MULTI__:"):
    # 多图参考依赖
    ref_images_str = yield_from.replace("__MULTI__:", "")
    ref_image_names = [ref.strip() for ref in ref_images_str.split(",")]
    # 过滤出存在于任务列表中的依赖
    actual_dependencies = [ref for ref in ref_image_names if ref in all_names]
    dependencies[name] = actual_dependencies
```

**效果**:
- Thumbnail 会等待所有参考图生成完成后才开始生成
- 保证依赖关系的正确性
- 支持拓扑排序，避免循环依赖

---

## 使用示例

### 完整的 tasks.json 示例

```json
[
  {
    "name": "player.png",
    "description": "玩家角色...",
    "size": "64×64",
    "yield_from": null,
    "is_background": false
  },
  {
    "name": "enemy.png",
    "description": "敌人角色...",
    "size": "64×64",
    "yield_from": null,
    "is_background": false
  },
  {
    "name": "background.png",
    "description": "游戏背景...",
    "size": "1920×1080",
    "yield_from": null,
    "is_background": true
  },
  {
    "name": "thumbnail.png",
    "description": "展示玩家与敌人战斗的精彩瞬间，背景为游戏场景...",
    "size": "1376×768",
    "yield_from": "__MULTI__:player.png,enemy.png,background.png",
    "is_background": true
  }
]
```

---

## 执行流程

### 1. **LLM 生成阶段**

```
用户输入游戏创意
    ↓
调用 generate_assets_json()
    ↓
LLM 根据新的 ASSETS_JSON_PROMPT 生成素材列表
    ↓
【自动】将 thumbnail.png 放在最后一个
【自动】选择 3-5 个代表性素材填入 yield_from
    ↓
返回 tasks.json
```

### 2. **图像生成阶段**

```
读取 tasks.json
    ↓
依赖分析：检测到 thumbnail 依赖多个素材
    ↓
拓扑排序分批：
  - Batch 1: player.png, enemy.png, background.png (并发)
  - Batch 2: thumbnail.png (等待 Batch 1 完成)
    ↓
生成 Batch 1 (并发执行)
    ↓
生成 Batch 2: thumbnail.png
  ├─ 读取 player.png (base64)
  ├─ 读取 enemy.png (base64)
  ├─ 读取 background.png (base64)
  ├─ 构建 parts = [prompt, img1, img2, img3]
  └─ 调用 Gemini API 生成缩略图
    ↓
完成
```

---

## 日志示例

### 依赖分析日志

```
📊 根据依赖关系分为 2 批执行:
  批次 1: 3 个任务 (无依赖)
    - player.png
    - enemy.png
    - background.png
  批次 2: 1 个任务
    - thumbnail.png → 依赖 [player.png, enemy.png, background.png]
```

### 生成日志

```
[4/4] 🎨 正在生成: thumbnail.png
  多图参考 (3张): player.png, enemy.png, background.png
  API 调用中...
  ✓ API 响应完成 (8.2s)
  ✓ 图像已保存
  背景已移除 (处理了 0 个像素)
  ✅ 完成 (总耗时: 12.5s)
```

---

## 测试文件

已创建测试文件 `test_multi_ref.json`，包含完整示例：

```bash
# 测试命令（如果需要）
python image_generation_function_async.py
```

---

## 兼容性说明

### ✅ 完全向后兼容

- `yield_from: null` - 纯文本生成（不变）
- `yield_from: "asset.png"` - 单图参考（不变）
- `yield_from: "__MIRROR__:asset.png"` - 镜像翻转（不变）
- `yield_from: "__MULTI__:a.png,b.png,c.png"` - **新增** 多图参考

### 格式识别优先级

```python
if yield_from.startswith("__MIRROR__:"):
    # 镜像模式
elif yield_from.startswith("__MULTI__:"):
    # 多图模式（新增）
else:
    # 单图模式
```

---

## 注意事项

1. **参考图数量**: 建议 3-5 张，过多可能超出 API 限制
2. **文件存在性**: 代码会自动检查文件是否存在，跳过不存在的
3. **降级处理**: 如果所有参考图都不存在，自动使用纯文本生成
4. **依赖顺序**: Thumbnail 会自动排在最后一批生成
5. **assets.md**: Thumbnail 依然不会出现在素材文档中（保持原逻辑）

---

## 总结

### 改动文件
- ✅ `prompt.py` - 更新 Thumbnail 生成规范
- ✅ `image_generation_function_async.py` - 支持多图参考解析和生成（异步版本）
- ✅ `image_generation_function.py` - 支持多图参考解析和生成（同步版本，保持一致性）
- ✅ `test_multi_ref.json` - 测试示例文件
- ✅ `THUMBNAIL_MULTI_REF_CHANGES.md` - 本说明文档

### 核心优势
- 🎯 Thumbnail 基于实际生成的素材，风格一致性更强
- 🚀 自动依赖管理，无需手动排序
- 🔄 完全向后兼容，不影响现有功能
- 📊 详细日志，便于调试和监控

---

## 下一步

如需测试多图参考功能，可使用以下测试任务：

```bash
# 1. 将 test_multi_ref.json 作为测试任务
# 2. 观察依赖分析和批次划分
# 3. 检查 thumbnail.png 是否正确使用了 3 张参考图
```

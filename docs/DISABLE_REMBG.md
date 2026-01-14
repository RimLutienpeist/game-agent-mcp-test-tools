# 完全禁用 rembg 指南

## 问题说明

即使设置了 `AUTO_REMOVE_BACKGROUND=false`，代码在导入时仍会加载 rembg 库，导致：
1. ⚠️ onnxruntime 警告信息
2. ⚠️ 尝试下载模型（如果模型不存在）

## 解决方案

### 方案1: 临时卸载 rembg（推荐用于测试）

```bash
# 卸载 rembg
venv/bin/pip uninstall rembg -y

# 运行测试（现在不会加载 rembg）
AUTO_REMOVE_BACKGROUND=false ./run_stage_test.sh -w generate-game-contents -s stage4 --workspace my_test

# 测试完成后，如需重新安装
venv/bin/pip install "rembg[cpu,cli]==2.0.72"
```

### 方案2: 忽略 onnxruntime 警告

onnxruntime 的 GPU 警告是**无害的**，不影响功能。如果你设置了 `AUTO_REMOVE_BACKGROUND=false`，代码**不会真正执行抠图**，只是会有警告信息。

**验证方法：**查看日志中是否有这一行：

```
自动移除背景: 关闭
```

如果看到"关闭"，说明抠图功能已被禁用，警告可以忽略。

### 方案3: 重定向错误输出

```bash
# 隐藏 onnxruntime 警告
AUTO_REMOVE_BACKGROUND=false ./run_stage_test.sh -w generate-game-contents -s stage4 --workspace my_test 2>/dev/null
```

---

## 验证抠图是否被跳过

查看测试日志，应该看到：

```
✓ 自动移除背景: 关闭  ← 确认已禁用
✓ 生成图像: asset1.png
⚠ 跳过背景移除  ← 确认跳过了抠图
✓ 保存原图: _originals/asset1.png
```

如果看到以上日志，说明：
- ✅ 抠图功能已被禁用
- ✅ 不会执行 rembg 处理
- ✅ onnxruntime 警告可以忽略（只是导入时的警告）

---

## 总结

**推荐做法：**

1. **如果只是测试**：忽略 onnxruntime 警告，只要看到"自动移除背景: 关闭"就没问题
2. **如果想完全避免警告**：临时卸载 rembg
3. **如果需要安静的输出**：重定向 stderr

**关键点：**
- ⚠️ 警告不代表错误
- ✅ 设置 `AUTO_REMOVE_BACKGROUND=false` 后，不会执行抠图
- ✅ 即使导入了 rembg，也不会真正使用它

祝测试顺利！🎉

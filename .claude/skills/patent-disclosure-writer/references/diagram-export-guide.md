# 专利附图导出实现指南

本文档说明如何正确使用专利交底书技能的附图导出功能，避免临时创建脚本的问题。

## 问题背景

当用户使用 `/patent-update-diagrams export_png=true` 导出黑白附图时，系统应该：
1. 使用技能自带的验证过的脚本
2. 确保输出质量一致
3. 避免临时创建脚本导致的质量不可控

## 正确实现方式

### 方式 1: 调用 patent-diagram-exporter 代理（推荐）

```python
# 在命令实现中调用 patent-diagram-exporter 子代理
Task(
    subagent_type="patent-diagram-exporter",
    prompt=f"""
    导出专利附图为黑白 PNG：
    - 目录: {directory}
    - 模式: 0[3-7]_*.md
    - 输出目录: figures
    - 强制重新生成: {force_regenerate}
    """
)
```

### 方式 2: 直接调用 export_mermaid.py 脚本

```bash
python .claude/skills/patent-disclosure-writer/scripts/export_mermaid.py \
  --dir . \
  --pattern "0[3-7]_*.md" \
  --output-dir figures
```

## 脚本位置

所有必需文件都位于技能目录内：

```
.claude/skills/patent-disclosure-writer/
├── scripts/
│   └── export_mermaid.py           # 导出脚本
└── templates/
    ├── mermaid-bw-theme.json       # 黑白主题配置
    └── mermaid-bw-style.css        # 黑白样式覆盖
```

## 错误示例

### ❌ 错误：临时创建脚本

```python
# 不要这样做！
script_content = """
import subprocess
# 临时的导出代码...
"""
with open("temp_export.py", "w") as f:
    f.write(script_content)
subprocess.run(["python", "temp_export.py"])
```

**问题**：
- 代码未经验证
- 输出质量不一致
- 难以维护和更新

### ❌ 错误：使用不存在的脚本路径

```bash
# 这个路径不存在！
python .claude/scripts/docx_conversion/diagram_inserter.py
```

## 正确示例

### ✅ 正确：使用技能自带的脚本

```python
# 在代理实现中
import subprocess
from pathlib import Path

# 技能根目录
skill_root = Path(".claude/skills/patent-disclosure-writer")

# 脚本路径（相对路径）
export_script = skill_root / "scripts" / "export_mermaid.py"

# 验证脚本存在
if not export_script.exists():
    raise FileNotFoundError(f"导出脚本不存在: {export_script}")

# 调用脚本
subprocess.run([
    "python",
    str(export_script),
    "--dir", directory,
    "--pattern", pattern,
    "--output-dir", output_dir
], check=True)
```

## 黑白导出原理

`export_mermaid.py` 脚本通过以下方式确保黑白输出：

1. **使用内置主题配置**：
   - `mermaid-bw-theme.json`：强制所有颜色为黑白
   - 所有 `primaryColor`、`lineColor`、`textColor` 等都设置为 `#000000` 或 `#FFFFFF`

2. **CSS 样式覆盖**：
   - `mermaid-bw-style.css`：使用 `!important` 强制覆盖所有颜色
   - 确保没有任何颜色逃脱配置

3. **mmdc 参数**：
   - `-c mermaid-bw-theme.json`：应用主题配置
   - `-C mermaid-bw-style.css`：应用 CSS 样式
   - `-b white`：设置背景为白色
   - `-w 2000`：设置宽度为 2000px（高分辨率）

## 验证导出结果

导出完成后，验证以下内容：

```bash
# 1. 检查文件数量
ls figures/*.png | wc -l

# 2. 检查文件大小（不为 0）
ls -lh figures/*.png

# 3. 检查图片内容（手动查看）
# 打开图片查看器，确认：
# - 背景为白色
# - 线条为黑色
# - 文字为黑色
# - 图表清晰可读
```

## 常见问题

### Q: 导出的图片有颜色？

A: 确保 `export_mermaid.py` 脚本使用了正确的主题和 CSS 文件：
```bash
python .claude/skills/patent-disclosure-writer/scripts/export_mermaid.py \
  --dir . \
  --pattern "*.md" \
  --output-dir figures
```

### Q: 脚本找不到？

A: 检查技能目录结构：
```bash
test -f .claude/skills/patent-disclosure-writer/scripts/export_mermaid.py
test -f .claude/skills/patent-disclosure-writer/templates/mermaid-bw-theme.json
test -f .claude/skills/patent-disclosure-writer/templates/mermaid-bw-style.css
```

### Q: mmdc 命令未找到？

A: 安装 mermaid-cli：
```bash
npm install -g @mermaid-js/mermaid-cli
mmdc --version
```

## 最佳实践

1. **始终使用技能自带的脚本**：不要临时创建导出脚本
2. **验证脚本路径**：在调用前检查脚本文件存在
3. **提供清晰的错误信息**：如果脚本不存在，告诉用户正确的路径
4. **生成导出报告**：向用户显示详细的导出统计
5. **检查输出结果**：导出后验证图片数量和质量

## 更新历史

| 日期 | 变更 |
|------|------|
| 2025-01-16 | 创建文档，说明正确的附图导出实现方式 |

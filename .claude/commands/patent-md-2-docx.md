---
description: 将 Markdown 格式的专利交底书转换为 DOCX 格式，自动导出黑白附图
arguments:
  - name: markdown_file
    description: Markdown 交底书文件路径（必需）
    required: true
  - name: output_dir
    description: 输出目录（可选，默认与 Markdown 文件同目录）
    required: false
  - name: export_figures
    description: 是否导出黑白附图（可选，默认 true）
    required: false
  - name: figures_dir
    description: 附图输出目录（可选，默认为输出目录下的 figures 文件夹）
    required: false
---

# 专利交底书 Markdown 转 DOCX

将 Markdown 格式的专利交底书转换为正式的 DOCX 格式文档，**自动将 Mermaid 图表导出为符合专利审核要求的黑白 PNG 图片**。

## 快速开始

```bash
# 基本转换（自动导出黑白附图）
/patent-md-2-docx markdown_file="专利申请技术交底书_[发明名称].md"

# 指定输出目录
/patent-md-2-docx markdown_file="专利申请技术交底书_[发明名称].md" output_dir="./output"

# 仅转换 DOCX，不导出附图
/patent-md-2-docx markdown_file="专利申请技术交底书_[发明名称].md" export_figures=false

# 自定义附图输出目录
/patent-md-2-docx markdown_file="专利申请技术交底书_[发明名称].md" figures_dir="./output/images"
```

## 前置要求

### 必需工具

- **pandoc**: 文档转换工具
  - 安装方法见 [README.md - 环境配置](../README.md#环境配置)
  - 验证安装: `pandoc --version`

- **mmdc** (Mermaid CLI): 附图导出工具
  - 安装: `npm install -g @mermaid-js/mermaid-cli`
  - 验证安装: `mmdc --version`

## 执行流程

### 1. 验证输入文件

检查 Markdown 文件是否存在且格式正确。

### 2. 导出黑白附图（可选，默认启用）

如果 `export_figures=true`（默认）：

1. 从 Markdown 文件中提取所有 Mermaid 图表
2. 使用专利审核要求的黑白主题配置导出为 PNG
3. 保存到 `figures/` 目录或指定目录

**黑白附图特点**：
- ✅ 纯黑白配色（线条黑、文字黑、背景白）
- ✅ 符合专利局审核要求
- ✅ 适合打印和正式提交
- ✅ 保持图表清晰度和可读性

### 3. 转换为 DOCX

使用 pandoc 将 Markdown 转换为 DOCX 格式。

### 4. 验证输出文件

确认 DOCX 文件和附图都已正确生成。

## 参数说明

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `markdown_file` | 是 | - | Markdown 交底书文件路径 |
| `output_dir` | 否 | 输入文件同目录 | 输出目录 |
| `export_figures` | 否 | true | 是否导出黑白附图 |
| `figures_dir` | 否 | output_dir/figures | 附图输出目录 |

## 输出文件

| 文件 | 说明 |
|------|------|
| `专利申请技术交底书_[发明名称].docx` | 生成的 DOCX 格式交底书 |
| `figures/fig1.png, fig2.png, ...` | 黑白附图（如果 export_figures=true） |

## 附图导出详情

### 导出命令

使用技能自带的 `export_mermaid.py` 脚本：

```bash
python .claude/skills/patent-disclosure-writer/scripts/export_mermaid.py \
  --markdown "专利申请技术交底书_[发明名称].md" \
  --output-dir "figures/"
```

### 导出效果对比

| 版本 | 配置 | 效果 | 适用场景 |
|------|------|------|----------|
| **黑白导出** | 自定义黑白主题 | 纯黑白、白色背景 | ✅ 专利审核、正式提交 |
| 默认导出 | 默认彩色主题 | 彩色、有背景 | ❌ 不符合专利要求 |
| Neutral 主题 | neutral + 白色背景 | 灰色调 | ⚠️ 可能不符合要求 |

### 支持的图表类型

- ✅ 流程图 (graph TD/LR)
- ✅ 序列图 (sequenceDiagram)
- ✅ 架构图 (subgraph)
- ✅ 时序图
- ✅ 协议格式图
- ✅ 状态图

## 注意事项

### Mermaid 图表处理

1. **附图编号**: 脚本自动识别 `#### 附图X：` 标记
2. **图说明**: `图X说明：` 内容不会被导出到图片中
3. **图表引用**: DOCX 中需要手动插入图片引用

### 编码要求

- 确保 Markdown 文件使用 **UTF-8 编码**
- Windows 用户注意保存时的编码选择

### 文件路径

- 建议使用相对路径（相对于工作目录）
- 避免使用包含空格的路径

## 错误处理

### mmdc 未安装

```
❌ 错误: 未找到 mmdc 命令

💡 解决方法:
npm install -g @mermaid-js/mermaid-cli
```

### 没有 Mermaid 图表

```
⚠️ 警告: 未在文件中找到 Mermaid 图表
继续生成 DOCX，但不会创建 figures 目录
```

### pandoc 未安装

```
❌ 错误: pandoc 未安装

💡 解决方法:
# Windows (使用 scoop)
scoop install pandoc

# macOS
brew install pandoc

# Linux
sudo apt-get install pandoc
```

## 高级功能

### 完整 Python 环境

完整的高级转换功能（字体设置、格式验证）需要 Python 环境。

详细信息见: [SKILL.md - Scripts](../.claude/skills/patent-disclosure-writer/SKILL.md#scripts)

### 手动导出附图

如果需要单独导出附图：

```bash
# 从单个 Markdown 文件导出
python .claude/skills/patent-disclosure-writer/scripts/export_mermaid.py \
  --markdown chapter.md \
  --output-dir figures/

# 批量处理目录
python .claude/skills/patent-disclosure-writer/scripts/export_mermaid.py \
  --dir . \
  --pattern "*.md"
```

## 完整示例

```bash
# 场景：生成完整的专利交底书 DOCX 和黑白附图

# 1. 运行专利生成
/patent

# 2. 转换为 DOCX 并导出黑白附图
/patent-md-2-docx markdown_file="专利申请技术交底书_一种基于AI的数据分析方法.md"

# 输出：
# - 专利申请技术交底书_一种基于AI的数据分析方法.docx
# - figures/fig1.png（流程图，黑白）
# - figures/fig2.png（架构图，黑白）
# - figures/fig3.png（序列图，黑白）
```

## 质量保证

生成的黑白附图符合以下标准：

- ✅ **颜色**: 纯黑白（无彩色）
- ✅ **背景**: 白色或透明
- ✅ **清晰度**: 高分辨率，适合打印
- ✅ **格式**: PNG，支持透明背景
- ✅ **命名**: fig1.png, fig2.png, ... 连续编号

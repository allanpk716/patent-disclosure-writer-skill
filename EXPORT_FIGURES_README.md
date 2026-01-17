# 专利附图导出 - 使用指南

## 功能说明

将专利交底书中的 Mermaid 附图导出为**符合专利审核要求的黑白 PNG 图片**。

## 脚本位置

`export_figures.py` 现已内置在技能的 scripts 目录中：

```
.claude/skills/patent-disclosure-writer/scripts/export_figures.py
```

## 使用方法

### 方法 1：直接使用技能中的脚本（推荐）

```bash
# 导出所有章节的附图（章节 03-07）
python .claude/skills/patent-disclosure-writer/scripts/export_figures.py --dir . --pattern "0[3-7]_*.md"

# 导出单个章节的附图
python .claude/skills/patent-disclosure-writer/scripts/export_figures.py --markdown "05_技术方案.md" --output-dir figures

# 自定义图片宽度
python .claude/skills/patent-disclosure-writer/scripts/export_figures.py --dir . --width 3000
```

### 方法 2：使用斜杠命令

```bash
# 在 Claude Code 中使用
/patent-export-figures
```

## 功能特点

- ✅ 纯黑白配色（线条黑、文字黑、背景白）
- ✅ 符合专利局审核要求
- ✅ 适合打印和正式提交
- ✅ 高分辨率，保持清晰度
- ✅ 自动检测附图编号并按编号命名
- ✅ 自动查找技能目录和模板文件

## 前置要求

需要先安装 `mermaid-cli`：

```bash
npm install -g @mermaid-js/mermaid-cli
```

验证安装：

```bash
mmdc --version
```

## 参数说明

| 参数 | 必需 | 说明 | 默认值 |
|------|------|------|--------|
| `--dir` | 否 | 章节文件所在目录 | 当前目录 |
| `--pattern` | 否 | 文件匹配模式 | `0[3-7]_*.md` |
| `--output-dir` | 否 | 输出目录名称 | `figures` |
| `--width` | 否 | 图片宽度像素 | `2000` |
| `--markdown` | 否 | 指定单个 Markdown 文件 | 无 |

**注意**：`--dir` 和 `--markdown` 参数互斥，只能使用其中一个。

## 输出示例

```
figures/
├── fig01_现有技术架构示意图.png
├── fig02_问题场景示意图.png
├── fig03_系统整体架构图.png
└── ...
```

## 脚本工作原理

`export_figures.py` 是一个包装脚本，它会：

1. **自动查找技能目录**：
   - 从当前脚本的相对位置查找
   - 检查 `.claude/skills/patent-disclosure-writer` 子目录
   - 从环境变量 `PATENT_SKILL_PATH` 获取
   - 从当前工作目录向上查找

2. **找到 export_mermaid.py 脚本**：
   - 在技能目录的 `scripts/` 子目录中查找

3. **传递所有参数并执行**：
   - 将所有命令行参数传递给 `export_mermaid.py`
   - 执行导出操作

## 错误处理

### 找不到技能目录

```
❌ 错误：找不到专利技能目录

💡 请确保在以下位置之一运行此脚本：
   1. 技能根目录
   2. 包含 .claude/skills/patent-disclosure-writer 的目录

💡 或者设置环境变量 PATENT_SKILL_PATH 指向技能目录
```

**解决方法**：
- 确保在安装了技能的项目目录中运行
- 或设置环境变量：`export PATENT_SKILL_PATH=/path/to/skill`

### mermaid-cli 未安装

```
❌ 错误：mermaid-cli 未安装

💡 解决方法：
1. 安装 Node.js（如果未安装）
   访问: https://nodejs.org/

2. 安装 mermaid-cli
   npm install -g @mermaid-js/mermaid-cli

3. 验证安装
   mmdc --version
```

## 高级用法

### 设置环境变量

如果脚本无法自动找到技能目录，可以设置环境变量：

```bash
# Windows PowerShell
$env:PATENT_SKILL_PATH="C:\WorkSpace\agent\patent-disclosure-writer-skill\.claude\skills\patent-disclosure-writer"

# Windows CMD
set PATENT_SKILL_PATH=C:\WorkSpace\agent\patent-disclosure-writer-skill\.claude\skills\patent-disclosure-writer

# Linux/Mac
export PATENT_SKILL_PATH=/path/to/skill
```

### 创建快捷脚本

在 Windows 上创建批处理文件：

```batch
@echo off
python .claude\skills\patent-disclosure-writer\scripts\export_figures.py %*
```

在 Linux/Mac 上创建 shell 脚本：

```bash
#!/bin/bash
python .claude/skills/patent-disclosure-writer/scripts/export_figures.py "$@"
```

## 导出效果

导出的 PNG 图片具有以下特性：

| 特性 | 说明 |
|------|------|
| 背景色 | 纯白色（#FFFFFF） |
| 线条颜色 | 纯黑色（#000000） |
| 文字颜色 | 纯黑色（#000000） |
| 分辨率 | 宽度可配置（默认 2000px），高度自动按比例 |
| 格式 | PNG（无损压缩） |
| 命名 | 按附图编号自动命名（fig01.png, fig02.png, ...） |

## 常见问题

### Q: 脚本在哪里？

A: 在技能的 scripts 目录中：
```
.claude/skills/patent-disclosure-writer/scripts/export_figures.py
```

### Q: 每个项目都要运行吗？

A: 是的，每个项目都需要在自己的目录中运行这个命令。

### Q: 可以设置全局环境变量吗？

A: 可以，在 Windows 系统设置中添加用户环境变量：
- 变量名：`PATENT_SKILL_PATH`
- 变量值：`C:\WorkSpace\agent\patent-disclosure-writer-skill\.claude\skills\patent-disclosure-writer`

## 相关文档

- [安装指南](INSTALL_GUIDE.md) - 如何安装和使用安装脚本
- [技能说明](.claude/skills/patent-disclosure-writer/README.md) - 技能完整文档
- [快速开始](QUICKSTART.md) - 快速开始指南

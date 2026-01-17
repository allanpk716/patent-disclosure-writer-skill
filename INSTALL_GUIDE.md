# 专利交底书技能 - 安装指南

## 快速开始

### 交互式安装（推荐）

```bash
# 运行安装脚本
python C:\WorkSpace\agent\patent-disclosure-writer-skill\install_patent_skill.py

# 按提示选择操作：
# [1] 安装技能 - 选择目标目录进行安装
# [2] 卸载技能 - 选择目标目录进行卸载
# [3] 更新技能 - 选择目标目录进行更新
# [4] 检查状态 - 查看目标目录的安装状态
# [0] 退出
```

### 目录选择选项

安装时会提示选择目标目录：

- **[1] 当前目录** - 安装到运行脚本的目录
- **[2] 父目录** - 安装到上一级目录
- **[3] 最近使用的目录** - 从历史记录中选择
- **[0] 手动输入路径** - 输入自定义路径
- **[Q] 取消** - 取消操作

## 安装后使用

安装完成后，在项目目录中：

### 1. 使用斜杠命令

```bash
# 启动 Claude
claude

# 生成专利交底书
/patent

# 更新附图
/patent-update-diagrams
```

### 2. 导出黑白附图

```bash
# 使用技能中的包装脚本导出
python .claude/skills/patent-disclosure-writer/scripts/export_figures.py --dir . --pattern "0[3-7]_*.md"

# 或指定单个章节
python .claude/skills/patent-disclosure-writer/scripts/export_figures.py --markdown "05_技术方案.md" --output-dir figures
```

## 安装内容

脚本会将以下内容安装到项目目录：

```
项目目录/
├── .claude/
│   ├── agents/           # 专利子代理
│   ├── skills/           # 技能定义（包含 scripts 和 export_figures.py）
│   ├── hooks/            # 钩子脚本
│   ├── commands/         # 斜杠命令定义
│   └── settings.json     # 配置文件
├── EXPORT_FIGURES_README.md
├── README.md
└── CLAUDE.md
```

## 工作流程建议

### 推荐的专利项目设置流程

```bash
# 1. 创建专利项目目录
mkdir "专利-项目名称"
cd "专利-项目名称"

# 2. 运行安装脚本
python C:\WorkSpace\agent\patent-disclosure-writer-skill\install_patent_skill.py
# 选择 [1] 安装技能
# 选择 [1] 当前目录

# 3. 启动 Claude 并生成交底书
claude
/patent

# 4. 导出黑白附图
python .claude/skills/patent-disclosure-writer/scripts/export_figures.py --dir . --pattern "0[3-7]_*.md"

# 5. 手动编辑 DOCX（如需要）
# 将生成的 PNG 图片插入到 Word 文档中
```

## 管理已安装的技能

### 更新技能

```bash
# 运行安装脚本
python install_patent_skill.py

# 选择 [3] 更新技能
# 选择目标目录
```

### 卸载技能

```bash
# 运行安装脚本
python install_patent_skill.py

# 选择 [2] 卸载技能
# 选择目标目录
# 确认卸载
```

### 检查状态

```bash
# 运行安装脚本
python install_patent_skill.py

# 选择 [4] 检查状态
# 选择目标目录
```

## 常见问题

### Q: 安装后找不到 export_figures.py？

A: 运行安装脚本，选择 [4] 检查状态，确认安装是否成功。

### Q: 技能更新后如何更新项目？

A: 运行安装脚本，选择 [3] 更新技能。更新会自动清理旧版本文件。

### Q: 如何卸载技能？

A: 运行安装脚本，选择 [2] 卸载技能，会提示确认后删除所有安装的文件。

### Q: 可以在多个项目中使用吗？

A: 可以！每个项目都需要单独安装：

```bash
# 在项目 1 目录中
python install_patent_skill.py
# 选择 [1] 安装技能 -> [1] 当前目录

# 在项目 2 目录中
python install_patent_skill.py
# 选择 [1] 安装技能 -> [1] 当前目录
```

### Q: 如何切换到其他目录？

A: 在安装脚本中，选择 [0] 手动输入路径，输入完整的目录路径。

## 环境变量

可以通过环境变量指定技能源目录：

```bash
# Windows CMD
set PATENT_SKILL_SOURCE=C:\WorkSpace\agent\patent-disclosure-writer-skill

# Windows PowerShell
$env:PATENT_SKILL_SOURCE="C:\WorkSpace\agent\patent-disclosure-writer-skill"

# Linux/Mac
export PATENT_SKILL_SOURCE=/path/to/skill
```

## 优势

使用安装脚本的优势：

- ✅ **独立项目**：每个项目有自己的技能副本，互不影响
- ✅ **路径正确**：脚本和配置文件都在项目目录中，路径正确
- ✅ **易于更新**：可以单独更新某个项目的技能
- ✅ **易于卸载**：一键卸载，不留残留
- ✅ **自动清理**：更新时自动清理旧版本文件
- ✅ **版本控制**：可以将安装的文件提交到版本控制
- ✅ **交互友好**：简单的菜单界面，无需记忆命令

## 与 --plugin-dir 的区别

| 方式 | 优点 | 缺点 |
|------|------|------|
| **安装脚本** | 路径正确、独立项目、易于管理、交互式菜单 | 需要每个项目单独安装 |
| **--plugin-dir** | 全局可用、无需安装 | 路径问题、脚本查找困难 |

**建议**：对于专利项目，使用安装脚本更好。

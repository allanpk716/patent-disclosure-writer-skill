# 专利交底书技能 - 快速开始

## 一键安装到你的专利项目

```bash
# 运行安装脚本
python C:\WorkSpace\agent\patent-disclosure-writer-skill\install_patent_skill.py

# 按提示选择 [1] 安装技能
# 然后选择目标目录
```

安装后即可使用：

```bash
# 生成专利交底书
claude
/patent

# 导出黑白附图
python .claude/skills/patent-disclosure-writer/scripts/export_figures.py --dir . --pattern "0[3-7]_*.md"
```

## 完整文档

详细使用说明请查看：

- [安装指南](INSTALL_GUIDE.md) - 如何安装和使用安装脚本
- [附图导出指南](EXPORT_FIGURES_README.md) - 如何导出黑白 PNG 附图
- [技能说明](.claude/skills/patent-disclosure-writer/README.md) - 技能完整文档

## 推荐的工作流程

```bash
# 1. 创建专利项目目录
mkdir "我的专利项目"
cd "我的专利项目"

# 2. 运行安装脚本
python C:\WorkSpace\agent\patent-disclosure-writer-skill\install_patent_skill.py
# 选择 [1] 安装技能
# 选择目标目录（如当前目录）

# 3. 启动 Claude
claude

# 4. 生成交底书
/patent

# 5. 导出黑白附图
# 退出 Claude 后运行
python .claude/skills/patent-disclosure-writer/scripts/export_figures.py --dir . --pattern "0[3-7]_*.md"

# 6. 查看 results
ls figures/
```

## 为什么使用安装脚本？

使用 `--plugin-dir` 的方式存在路径问题：

```bash
# 这样用会有问题
claude --plugin-dir C:\WorkSpace\agent\patent-disclosure-writer-skill
/patent-export-figures  # ❌ 找不到脚本
```

使用安装脚本后：

```bash
# 在项目目录中安装一次
python install_patent_skill.py
# 选择 [1] 安装技能

# 之后直接使用
python .claude/skills/patent-disclosure-writer/scripts/export_figures.py --dir .  # ✅ 正常工作
```

## 管理技能

```bash
# 运行安装脚本
python install_patent_skill.py

# 按提示选择操作：
# [1] 安装技能
# [2] 卸载技能
# [3] 更新技能
# [4] 检查状态
```

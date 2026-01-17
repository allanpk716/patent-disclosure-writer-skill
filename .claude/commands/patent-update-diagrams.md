---
description: 智能扫描专利章节文档，分析并补充缺失的附图（仅处理章节03-07）。生成的 Mermaid 附图可使用 export_mermaid.py 导出为黑白 PNG。
arguments:
  - name: directory
    description: 专利章节文件所在目录（默认当前目录）
    required: false
  - name: force_regenerate
    description: 是否强制重新生成所有附图（默认false，仅补充缺失）
    required: false
  - name: skip_confirmation
    description: 跳过用户确认，直接执行（默认false）
    required: false
  - name: export_png
    description: 是否同时导出黑白 PNG 图片（默认false）
    required: false
---

# 专利附图智能更新

智能扫描专利章节文档（03-07），分析并补充缺失的附图。**支持将生成的 Mermaid 附图导出为符合专利审核要求的黑白 PNG 图片**。

## 快速开始

```bash
# 补充缺失的附图（Mermaid 格式）
/patent-update-diagrams

# 补充缺失的附图，并同时导出黑白 PNG
/patent-update-diagrams export_png=true

# 指定目录
/patent-update-diagrams directory="./patent_chapters"

# 强制重新生成所有附图
/patent-update-diagrams force_regenerate=true
```

## 功能说明

本命令专注于**附图补充**，不修改章节正文内容：

1. 扫描章节 03-07（背景技术、技术问题、技术方案、有益效果、具体实施方式）
2. 智能分析每个章节是否需要附图
3. 检测现有附图编号，确保连续性
4. 调用专门的附图生成器生成缺失的附图
5. 将附图嵌入到章节文件中
6. 如果设置了 `export_png=true`，调用 `patent-diagram-exporter` 代理导出黑白 PNG

**不处理**：章节 01、02、08、09（这些章节不需要附图）

## 实现代理

本命令由以下子代理实现：

- **patent-diagram-exporter**（代理 32）：负责将 Mermaid 图表导出为黑白 PNG
- 使用技能自带的 `export_mermaid.py` 脚本
- 自动应用黑白主题配置（`mermaid-bw-theme.json` 和 `mermaid-bw-style.css`）
- 无需临时创建脚本，确保输出质量一致

## 参数说明

| 参数 | 必需 | 说明 |
|------|------|------|
| `directory` | 否 | 章节文件所在目录，默认当前目录 |
| `force_regenerate` | 否 | 是否强制重新生成所有附图，默认 false |
| `skip_confirmation` | 否 | 跳过用户确认直接执行，默认 false |
| `export_png` | 否 | 是否同时导出黑白 PNG 图片，默认 false |

## 执行步骤

1. 扫描章节文件（03-07）
2. 分析章节内容，判断需要哪些附图
3. 统计现有附图编号
4. 用户确认（可跳过）
5. 调用附图生成器
6. 插入附图到章节文件
7. 生成报告

## 附图类型

| 附图类型 | 生成器 | 适用章节 |
|---------|--------|----------|
| 流程图 | flowchart-generator | 07 具体实施方式 |
| 时序图 | sequence-generator | 07 具体实施方式 |
| 协议格式图 | protocol-generator | 05 技术方案 |
| 架构图/结构图/原理图 | architecture-generator | 03、04、05 |

## 输出报告

```
附图更新完成

扫描章节: 5个
需要更新: 3个章节
生成附图: 6幅
```

## 注意事项

- **只处理章节 03-07**：其他章节不需要附图
- **不修改正文内容**：只插入附图
- **附图编号全局连续**：确保从 1 开始连续
- **Mermaid 格式**：生成的附图使用 Mermaid 语法

## 黑白 PNG 导出

本命令可以同时将生成的 Mermaid 附图导出为黑白 PNG 图片：

### 导出效果

- ✅ 纯黑白配色（线条黑、文字黑、背景白）
- ✅ 符合专利局审核要求
- ✅ 适合打印和正式提交
- ✅ 高分辨率，保持清晰度

### 手动导出

如果需要在更新后单独导出黑白附图：

```bash
# 导出单个章节的附图
python .claude/skills/patent-disclosure-writer/scripts/export_mermaid.py \
  --markdown "05_技术方案.md" \
  --output-dir figures/

# 批量导出所有章节的附图
python .claude/skills/patent-disclosure-writer/scripts/export_mermaid.py \
  --dir . \
  --pattern "0[3-7]_*.md"
```

### 前置要求

使用黑白导出功能需要安装 mmdc：

```bash
npm install -g @mermaid-js/mermaid-cli
```

## 错误处理

| 错误 | 解决方法 |
|------|----------|
| 章节文件缺失 | 运行 `/patent` 命令先生成章节 |
| 生成器调用失败 | 检查 MCP 服务是否已配置 |
| 附图编号不连续 | 检查现有附图或使用 force_regenerate |

## 详细实现

实现细节（智能判断逻辑、编号管理算法）见: [SKILL.md - 附图生成](../.claude/skills/patent-disclosure-writer/SKILL.md#附图生成)

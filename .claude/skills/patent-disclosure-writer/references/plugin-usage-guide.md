# 插件使用场景下的脚本路径问题解决方案

## 问题描述

当使用 `--plugin-dir` 参数加载技能时：

```bash
claude --dangerously-skip-permissions --plugin-dir C:\WorkSpace\agent\patent-disclosure-writer-skill
```

用户在**外部项目目录**中使用斜杠命令（如 `/patent-export-figures`），此时：
1. **工作目录**：用户的项目目录（不是技能目录）
2. **脚本位置**：技能安装目录（可能在其他位置）
3. **路径问题**：硬编码的绝对路径无法找到脚本

## 解决方案

### 方案 1：智能脚本查找（推荐）

在斜杠命令实现中，使用多级查找策略：

```python
# 在斜杠命令实现中查找脚本
def find_export_script():
    """查找 export_mermaid.py 脚本"""
    import subprocess
    from pathlib import Path

    # 方法 1: 检查相对路径
    relative_paths = [
        ".claude/skills/patent-disclosure-writer/scripts/export_mermaid.py",
        ".claude/skills/patent-disclosure-writer/scripts/export_mermaid.py",
    ]

    for rel_path in relative_paths:
        p = Path(rel_path)
        if p.exists():
            return str(p.resolve())

    # 方法 2: 使用 find 命令递归查找
    try:
        result = subprocess.run(
            ["find", ".", "-name", "export_mermaid.py", "-type", "f"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            # 取第一个匹配结果
            return result.stdout.strip().split('\n')[0]
    except:
        pass

    # 方法 3: 使用 Python 查找
    try:
        code = '''
from pathlib import Path
for p in Path(".").rglob("export_mermaid.py"):
    if "scripts" in str(p):
        print(p.resolve())
        break
'''
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except:
        pass

    return None
```

### 方案 2：脚本内部路径解析（已实现）

`export_mermaid.py` 脚本已经支持自动查找模板文件：

```python
@staticmethod
def find_skill_root() -> Path:
    """查找技能根目录"""
    # 方法 1: 使用 __file__ 获取脚本所在位置
    script_path = Path(__file__).resolve()
    skill_root = script_path.parent.parent

    # 方法 2: 验证 templates 目录存在
    if (skill_root / "templates").exists():
        return skill_root

    # 方法 3: 从当前工作目录查找
    cwd = Path.cwd()
    if (cwd / "templates").exists():
        return cwd

    # 方法 4: 搜索父目录
    for parent in [cwd, *cwd.parents]:
        if (parent / "templates").exists():
            return parent

    return skill_root
```

这意味着**只要脚本能够被执行，它就能自动找到模板文件**。

### 方案 3：环境变量配置（可选）

支持通过环境变量指定技能路径：

```python
# 在斜杠命令实现中
import os

skill_path = os.environ.get('PATENT_SKILL_PATH')
if skill_path:
    script_path = Path(skill_path) / "scripts" / "export_mermaid.py"
    if script_path.exists():
        return str(script_path)
```

用户可以设置：
```bash
export PATENT_SKILL_PATH=C:\WorkSpace\agent\patent-disclosure-writer-skill\.claude\skills\patent-disclosure-writer
```

## 实现建议

### 在斜杠命令中实现

当实现 `/patent-export-figures` 命令时：

1. **查找脚本**：
```python
script_path = find_export_script()
if not script_path:
    print("❌ 错误：找不到 export_mermaid.py 脚本")
    print("💡 请确保 patent-disclosure-writer 技能已正确安装")
    return
```

2. **构建命令**：
```python
cmd = ["python", script_path, "--dir", ".", "--pattern", "0[3-7]_*.md"]
```

3. **执行命令**：
```python
result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print(f"❌ 导出失败: {result.stderr}")
```

## 测试场景

### 场景 1：开发环境

```bash
# 在技能目录中
cd C:\WorkSpace\agent\patent-disclosure-writer-skill
claude
/patent-export-figures
```

**预期**：直接使用 `.claude/skills/patent-disclosure-writer/scripts/export_mermaid.py`

### 场景 2：插件环境（外部项目）

```bash
# 在用户项目目录中
cd C:\Users\User\MyProject
claude --plugin-dir C:\WorkSpace\agent\patent-disclosure-writer-skill
/patent-export-figures
```

**预期**：使用智能查找找到脚本

### 场景 3：全局安装（未来）

如果技能支持全局安装（npm/yarn 方式）：

```bash
# 任何目录
cd /any/directory
claude
/patent-export-figures
```

**预期**：从全局安装位置找到脚本

## 错误处理

### 友好的错误信息

```
❌ 错误：找不到 export_mermaid.py 脚本

📂 搜索位置：
1. ./.claude/skills/patent-disclosure-writer/scripts/export_mermaid.py
2. ./export_mermaid.py（递归查找）

💡 可能的原因：
1. 技能未正确安装
2. 技能目录结构不完整

💡 解决方法：
1. 检查技能是否正确安装
2. 验证技能目录结构：
   .claude/skills/patent-disclosure-writer/
   ├── scripts/
   │   └── export_mermaid.py
   └── templates/
       ├── mermaid-bw-theme.json
       └── mermaid-bw-style.css

3. 或手动运行脚本：
   python <path_to_script>/export_mermaid.py --dir .
```

## 调试技巧

### 查看脚本查找过程

```python
import logging
logging.basicConfig(level=logging.DEBUG)

def find_export_script():
    logger = logging.getLogger(__name__)

    # 方法 1
    for rel_path in relative_paths:
        logger.debug(f"检查相对路径: {rel_path}")

    # 方法 2
    logger.debug(f"执行 find 命令...")
    logger.debug(f"find 结果: {result.stdout}")

    # ...
```

### 验证脚本功能

```bash
# 找到脚本后，测试它是否正常工作
python <script_path> --help
```

## 总结

关键要点：

1. **脚本内部已解决**：`export_mermaid.py` 脚本使用 `Path(__file__)` 自动查找模板文件
2. **命令需要查找**：斜杠命令实现需要找到 `export_mermaid.py` 脚本的位置
3. **智能查找策略**：使用多级查找（相对路径 → find 命令 → Python 递归）
4. **友好错误提示**：找不到脚本时提供清晰的错误信息和解决方法

核心代码示例：

```python
# 斜杠命令实现中
def execute_patent_export_figures(directory=".", pattern="0[3-7]_*.md", output_dir="figures", width=2000, markdown=None):
    """执行附图导出"""

    # 1. 查找脚本
    script_path = find_export_script()
    if not script_path:
        show_error("找不到脚本")
        return

    # 2. 构建命令
    if markdown:
        cmd = ["python", script_path, "--markdown", markdown, "--output-dir", output_dir]
    else:
        cmd = ["python", script_path, "--dir", directory, "--pattern", pattern, "--output-dir", output_dir]

    if width != 2000:
        cmd.extend(["--width", str(width)])

    # 3. 执行
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)

    # 4. 报告
    if result.returncode == 0:
        print("✅ 导出成功")
    else:
        print(f"❌ 导出失败: {result.stderr}")
```

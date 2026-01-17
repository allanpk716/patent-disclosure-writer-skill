---
description: /patent-export-figures 命令的实现逻辑
---

# /patent-export-figures 命令实现

当用户调用 `/patent-export-figures` 命令时，按以下步骤执行：

## 步骤 1：查找 export_mermaid.py 脚本

由于技能作为插件加载时，脚本位置不确定，需要智能查找：

```python
# 在斜杠命令实现中
from pathlib import Path
import subprocess
import sys

def find_export_script():
    """查找 export_mermaid.py 脚本"""
    script_name = "export_mermaid.py"

    # 方法 1: 使用 Python 递归查找（推荐）
    code = f'''
import sys
from pathlib import Path

def find_script():
    # 搜索当前目录及子目录
    for p in Path(".").rglob("{script_name}"):
        # 只返回 scripts 目录中的脚本
        if "scripts" in str(p):
            print(p.resolve())
            return True
    return False

if not find_script():
    # 如果当前目录找不到，尝试向上查找
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        for p in parent.rglob("{script_name}"):
            if "scripts" in str(p):
                print(p.resolve())
                sys.exit(0)
    sys.exit(1)
'''

    try:
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            timeout=30,
            cwd="."  # 在当前工作目录执行
        )

        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception as e:
        pass

    return None

# 查找脚本
script_path = find_export_script()
```

## 步骤 2：处理找不到脚本的情况

```python
if not script_path:
    print("❌ 错误：找不到 export_mermaid.py 脚本")
    print("")
    print("💡 可能的原因：")
    print("   1. 技能未正确安装")
    print("   2. 技能目录结构不完整")
    print("")
    print("💡 解决方法：")
    print("   方法 1: 直接使用技能中的脚本")
    print("   方法 2: 手动指定脚本路径")
    print("   方法 3: 检查技能安装")
    return
```

## 步骤 3：构建并执行命令

```python
# 构建命令参数
args = {
    "directory": directory or ".",
    "pattern": pattern or "0[3-7]_*.md",
    "output_dir": output_dir or "figures",
    "width": width or 2000,
}

cmd = [sys.executable, script_path]

if markdown:
    cmd.extend(["--markdown", markdown, "--output-dir", args["output_dir"]])
else:
    cmd.extend(["--dir", args["directory"], "--pattern", args["pattern"], "--output-dir", args["output_dir"]])

if args["width"] != 2000:
    cmd.extend(["--width", str(args["width"])])

# 执行命令
print(f"📂 工作目录: {Path.cwd()}")
print(f"📜 脚本路径: {script_path}")
print("")

result = subprocess.run(cmd, capture_output=True, text=True)

# 输出结果
print(result.stdout)
if result.stderr:
    print(result.stderr, file=sys.stderr)

if result.returncode == 0:
    print("✅ 导出完成")
else:
    print(f"❌ 导出失败 (退出码: {result.returncode})")
```

## 替代方案：内联 Python 代码

如果上述方法都失败，可以在命令中直接内联实现导出逻辑：

```python
# 直接在斜杠命令中实现导出逻辑，不依赖外部脚本
import re
import subprocess
from pathlib import Path

def export_mermaid_figures(directory=".", pattern="0[3-7]_*.md", output_dir="figures", width=2000):
    """导出 Mermaid 附图为黑白 PNG"""

    # 查找所有 Markdown 文件
    md_files = list(Path(directory).glob(pattern))
    if not md_files:
        print("❌ 未找到匹配的 Markdown 文件")
        return False

    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 正则表达式
    mermaid_pattern = re.compile(r'```mermaid\n(.*?)\n```', re.DOTALL)
    figure_pattern = re.compile(r'####\s*附图(\d+)：')

    # 处理每个文件
    for md_file in md_files:
        content = md_file.read_text(encoding='utf-8')

        # 查找 Mermaid 代码块
        mermaid_blocks = mermaid_pattern.findall(content)
        if not mermaid_blocks:
            continue

        # 查找附图编号
        figure_numbers = [int(m.group(1)) for m in figure_pattern.finditer(content)]

        # 导出每个图表
        for i, mermaid_code in enumerate(mermaid_blocks):
            fig_num = figure_numbers[i] if i < len(figure_numbers) else i + 1

            # 创建临时 .mmd 文件
            temp_mmd = output_path / f"temp_fig{fig_num}.mmd"
            temp_mmd.write_text(mermaid_code, encoding='utf-8')

            # 导出为 PNG（使用 mmdc）
            output_png = output_path / f"fig{fig_num}.png"

            # 这里需要黑白主题配置...
            # 由于找不到模板文件，可以使用简单的配置
            cmd = [
                "mmdc",
                "-i", str(temp_mmd),
                "-o", str(output_png),
                "-b", "white",
                "-w", str(width),
                "-t", "default"  # 使用默认主题
            ]

            try:
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"✅ {output_png}")
            except subprocess.CalledProcessError as e:
                print(f"❌ 导出失败: {output_png}")
                print(f"   错误: {e.stderr.decode() if e.stderr else '未知错误'}")
            finally:
                temp_mmd.unlink()

    return True
```

## 最简单的解决方案

**export_figures.py 现已内置在技能的 scripts 目录中**：

用户可以：
1. 直接使用：`python .claude/skills/patent-disclosure-writer/scripts/export_figures.py --dir .`
2. 或通过斜杠命令调用

这个包装脚本会自动：
- 查找技能目录
- 找到 `export_mermaid.py` 和模板文件
- 执行导出操作

## 命令实现模板

```python
# /patent-export-figures 斜杠命令的实现
def execute_patent_export_figures(**kwargs):
    """执行附图导出"""

    # 1. 尝试查找 export_mermaid.py
    script_path = find_export_script()
    if script_path:
        cmd = [sys.executable, script_path]
        cmd.extend(build_args(kwargs))
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        return result.returncode == 0

    # 2. 找不到，使用内联实现
    print("⚠️ 使用内联实现（部分功能受限）")
    return export_mermaid_figures(**kwargs)
```

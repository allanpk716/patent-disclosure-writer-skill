#!/usr/bin/env python3
"""
export_figures.py - 专利附图导出包装脚本

这是 export_mermaid.py 的包装脚本，可以从任何位置调用。
它会自动查找技能目录和模板文件。

使用方法:
    python export_figures.py --dir . --pattern "0[3-7]_*.md"
    python export_figures.py --markdown chapter.md --output-dir figures/
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def find_skill_directory() -> Path:
    """
    查找技能目录

    Returns:
        技能目录的绝对路径，如果找不到则返回 None
    """
    # 方法 1: 从当前脚本的相对位置查找
    # 这个脚本应该在技能根目录
    current_dir = Path(__file__).parent.resolve()

    # 检查可能的技能目录结构
    possible_roots = [
        current_dir,  # 脚本所在目录
        current_dir / ".claude" / "skills" / "patent-disclosure-writer",  # 子目录
        current_dir.parent,  # 父目录
    ]

    for root in possible_roots:
        # 检查是否有 scripts 和 templates 目录
        if (root / "scripts" / "export_mermaid.py").exists() and \
           (root / "templates" / "mermaid-bw-theme.json").exists():
            return root

    # 方法 2: 从环境变量获取
    skill_path = os.environ.get('PATENT_SKILL_PATH')
    if skill_path:
        p = Path(skill_path)
        if (p / "scripts" / "export_mermaid.py").exists():
            return p

    # 方法 3: 从当前工作目录向上查找
    cwd = Path.cwd()
    for parent in [cwd, *cwd.parents]:
        if (parent / "scripts" / "export_mermaid.py").exists():
            return parent

    return None


def main():
    """主函数"""
    # 查找技能目录
    skill_dir = find_skill_directory()

    if not skill_dir:
        print("❌ 错误：找不到专利技能目录", file=sys.stderr)
        print("", file=sys.stderr)
        print("💡 请确保在以下位置之一运行此脚本：", file=sys.stderr)
        print("   1. 技能根目录", file=sys.stderr)
        print("   2. 包含 .claude/skills/patent-disclosure-writer 的目录", file=sys.stderr)
        print("", file=sys.stderr)
        print("💡 或者设置环境变量 PATENT_SKILL_PATH 指向技能目录", file=sys.stderr)
        sys.exit(20)

    # 找到 export_mermaid.py 脚本
    export_script = skill_dir / "scripts" / "export_mermaid.py"

    if not export_script.exists():
        print(f"❌ 错误：找不到导出脚本 {export_script}", file=sys.stderr)
        sys.exit(20)

    # 将所有参数传递给 export_mermaid.py
    cmd = [sys.executable, str(export_script)] + sys.argv[1:]

    # 执行脚本
    try:
        result = subprocess.run(cmd, check=False)
        sys.exit(result.returncode)
    except FileNotFoundError:
        print(f"❌ 错误：找不到 Python 解释器 {sys.executable}", file=sys.stderr)
        sys.exit(20)
    except Exception as e:
        print(f"❌ 错误：{e}", file=sys.stderr)
        sys.exit(20)


if __name__ == "__main__":
    main()

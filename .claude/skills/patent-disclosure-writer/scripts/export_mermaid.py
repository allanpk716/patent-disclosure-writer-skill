#!/usr/bin/env python3
"""
export_mermaid.py - 将 Mermaid 图表导出为黑白 PNG 图片

本脚本用于将专利交底书中的 Mermaid 图表导出为符合专利审核要求的黑白图片。
使用自定义黑白主题配置，确保输出为纯黑白、白色背景。

使用方法:
    python export_mermaid.py --input <input.mmd> --output <output.png>
    python export_mermaid.py --dir <directory> --pattern "*.md"

Exit codes:
    0: 导出成功
    20: 导出失败
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple, Optional

# 设置 UTF-8 编码输出（Windows 兼容）
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


# Mermaid 代码块正则表达式
MERMAID_BLOCK_PATTERN = re.compile(
    r'```mermaid\n(.*?)\n```',
    re.DOTALL
)

# 附图标记正则表达式
FIGURE_PATTERN = re.compile(r'####\s*附图(\d+)：')


class MermaidExporter:
    """Mermaid 图表导出器"""

    @staticmethod
    def find_skill_root() -> Path:
        """
        查找技能根目录

        Returns:
            技能根目录的绝对路径
        """
        # 方法 1: 使用 __file__ 获取脚本所在位置
        script_path = Path(__file__).resolve()
        # 脚本位于 scripts/ 目录，技能根目录是它的上级目录
        skill_root = script_path.parent.parent

        # 方法 2: 验证 templates 目录存在
        if (skill_root / "templates").exists():
            return skill_root

        # 方法 3: 尝试从当前工作目录查找（适用于开发环境）
        cwd = Path.cwd()
        if (cwd / "templates").exists():
            return cwd

        # 方法 4: 搜索父目录中的 templates 文件夹
        for parent in [cwd, *cwd.parents]:
            if (parent / "templates").exists():
                return parent

        # 如果都找不到，返回脚本所在目录的父目录（最可能的位置）
        return skill_root

    @staticmethod
    def find_mmdc() -> Optional[str]:
        """
        查找 mmdc 命令的路径

        Returns:
            mmdc 命令的完整路径，如果找不到则返回 None
        """
        # 首先尝试直接查找
        mmdc_path = shutil.which("mmdc")
        if mmdc_path:
            return mmdc_path

        # 如果找不到，尝试常见的 npm 安装路径
        home = Path.home()
        common_paths = [
            home / "AppData" / "Roaming" / "npm" / "mmdc.cmd",  # Windows
            home / ".npm" / "global" / "bin" / "mmdc",  # Linux/Mac
            Path("/usr/local/bin") / "mmdc",  # Linux/Mac
        ]

        for path in common_paths:
            if path.exists():
                return str(path)

        return None

    def __init__(self,
                 theme_config: Path = None,
                 style_css: Path = None,
                 background: str = "white",
                 width: int = 2000):
        """
        初始化导出器

        Args:
            theme_config: 黑白主题配置文件路径
            style_css: 黑白样式 CSS 文件路径
            background: 背景颜色 (默认: white)
            width: 图片宽度像素 (默认: 2000，高度自动按比例)
        """
        # 查找技能根目录
        skill_root = self.find_skill_root()

        if theme_config is None:
            # 默认使用技能自带的黑白主题配置
            theme_config = skill_root / "templates" / "mermaid-bw-theme.json"

        if style_css is None:
            # 默认使用技能自带的黑白样式 CSS
            style_css = skill_root / "templates" / "mermaid-bw-style.css"

        self.theme_config = Path(theme_config)
        self.style_css = Path(style_css)
        self.background = background
        self.width = width
        self.skill_root = skill_root

        # 验证主题配置文件存在
        if not self.theme_config.exists():
            raise FileNotFoundError(
                f"主题配置文件不存在: {self.theme_config}\n"
                f"技能根目录: {skill_root}\n"
                f"请确保技能已正确安装。"
            )

        # 验证 CSS 文件存在
        if not self.style_css.exists():
            raise FileNotFoundError(
                f"样式文件不存在: {self.style_css}\n"
                f"技能根目录: {skill_root}\n"
                f"请确保技能已正确安装。"
            )

    def export_file(self,
                   input_file: Path,
                   output_file: Path) -> bool:
        """
        导出单个 Mermaid 文件

        Args:
            input_file: 输入的 .mmd 文件
            output_file: 输出的 PNG 文件

        Returns:
            是否成功
        """
        print(f"导出: {input_file} -> {output_file}")

        # 查找 mmdc 命令
        mmdc_path = self.find_mmdc()
        if not mmdc_path:
            print("  错误: 未找到 mmdc 命令。请先安装: npm install -g @mermaid-js/mermaid-cli")
            return False

        cmd = [
            mmdc_path,
            "-i", str(input_file),
            "-o", str(output_file),
            "-c", str(self.theme_config),
            "-C", str(self.style_css),  # 添加 CSS 样式文件
            "-b", self.background,
            "-w", str(self.width)  # 添加宽度参数
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                encoding='utf-8',
                shell=True  # Windows 需要
            )
            print(f"  成功: {output_file}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  失败: {e}")
            if e.stderr:
                print(f"  错误: {e.stderr}")
            return False
        except FileNotFoundError:
            print(f"  错误: 未找到 mmdc 命令。请先安装: npm install -g @mermaid-js/mermaid-cli")
            return False

    def extract_from_markdown(self,
                             markdown_file: Path) -> List[Tuple[str, int]]:
        """
        从 Markdown 文件中提取 Mermaid 图表

        Args:
            markdown_file: Markdown 文件路径

        Returns:
            List of (mermaid_code, figure_number) tuples
        """
        content = markdown_file.read_text(encoding='utf-8')

        # 查找所有 Mermaid 代码块
        mermaid_blocks = MERMAID_BLOCK_PATTERN.findall(content)

        # 查找附图编号
        figure_numbers = []
        for match in FIGURE_PATTERN.finditer(content):
            figure_numbers.append(int(match.group(1)))

        # 组合结果
        results = []
        for i, code in enumerate(mermaid_blocks):
            fig_num = figure_numbers[i] if i < len(figure_numbers) else i + 1
            results.append((code, fig_num))

        return results

    def export_markdown(self,
                       markdown_file: Path,
                       output_dir: Path = None) -> List[Path]:
        """
        从 Markdown 文件中提取并导出所有 Mermaid 图表

        Args:
            markdown_file: Markdown 文件路径
            output_dir: 输出目录 (默认: markdown_file 同目录下的 figures 文件夹)

        Returns:
            成功导出的文件路径列表
        """
        print(f"处理文件: {markdown_file}")

        if output_dir is None:
            output_dir = markdown_file.parent / "figures"
        output_dir.mkdir(parents=True, exist_ok=True)

        # 提取 Mermaid 图表
        diagrams = self.extract_from_markdown(markdown_file)

        if not diagrams:
            print("  未找到 Mermaid 图表")
            return []

        # 导出每个图表
        exported_files = []
        for mermaid_code, fig_num in diagrams:
            # 创建临时 .mmd 文件
            temp_mmd = output_dir / f"temp_fig{fig_num}.mmd"
            temp_mmd.write_text(mermaid_code, encoding='utf-8')

            # 导出为 PNG
            output_png = output_dir / f"fig{fig_num}.png"
            if self.export_file(temp_mmd, output_png):
                exported_files.append(output_png)

            # 删除临时文件
            temp_mmd.unlink()

        print(f"  共导出 {len(exported_files)} 个图表")
        return exported_files

    def export_directory(self,
                        directory: Path,
                        pattern: str = "*.md",
                        output_subdir: str = "figures") -> List[Path]:
        """
        批量导出目录中的所有 Markdown 文件

        Args:
            directory: 目录路径
            pattern: 文件匹配模式
            output_subdir: 输出子目录名称

        Returns:
            所有成功导出的文件路径列表
        """
        all_exported = []

        for md_file in directory.glob(pattern):
            output_dir = md_file.parent / output_subdir
            exported = self.export_markdown(md_file, output_dir)
            all_exported.extend(exported)

        return all_exported


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="将 Mermaid 图表导出为黑白 PNG 图片",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 导出单个 Mermaid 文件
    python export_mermaid.py --input diagram.mmd --output diagram.png

    # 从 Markdown 文件提取并导出所有图表
    python export_mermaid.py --markdown chapter.md --output-dir figures/

    # 批量处理目录中的所有 Markdown 文件
    python export_mermaid.py --dir . --pattern "*.md"

    # 使用自定义主题配置
    python export_mermaid.py --input diagram.mmd --output diagram.png --theme my-theme.json

Exit codes:
    0: 导出成功
    20: 导出失败
        """
    )

    # 单文件导出模式
    parser.add_argument(
        "--input", "-i",
        type=str,
        help="输入的 Mermaid (.mmd) 文件"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="输出的 PNG 文件"
    )

    # Markdown 提取模式
    parser.add_argument(
        "--markdown", "-m",
        type=str,
        help="从 Markdown 文件提取并导出 Mermaid 图表"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="输出目录（仅用于 --markdown 模式）"
    )

    # 批量处理模式
    parser.add_argument(
        "--dir", "-d",
        type=str,
        help="批量处理的目录"
    )
    parser.add_argument(
        "--pattern",
        type=str,
        default="*.md",
        help="文件匹配模式 (默认: *.md)"
    )

    # 主题配置
    parser.add_argument(
        "--theme", "-t",
        type=str,
        help="黑白主题配置文件路径 (默认使用内置配置)"
    )
    parser.add_argument(
        "--css",
        type=str,
        help="黑白样式 CSS 文件路径 (默认使用内置配置)"
    )
    parser.add_argument(
        "--background", "-b",
        type=str,
        default="white",
        help="背景颜色 (默认: white)"
    )
    parser.add_argument(
        "--width", "-w",
        type=int,
        default=2000,
        help="图片宽度像素 (默认: 2000，高度自动按比例)"
    )

    args = parser.parse_args()

    # 验证参数
    modes = sum([
        bool(args.input and args.output),
        bool(args.markdown),
        bool(args.dir)
    ])

    if modes == 0:
        parser.print_help()
        print("\n错误: 必须指定一种模式 (--input/--output, --markdown, 或 --dir)")
        sys.exit(1)

    if modes > 1:
        parser.print_help()
        print("\n错误: 只能使用一种模式")
        sys.exit(1)

    # 创建导出器
    try:
        theme_config = Path(args.theme) if args.theme else None
        style_css = Path(args.css) if args.css else None
        exporter = MermaidExporter(theme_config, style_css, args.background, args.width)
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(20)

    # 执行导出
    success = False

    if args.input and args.output:
        # 单文件导出模式
        success = exporter.export_file(
            Path(args.input),
            Path(args.output)
        )

    elif args.markdown:
        # Markdown 提取模式
        output_dir = Path(args.output_dir) if args.output_dir else None
        exported = exporter.export_markdown(
            Path(args.markdown),
            output_dir
        )
        success = len(exported) > 0

    elif args.dir:
        # 批量处理模式
        all_exported = exporter.export_directory(
            Path(args.dir),
            args.pattern
        )
        success = len(all_exported) > 0

    sys.exit(0 if success else 20)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
install_patent_skill.py - 专利交底书技能安装脚本

将专利交底书技能安装到指定的项目目录中，使其可以在该目录下正常使用。

使用方法:
    python install_patent_skill.py

环境变量:
    PATENT_SKILL_SOURCE    技能源目录（默认从脚本位置推断）
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime

# 设置 UTF-8 编码输出（Windows 兼容）
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')


class PatentSkillInstaller:
    """专利技能安装器"""

    # 需要安装的文件和目录
    INSTALL_ITEMS = [
        ".claude/agents",
        ".claude/skills",
        ".claude/hooks",
        ".claude/settings.json",
        ".claude/commands",
        "templates",
        "EXPORT_FIGURES_README.md",
        "README.md",
        "CLAUDE.md",
    ]

    # 旧版本文件和目录（需要清理的）
    OLD_VERSION_ITEMS = [
        ".claude/settings.json.backup_*",
        ".patent-skill-install.log",
        "export_figures.pyc",
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
    ]

    def __init__(self, target_dir: Path, source_dir: Optional[Path] = None):
        """
        初始化安装器

        Args:
            target_dir: 目标安装目录
            source_dir: 技能源目录（默认从脚本位置推断）
        """
        self.target_dir = Path(target_dir).resolve()
        self.source_dir = self._find_source_dir(source_dir)
        self.install_log = self.target_dir / ".patent-skill-install.log"

        if not self.source_dir.exists():
            raise FileNotFoundError(f"技能源目录不存在: {self.source_dir}")

        # 获取源版本
        self.source_version = self._get_source_version()

    def _find_source_dir(self, source_dir: Optional[Path]) -> Path:
        """
        查找技能源目录

        Args:
            source_dir: 用户指定的源目录

        Returns:
            技能源目录的绝对路径
        """
        # 方法 1: 用户指定的目录
        if source_dir:
            return Path(source_dir).resolve()

        # 方法 2: 环境变量
        env_path = os.environ.get('PATENT_SKILL_SOURCE')
        if env_path:
            return Path(env_path).resolve()

        # 方法 3: 从脚本位置推断
        script_path = Path(__file__).resolve()
        skill_root = script_path.parent

        # 验证这是技能目录
        if (skill_root / ".claude" / "skills" / "patent-disclosure-writer").exists():
            return skill_root

        # 方法 4: 检查父目录
        for parent in [script_path.parent, script_path.parent.parent]:
            if (parent / ".claude" / "skills" / "patent-disclosure-writer").exists():
                return parent

        return skill_root

    def _get_source_version(self) -> str:
        """获取源版本"""
        version_file = self.source_dir / ".claude" / "skills" / "patent-disclosure-writer" / "SKILL.md"
        if version_file.exists():
            try:
                content = version_file.read_text(encoding='utf-8')
                for line in content.split('\n')[:20]:
                    if 'version:' in line.lower():
                        return line.split(':')[1].strip().split()[0]
            except:
                pass
        return "未知版本"

    def get_installed_version(self) -> Optional[str]:
        """
        获取已安装的版本

        Returns:
            已安装的版本号，如果未安装则返回 None
        """
        version_file = self.target_dir / ".claude" / "skills" / "patent-disclosure-writer" / "SKILL.md"
        if not version_file.exists():
            return None

        try:
            content = version_file.read_text(encoding='utf-8')
            for line in content.split('\n')[:20]:
                if 'version:' in line.lower():
                    return line.split(':')[1].strip().split()[0]
        except:
            pass

        return "未知版本"

    def clean_old_version(self) -> Tuple[int, List[str]]:
        """
        清理旧版本文件

        Returns:
            (清理数量, 清理的文件列表)
        """
        cleaned_count = 0
        cleaned_files = []

        print("\n" + "="*60)
        print("清理旧版本文件")
        print("="*60)

        # 清理备份文件
        for backup_file in self.target_dir.glob(".claude/settings.json.backup_*"):
            try:
                backup_file.unlink()
                cleaned_count += 1
                cleaned_files.append(str(backup_file.relative_to(self.target_dir)))
                print(f"✓ 删除备份: {backup_file.name}")
            except Exception as e:
                print(f"⚠️  无法删除 {backup_file.name}: {e}")

        # 清理旧的安装日志
        if self.install_log.exists():
            try:
                self.install_log.unlink()
                cleaned_count += 1
                cleaned_files.append(".patent-skill-install.log")
                print(f"✓ 删除旧日志")
            except Exception as e:
                print(f"⚠️  无法删除日志: {e}")

        # 清理 __pycache__
        for pycache in self.target_dir.rglob("__pycache__"):
            if pycache.is_dir():
                try:
                    shutil.rmtree(pycache)
                    cleaned_count += 1
                    rel_path = pycache.relative_to(self.target_dir)
                    cleaned_files.append(str(rel_path))
                    print(f"✓ 删除缓存: {rel_path}")
                except Exception as e:
                    print(f"⚠️  无法删除 {pycache}: {e}")

        # 清理 .pyc 文件
        for pyc_file in self.target_dir.rglob("*.pyc"):
            try:
                pyc_file.unlink()
                cleaned_count += 1
                rel_path = pyc_file.relative_to(self.target_dir)
                cleaned_files.append(str(rel_path))
            except Exception as e:
                pass

        # 清理旧版本可能创建的 commands 目录（根目录下）
        old_commands_dir = self.target_dir / "commands"
        if old_commands_dir.exists() and old_commands_dir.is_dir():
            try:
                shutil.rmtree(old_commands_dir)
                cleaned_count += 1
                cleaned_files.append("commands")
                print(f"✓ 删除旧目录: commands")
            except Exception as e:
                print(f"⚠️  无法删除旧目录 commands: {e}")

        if cleaned_count > 0:
            print(f"\n✓ 共清理 {cleaned_count} 项")
        else:
            print("✓ 无需清理")

        return cleaned_count, cleaned_files

    def prompt_target_directory(self) -> Optional[Path]:
        """
        交互式询问目标目录

        Returns:
            用户选择的目录，如果取消则返回 None
        """
        print("\n" + "="*60)
        print("专利交底书技能安装向导")
        print("="*60)
        print()
        print(f"当前源目录: {self.source_dir}")
        print(f"源版本: {self.source_version}")
        print()

        # 检查是否已安装
        installed_version = self.get_installed_version()
        if installed_version:
            print(f"⚠️  检测到已安装版本: {installed_version}")
            print()

        # 提供选项
        print("请选择目标目录:")
        print()
        print("  [1] 当前目录")
        print(f"      {Path.cwd()}")
        print()
        print("  [2] 父目录")
        print(f"      {Path.cwd().parent}")
        print()

        # 检查最近使用的目录
        recent_dirs = self._get_recent_directories()
        if recent_dirs:
            print("  [3] 最近使用的目录:")
            for i, (date, directory) in enumerate(recent_dirs[:3], 4):
                print(f"      [{i}] {directory}")
                print(f"          (最后使用: {date})")
            print()

        print("  [0] 手动输入路径")
        print("  [Q] 取消")
        print()

        while True:
            try:
                choice = input("请选择 (0-3/Q): ").strip()

                if choice.upper() == 'Q':
                    print("取消安装")
                    return None

                elif choice == '1':
                    return Path.cwd()

                elif choice == '2':
                    return Path.cwd().parent

                elif choice == '3' and recent_dirs:
                    # 让用户选择最近目录
                    for i, (date, directory) in enumerate(recent_dirs[:3], 1):
                        print(f"  [{i}] {directory}")

                    sub_choice = input("选择最近目录 (1-3/Enter返回): ").strip()
                    if sub_choice and sub_choice.isdigit() and 1 <= int(sub_choice) <= len(recent_dirs):
                        idx = int(sub_choice) - 1
                        return Path(recent_dirs[idx][1])
                    else:
                        continue

                elif choice == '0':
                    # 手动输入路径
                    path_str = input("请输入目录路径: ").strip()
                    path = Path(path_str).expanduser().resolve()

                    if not path.exists():
                        print(f"⚠️  目录不存在: {path}")
                        create = input("是否创建? (y/N): ").strip().lower()
                        if create == 'y':
                            path.mkdir(parents=True, exist_ok=True)
                            print(f"✓ 已创建目录")
                        else:
                            continue

                    return path

                else:
                    print("无效选择，请重试")

            except KeyboardInterrupt:
                print("\n\n用户取消")
                return None
            except Exception as e:
                print(f"错误: {e}")
                return None

    def _get_recent_directories(self) -> List[Tuple[str, str]]:
        """
        获取最近使用的目录

        Returns:
            [(日期, 目录路径), ...] 列表
        """
        recent_dirs = []

        # 从历史记录中查找（如果有）
        # 这里可以扩展为从配置文件读取

        # 检查常见的专利目录位置
        home = Path.home()
        common_paths = [
            home / "SynologyDrive" / "JobDoc" / "z专利" / "正在写的专利",
        ]

        for base_dir in common_paths:
            if base_dir.exists():
                for project_dir in base_dir.iterdir():
                    if project_dir.is_dir():
                        # 检查是否是专利目录（有章节文件）
                        has_chapters = any(
                            p.name.startswith(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'))
                            and p.suffix == '.md'
                            for p in project_dir.glob('*.md')
                        )
                        if has_chapters:
                            # 获取最后修改时间
                            mtime = datetime.fromtimestamp(project_dir.stat().st_mtime)
                            recent_dirs.append((mtime.strftime('%Y-%m-%d'), str(project_dir)))

        # 按日期排序，取最近3个
        recent_dirs.sort(key=lambda x: x[0], reverse=True)
        return recent_dirs[:3]

    def save_to_recent(self, directory: Path):
        """保存到最近使用的目录"""
        # 可以实现为保存到配置文件
        pass

    def install(self, force: bool = False, skip_clean: bool = False) -> bool:
        """
        安装技能

        Args:
            force: 是否强制覆盖已存在的文件
            skip_clean: 是否跳过清理旧版本

        Returns:
            是否安装成功
        """
        print("\n" + "="*60)
        print("开始安装专利交底书技能")
        print("="*60)
        print(f"源版本: {self.source_version}")
        print(f"目标目录: {self.target_dir}")
        print("="*60 + "\n")

        # 检查已安装版本
        installed_version = self.get_installed_version()
        if installed_version:
            if installed_version == self.source_version and not force:
                print(f"✓ 已安装最新版本: {installed_version}")
                print()
                return True

            print(f"已安装版本: {installed_version}")
            print(f"准备更新到: {self.source_version}")
            print()

        # 自动清理旧版本
        if not skip_clean and installed_version:
            print("自动清理旧版本文件...")
            cleaned_count, cleaned_files = self.clean_old_version()
            if cleaned_count > 0:
                print()
            force = True  # 清理后强制覆盖

        # 创建目标目录
        self.target_dir.mkdir(parents=True, exist_ok=True)

        # 统计信息
        copied_count = 0
        skipped_count = 0
        error_count = 0
        replaced_count = 0

        # 复制文件和目录
        for item in self.INSTALL_ITEMS:
            source_path = self.source_dir / item

            if not source_path.exists():
                print(f"⚠️  源文件不存在，跳过: {item}")
                skipped_count += 1
                continue

            target_path = self.target_dir / item

            try:
                if source_path.is_dir():
                    # 复制目录
                    if target_path.exists():
                        if force:
                            shutil.rmtree(target_path)
                            replaced_count += 1
                            print(f"♻️  替换目录: {item}")
                        else:
                            print(f"⊗ 目录已存在，跳过: {item}")
                            skipped_count += 1
                            continue

                    shutil.copytree(source_path, target_path,
                                    ignore=shutil.ignore_patterns(
                                        "*.pyc", "__pycache__", ".git",
                                        "*.pyo", ".DS_Store", "Thumbs.db"
                                    ))
                    copied_count += 1
                    if replaced_count == 0 or item != ".claude/agents":
                        print(f"✓ 复制目录: {item}")

                else:
                    # 复制文件
                    if target_path.exists() and not force:
                        print(f"⊗ 文件已存在，跳过: {item}")
                        skipped_count += 1
                        continue

                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(source_path, target_path)
                    copied_count += 1
                    print(f"✓ 复制文件: {item}")

            except Exception as e:
                error_count += 1
                print(f"✗ 复制失败: {item} - {e}")

        # 写入安装日志
        self._write_install_log(copied_count, skipped_count, error_count, replaced_count)

        # 保存到最近目录
        self.save_to_recent(self.target_dir)

        # 显示安装结果
        print("\n" + "="*60)
        print("安装完成")
        print("="*60)
        print(f"✓ 新增: {copied_count} 项")
        if replaced_count > 0:
            print(f"♻️  替换: {replaced_count} 项")
        if skipped_count > 0:
            print(f"⊗ 跳过: {skipped_count} 项")
        if error_count > 0:
            print(f"✗ 失败: {error_count} 项")

        # 显示使用说明
        print("\n使用说明:")
        print("-" * 40)
        print("1. 生成专利交底书:")
        print("   cd {0}".format(self.target_dir))
        print("   claude")
        print("   /patent")
        print()
        print("2. 导出黑白附图:")
        print("   cd {0}".format(self.target_dir))
        print("   python .claude/skills/patent-disclosure-writer/scripts/export_figures.py --dir .")
        print()
        print("3. 查看详细文档:")
        print("   cat {0}/EXPORT_FIGURES_README.md".format(self.target_dir))
        print("-" * 40)

        return error_count == 0

    def uninstall(self, non_interactive: bool = False) -> bool:
        """
        卸载技能

        Args:
            non_interactive: 是否为非交互模式（跳过确认）

        Returns:
            是否卸载成功
        """
        print("\n" + "="*60)
        print("卸载专利交底书技能")
        print("="*60 + "\n")

        # 检查是否已安装
        installed_version = self.get_installed_version()
        if not installed_version:
            print("❌ 技能未安装")
            return False

        print(f"当前版本: {installed_version}")
        print(f"目标目录: {self.target_dir}")
        print()

        # 非交互模式或确认卸载
        if not non_interactive:
            try:
                response = input("确认卸载? (y/N): ").strip().lower()
                if response != 'y':
                    print("取消卸载")
                    return False
            except EOFError:
                # 非交互环境，默认取消
                print("⚠️  检测到非交互环境，使用 --no-interactive 或 --yes 跳过确认")
                print("取消卸载")
                return False

        # 删除安装的文件
        removed_count = 0
        error_count = 0

        for item in reversed(self.INSTALL_ITEMS):
            target_path = self.target_dir / item

            if not target_path.exists():
                continue

            try:
                if target_path.is_dir():
                    shutil.rmtree(target_path)
                else:
                    target_path.unlink()
                removed_count += 1
                print(f"✓ 删除: {item}")

            except Exception as e:
                error_count += 1
                print(f"✗ 删除失败: {item} - {e}")

        # 删除安装日志
        if self.install_log.exists():
            self.install_log.unlink()

        # 清理旧版本可能创建的 commands 目录（根目录下）
        old_commands_dir = self.target_dir / "commands"
        if old_commands_dir.exists():
            try:
                shutil.rmtree(old_commands_dir)
                removed_count += 1
                print(f"✓ 删除旧目录: commands")
            except Exception as e:
                print(f"⚠️  无法删除旧目录 commands: {e}")

        # 尝试删除空目录
        for parent_dir in [
            self.target_dir / ".claude" / "skills",
            self.target_dir / ".claude" / "agents",
            self.target_dir / ".claude" / "hooks",
            self.target_dir / ".claude" / "commands",
            self.target_dir / ".claude",
            self.target_dir / "templates",
        ]:
            try:
                if parent_dir.exists() and not any(parent_dir.iterdir()):
                    parent_dir.rmdir()
                    print(f"✓ 删除空目录: {parent_dir.relative_to(self.target_dir)}")
            except:
                pass

        print("\n" + "="*60)
        print(f"卸载完成 (删除 {removed_count} 项)")
        if error_count > 0:
            print(f"警告: {error_count} 项删除失败")
        print("="*60)

        return error_count == 0

    def update(self) -> bool:
        """
        更新技能

        Returns:
            是否更新成功
        """
        # 更新就是强制重新安装
        return self.install(force=True)

    def _write_install_log(self, copied: int, skipped: int, errors: int, replaced: int):
        """写入安装日志"""
        try:
            with open(self.install_log, 'w', encoding='utf-8') as f:
                f.write(f"# 专利技能安装日志\n\n")
                f.write(f"安装时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"源目录: {self.source_dir}\n")
                f.write(f"源版本: {self.source_version}\n")
                f.write(f"目标目录: {self.target_dir}\n")
                f.write(f"新增项数: {copied}\n")
                f.write(f"替换项数: {replaced}\n")
                f.write(f"跳过项数: {skipped}\n")
                f.write(f"错误项数: {errors}\n")
        except Exception as e:
            print(f"⚠️  无法写入安装日志: {e}")


def show_menu() -> str:
    """显示主菜单并获取用户选择"""
    while True:
        print("\n" + "="*60)
        print("专利交底书技能安装工具")
        print("="*60)
        print("\n请选择操作:")
        print("  [1] 安装技能")
        print("  [2] 卸载技能")
        print("  [3] 更新技能")
        print("  [4] 检查状态")
        print("  [0] 退出")
        print()

        try:
            choice = input("请输入选项 [0-4]: ").strip()
            if choice in ['0', '1', '2', '3', '4', 'q', 'Q']:
                return choice
            print("无效选项，请重新输入")
        except (EOFError, KeyboardInterrupt):
            print("\n\n退出")
            sys.exit(0)


def main():
    """主函数 - 交互式菜单"""
    # 首先检测技能源目录
    try:
        temp_installer = PatentSkillInstaller(target_dir=".")
        source_dir = temp_installer.source_dir
        print(f"检测到技能目录: {source_dir}")
    except FileNotFoundError:
        print("错误: 无法找到技能源目录")
        print("\n请确保在技能目录中运行此脚本，或设置环境变量 PATENT_SKILL_SOURCE")
        sys.exit(1)

    while True:
        choice = show_menu()

        if choice in ['0', 'q', 'Q']:
            print("退出")
            break

        try:
            if choice == '1':
                # 安装技能
                target_path = temp_installer.prompt_target_directory()
                if target_path is None:
                    print("取消安装")
                    continue

                installer = PatentSkillInstaller(target_dir=target_path)
                installer.install()

            elif choice == '2':
                # 卸载技能
                target_path = temp_installer.prompt_target_directory()
                if target_path is None:
                    print("取消卸载")
                    continue

                installer = PatentSkillInstaller(target_dir=target_path)
                installer.uninstall()

            elif choice == '3':
                # 更新技能
                target_path = temp_installer.prompt_target_directory()
                if target_path is None:
                    print("取消更新")
                    continue

                installer = PatentSkillInstaller(target_dir=target_path)
                print("更新专利交底书技能...")
                installer.install(force=True)

            elif choice == '4':
                # 检查状态
                target_path = temp_installer.prompt_target_directory()
                if target_path is None:
                    print("取消检查")
                    continue

                installer = PatentSkillInstaller(target_dir=target_path)
                version = installer.get_installed_version()
                if version:
                    print(f"\n✓ 技能已安装")
                    print(f"  版本: {version}")
                    print(f"  目录: {installer.target_dir}")
                else:
                    print("\n⊗ 技能未安装")

        except KeyboardInterrupt:
            print("\n\n操作已取消")
            continue
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            input("\n按回车键继续...")


if __name__ == "__main__":
    main()

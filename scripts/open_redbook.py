#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书创作者平台浏览器启动脚本
支持 macOS 和 Windows 系统
"""

import sys
import platform
import subprocess
import webbrowser

REDBOOK_CREATOR_URL = "https://creator.xiaohongshu.com/new/home"


def get_system_info():
    """获取系统信息"""
    system = platform.system()
    version = platform.version()
    return system, version


def open_with_safari(url):
    """使用 Safari 打开 URL (macOS)"""
    try:
        subprocess.run(
            ["open", "-a", "Safari", url],
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False
    except FileNotFoundError:
        return False


def open_with_default_browser(url):
    """使用系统默认浏览器打开 URL"""
    try:
        webbrowser.open(url)
        return True
    except Exception:
        return False


def open_with_edge(url):
    """使用 Edge 打开 URL (Windows)"""
    try:
        subprocess.run(
            ["start", "msedge", url],
            shell=True,
            check=True,
            capture_output=True
        )
        return True
    except subprocess.CalledProcessError:
        return False


def main():
    system, version = get_system_info()
    print(f"检测到系统: {system}")
    print(f"正在打开小红书创作者平台...")

    success = False

    if system == "Darwin":  # macOS
        # 优先尝试使用 Safari
        success = open_with_safari(REDBOOK_CREATOR_URL)
        if not success:
            print("Safari 启动失败，尝试使用默认浏览器...")
            success = open_with_default_browser(REDBOOK_CREATOR_URL)

    elif system == "Windows":
        # Windows 系统优先使用 Edge
        success = open_with_edge(REDBOOK_CREATOR_URL)
        if not success:
            print("Edge 启动失败，尝试使用默认浏览器...")
            success = open_with_default_browser(REDBOOK_CREATOR_URL)

    else:  # Linux 或其他系统
        success = open_with_default_browser(REDBOOK_CREATOR_URL)

    if success:
        print("浏览器已打开！")
        print(f"访问地址: {REDBOOK_CREATOR_URL}")
        print("\n请在浏览器中登录您的小红书账号，然后开始创作。")
    else:
        print("自动打开浏览器失败。")
        print(f"\n请手动访问: {REDBOOK_CREATOR_URL}")
        sys.exit(1)


if __name__ == "__main__":
    main()

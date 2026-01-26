#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML 转图片脚本
将 HTML 文件转换为 PNG 图片
支持 macOS 和 Windows
"""

import sys
import os
import platform
import subprocess
import argparse
from pathlib import Path


def check_chrome_installed():
    """检查 Chrome 是否安装"""
    system = platform.system()

    if system == "Darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    elif system == "Windows":
        chrome_paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
    else:  # Linux
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
        ]

    for path in chrome_paths:
        if os.path.exists(path):
            return path

    return None


def html_to_png_with_chrome(html_path, output_path, width=1080, height=1920):
    """使用 Chrome headless 模式将 HTML 转为 PNG

    默认尺寸: 1080x1920 (9:16 比例，小红书标准竖版比例)
    直接按原尺寸截图，不做缩放或裁剪
    """
    chrome_path = check_chrome_installed()

    if not chrome_path:
        return False, "Chrome 未安装"

    # 确保路径是绝对路径
    html_path = os.path.abspath(html_path)
    output_path = os.path.abspath(output_path)

    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Chrome headless 截图命令
    # 直接按 1080x1920 截图，保持原图，不做缩放
    cmd = [
        chrome_path,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        f"--window-size={width},{height}",
        f"--screenshot={output_path}",
        "--hide-scrollbars",
        f"file://{html_path}"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        if os.path.exists(output_path):
            return True, output_path
        else:
            return False, f"截图失败: {result.stderr}"

    except subprocess.TimeoutExpired:
        return False, "截图超时"
    except Exception as e:
        return False, str(e)


def convert_all_html_to_png(images_dir):
    """将目录下所有 HTML 文件转换为 PNG"""
    images_dir = Path(images_dir)

    if not images_dir.exists():
        print(f"❌ 目录不存在: {images_dir}")
        return False

    html_files = list(images_dir.glob("*.html"))

    if not html_files:
        print(f"❌ 未找到 HTML 文件: {images_dir}")
        return False

    print(f"找到 {len(html_files)} 个 HTML 文件")

    chrome_path = check_chrome_installed()
    if not chrome_path:
        print("\n❌ 未检测到 Chrome 浏览器")
        print("\n请安装 Google Chrome 后重试：")
        print("  macOS: https://www.google.com/chrome/")
        print("  Windows: https://www.google.com/chrome/")
        print("\n或者手动在浏览器中打开 HTML 文件并截图保存")
        return False

    print(f"使用 Chrome: {chrome_path}")
    print()

    success_count = 0
    for html_file in html_files:
        png_file = html_file.with_suffix(".png")
        print(f"转换: {html_file.name} -> {png_file.name} ...", end=" ")

        success, result = html_to_png_with_chrome(
            str(html_file),
            str(png_file),
            width=1080,
            height=1920
        )

        if success:
            print("✅")
            success_count += 1
            # 删除原 HTML 文件
            # html_file.unlink()
        else:
            print(f"❌ {result}")

    print(f"\n完成: {success_count}/{len(html_files)} 个文件转换成功")
    return success_count == len(html_files)


def main():
    parser = argparse.ArgumentParser(description='HTML 转 PNG 图片工具')
    parser.add_argument('path', type=str, help='HTML 文件或包含 HTML 文件的目录')
    parser.add_argument('--output', '-o', type=str, help='输出文件路径（仅单文件模式）')
    parser.add_argument('--width', '-W', type=int, default=1080, help='图片宽度（默认 1080）')
    parser.add_argument('--height', '-H', type=int, default=1920, help='图片高度（默认 1920，9:16 比例）')

    args = parser.parse_args()
    path = Path(args.path)

    if path.is_dir():
        # 目录模式：转换目录下所有 HTML 文件
        success = convert_all_html_to_png(path)
        sys.exit(0 if success else 1)

    elif path.is_file() and path.suffix.lower() == '.html':
        # 单文件模式
        output = args.output or str(path.with_suffix('.png'))

        success, result = html_to_png_with_chrome(
            str(path),
            output,
            args.width,
            args.height
        )

        if success:
            print(f"✅ 已生成: {result}")
            sys.exit(0)
        else:
            print(f"❌ 转换失败: {result}")
            sys.exit(1)

    else:
        print(f"❌ 无效的路径: {path}")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书创作者平台上传辅助脚本
使用 Chrome 浏览器打开上传页面
支持 macOS 和 Windows 系统
"""

import sys
import os
import json
import platform
import subprocess
import argparse
from pathlib import Path

# 小红书图文上传页面
REDBOOK_UPLOAD_URL = "https://creator.xiaohongshu.com/publish/publish?from=menu&target=image"


def get_system_info():
    """获取系统信息"""
    system = platform.system()
    return system


def check_chrome_installed():
    """检查 Chrome 是否安装，返回 Chrome 路径"""
    system = get_system_info()

    if system == "Darwin":  # macOS
        chrome_paths = [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        ]
        chrome_app = "/Applications/Google Chrome.app"
    elif system == "Windows":
        chrome_paths = [
            os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
            os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
        ]
        chrome_app = None
    else:  # Linux
        chrome_paths = [
            "/usr/bin/google-chrome",
            "/usr/bin/google-chrome-stable",
        ]
        chrome_app = None

    for path in chrome_paths:
        if os.path.exists(path):
            return path, chrome_app if system == "Darwin" else path

    return None, None


def open_chrome(url):
    """使用 Chrome 打开 URL"""
    system = get_system_info()
    chrome_path, chrome_app = check_chrome_installed()

    if not chrome_path:
        return False, "Chrome 未安装"

    try:
        if system == "Darwin":  # macOS
            # 使用 open 命令打开 Chrome
            subprocess.run(
                ["open", "-a", "Google Chrome", url],
                check=True,
                capture_output=True
            )
        elif system == "Windows":
            subprocess.run(
                [chrome_path, url],
                check=True,
                capture_output=True
            )
        else:  # Linux
            subprocess.run(
                [chrome_path, url],
                check=True,
                capture_output=True
            )
        return True, None

    except subprocess.CalledProcessError as e:
        return False, str(e)
    except FileNotFoundError:
        return False, "Chrome 未安装"
    except Exception as e:
        return False, str(e)


def copy_to_clipboard(text):
    """复制文本到剪贴板"""
    system = get_system_info()

    try:
        # 尝试使用 pyperclip
        import pyperclip
        pyperclip.copy(text)
        return True
    except ImportError:
        pass

    try:
        if system == "Darwin":  # macOS
            process = subprocess.Popen(['pbcopy'], stdin=subprocess.PIPE)
            process.communicate(text.encode('utf-8'))
            return True
        elif system == "Windows":
            process = subprocess.Popen(['clip'], stdin=subprocess.PIPE, shell=True)
            process.communicate(text.encode('utf-8'))
            return True
    except Exception:
        pass

    return False


def load_config(config_path):
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ 配置文件不存在: {config_path}")
        return None
    except json.JSONDecodeError:
        print(f"❌ 配置文件格式错误: {config_path}")
        return None


def print_separator():
    """打印分隔线"""
    print("\n" + "=" * 50 + "\n")


def interactive_upload(config):
    """交互式上传流程"""
    title = config.get('title', '')
    content = config.get('content', '')
    tags = config.get('tags', [])
    images = config.get('images', [])

    print_separator()
    print("📱 小红书帖子上传助手")
    print_separator()

    # 检查 Chrome
    chrome_path, _ = check_chrome_installed()
    if not chrome_path:
        print("❌ 未检测到 Chrome 浏览器")
        print("\n请安装 Google Chrome 后重试：")
        print("  下载地址: https://www.google.com/chrome/")
        print(f"\n或手动打开以下链接：")
        print(f"  {REDBOOK_UPLOAD_URL}")
        return

    # 步骤1：打开上传页面
    print("步骤 1/4：打开小红书上传页面...")
    success, error = open_chrome(REDBOOK_UPLOAD_URL)
    if success:
        print("✅ Chrome 已打开")
        print(f"   地址：{REDBOOK_UPLOAD_URL}")
    else:
        print(f"❌ 打开失败: {error}")
        print(f"\n请手动打开：{REDBOOK_UPLOAD_URL}")
        return

    input("\n按回车键继续...")

    print_separator()

    # 步骤2：上传图片
    print("步骤 2/4：上传配图")
    print("\n请按以下顺序上传图片：")
    for i, img in enumerate(images, 1):
        # 将 .html 替换为 .png
        img_png = img.replace('.html', '.png')
        print(f"  {i}. {img_png}")

    input("\n图片上传完成后，按回车键继续...")

    print_separator()

    # 步骤3：填充标题
    print("步骤 3/4：填充标题")
    print(f"\n标题内容：\n{title}")

    if copy_to_clipboard(title):
        print("\n✅ 标题已复制到剪贴板，请在小红书标题框中粘贴 (Cmd+V / Ctrl+V)")
    else:
        print("\n⚠️ 无法自动复制，请手动复制上方标题")

    input("\n标题填充完成后，按回车键继续...")

    print_separator()

    # 步骤4：填充正文
    print("步骤 4/4：填充正文和标签")

    # 组合正文和标签
    tags_text = ' '.join([f'#{tag}' if not tag.startswith('#') else tag for tag in tags])
    full_content = f"{content}\n\n{tags_text}"

    print(f"\n正文内容：\n{'-' * 40}")
    print(full_content[:200] + "..." if len(full_content) > 200 else full_content)
    print(f"{'-' * 40}")

    if copy_to_clipboard(full_content):
        print("\n✅ 正文和标签已复制到剪贴板，请在小红书正文框中粘贴 (Cmd+V / Ctrl+V)")
    else:
        print("\n⚠️ 无法自动复制，请手动复制正文内容")

    print_separator()
    print("🎉 内容准备完成！")
    print("\n请在小红书页面：")
    print("  1. 检查图片顺序是否正确")
    print("  2. 检查标题和正文是否完整")
    print("  3. 点击「发布」按钮")
    print_separator()


def quick_open():
    """快速打开上传页面"""
    print("正在打开小红书图文上传页面...")

    # 检查 Chrome
    chrome_path, _ = check_chrome_installed()
    if not chrome_path:
        print("\n❌ 未检测到 Chrome 浏览器")
        print("\n请先安装 Google Chrome：")
        print("  下载地址: https://www.google.com/chrome/")
        print(f"\n或手动打开以下链接：")
        print(f"  {REDBOOK_UPLOAD_URL}")
        sys.exit(1)

    success, error = open_chrome(REDBOOK_UPLOAD_URL)

    if success:
        print("✅ Chrome 已打开！")
        print(f"访问地址: {REDBOOK_UPLOAD_URL}")
        print("\n请在浏览器中：")
        print("  1. 确认已登录小红书账号")
        print("  2. 上传配图（PNG 格式）")
        print("  3. 填写标题和正文")
        print("  4. 添加标签")
        print("  5. 点击发布")
    else:
        print(f"❌ 打开失败: {error}")
        print(f"\n请手动打开: {REDBOOK_UPLOAD_URL}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='小红书上传辅助工具（使用 Chrome）')
    parser.add_argument('--config', '-c', type=str, help='配置文件路径 (config.json)')
    parser.add_argument('--quick', '-q', action='store_true', help='快速模式：仅打开上传页面')

    args = parser.parse_args()

    if args.quick or not args.config:
        quick_open()
    else:
        config = load_config(args.config)
        if config:
            interactive_upload(config)
        else:
            print("\n切换到快速模式...")
            quick_open()


if __name__ == "__main__":
    main()

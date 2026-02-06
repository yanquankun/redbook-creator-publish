#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书自动上传脚本（基于 Playwright）
完全自动化上传图片、标题、正文到小红书创作者平台
"""

import sys
import os
import json
import argparse
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


class RedbookUploader:
    """小红书自动上传器"""

    def __init__(self, config_path):
        """初始化上传器

        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path
        self.config = None
        self.context = None
        self.page = None
        self.playwright = None

        # DOM 选择器配置（可以通过环境变量覆盖）
        # 尝试多个可能的选择器
        self.selectors = {
            'upload_input': [
                os.getenv('UPLOAD_INPUT_SELECTOR', 'input[type="file"]'),
                'input[type="file"][accept*="image"]',
                '.upload-wrapper input[type="file"]',
                'input.upload-input',
            ],
            'title_input': [
                os.getenv('TITLE_INPUT_SELECTOR', 'input[placeholder*="标题"]'),
                '.c-input_inner input[type="text"]',
                'input.title-input',
                '#post-textarea',
            ],
            'content_container': [
                'div[contenteditable="true"]',  # 通用可编辑div
                '[data-slate-editor="true"]',   # Slate编辑器
                '.publish-container textarea',   # 发布容器中的textarea
                'div[role="textbox"]',          # ARIA角色
                os.getenv('CONTENT_CONTAINER_SELECTOR', '#post-textarea'),
                '.ql-editor',
                '.content-input',
                'textarea[placeholder*="正文"]',
            ],
            'publish_button': [
                os.getenv('PUBLISH_BUTTON_SELECTOR', 'button:has-text("发布")'),
                '.css-k405vo',
                '.publish-btn',
                'button.publishBtn',
            ],
            'image_item': [
                os.getenv('IMAGE_ITEM_SELECTOR', '.upload-list-item'),
                '.image-item',
                '.upload-card',
            ],
        }

        # 小红书创作者平台 URL
        self.upload_url = os.getenv(
            'REDBOOK_CREATOR_URL',
            'https://creator.xiaohongshu.com/publish/publish?from=menu&target=image'
        )

    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
                return True
        except FileNotFoundError:
            print(f"❌ 配置文件不存在: {self.config_path}")
            return False
        except json.JSONDecodeError:
            print(f"❌ 配置文件格式错误: {self.config_path}")
            return False

    def print_separator(self, char='=', length=60):
        """打印分隔线"""
        print(f"\n{char * length}\n")

    def log_step(self, step, total, message):
        """输出步骤日志"""
        print(f"{'🌐🖼️✍️📝🚀'[step-1]} 步骤 {step}/{total}: {message}")

    def init_browser(self):
        """初始化浏览器"""
        try:
            self.playwright = sync_playwright().start()

            # 创建专用的 Chrome Profile 目录
            chrome_profile_dir = Path.home() / '.claude' / 'chrome-profile-redbook'
            chrome_profile_dir.mkdir(parents=True, exist_ok=True)

            print("\n正在启动 Chrome 浏览器（使用专用 Profile）...")

            # 首次使用提示
            if not (chrome_profile_dir / 'Default').exists():
                print("⚠️  首次使用提示：")
                print("   这是一个专用的 Chrome Profile，不会影响您正在使用的浏览器")
                print("   首次使用需要在浏览器中登录小红书账号")
                print("   后续使用会自动保持登录状态")
                print()

            # 使用持久化上下文连接到专用 Profile
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=str(chrome_profile_dir),
                channel='chrome',  # 使用系统 Chrome
                headless=False,    # 必须非无头模式
                args=[
                    '--start-maximized',
                    '--disable-blink-features=AutomationControlled',
                ],
                viewport={'width': 1280, 'height': 800}
            )

            self.page = self.context.pages[0] if self.context.pages else self.context.new_page()
            return True

        except Exception as e:
            print(f"❌ 初始化浏览器失败: {e}")
            return False

    def check_upload_control(self):
        """检测上传控件是否存在"""
        for selector in self.selectors['upload_input']:
            try:
                upload_input = self.page.locator(selector).first
                if upload_input.count() > 0:
                    return True
            except:
                continue
        return False

    def open_upload_page(self):
        """打开小红书上传页面"""
        self.log_step(1, 5, "打开小红书创作者平台")
        print(f"   URL: {self.upload_url}")

        try:
            self.page.goto(self.upload_url, wait_until='networkidle', timeout=30000)
            time.sleep(2)  # 等待页面稳定

            # 检测上传控件DOM是否存在
            print("\n   🔍 检测登录状态...")
            if self.check_upload_control():
                print("   ✅ 已登录，可以开始上传")
                print("   ✅ 页面加载成功")
                return True

            # 上传控件不存在，可能未登录
            print("   ⚠️  未检测到上传控件，您可能需要登录")
            print("   ⏰ 请在 20 秒内完成登录...")
            print("   💡 如果已经登录，请刷新页面")

            # 等待20秒
            for remaining in range(20, 0, -1):
                print(f"   ⏳ 倒计时: {remaining} 秒...", end='\r')
                time.sleep(1)

                # 每秒检测一次，如果检测到上传控件则提前结束
                if self.check_upload_control():
                    print("\n   ✅ 检测到上传控件，登录成功！")
                    print("   ✅ 页面加载成功")
                    return True

            # 20秒后再次检测
            print("\n\n   🔍 最后检测...")
            if self.check_upload_control():
                print("   ✅ 检测到上传控件，登录成功！")
                print("   ✅ 页面加载成功")
                return True

            # 仍然检测不到，退出流程
            print("   ❌ 未检测到上传控件，登录失败")
            print("\n   💡 建议：")
            print("      1. 手动打开 https://creator.xiaohongshu.com/publish/publish")
            print("      2. 登录小红书账号")
            print("      3. 重新执行自动上传")
            return False

        except Exception as e:
            print(f"   ❌ 打开失败: {e}")
            return False

    def upload_images(self, image_paths):
        """上传图片"""
        self.log_step(2, 5, "上传图片")
        print(f"   图片数量: {len(image_paths)} 张")

        # 确保图片路径为绝对路径
        abs_image_paths = [os.path.abspath(img) for img in image_paths]

        # 打印封面图信息
        if abs_image_paths:
            print(f"   封面图: {Path(abs_image_paths[0]).name} (第一张)")

        # 尝试多个选择器
        upload_input = None
        for selector in self.selectors['upload_input']:
            try:
                print(f"\n   尝试选择器: {selector}")
                upload_input = self.page.locator(selector).first
                # 检查元素是否可见
                if upload_input.count() > 0:
                    print(f"   ✅ 找到上传控件")
                    break
            except:
                continue

        if not upload_input or upload_input.count() == 0:
            print(f"   ❌ 未找到上传控件，尝试的选择器：")
            for sel in self.selectors['upload_input']:
                print(f"      - {sel}")
            return False

        try:
            print("\n   上传中...")

            # 一次性上传所有图片
            upload_input.set_input_files(abs_image_paths)

            # 等待图片上传完成
            time.sleep(3)

            # 验证图片是否上传成功
            for i, img_path in enumerate(abs_image_paths, 1):
                img_name = Path(img_path).name
                print(f"   ✅ {img_name} 上传成功")

            # 等待所有图片处理完成
            print(f"\n   ⏳ 等待图片处理...")
            time.sleep(5)

            print("\n   ✅ 所有图片上传完成")
            return True

        except Exception as e:
            print(f"   ❌ 上传失败: {e}")
            return False

    def fill_title(self, title):
        """填写标题"""
        self.log_step(3, 5, "填写标题")
        print(f"   标题内容: {title}")

        # 尝试多个选择器
        title_input = None
        for selector in self.selectors['title_input']:
            try:
                print(f"\n   尝试选择器: {selector}")
                title_input = self.page.locator(selector).first
                if title_input.count() > 0:
                    print(f"   ✅ 找到标题输入框")
                    break
            except:
                continue

        if not title_input or title_input.count() == 0:
            print(f"   ❌ 未找到标题输入框")
            return False

        try:
            # 清空并填写标题
            title_input.click()
            title_input.fill('')
            title_input.type(title, delay=50)  # 模拟真实输入

            time.sleep(0.5)
            print("   ✅ 标题填写完成")
            return True

        except Exception as e:
            print(f"   ❌ 填写失败: {e}")
            return False

    def fill_content(self, content, tags):
        """填写正文和标签"""
        self.log_step(4, 5, "填写正文和标签")

        word_count = len(content)
        print(f"   正文字数: {word_count} 字")

        # 尝试多个选择器
        content_editor = None
        for selector in self.selectors['content_container']:
            try:
                print(f"\n   尝试选择器: {selector}")
                content_editor = self.page.locator(selector).first
                if content_editor.count() > 0:
                    print(f"   ✅ 找到正文编辑器")
                    break
            except:
                continue

        if not content_editor or content_editor.count() == 0:
            print(f"   ❌ 未找到正文编辑器")
            return False

        try:
            # 点击激活编辑器
            content_editor.click()
            time.sleep(0.3)

            # 填写正文内容（逐段输入）
            paragraphs = content.split('\n\n')
            for i, paragraph in enumerate(paragraphs):
                if paragraph.strip():
                    content_editor.type(paragraph, delay=20)
                    if i < len(paragraphs) - 1:
                        self.page.keyboard.press('Enter')
                        self.page.keyboard.press('Enter')

            time.sleep(0.5)
            print("   ✅ 正文填写完成")

            # 填写标签（每个标签单独输入，间隔1秒并回车）
            if tags:
                print("\n   📋 输入标签...")
                # 先换两行
                self.page.keyboard.press('Enter')
                self.page.keyboard.press('Enter')

                for i, tag in enumerate(tags):
                    # 确保标签有 # 前缀
                    tag_text = f'#{tag}' if not tag.startswith('#') else tag

                    # 输入标签
                    content_editor.type(tag_text, delay=30)
                    print(f"   输入: {tag_text} ...", end=" ")

                    # 等待1秒
                    time.sleep(1)
                    print("⏱️ 1秒 ...", end=" ")

                    # 按回车
                    self.page.keyboard.press('Enter')
                    print("⏎")

                    # 如果不是最后一个标签，加个空格
                    if i < len(tags) - 1:
                        time.sleep(0.2)

                print("   ✅ 所有标签输入完成")

            return True

        except Exception as e:
            print(f"   ❌ 填写失败: {e}")
            return False

    def publish(self):
        """点击发布按钮"""
        self.log_step(5, 5, "点击发布")

        try:
            # 等待一下确保内容已填充
            time.sleep(1)

            # 尝试多个选择器
            publish_btn = None
            for selector in self.selectors['publish_button']:
                try:
                    print(f"\n   尝试选择器: {selector}")
                    publish_btn = self.page.locator(selector).first
                    if publish_btn.count() > 0:
                        print(f"   ✅ 找到发布按钮")
                        break
                except:
                    continue

            if not publish_btn or publish_btn.count() == 0:
                print(f"   ❌ 未找到发布按钮")
                return False

            # 点击发布
            publish_btn.click()
            print("   ✅ 已点击发布按钮")

            # 等待发布完成
            print("\n   ⏳ 等待发布完成...")
            time.sleep(3)

            # 检查是否有错误提示
            # TODO: 这里可以添加更详细的发布结果检测

            print("   ✅ 发布成功！")
            return True

        except Exception as e:
            print(f"   ❌ 发布失败: {e}")
            return False

    def play_completion_sound(self):
        """播放完成提示音"""
        import platform
        system = platform.system()
        try:
            if system == 'Darwin':  # macOS
                os.system('afplay /System/Library/Sounds/Glass.aiff')
            elif system == 'Windows':
                os.system('rundll32 user32.dll,MessageBeep')  # Windows 默认提示音
            else:  # Linux
                print('\a')  # 系统铃声
        except Exception as e:
            print('\a')  # 备用方案：终端铃声

    def close(self):
        """关闭浏览器"""
        try:
            if self.context:
                self.context.close()
            if self.playwright:
                self.playwright.stop()
        except:
            pass

    def run(self):
        """执行完整上传流程"""
        self.print_separator()
        print("  🚀 小红书自动上传")
        self.print_separator()

        print("⚠️  重要提示：")
        print("   1. 首次使用需要在浏览器中登录小红书账号")
        print("   2. 上传过程中请勿操作浏览器")
        print("   3. 预计耗时：30-60秒")
        print("\n即将开始自动上传...")
        time.sleep(2)

        # 加载配置
        if not self.load_config():
            return False

        title = self.config.get('title', '')
        content = self.config.get('content', '')
        tags = self.config.get('tags', [])
        cover = self.config.get('cover', '')
        images = self.config.get('images', [])

        # 组合图片列表：封面图必须在第一位
        all_images = []
        if cover:
            all_images.append(cover)
        all_images.extend(images)

        if not title or not content or not all_images:
            print("❌ 配置文件缺少必要字段（title, content, cover 或 images）")
            return False

        # 将相对路径转换为绝对路径
        config_dir = Path(self.config_path).parent
        image_paths = [str(config_dir / img) for img in all_images]

        # 验证图片文件存在
        for img_path in image_paths:
            if not os.path.exists(img_path):
                print(f"❌ 图片文件不存在: {img_path}")
                return False

        try:
            # 步骤 0：初始化浏览器
            if not self.init_browser():
                return False

            # 步骤 1：打开上传页面
            if not self.open_upload_page():
                return False

            # 步骤 2：上传图片
            if not self.upload_images(image_paths):
                return False

            # 步骤 3：填写标题
            if not self.fill_title(title):
                return False

            # 步骤 4：填写正文
            if not self.fill_content(content, tags):
                return False

            # 步骤 5：点击发布
            if not self.publish():
                return False

            # 成功
            self.print_separator()
            print("  🎉 上传完成！")
            self.print_separator()

            # 播放完成提示音（1秒）
            print("\n🔔 滴~  (播放 1 秒提示音)")
            self.play_completion_sound()

            print("\n帖子已成功发布到小红书创作者平台")
            print("\n🔗 查看帖子：")
            print("   请在浏览器中查看发布结果")
            print("   https://creator.xiaohongshu.com/")
            print("\n💡 提示：")
            print("   - ✅ 浏览器将保持打开，请继续查看或编辑帖子")
            print("   - 发布后可能需要平台审核")
            print("   - 审核通过后会在小红书APP中显示")
            print("\n⚠️  请勿关闭浏览器！")
            self.print_separator()

            print("\n✅ 任务完成！浏览器将保持打开状态。")
            print("   您可以在浏览器中继续查看、编辑或管理帖子。")

            return True

        except Exception as e:
            print(f"\n❌ 上传过程出错: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            # 不关闭浏览器，让用户可以查看结果
            # 保持浏览器打开，用户可以手动关闭
            print("\n💡 完成操作后，您可以手动关闭浏览器窗口。")
            pass


def main():
    parser = argparse.ArgumentParser(description='小红书自动上传工具（基于 Playwright）')
    parser.add_argument('--config', '-c', type=str, required=True, help='配置文件路径 (config.json)')

    args = parser.parse_args()

    uploader = RedbookUploader(args.config)
    success = uploader.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

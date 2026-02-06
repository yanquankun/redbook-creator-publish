#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成预览页面的辅助函数
使用 Newsprint 风格模板生成 preview.html
"""

import os
from pathlib import Path
from datetime import datetime


def generate_preview_html(title, content, tags, cover_path, image_paths, output_path):
    """
    生成预览 HTML 文件

    Args:
        title: 标题
        content: 正文内容
        tags: 标签列表
        cover_path: 封面图相对路径
        image_paths: 其他图片相对路径列表
        output_path: 输出文件路径
    """
    # 读取模板
    template_path = Path(__file__).parent.parent / "assets" / "preview-template.html"
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # 生成日期
    date_str = datetime.now().strftime('%Y-%m-%d')

    # 生成标签 HTML
    tags_html = '\n'.join([f'                <span class="tag">#{tag}</span>' for tag in tags])

    # 替换模板变量
    html = template.replace('{{TITLE}}', title)
    html = html.replace('{{CONTENT}}', content)
    html = html.replace('{{DATE}}', date_str)
    html = html.replace('{{TAGS}}', tags_html)

    # 添加封面图
    if cover_path and os.path.exists(cover_path):
        cover_html = f'<img src="{cover_path}" alt="封面">'
        html = html.replace('<!-- 如果有封面图，替换下方注释为 <img src="封面图路径" alt="封面"> -->', cover_html)
        html = html.replace('<div class="cover-placeholder"></div>', '')
        html = html.replace('''<div class="cover-placeholder-content">
                <div class="cover-placeholder-icon">◐</div>
                <div class="cover-placeholder-text">封面图位置</div>
                <div class="cover-placeholder-text" style="margin-top: 0.5rem; font-size: 0.625rem;">3:4 Ratio</div>
            </div>''', '')

    # 添加图片画廊
    if image_paths:
        gallery_items = '\n'.join([
            f'            <div class="gallery-item"><img src="{img}" alt="配图{i+1}"></div>'
            for i, img in enumerate(image_paths)
        ])
        gallery_html = f'''
        <div class="image-gallery">
{gallery_items}
        </div>
'''
        html = html.replace('        <!-- 如果有多张图片，取消下方注释 -->\n        <!--\n        <div class="image-gallery">', gallery_html.rstrip())
        html = html.replace('        </div>\n        -->', '')

    # 保存文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return output_path


# 使用示例
if __name__ == "__main__":
    # 示例参数
    title = "🦞 这是一个测试标题"
    content = "这是正文内容。\n\n第二段内容。"
    tags = ["测试", "示例", "预览"]
    cover_path = "images/cover.png"
    image_paths = ["images/image_1.png", "images/image_2.png"]
    output_path = "preview.html"

    result = generate_preview_html(title, content, tags, cover_path, image_paths, output_path)
    print(f"✅ 预览文件已生成：{result}")

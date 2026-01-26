# 小红书帖子创作与发布技能

专业的小红书内容创作与自动发布工具。

## 功能介绍

这个技能可以帮你：

1. **生成优质小红书内容**：基于话题搜索生成标题、正文（300-500字）、标签
2. **自动生成配图**：3-6张 PNG 格式配图（Newsprint 报纸风格）
3. **自动上传发布**：使用 Playwright 自动上传到小红书创作者平台

## 生成的文件

```
redbook-article/
└── [话题]-[日期]/
    ├── [话题]-[日期].html      # 预览文件（可在浏览器打开查看）
    ├── [话题]-[日期].md        # Markdown 文档
    ├── [话题]-[日期].txt       # 纯文本（可直接复制）
    ├── images/                 # 配图文件夹
    │   ├── cover.png          # 封面图
    │   ├── content-1.png      # 内容图
    │   └── ...
    └── config.json            # 配置信息
```

## 前置环境

### 必需

- **Python 3+**：浏览器自动化需要 Python 环境
  ```bash
  # macOS
  brew install python3

  # Windows
  # 访问 https://www.python.org/ 下载安装（勾选 Add to PATH）

  # 验证
  python3 --version
  ```

### 首次使用自动安装

- **Playwright**：Python 浏览器自动化库（首次使用时自动安装，约 1-2 分钟）

### 可选

- **Google Chrome**：用于 HTML 转 PNG 配图功能
  - [下载 Chrome](https://www.google.com/chrome/)
  - 如未安装，Playwright 会使用自带的 Chromium 进行上传

## 使用方法

```bash
# 在 Claude Code 中直接调用
/redbook-creator-publish 分享一个提高工作效率的AI工具
```

## 自动上传说明

- **首次使用**：浏览器会自动打开，需要手动登录小红书账号
- **后续使用**：Playwright 会记住登录状态，无需重复登录
- **上传过程**：自动填写标题、正文、标签，上传图片，点击发布
- **失败降级**：如果自动上传失败，会提供详细的手动上传指引

## 常见问题

### Python 版本过低

```
❌ 未检测到 Python 3+ 环境
```

解决：安装 Python 3.0 或更高版本

### Playwright 安装失败

```bash
# 手动安装
pip3 install playwright
playwright install chromium
```

### 自动上传失败

可能原因：
1. 未登录小红书账号
2. 网络连接问题
3. 小红书平台更新了页面结构

解决：查看错误提示，使用生成的 .txt 文件手动上传

## 技术栈

- [Playwright for Python](https://playwright.dev/python/) - 浏览器自动化
- Python 3+ - 脚本运行环境
- Chrome/Chromium - 配图转换和自动化

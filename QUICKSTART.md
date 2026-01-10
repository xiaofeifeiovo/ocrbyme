# OCRByMe 快速入门指南

## 🎯 项目概述

OCRByMe 是一个简洁高效的 PDF 转 Markdown OCR 工具,使用阿里云 Qwen3-VL-Flash API 进行文档识别。

### 核心特性

- ✅ **高精度 OCR**: 使用 Qwen3-VL-Flash,支持复杂布局(多栏、表格)
- ✅ **保留格式**: Markdown 输出,保留原始文档结构
- ✅ **图片提取**: 自动提取并保存 PDF 中的嵌入图片
- ✅ **简单易用**: 一个命令完成转换
- ✅ **进度显示**: 实时显示处理进度

## 📋 系统要求

### 必需

- **Python**: 3.10 或更高版本
- **Poppler**: PDF 处理依赖

### 可选

- **pypdf**: 用于快速获取 PDF 页数 (推荐安装)

## 🚀 快速安装

### 1. 检查 Python 版本

```bash
python --version
```

确保版本 >= 3.10。

### 2. 安装 Poppler

**Windows**:

使用 Chocolatey:
```powershell
choco install poppler
```

或手动下载: [poppler-windows](http://blog.alivate.com.au/poppler-windows/)

**Linux (Ubuntu/Debian)**:
```bash
sudo apt-get update
sudo apt-get install poppler-utils
```

**macOS**:
```bash
brew install poppler
```

### 3. 克隆项目

```bash
git clone https://github.com/xiaofeifei/ocrbyme.git
cd ocrbyme
```

### 4. 创建虚拟环境

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate
```

### 5. 安装依赖

```bash
# 安装核心依赖
pip install -e .

# (可选) 安装开发依赖
pip install -e ".[dev]"

# (可选) 安装 pypdf (推荐)
pip install pypdf
```

### 6. 配置 API Key

```bash
# 复制环境变量模板
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/macOS

# 编辑 .env 文件
notepad .env  # Windows
# nano .env   # Linux/macOS
```

在 `.env` 文件中设置:

```bash
DASHSCOPE_API_KEY=你的API密钥
```

#### 获取 API Key

1. 访问 [阿里云百炼控制台](https://bailian.console.aliyun.com/)
2. 开通服务
3. 创建 API Key
4. 复制 API Key 到 `.env` 文件

## 📖 使用方法

### 基本用法

```bash
# 最简单的用法 (自动生成 input.md)
ocrbyme document.pdf

# 指定输出文件
ocrbyme document.pdf -o output.md

# 处理特定页面
ocrbyme document.pdf --pages 1-10
ocrbyme document.pdf --pages 1,3,5-7

# 高分辨率模式 (适合复杂布局,但速度较慢)
ocrbyme document.pdf --dpi 300

# 只转换前 3 页,不提取图片
ocrbyme document.pdf --first-page 1 --last-page 3 --no-extract-images

# 显示详细日志
ocrbyme document.pdf --verbose
```

### 命令行选项

```
Usage: ocrbyme [OPTIONS] INPUT_PDF

  PDF 转 Markdown OCR 工具 - 使用 Qwen3-VL-Flash API

Options:
  -o, --output PATH              输出 Markdown 文件路径
                                  (默认: input_pdf.md)

  --pages TEXT                   页码范围
                                  例如: '1-5' 或 '1,3,5-7'

  --dpi INTEGER                  PDF 转图像的 DPI
                                  默认: 200 (推荐: 150-300)

  --first-page INTEGER           起始页码 (从 1 开始)

  --last-page INTEGER            结束页码

  --no-extract-images            不提取和保存嵌入的图片

  --timeout INTEGER              API 请求超时 (秒)
                                  默认: 60

  -v, --verbose                  显示详细日志

  --help                         显示帮助信息

  --version                      显示版本信息
```

## 📝 输出示例

### 输入

```bash
ocrbyme document.pdf --pages 1-3 --dpi 200
```

### 处理过程

```
🚀 OCRByMe - PDF 转 Markdown OCR 工具
版本: 0.1.0

📄 PDF 文件: document.pdf
📑 总页数: 10
📖 处理页数: 3 页
   页码: 1, 2, 3
📁 输出文件: document.md

📷 步骤 1/3: 转换 PDF 为图像...
████████████████████████████████████████ 100%
✅ 转换完成: 3 页

🤖 步骤 2/3: OCR 处理...
████████████████████████████████████████ 100%
✅ OCR 处理完成

📝 步骤 3/3: 生成 Markdown...
✅ Markdown 文件已生成: document.md

==================================================
╭────────────────────────────────╮
│         ✅ 转换成功!            │
│                                │
│ 📄 输入文件: document.pdf      │
│ 📝 输出文件: document.md        │
│ 📑 处理页数: 3                  │
│ 🖼️  提取图片: 是                │
╰────────────────────────────────╯
```

### 生成的 Markdown (document.md)

\`\`\`markdown
# 文档

> 由 OCRByMe 生成
> 来源: document.pdf
> 页数: 3
> 生成时间: 2025-01-10 20:30:00

---

## 第 1 页

# 第一章

这是第一页的内容...

---

## 第 2 页

## 表格示例

| 列 1 | 列 2 | 列 3 |
|------|------|------|
| 数据 1 | 数据 2 | 数据 3 |

![图表](document_images/page_2_img_1.png)

表格说明文字...

---

## 第 3 页

## 结论

总结内容...

---

<!-- 文档结束 -->
\`\`\`

## 🔧 高级用法

### 批量处理

```bash
# 处理多个 PDF (Windows)
for %f in (*.pdf) do ocrbyme "%f" -o "%~nf.md"

# 处理多个 PDF (Linux/macOS)
for f in *.pdf; do ocrbyme "$f" -o "${f%.pdf}.md"; done
```

### 自定义配置

在 `.env` 文件中添加:

```bash
# API 配置
DASHSCOPE_API_KEY=你的API密钥
OCRBYME_MODEL_NAME=qwen3-vl-flash
OCRBYME_TIMEOUT=60

# PDF 处理配置
OCRBYME_DEFAULT_DPI=200

# 输出配置
OCRBYME_IMAGE_SUBDIR=images
```

### Python API 使用

```python
from pathlib import Path
from ocrbyme.core import PDFProcessor, QwenVLClient, MarkdownGenerator

# 初始化组件
pdf_processor = PDFProcessor(dpi=200)
ocr_client = QwenVLClient()
markdown_gen = MarkdownGenerator(output_dir=Path("./output"))

# 处理流程
pdf_path = Path("document.pdf")
images = pdf_processor.convert_to_images(pdf_path, first_page=1, last_page=1)

# 保存临时图像
import tempfile
with tempfile.TemporaryDirectory() as temp_dir:
    temp_path = Path(temp_dir)
    img_path = temp_path / "page_1.png"
    images[0].save(img_path)

    # OCR 识别
    markdown_text = ocr_client.ocr_image(img_path)

# 生成 Markdown
output_path = markdown_gen.generate(
    [markdown_text],
    metadata={"source": str(pdf_path), "page_count": 1}
)

print(f"✅ 完成: {output_path}")
```

## 🐛 故障排除

### 1. "Poppler 未找到" 错误

**问题**: `pdf2image.pdftoppm_error: Unable to get page count`

**解决方案**:
- Windows: 安装 Poppler 并添加到 PATH
- Linux: `sudo apt-get install poppler-utils`
- macOS: `brew install poppler`

### 2. "API Key 未设置" 错误

**问题**: `DASHSCOPE_API_KEY 未设置`

**解决方案**:
```bash
# 检查环境变量
echo %DASHSCOPE_API_KEY%  # Windows
echo $DASHSCOPE_API_KEY   # Linux/macOS

# 或检查 .env 文件
cat .env
```

### 3. "API 认证失败" 错误

**问题**: `API 认证失败,请检查 API Key`

**解决方案**:
- 确认 API Key 是否正确
- 确认 API Key 已开通百炼服务
- 确认账户余额充足

### 4. OCR 识别不准确

**解决方案**:
```bash
# 提高分辨率
ocrbyme document.pdf --dpi 300

# 确保使用高分辨率模式 (默认启用)
# 检查 .env 文件中是否有 OCRBYME_HIGH_RESOLUTION=true
```

### 5. 处理速度慢

**原因**: DPI 设置过高或页数过多

**解决方案**:
```bash
# 降低 DPI
ocrbyme document.pdf --dpi 150

# 减少处理页数
ocrbyme document.pdf --pages 1-5
```

## 📚 更多资源

- [完整文档](README.md)
- [MCP 部署教程](CLAUDE_CODE_DEPLOYMENT.md)
- [测试文档](TESTING_SUMMARY.md)
- [项目计划](.claude/plans/concurrent-kindling-pike.md)
- [阿里云百炼文档](https://help.aliyun.com/zh/model-studio/vision)
- [Qwen3-VL GitHub](https://github.com/QwenLM/Qwen3-VL)

## 🤖 在 Claude Code 中使用（MCP 服务器）

### 快速配置（3 步）

#### 步骤 1：安装 MCP 支持

```bash
pip install -e ".[mcp]"
```

#### 步骤 2：配置 Claude Code

**Windows** - 打开配置文件：
```powershell
notepad "%APPDATA%\Claude\claude_desktop_config.json"
```

**macOS / Linux**：
```bash
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

添加以下配置：
```json
{
  "mcpServers": {
    "ocrbyme": {
      "command": "ocrbyme-mcp",
      "env": {
        "DASHSCOPE_API_KEY": "sk-你的实际API密钥"
      }
    }
  }
}
```

#### 步骤 3：重启 Claude Code 并使用

重启后在对话中使用：
```
你：帮我把 C:\Documents\report.pdf 转换成 Markdown

Claude：[调用 pdf_to_markdown 工具]
      转换完成！
      - 输出文件：C:\Documents\report.md
      - 处理页数：15 页
      - 提取图片：8 张
```

### MCP 可用功能

- ✅ **PDF 转 Markdown**：完整转换流程
- ✅ **页码范围**：指定转换页面
- ✅ **自定义 DPI**：控制分辨率
- ✅ **图片提取**：自动提取 PDF 图片
- ✅ **批量处理**：处理多个文件

### 详细的 MCP 配置教程

查看 [CLAUDE_CODE_DEPLOYMENT.md](CLAUDE_CODE_DEPLOYMENT.md) 获取：
- 多种配置方式
- 高级选项
- 故障排除
- 性能优化建议

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

## 📄 许可证

MIT License

---

**享受使用 OCRByMe!** 🎉

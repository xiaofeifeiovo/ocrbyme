# OCRByMe

PDF 转 Markdown OCR 工具 - 使用 Qwen3-VL-Flash API

## 功能特性

- ✅ 将整个 PDF 文件转换为 Markdown 文件
- ✅ 处理 PDF 的每一页作为图像
- ✅ 从 PDF 中提取文本和嵌入的图片
- ✅ 保留原始布局(多栏、表格等复杂结构)
- ✅ 图片嵌入到 Markdown 中
- ✅ 使用 Qwen3-VL-Flash 高精度 OCR

## 安装

### 前置要求

- Python 3.10+
- Poppler (pdf2image 依赖)

**Windows**: 安装 [poppler-utils](http://blog.alivate.com.au/poppler-windows/)
```powershell
# 使用 chocolatey
choco install poppler
```

**Linux**:
```bash
sudo apt-get install poppler-utils
```

**macOS**:
```bash
brew install poppler
```

### 安装 OCRByMe

```bash
# 克隆项目
git clone https://github.com/xiaofeifei/ocrbyme.git
cd ocrbyme

# 创建虚拟环境
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS

# 安装依赖
pip install -e .

# 配置 API Key
cp .env.example .env
# 编辑 .env 文件,填入你的 DASHSCOPE_API_KEY
```

## 使用

### 基本用法

```bash
# 最简单的用法 (输出为 input.md)
ocrbyme document.pdf

# 指定输出文件
ocrbyme document.pdf -o output.md

# 处理特定页面
ocrbyme document.pdf --pages 1-10
ocrbyme document.pdf --pages 1,3,5-7

# 高分辨率模式 (适合复杂布局)
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
  --pages TEXT                   页码范围,例如 '1-5' 或 '1,3,5-7'
  --dpi INTEGER                  PDF 转图像的 DPI (默认: 200)
  --first-page INTEGER           起始页码
  --last-page INTEGER            结束页码
  --no-extract-images            不提取和保存嵌入的图片
  --timeout INTEGER              API 请求超时 (秒,默认: 60)
  -v, --verbose                  显示详细日志
  --help                         显示帮助信息
  --version                      显示版本信息
```

## 配置

### 环境变量

在 `.env` 文件中配置:

```bash
# 必需: Qwen3-VL-Flash API Key
DASHSCOPE_API_KEY=your_api_key_here

# 可选配置
# OCRBYME_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
# OCRBYME_MODEL_NAME=qwen3-vl-flash
# OCRBYME_DEFAULT_DPI=200
# OCRBYME_TIMEOUT=60
```

### 获取 API Key

1. 访问 [阿里云百炼控制台](https://bailian.console.aliyun.com/)
2. 开通服务并创建 API Key
3. 将 API Key 配置到 `.env` 文件中

## 示例

### 输入 PDF

假设你有一个 `document.pdf` 文件,包含 3 页,其中有表格和图片。

### 运行转换

```bash
ocrbyme document.pdf --pages 1-3 --dpi 200
```

### 输出 Markdown

生成的 `document.md`:

\`\`\`markdown
# Document Title

> 由 OCRByMe 生成
> 来源: document.pdf
> 页数: 3
> 生成时间: 2025-01-10 20:30:00

---

## 第 1 页

# Introduction

This is the first page of the document with some text.

---

## 第 2 页

## Table Example

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

![示意图](document_images/page_2_img_1.png)

The table above shows some data.

---

## 第 3 页

## Conclusion

This is the final page with a summary.

---

<!-- 文档结束 -->
\`\`\`

### 生成的图片

```
document_images/
├── page_2_img_1.png
└── ...
```

## 技术细节

### OCR 模型

- **模型**: Qwen3-VL-Flash
- **API**: 阿里云百炼 OpenAI 兼容接口
- **高分辨率模式**: 启用 `vl_high_resolution_images=True` 提升识别精度
- **Markdown 模式**: 使用提示词 `"qwenvl markdown"` 触发格式化输出

### PDF 处理

- **库**: pdf2image (封装 Poppler)
- **默认 DPI**: 200 (平衡质量和速度)
- **输出格式**: PNG (无损)

## MCP 服务器支持

OCRByMe 可以作为 [MCP (Model Context Protocol)](https://modelcontextprotocol.io/) 服务器运行，允许 AI 助手（如 Claude Desktop、Cursor）直接调用 PDF 转 Markdown 功能。

### 安装 MCP 支持

```bash
# 安装基础功能 + MCP 支持
pip install -e ".[mcp]"

# 或安装所有功能（开发 + MCP）
pip install -e ".[all]"
```

### 使用 MCP Inspector 调试

```bash
# 设置 API Key
set DASHSCOPE_API_KEY=your_api_key_here

# 启动 MCP Inspector
npx @modelcontextprotocol/inspector ocrbyme-mcp
```

Inspector 会自动打开浏览器界面，你可以测试 `pdf_to_markdown` 工具的调用。

### Claude Desktop 配置

编辑 Claude Desktop 配置文件：

- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

添加以下配置：

```json
{
  "mcpServers": {
    "ocrbyme": {
      "command": "ocrbyme-mcp",
      "env": {
        "DASHSCOPE_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

如果使用虚拟环境，可以指定完整路径：

```json
{
  "mcpServers": {
    "ocrbyme": {
      "command": "venv\\Scripts\\python.exe",
      "args": ["-m", "ocrbyme.mcp_server"],
      "env": {
        "DASHSCOPE_API_KEY": "your_api_key_here",
        "PYTHONPATH": "C:\\Users\\xiaofeifei\\Desktop\\workspace\\ocrbyme\\src"
      }
    }
  }
}
```

重启 Claude Desktop 后即可在对话中使用 PDF 转换功能：

```
你：帮我把 C:\docs\report.pdf 转换成 Markdown 格式
Claude：[调用 pdf_to_markdown 工具] 已完成转换，生成了 report.md，共 15 页...
```

### 可用工具

MCP 服务器提供以下工具：

#### `pdf_to_markdown`
将 PDF 文件转换为 Markdown 格式

**参数**：
- `pdf_path` (必需): PDF 文件的绝对路径
- `output_path` (可选): 输出 Markdown 文件路径，默认为 input_pdf.md
- `pages` (可选): 页码范围，例如 "1-5" 或 "1,3,5-7"
- `dpi` (可选): PDF 转图像的 DPI，默认 200（范围：72-600）
- `extract_images` (可选): 是否提取 PDF 嵌入图片，默认 true
- `timeout` (可选): API 请求超时时间（秒），默认 60

**返回**：JSON 格式的处理结果
```json
{
  "success": true,
  "output_path": "C:\\docs\\report.md",
  "page_count": 15,
  "images_extracted": 8
}
```

### 在其他 AI 工具中使用

#### Cursor

在 Cursor 的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "ocrbyme": {
      "command": "ocrbyme-mcp",
      "env": {
        "DASHSCOPE_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

#### Cline (VSCode 插件)

在 Cline 的 MCP 配置中添加相同的配置。

## 开发

### 运行测试

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 运行测试并查看覆盖率
pytest --cov=ocrbyme
```

### 代码格式化

```bash
# 使用 Black 格式化代码
black src/ tests/

# 使用 Ruff 检查代码
ruff check src/ tests/

# 使用 MyPy 进行类型检查
mypy src/
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request!

## 致谢

- [Qwen3-VL](https://github.com/QwenLM/Qwen3-VL) - 阿里通义千问视觉语言模型
- [pdf2image](https://github.com/Belval/pdf2image) - PDF 转图像工具
- [Click](https://click.palletsprojects.com/) - Python CLI 框架
- [Rich](https://rich.readthedocs.io/) - 终端美化库

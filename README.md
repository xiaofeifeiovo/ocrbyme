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

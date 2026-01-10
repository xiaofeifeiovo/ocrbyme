# 测试夹具说明

此目录用于存放测试过程中使用的各种测试文件。

## 文件说明

### test_document.pdf
用于测试 MCP 服务器功能的示例 PDF 文件。

如果你没有此文件，可以：

1. 创建一个简单的 PDF 文件
2. 从其他地方复制一个 PDF 文件
3. 或者跳过需要真实 PDF 的集成测试

### 生成测试 PDF

你可以使用以下 Python 脚本生成一个简单的测试 PDF：

```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_pdf(filename="test_document.pdf"):
    c = canvas.Canvas(filename, pagesize=letter)

    # 第一页
    c.drawString(100, 750, "Test Document - Page 1")
    c.drawString(100, 700, "This is a test PDF for OCRByMe MCP server testing.")

    # 添加一些简单的内容
    for i in range(5):
        c.drawString(100, 650 - i*30, f"Line {i+1}: This is test content.")

    c.showPage()

    # 第二页
    c.drawString(100, 750, "Test Document - Page 2")
    c.drawString(100, 700, "More test content on the second page.")

    c.save()

if __name__ == "__main__":
    create_test_pdf("tests/fixtures/test_document.pdf")
```

或者使用你现有的任何 PDF 文件。

## 注意事项

- 不要在此目录中放入包含敏感信息的 PDF
- 测试 PDF 应该尽可能小（几页即可）
- 确保测试 PDF 可以正常读取

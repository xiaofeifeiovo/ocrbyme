"""创建测试 PDF 文件 - 简化版"""

from pathlib import Path

from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
    Image as RLImage,
    PageBreak,
    Paragraph,
)
from reportlab.lib import colors


def create_test_image(output_path: Path) -> None:
    """创建一个测试图片"""
    img = Image.new("RGB", (600, 300), color="#f0f0f0")
    draw = ImageDraw.Draw(img)

    # 绘制背景
    draw.rectangle([0, 0, 600, 300], fill="#4A90E2")

    # 绘制形状
    draw.ellipse([50, 50, 250, 250], fill="#FF6B6B")
    draw.rectangle([350, 50, 550, 250], fill="#4ECDC4")

    # 添加文字
    try:
        from PIL import ImageFont
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    draw.text((300, 150), "Test Image", fill="white", font=font, anchor="mm")
    img.save(output_path)


def create_test_pdf(output_path: Path) -> None:
    """创建测试 PDF 文件"""
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # 第 1 页: 标题
    elements.append(Paragraph("OCRByMe Test Document", styles['Heading1']))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("This is a test document for OCR functionality.", styles['Normal']))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Features:", styles['Heading2']))
    elements.append(Paragraph("- Title and paragraphs", styles['Normal']))
    elements.append(Paragraph("- Images and graphics", styles['Normal']))
    elements.append(Paragraph("- Tables", styles['Normal']))
    elements.append(Paragraph("- Mixed language content", styles['Normal']))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(PageBreak())

    # 第 2 页: 图片
    elements.append(Paragraph("Chapter 2: Images", styles['Heading1']))
    elements.append(Spacer(1, 0.2 * inch))

    # 创建测试图片
    img_path = Path("test_image.png")
    create_test_image(img_path)

    img = RLImage(str(img_path), width=5 * inch, height=2.5 * inch)
    elements.append(img)
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Figure 1: Test image with shapes", styles['Normal']))
    elements.append(PageBreak())

    # 第 3 页: 表格
    elements.append(Paragraph("Chapter 3: Tables", styles['Heading1']))
    elements.append(Spacer(1, 0.2 * inch))

    table_data = [
        ["Product", "Price", "Stock", "Status"],
        ["OCRByMe Pro", "$99.00", "100", "Available"],
        ["OCRByMe Basic", "$49.00", "200", "Available"],
        ["OCRByMe Free", "$0.00", "Unlimited", "Available"],
    ]

    table = Table(table_data, colWidths=[2.5 * inch, 1.5 * inch, 1.5 * inch, 1 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(PageBreak())

    # 第 4 页: 中英文混合
    elements.append(Paragraph("Chapter 4: Mixed Language", styles['Heading1']))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("OCRByMe supports multiple languages including Chinese, English, and Japanese.", styles['Normal']))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("中文测试: OCRByMe 支持中文识别", styles['Normal']))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("日本語テスト: OCRByMeは日本語をサポートしています", styles['Normal']))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(PageBreak())

    # 第 5 页: 总结
    elements.append(Paragraph("Chapter 5: Summary", styles['Heading1']))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Key Features:", styles['Heading2']))
    elements.append(Paragraph("1. High accuracy OCR using Qwen3-VL-Flash", styles['Normal']))
    elements.append(Paragraph("2. Markdown format output", styles['Normal']))
    elements.append(Paragraph("3. Automatic image extraction", styles['Normal']))
    elements.append(Paragraph("4. Simple to use - one command", styles['Normal']))
    elements.append(Paragraph("5. Support for 33 languages", styles['Normal']))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph("Get started: ocrbyme your_document.pdf", styles['Normal']))

    # 构建 PDF
    doc.build(elements)

    # 清理临时图片
    if img_path.exists():
        img_path.unlink()

    print(f"✅ Test PDF created: {output_path}")
    print(f"📄 Contains 5 pages:")
    print("   - Page 1: Title and introduction")
    print("   - Page 2: Images")
    print("   - Page 3: Tables")
    print("   - Page 4: Mixed language")
    print("   - Page 5: Summary")


if __name__ == "__main__":
    output_path = Path("test_document.pdf")
    create_test_pdf(output_path)

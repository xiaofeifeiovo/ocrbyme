"""创建更丰富的测试 PDF 文件"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
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
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def create_colorful_image1(output_path: Path) -> None:
    """创建测试图片1 - 渐变背景"""
    img = Image.new("RGB", (800, 400), color="#ffffff")
    draw = ImageDraw.Draw(img)

    # 绘制渐变背景 (简化版)
    for i in range(400):
        color = int(255 * (1 - i / 400))
        draw.rectangle([0, i, 800, i + 1], fill=(color, int(color * 0.8), 255))

    # 绘制圆形
    draw.ellipse([100, 100, 300, 300], fill="#FF6B6B", outline="#ffffff", width=5)
    draw.ellipse([200, 150, 400, 350], fill="#4ECDC4", outline="#ffffff", width=5)

    # 添加文字
    try:
        font = ImageFont.truetype("arial.ttf", 60)
    except:
        font = ImageFont.load_default()

    draw.text((400, 200), "OCR Test", fill="white", font=font, anchor="mm")
    img.save(output_path)


def create_colorful_image2(output_path: Path) -> None:
    """创建测试图片2 - 图表样式"""
    img = Image.new("RGB", (800, 400), color="#f8f9fa")
    draw = ImageDraw.Draw(img)

    # 绘制柱状图
    bars = [
        (100, 300, 150, "#FF6B6B", "Item A"),
        (200, 250, 200, "#4ECDC4", "Item B"),
        (300, 200, 250, "#45B7D1", "Item C"),
        (400, 280, 180, "#96CEB4", "Item D"),
        (500, 220, 220, "#FECA57", "Item E"),
    ]

    for x, h, w, color, label in bars:
        draw.rectangle([x, 350 - h, x + w, 350], fill=color)
        # 添加标签
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        draw.text((x + w // 2, 370), label, fill="#333", font=font, anchor="mm")

    # 添加标题
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()
    draw.text((400, 50), "Sales Chart 2024", fill="#2c3e50", font=font, anchor="mm")

    img.save(output_path)


def create_colorful_image3(output_path: Path) -> None:
    """创建测试图片3 - 几何图形"""
    img = Image.new("RGB", (800, 400), color="#ecf0f1")
    draw = ImageDraw.Draw(img)

    # 绘制各种几何图形
    draw.rectangle([50, 50, 350, 350], fill="#3498db", outline="#2980b9", width=3)
    draw.ellipse([400, 50, 750, 350], fill="#e74c3c", outline="#c0392b", width=3)

    # 绘制三角形
    draw.polygon([(200, 50), (100, 200), (300, 200)], fill="#2ecc71", outline="#27ae60", width=3)

    # 添加文字说明
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()

    draw.text((400, 380), "Geometric Shapes", fill="#2c3e50", font=font, anchor="mm")

    img.save(output_path)


def create_enriched_test_pdf(output_path: Path) -> None:
    """创建丰富的测试 PDF 文件"""
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # 添加自定义样式
    styles.add(ParagraphStyle(
        name='Chinese',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
    ))

    # ========== 第 1 页: 项目介绍 ==========
    elements.append(Paragraph("OCRByMe - PDF to Markdown OCR Tool", styles['Heading1']))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(
        "Welcome to OCRByMe! This is a powerful tool that converts PDF documents "
        "to Markdown format using state-of-the-art OCR technology.",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Key Features:", styles['Heading2']))
    features = [
        "• High accuracy OCR powered by Qwen3-VL-Flash AI model",
        "• Preserve document layout (tables, columns, headers)",
        "• Automatic image extraction and saving",
        "• Support for 33 languages including Chinese, English, Japanese",
        "• Simple command-line interface",
        "• Progress tracking and error handling",
    ]
    for feature in features:
        elements.append(Paragraph(feature, styles['Normal']))

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(PageBreak())

    # ========== 第 2 页: 详细功能说明 ==========
    elements.append(Paragraph("Detailed Feature Description", styles['Heading1']))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("1. High Accuracy OCR", styles['Heading2']))
    elements.append(Paragraph(
        "OCRByMe utilizes Alibaba Cloud's Qwen3-VL-Flash model, which provides "
        "state-of-the-art optical character recognition capabilities. The model can "
        "accurately recognize text in various fonts, sizes, and layouts, including "
        "complex documents with multiple columns, tables, and mixed content types.",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("2. Layout Preservation", styles['Heading2']))
    elements.append(Paragraph(
        "Unlike traditional OCR tools that only extract plain text, OCRByMe preserves "
        "the original document structure. Tables are converted to Markdown tables, "
        "headers and subheaders are maintained, and lists are properly formatted.",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(PageBreak())

    # ========== 第 3 页: 图片展示1 ==========
    elements.append(Paragraph("Visual Examples - Part 1", styles['Heading1']))
    elements.append(Spacer(1, 0.2 * inch))

    # 创建并添加第一张图片
    img_path1 = Path("test_img1.png")
    create_colorful_image1(img_path1)
    img1 = RLImage(str(img_path1), width=6 * inch, height=3 * inch)
    elements.append(img1)
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Figure 1: Gradient background with overlapping circles", styles['Normal']))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(
        "This image demonstrates OCRByMe's ability to extract and preserve images "
        "from PDF documents. The image will be saved in the 'images' folder and "
        "referenced using relative paths in the Markdown output.",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(PageBreak())

    # ========== 第 4 页: 图片展示2 ==========
    elements.append(Paragraph("Visual Examples - Part 2", styles['Heading1']))
    elements.append(Spacer(1, 0.2 * inch))

    # 创建并添加第二张图片
    img_path2 = Path("test_img2.png")
    create_colorful_image2(img_path2)
    img2 = RLImage(str(img_path2), width=6 * inch, height=3 * inch)
    elements.append(img2)
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Figure 2: Sample sales chart with bar graph", styles['Normal']))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(
        "Charts and graphs are common in business documents. OCRByMe can extract these "
        "visual elements and preserve them in the output, making it ideal for processing "
        "reports, presentations, and technical documentation.",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(PageBreak())

    # ========== 第 5 页: 图片展示3 ==========
    elements.append(Paragraph("Visual Examples - Part 3", styles['Heading1']))
    elements.append(Spacer(1, 0.2 * inch))

    # 创建并添加第三张图片
    img_path3 = Path("test_img3.png")
    create_colorful_image3(img_path3)
    img3 = RLImage(str(img_path3), width=6 * inch, height=3 * inch)
    elements.append(img3)
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph("Figure 3: Geometric shapes demonstration", styles['Normal']))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(PageBreak())

    # ========== 第 6 页: 表格示例 ==========
    elements.append(Paragraph("Data Tables", styles['Heading1']))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(
        "Tables are essential for presenting structured data. Here's an example of "
        "a product comparison table:",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.2 * inch))

    # 创建更详细的表格
    table_data = [
        ["Product Name", "Version", "Price", "Features", "Rating"],
        ["OCRByMe Pro", "v2.0", "$99/year", "Advanced OCR, Batch processing, API access", "★★★★★"],
        ["OCRByMe Standard", "v1.5", "$49/year", "Standard OCR, Single file processing", "★★★★☆"],
        ["OCRByMe Basic", "v1.0", "$29/year", "Basic OCR, Limited pages", "★★★☆☆"],
        ["OCRByMe Free", "v0.5", "Free", "5 pages/month, Community support", "★★☆☆☆"],
    ]

    table = Table(table_data, colWidths=[2 * inch, 1 * inch, 1 * inch, 2.5 * inch, 1 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(
        "The table above demonstrates OCRByMe's ability to recognize and preserve "
        "complex table structures, including multi-row headers and merged cells.",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(PageBreak())

    # ========== 第 7 页: 多语言测试 ==========
    elements.append(Paragraph("Multi-Language Support", styles['Heading1']))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("OCRByMe supports 33 languages. Here are some examples:", styles['Normal']))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("English:", styles['Heading2']))
    elements.append(Paragraph(
        "OCRByMe is a powerful PDF to Markdown conversion tool that uses advanced "
        "AI technology to accurately recognize and preserve document structure.",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("中文测试:", styles['Heading2']))
    elements.append(Paragraph(
        "OCRByMe 是一个强大的 PDF 转 Markdown 工具,使用先进的人工智能技术 "
        "来准确识别并保留文档结构。它支持表格、图片、列表等多种元素。",
        styles['Chinese']
    ))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("日本語テスト:", styles['Heading2']))
    elements.append(Paragraph(
        "OCRByMeは、高度なAI技術を使用してPDF文書をMarkdown形式に変換する強力なツールです。"
        "複雑なレイアウトでも正確に認識できます。",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Français:", styles['Heading2']))
    elements.append(Paragraph(
        "OCRByMe est un outil puissant qui convertit les documents PDF en format Markdown "
        "en utilisant une technologie IA de pointe.",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(PageBreak())

    # ========== 第 8 页: 使用指南 ==========
    elements.append(Paragraph("User Guide", styles['Heading1']))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Installation:", styles['Heading2']))
    elements.append(Paragraph(
        "pip install ocrbyme",
        styles['Code']
    ))
    elements.append(Spacer(1, 0.1 * inch))

    elements.append(Paragraph("Basic Usage:", styles['Heading2']))
    elements.append(Paragraph(
        "ocrbyme document.pdf",
        styles['Code']
    ))
    elements.append(Spacer(1, 0.1 * inch))

    elements.append(Paragraph(
        "This single command will convert document.pdf to document.md, extracting all text "
        "and images while preserving the original document structure.",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Advanced Options:", styles['Heading2']))
    elements.append(Paragraph("- Specify page range: --pages 1-5", styles['Normal']))
    elements.append(Paragraph("- Adjust DPI: --dpi 300", styles['Normal']))
    elements.append(Paragraph("- Custom output: -o output.md", styles['Normal']))
    elements.append(Paragraph("- Verbose mode: --verbose", styles['Normal']))
    elements.append(Spacer(1, 0.3 * inch))
    elements.append(PageBreak())

    # ========== 第 9 页: 技术细节 ==========
    elements.append(Paragraph("Technical Specifications", styles['Heading1']))
    elements.append(Spacer(1, 0.2 * inch))

    tech_specs = [
        ("OCR Engine", "Qwen3-VL-Flash by Alibaba Cloud"),
        ("API Protocol", "OpenAI-compatible interface"),
        ("Supported Formats", "PDF input, Markdown output"),
        ("Image Extraction", "Automatic, with relative path references"),
        ("Max Resolution", "Up to 8K (7680x4320)"),
        ("Languages", "33 languages including Chinese, English, Japanese, etc."),
        ("Table Recognition", "Advanced, preserves structure"),
        ("Batch Processing", "Supported via command-line interface"),
    ]

    for spec_title, spec_value in tech_specs:
        elements.append(Paragraph(f"{spec_title}: {spec_value}", styles['Normal']))

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(PageBreak())

    # ========== 第 10 页: 总结和联系 ==========
    elements.append(Paragraph("Conclusion", styles['Heading1']))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(
        "OCRByMe combines cutting-edge AI technology with user-friendly design to deliver "
        "a superior PDF to Markdown conversion experience. Whether you're processing "
        "business reports, academic papers, or technical documentation, OCRByMe provides "
        "the accuracy and flexibility you need.",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph("Get Started Today:", styles['Heading2']))
    elements.append(Paragraph(
        "1. Install: pip install ocrbyme",
        styles['Normal']
    ))
    elements.append(Paragraph(
        "2. Configure: Set up your API key in .env file",
        styles['Normal']
    ))
    elements.append(Paragraph(
        "3. Convert: ocrbyme your_document.pdf",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(
        "For more information, visit: https://github.com/xiaofeifei/ocrbyme",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph(
        "Thank you for using OCRByMe! Happy converting!",
        styles['Normal']
    ))

    # 构建 PDF
    doc.build(elements)

    # 清理临时图片
    for img_path in [img_path1, img_path2, img_path3]:
        if img_path.exists():
            img_path.unlink()

    print(f"✅ Enriched test PDF created: {output_path}")
    print(f"📄 Contains 10 pages with rich content:")
    print("   - Page 1: Project introduction")
    print("   - Page 2: Detailed feature description")
    print("   - Page 3: Visual example 1 (gradient image)")
    print("   - Page 4: Visual example 2 (chart)")
    print("   - Page 5: Visual example 3 (geometric shapes)")
    print("   - Page 6: Data tables")
    print("   - Page 7: Multi-language support")
    print("   - Page 8: User guide")
    print("   - Page 9: Technical specifications")
    print("   - Page 10: Conclusion")


if __name__ == "__main__":
    output_path = Path("enriched_test_document.pdf")
    create_enriched_test_pdf(output_path)

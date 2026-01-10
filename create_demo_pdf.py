"""创建演示用的 PDF 文件"""

from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, PageBreak


def create_demo_pdf(output_path: Path) -> None:
    """创建演示 PDF 文件"""
    doc = SimpleDocTemplate(str(output_path), pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()

    # 第 1 页: 演示内容
    elements.append(Paragraph("OCRByMe Demo Document", styles['Heading1']))
    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(
        "This is a demonstration document for OCRByMe tool. "
        "When you place this PDF in the project folder and double-click run_ocr.bat, "
        "it will be automatically converted to Markdown format.",
        styles['Normal']
    ))
    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Key Features:", styles['Heading2']))
    features = [
        "Automatically finds and processes PDF files",
        "Saves output to 'out' folder",
        "Copies content to clipboard automatically",
        "Opens output folder when done",
        "Simple one-click operation",
    ]
    for feature in features:
        elements.append(Paragraph(f"• {feature}", styles['Normal']))

    elements.append(Spacer(1, 0.2 * inch))

    elements.append(Paragraph("Usage Instructions:", styles['Heading2']))
    steps = [
        "1. Copy your PDF file to the ocrbyme folder",
        "2. Double-click run_ocr.bat",
        "3. Wait for processing to complete",
        "4. Find the result in the 'out' folder",
        "5. Content is already in your clipboard (Ctrl+V to paste)",
    ]
    for step in steps:
        elements.append(Paragraph(step, styles['Normal']))

    elements.append(Spacer(1, 0.3 * inch))

    elements.append(Paragraph(
        "This tool makes PDF to Markdown conversion as easy as a single click!",
        styles['Normal']
    ))

    # 构建 PDF
    doc.build(elements)

    print(f"✅ Demo PDF created: {output_path}")


if __name__ == "__main__":
    output_path = Path("demo_sample.pdf")
    create_demo_pdf(output_path)

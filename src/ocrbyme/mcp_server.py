"""MCP 服务器模块 - 提供 PDF 转 Markdown 工具"""

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from ocrbyme.config import Settings
from ocrbyme.core import MarkdownGenerator, PDFProcessor, QwenVLClient
from ocrbyme.core.prompt_templates import PromptTemplate
from ocrbyme.models.types import (
    APIError,
    ConfigurationError,
    PDFProcessingError,
)

logger = logging.getLogger(__name__)

# 初始化 FastMCP 服务器
app = FastMCP("ocrbyme")


@app.tool()
async def pdf_to_markdown(
    pdf_path: str,
    output_path: str | None = None,
    pages: str | None = None,
    dpi: int = 300,
    extract_images: bool = True,
    timeout: int = 60,
    ocr_mode: str = "academic",
    custom_prompt: str | None = None,
    enhance_images: bool = True,
) -> str:
    """将 PDF 文件转换为 Markdown 格式

    Args:
        pdf_path: PDF 文件的绝对路径
        output_path: 输出 Markdown 文件路径（默认为 input_pdf.md）
        pages: 页码范围，例如 "1-5" 或 "1,3,5-7"（默认：全部页面）
        dpi: PDF 转图像的 DPI，默认 300（范围：72-600）
        extract_images: 是否提取和保存 PDF 嵌入的图片，默认 True
        timeout: API 请求超时时间（秒），默认 60
        ocr_mode: OCR 模式 (academic/document/table/formula/mixed)，默认 academic
        custom_prompt: 自定义提示词指令（可选）
        enhance_images: 是否启用图像增强预处理，默认 True

    Returns:
        JSON 字符串，包含：
        - success: 是否成功
        - output_path: 输出文件路径
        - page_count: 处理页数
        - images_extracted: 提取的图片数量
        - error: 错误信息（如果失败）

    Example:
        pdf_to_markdown("C:/docs/document.pdf")
        pdf_to_markdown("C:/docs/document.pdf", pages="1-5", dpi=300, ocr_mode="academic")
    """
    try:
        # 1. 验证输入
        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            return json.dumps({
                "success": False,
                "error": f"PDF 文件不存在: {pdf_path}"
            }, ensure_ascii=False)

        # 2. 获取 MCP 配置
        settings = get_mcp_settings(timeout)

        # 3. 解析页码范围
        total_pages = PDFProcessor.get_page_count_from_path(pdf_file)
        page_numbers = parse_page_range(pages, total_pages)

        # 4. 确定输出路径
        if output_path is None:
            output_path = str(pdf_file.with_suffix('.md'))
        output_file = Path(output_path)
        output_dir = output_file.parent
        images_dir = output_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        # 5. 转换 PDF 为图像
        logger.info(f"开始转换 PDF: {pdf_file.name}, 页数: {len(page_numbers)}")
        processor = PDFProcessor(
            dpi=dpi,
            images_dir=images_dir,
            enable_image_enhancement=enhance_images,
        )
        first = page_numbers[0]
        last = page_numbers[-1]
        images = processor.convert_to_images(pdf_file, first_page=first, last_page=last)
        logger.info(f"PDF 转换完成: {len(images)} 页")

        # 6. 批量 OCR 处理
        logger.info("开始 OCR 处理...")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            image_paths = []
            for i, img in enumerate(images, 1):
                img_path = temp_path / f"page_{i}.png"
                img.save(img_path)
                image_paths.append(img_path)

            # 获取提示词
            prompt = PromptTemplate.get_prompt(
                mode=ocr_mode,
                custom_instruction=custom_prompt,
            )

            # 使用自定义 api_key 初始化客户端
            ocr_client = QwenVLClient(
                api_key=settings.dashscope_api_key,
                timeout=timeout,
                temperature=settings.temperature,
            )

            # 批量 OCR 处理
            ocr_results = []
            for img_path in image_paths:
                result = ocr_client.ocr_image(img_path, prompt=prompt)
                ocr_results.append(result)

            ocr_client.close()
        logger.info("OCR 处理完成")

        # 7. 提取 PDF 嵌入图片
        extracted_images = {}
        if extract_images:
            logger.info("提取 PDF 嵌入图片...")
            extracted_images = processor.extract_all_images(pdf_file)
            total_images = sum(len(imgs) for imgs in extracted_images.values())
            logger.info(f"提取了 {total_images} 张图片")

        # 8. 生成 Markdown
        logger.info("生成 Markdown 文件...")
        markdown_gen = MarkdownGenerator(
            output_dir=output_dir,
            extract_images=extract_images,
        )

        metadata = {
            "source": str(pdf_file),
            "page_count": len(page_numbers),
        }

        markdown_gen.generate(
            ocr_results, metadata, output_file, extracted_images
        )
        logger.info(f"Markdown 文件已生成: {output_file}")

        # 9. 返回结果
        total_images = sum(len(imgs) for imgs in extracted_images.values())
        return json.dumps({
            "success": True,
            "output_path": str(output_file),
            "page_count": len(page_numbers),
            "images_extracted": total_images,
        }, ensure_ascii=False)

    except ConfigurationError as e:
        logger.error(f"配置错误: {e}")
        return json.dumps({
            "success": False,
            "error": f"配置错误: {e}"
        }, ensure_ascii=False)

    except PDFProcessingError as e:
        logger.error(f"PDF 处理失败: {e}")
        return json.dumps({
            "success": False,
            "error": f"PDF 处理失败: {e}"
        }, ensure_ascii=False)

    except APIError as e:
        logger.error(f"API 调用失败: {e}")
        return json.dumps({
            "success": False,
            "error": f"API 调用失败: {e}"
        }, ensure_ascii=False)

    except Exception as e:
        logger.exception("MCP 工具执行失败")
        return json.dumps({
            "success": False,
            "error": f"未知错误: {e}"
        }, ensure_ascii=False)


def get_mcp_settings(timeout: int = 60) -> Settings:
    """获取 MCP 专用配置（不使用缓存）

    优先从环境变量读取 API Key，支持 MCP 客户端传入

    Args:
        timeout: 超时时间（秒）

    Returns:
        Settings: 配置对象

    Raises:
        ConfigurationError: API Key 未设置
    """
    api_key = os.getenv("DASHSCOPE_API_KEY") or os.getenv("OCRBYME_DASHSCOPE_API_KEY")

    if not api_key:
        raise ConfigurationError(
            "DASHSCOPE_API_KEY 环境变量未设置。"
            "请通过 MCP 客户端的 env 参数传入。"
        )

    return Settings(
        dashscope_api_key=api_key,
        timeout=timeout,
    )


def parse_page_range(
    pages_str: str | None,
    total_pages: int,
) -> list[int]:
    """解析页码范围（复用 CLI 逻辑）

    Args:
        pages_str: 页码范围字符串 (例如: "1-5" 或 "1,3,5-7")
        total_pages: PDF 总页数

    Returns:
        页码列表 (从 1 开始)
    """
    if not pages_str:
        return list(range(1, total_pages + 1))

    page_numbers = []
    for part in pages_str.split(","):
        part = part.strip()
        if "-" in part:
            start, end = part.split("-")
            page_numbers.extend(range(int(start), int(end) + 1))
        else:
            page_numbers.append(int(part))

    return sorted(set(p for p in page_numbers if 1 <= p <= total_pages))


def main() -> None:
    """MCP 服务器入口点"""
    import sys

    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 验证配置
    try:
        get_mcp_settings()
    except ConfigurationError as e:
        print(f"❌ 配置错误: {e}", file=sys.stderr)
        print(f"\n提示: 请在 MCP 客户端配置中设置 DASHSCOPE_API_KEY 环境变量", file=sys.stderr)
        sys.exit(1)

    # 启动服务器
    logger.info("启动 OCRByMe MCP 服务器...")
    app.run(transport="stdio")


if __name__ == "__main__":
    main()

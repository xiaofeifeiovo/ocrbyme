"""CLI 接口模块 - 命令行工具"""

import logging
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)

from ocrbyme import __version__
from ocrbyme.config import get_settings
from ocrbyme.core import MarkdownGenerator, PDFProcessor, QwenVLClient
from ocrbyme.core.prompt_templates import PromptTemplate, OCRMode
from ocrbyme.models.types import (
    APIError,
    ConfigurationError,
    OCRByMeError,
    PDFProcessingError,
)

# 初始化 Rich 控制台
console = Console()


def setup_logging(verbose: bool = False) -> logging.Logger:
    """配置日志

    Args:
        verbose: 是否显示详细日志

    Returns:
        Logger 实例
    """
    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True, console=console)],
    )

    return logging.getLogger("ocrbyme")


def parse_page_range(
    pages_str: str | None,
    total_pages: int,
    first_page: int | None = None,
    last_page: int | None = None,
) -> list[int]:
    """解析页码范围

    Args:
        pages_str: 页码范围字符串 (例如: "1-5" 或 "1,3,5-7")
        total_pages: PDF 总页数
        first_page: 起始页码
        last_page: 结束页码

    Returns:
        页码列表 (从 1 开始)
    """
    if first_page is not None and last_page is not None:
        return list(range(first_page, last_page + 1))

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

    # 验证和去重
    page_numbers = sorted(set(p for p in page_numbers if 1 <= p <= total_pages))

    return page_numbers


@click.command()
@click.argument(
    "input_pdf",
    type=click.Path(exists=True, path_type=Path),
)
@click.option(
    "-o",
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="输出 Markdown 文件路径 (默认: input_pdf.md)",
)
@click.option(
    "--pages",
    type=str,
    default=None,
    help="页码范围,例如 '1-5' 或 '1,3,5-7'",
)
@click.option(
    "--dpi",
    type=int,
    default=200,
    show_default=True,
    help="PDF 转图像的 DPI (越高越清晰但越慢)",
)
@click.option(
    "--first-page",
    type=int,
    default=None,
    help="起始页码 (从 1 开始)",
)
@click.option(
    "--last-page",
    type=int,
    default=None,
    help="结束页码",
)
@click.option(
    "--no-extract-images",
    is_flag=True,
    help="不提取和保存嵌入的图片",
)
@click.option(
    "--timeout",
    type=int,
    default=60,
    show_default=True,
    help="API 请求超时 (秒)",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="显示详细日志",
)
@click.option(
    "--ocr-mode",
    type=click.Choice(
        ["academic", "document", "table", "formula", "mixed"],
        case_sensitive=False
    ),
    default="academic",
    show_default=True,
    help="OCR 模式 (academic=学术论文, document=通用文档, table=表格, formula=公式, mixed=混合)",
)
@click.option(
    "--custom-prompt",
    type=str,
    default=None,
    help="自定义提示词指令 (追加到默认提示词末尾)",
)
@click.option(
    "--enhance-images/--no-enhance-images",
    default=True,
    show_default=True,
    help="启用/禁用图像增强预处理 (提升识别质量)",
)
@click.option(
    "--temperature",
    type=float,
    default=None,
    help="API 温度参数 (0.0-2.0, 默认 0.0, 值越小越稳定)",
)
@click.version_option(version=__version__)
def main(
    input_pdf: Path,
    output: Path | None,
    pages: str | None,
    dpi: int,
    first_page: int | None,
    last_page: int | None,
    no_extract_images: bool,
    timeout: int,
    verbose: bool,
    ocr_mode: str,
    custom_prompt: str | None,
    enhance_images: bool,
    temperature: float | None,
) -> None:
    """PDF 转 Markdown OCR 工具 - 使用 Qwen3-VL-Flash API

    示例:

        ocrbyme document.pdf

        ocrbyme document.pdf -o output.md --pages 1-10

        ocrbyme document.pdf --dpi 300 --verbose
    """
    # 配置日志
    logger = setup_logging(verbose)

    try:
        # ========== 1. 验证配置 ==========
        console.print("[bold cyan]🚀 OCRByMe - PDF 转 Markdown OCR 工具[/bold cyan]")
        console.print(f"版本: {__version__}\n")

        try:
            settings = get_settings()
            logger.debug("配置验证成功")
        except ConfigurationError as e:
            console.print(f"[bold red]❌ 配置错误:[/bold red] {e}")
            sys.exit(1)

        # ========== 2. 解析参数和页码范围 ==========
        # 获取 PDF 总页数
        try:
            total_pages = PDFProcessor.get_page_count_from_path(input_pdf)
            console.print(f"📄 PDF 文件: {input_pdf.name}")
            console.print(f"📑 总页数: {total_pages}")
        except Exception as e:
            console.print(f"[bold red]❌ 读取 PDF 失败:[/bold red] {e}")
            sys.exit(1)

        # 解析页码范围
        try:
            page_numbers = parse_page_range(pages, total_pages, first_page, last_page)
            console.print(f"📖 处理页数: {len(page_numbers)} 页")
            if len(page_numbers) < total_pages:
                console.print(f"   页码: {', '.join(map(str, page_numbers))}")
        except Exception as e:
            console.print(f"[bold red]❌ 页码范围解析失败:[/bold red] {e}")
            sys.exit(1)

        # 确定输出路径
        if output is None:
            output = input_pdf.with_suffix(".md")
        console.print(f"📁 输出文件: {output}")

        # ========== 3. 转换 PDF 为图像 ==========
        console.print("\n[bold yellow]📷 步骤 1/3: 转换 PDF 为图像...[/bold yellow]")

        # 创建输出目录和图片目录
        output_dir = output.parent
        images_dir = output_dir / "images"
        images_dir.mkdir(parents=True, exist_ok=True)

        try:
            processor = PDFProcessor(
                dpi=dpi,
                images_dir=images_dir,
                enable_image_enhancement=enhance_images,
            )
            first = page_numbers[0]
            last = page_numbers[-1]

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TaskProgressColumn(),
                console=console,
            ) as progress:
                task = progress.add_task(
                    "转换中...", total=None
                )

                images = processor.convert_to_images(
                    input_pdf, first_page=first, last_page=last
                )

                progress.update(task, completed=100, total=100)

            console.print(f"✅ 转换完成: {len(images)} 页")

        except PDFProcessingError as e:
            console.print(f"[bold red]❌ PDF 转换失败:[/bold red] {e}")
            sys.exit(1)

        # ========== 4. 批量 OCR (带进度条) ==========
        console.print("\n[bold yellow]🤖 步骤 2/3: OCR 处理...[/bold yellow]")

        try:
            # 创建临时目录保存图像
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # 保存图像到临时目录
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

                # OCR 处理
                ocr_client = QwenVLClient(
                    timeout=timeout,
                    temperature=temperature,
                )

                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TaskProgressColumn(),
                    TimeRemainingColumn(),
                    console=console,
                ) as progress:
                    task = progress.add_task("OCR 处理中...", total=len(image_paths))

                    ocr_results = []
                    for img_path in image_paths:
                        try:
                            markdown = ocr_client.ocr_image(img_path, prompt=prompt)
                            ocr_results.append(markdown)
                        except Exception as e:
                            logger.error(f"OCR 失败: {e}")
                            ocr_results.append(f"<!-- OCR 失败: {e} -->")

                        progress.update(task, advance=1)

                ocr_client.close()
                console.print("✅ OCR 处理完成")

        except APIError as e:
            console.print(f"[bold red]❌ API 调用失败:[/bold red] {e}")
            if e.status_code == 401:
                console.print(
                    "[yellow]提示: 请检查 DASHSCOPE_API_KEY 是否正确[/yellow]"
                )
            sys.exit(1)
        except Exception as e:
            console.print(f"[bold red]❌ OCR 处理失败:[/bold red] {e}")
            sys.exit(1)

        # ========== 5. 生成 Markdown ==========
        console.print("\n[bold yellow]📝 步骤 3/3: 生成 Markdown...[/bold yellow]")

        try:
            # 提取 PDF 中的图片
            console.print("   [info]正在提取 PDF 嵌入图片...", )
            extracted_images = processor.extract_all_images(input_pdf)

            if extracted_images:
                total_images = sum(len(imgs) for imgs in extracted_images.values())
                console.print(f" ✅ 提取了 {total_images} 张图片")
            else:
                console.print(" ℹ️  未找到图片")

            markdown_gen = MarkdownGenerator(
                output_dir=output_dir,
                extract_images=not no_extract_images,
            )

            metadata = {
                "source": str(input_pdf),
                "page_count": len(page_numbers),
            }

            output_path = markdown_gen.generate(
                ocr_results, metadata, output, extracted_images
            )
            console.print(f"✅ Markdown 文件已生成: {output_path}")

        except Exception as e:
            console.print(f"[bold red]❌ 生成 Markdown 失败:[/bold red] {e}")
            sys.exit(1)

        # ========== 6. 显示结果摘要 ==========
        console.print("\n" + "=" * 50)
        console.print(
            Panel.fit(
                f"[bold green]✅ 转换成功![/bold green]\n\n"
                f"📄 输入文件: {input_pdf.name}\n"
                f"📝 输出文件: {output_path.name}\n"
                f"📑 处理页数: {len(page_numbers)}\n"
                f"🖼️  提取图片: {'是' if not no_extract_images else '否'}",
                title="结果摘要",
                border_style="green",
            )
        )

        logger.info("转换完成!")

    except OCRByMeError as e:
        console.print(f"[bold red]❌ 错误:[/bold red] {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  用户取消[/yellow]")
        sys.exit(130)
    except Exception as e:
        logger.exception("未预期的错误")
        console.print(f"[bold red]❌ 未预期的错误:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

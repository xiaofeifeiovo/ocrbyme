"""Markdown 生成器模块 - 合并 OCR 结果并生成最终 Markdown"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from ocrbyme.core.image_manager import ImageManager
from ocrbyme.models.types import OCRByMeError

logger = logging.getLogger(__name__)


class MarkdownGenerationError(OCRByMeError):
    """Markdown 生成错误"""
    pass


class MarkdownGenerator:
    """Markdown 生成器

    合并 OCR 结果并生成最终的 Markdown 文件。
    """

    def __init__(
        self,
        output_dir: Path,
        extract_images: bool = True,
        image_subdir: str = "images",
    ) -> None:
        """初始化 Markdown 生成器

        Args:
            output_dir: 输出目录
            extract_images: 是否从 OCR 结果中提取图片
            image_subdir: 图片保存子目录名
        """
        self.output_dir = Path(output_dir)
        self.extract_images = extract_images
        self.image_subdir = image_subdir

        # 创建输出目录
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 初始化图片管理器
        if self.extract_images:
            self.image_manager = ImageManager(self.output_dir, image_subdir)
        else:
            self.image_manager = None

        logger.info(
            f"Markdown 生成器初始化: "
            f"输出目录={self.output_dir}, "
            f"提取图片={extract_images}"
        )

    def generate(
        self,
        ocr_results: list[str],
        metadata: dict[str, Any] | None = None,
        output_path: Path | None = None,
    ) -> Path:
        """生成最终的 Markdown 文件

        Args:
            ocr_results: 每页的 OCR 结果 (Markdown 文本列表)
            metadata: 元数据 (来源 PDF,页数等)
            output_path: 输出文件路径 (None 则使用默认名称)

        Returns:
            生成的 Markdown 文件路径

        Raises:
            MarkdownGenerationError: 生成失败
        """
        try:
            # 处理图片
            if self.extract_images and self.image_manager:
                processed_results, saved_images = (
                    self.image_manager.extract_and_save_images_from_markdown_list(
                        ocr_results
                    )
                )
                logger.info(f"提取并保存 {len(saved_images)} 张图片")
            else:
                processed_results = ocr_results
                saved_images = []

            # 构建最终 Markdown 内容
            markdown_content = self._build_markdown(
                processed_results, metadata, saved_images
            )

            # 确定输出路径
            if output_path is None:
                if metadata and "source" in metadata:
                    source_path = Path(metadata["source"])
                    output_path = self.output_dir / f"{source_path.stem}.md"
                else:
                    output_path = self.output_dir / "output.md"

            output_path = Path(output_path)

            # 写入文件
            output_path.write_text(markdown_content, encoding="utf-8")
            logger.info(f"Markdown 文件已生成: {output_path}")

            return output_path

        except Exception as e:
            raise MarkdownGenerationError(f"生成 Markdown 失败: {e}") from e

    def _build_markdown(
        self,
        ocr_results: list[str],
        metadata: dict[str, Any] | None,
        saved_images: list[Path],
    ) -> str:
        """构建 Markdown 内容

        Args:
            ocr_results: 处理后的 OCR 结果
            metadata: 元数据
            saved_images: 保存的图片列表

        Returns:
            完整的 Markdown 内容
        """
        lines = []

        # 标题
        lines.append("# 文档")
        lines.append("")

        # 元数据
        if metadata:
            lines.append("> 由 OCRByMe 生成")
            if "source" in metadata:
                source_name = Path(metadata["source"]).name
                lines.append(f"> 来源: {source_name}")
            if "page_count" in metadata:
                lines.append(f"> 页数: {metadata['page_count']}")
            lines.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            lines.append("")
            lines.append("---")
            lines.append("")

        # 每页内容
        for page_num, result in enumerate(ocr_results, 1):
            # 页码标题
            lines.append(f"## 第 {page_num} 页")
            lines.append("")
            lines.append("---")
            lines.append("")

            # OCR 结果
            lines.append(result)
            lines.append("")
            lines.append("---")
            lines.append("")

        # 结尾
        lines.append("<!-- 文档结束 -->")

        return "\n".join(lines)

    def generate_simple(
        self,
        ocr_results: list[str],
        output_path: Path,
    ) -> Path:
        """生成简单的 Markdown 文件 (无元数据和格式化)

        Args:
            ocr_results: OCR 结果列表
            output_path: 输出文件路径

        Returns:
            生成的 Markdown 文件路径
        """
        try:
            # 直接合并所有结果
            content = "\n\n---\n\n".join(ocr_results)

            # 写入文件
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(content, encoding="utf-8")

            logger.info(f"简单 Markdown 文件已生成: {output_path}")
            return output_path

        except Exception as e:
            raise MarkdownGenerationError(f"生成简单 Markdown 失败: {e}") from e

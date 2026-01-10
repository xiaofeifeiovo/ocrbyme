"""PDF 图片提取器 - 从 PDF 中提取嵌入式图片"""

import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Tuple
import io
from PIL import Image


class PDFImageExtractor:
    """从 PDF 文件中提取图片"""

    def __init__(self, images_dir: Path):
        """
        初始化图片提取器

        Args:
            images_dir: 图片保存目录
        """
        self.images_dir = Path(images_dir)
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def extract_images(self, pdf_path: Path, page_num: int) -> List[Tuple[Path, str]]:
        """
        从 PDF 页面提取图片

        Args:
            pdf_path: PDF 文件路径
            page_num: 页码（从 1 开始）

        Returns:
            图片路径和描述的列表 [(image_path, description), ...]
        """
        doc = fitz.open(str(pdf_path))
        page = doc[page_num - 1]  # fitz 页码从 0 开始
        image_list = page.get_images()
        extracted_images = []

        for img_index, img in enumerate(image_list, start=1):
            try:
                # 获取图片
                xref = img[0]
                base_image = doc.extract_image(xref)

                if base_image:
                    # 获取图片字节
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]

                    # 保存图片
                    image_filename = f"page_{page_num}_img_{img_index}.{image_ext}"
                    image_path = self.images_dir / image_filename

                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)

                    # 获取图片位置信息
                    img_rects = page.get_image_rects(xref)
                    description = f"Image {img_index} on page {page_num}"

                    extracted_images.append((image_path, description))

            except Exception as e:
                print(f"Warning: Failed to extract image {img_index} from page {page_num}: {e}")
                continue

        doc.close()
        return extracted_images

    def extract_all_images(self, pdf_path: Path) -> dict:
        """
        从 PDF 所有页面提取图片

        Args:
            pdf_path: PDF 文件路径

        Returns:
            字典 {page_num: [(image_path, description), ...], ...}
        """
        doc = fitz.open(str(pdf_path))
        all_images = {}

        for page_num in range(len(doc)):
            page = page_num + 1  # 转换为从 1 开始
            images = self.extract_images(pdf_path, page)
            if images:
                all_images[page_num] = images

        doc.close()
        return all_images

    def get_page_image_count(self, pdf_path: Path, page_num: int) -> int:
        """
        获取指定页面的图片数量

        Args:
            pdf_path: PDF 文件路径
            page_num: 页码（从 1 开始）

        Returns:
            图片数量
        """
        doc = fitz.open(str(pdf_path))
        page = doc[page_num - 1]
        image_count = len(page.get_images())
        doc.close()
        return image_count

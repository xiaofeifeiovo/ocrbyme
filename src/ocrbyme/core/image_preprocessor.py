"""图像预处理模块

提供图像增强功能,提升 OCR 识别质量。
"""

import logging
from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)


class ImagePreprocessor:
    """图像预处理器

    对 PDF 转换后的图像进行增强,提升 OCR 识别精度。
    """

    def __init__(
        self,
        enable_enhancement: bool = True,
        contrast_factor: float = 1.2,
        sharpness_factor: float = 1.5,
        brightness_factor: float = 1.0,
        apply_denoise: bool = True,
    ) -> None:
        """初始化图像预处理器

        Args:
            enable_enhancement: 是否启用图像增强
            contrast_factor: 对比度系数 (1.0=原始, >1.0=增强)
            sharpness_factor: 锐化系数 (1.0=原始, >1.0=锐化)
            brightness_factor: 亮度系数 (1.0=原始, >1.0=变亮)
            apply_denoise: 是否应用降噪滤镜
        """
        self.enable_enhancement = enable_enhancement
        self.contrast_factor = contrast_factor
        self.sharpness_factor = sharpness_factor
        self.brightness_factor = brightness_factor
        self.apply_denoise = apply_denoise

        logger.debug(
            f"图像预处理器初始化: enhancement={enable_enhancement}, "
            f"contrast={contrast_factor}, sharpness={sharpness_factor}"
        )

    def preprocess(self, image: Image.Image) -> Image.Image:
        """预处理单张图像

        Args:
            image: PIL Image 对象

        Returns:
            处理后的 PIL Image 对象
        """
        if not self.enable_enhancement:
            return image

        img = image.copy()

        # 1. 对比度增强
        if self.contrast_factor != 1.0:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(self.contrast_factor)
            logger.debug(f"应用对比度增强: {self.contrast_factor}")

        # 2. 锐化 (提升文字边缘清晰度)
        if self.sharpness_factor != 1.0:
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(self.sharpness_factor)
            logger.debug(f"应用锐化: {self.sharpness_factor}")

        # 3. 亮度调整
        if self.brightness_factor != 1.0:
            enhancer = ImageEnhance.Brightness(img)
            img = enhancer.enhance(self.brightness_factor)
            logger.debug(f"应用亮度调整: {self.brightness_factor}")

        # 4. 降噪 (轻微模糊去除噪点)
        if self.apply_denoise:
            img = img.filter(ImageFilter.MedianFilter(size=3))
            logger.debug("应用降噪滤镜")

        return img

    def preprocess_batch(
        self,
        image_paths: list[Path],
    ) -> list[Image.Image]:
        """批量预处理图像

        Args:
            image_paths: 图像路径列表

        Returns:
            处理后的 PIL Image 对象列表
        """
        results = []

        for i, img_path in enumerate(image_paths, 1):
            logger.debug(f"预处理图像 {i}/{len(image_paths)}: {img_path.name}")

            with Image.open(img_path) as img:
                processed_img = self.preprocess(img)
                results.append(processed_img)

        return results

"""图像预处理模块测试"""

import pytest
from PIL import Image
from ocrbyme.core.image_preprocessor import ImagePreprocessor


def test_preprocessor_disabled():
    """测试禁用预处理"""
    preprocessor = ImagePreprocessor(enable_enhancement=False)

    # 创建测试图片
    img = Image.new("RGB", (100, 100), color="white")
    result = preprocessor.preprocess(img)

    assert result.size == img.size


def test_contrast_enhancement():
    """测试对比度增强"""
    preprocessor = ImagePreprocessor(
        enable_enhancement=True,
        contrast_factor=1.5,
    )

    img = Image.new("RGB", (100, 100), color="white")
    result = preprocessor.preprocess(img)

    assert result.size == img.size


def test_sharpness_enhancement():
    """测试锐化增强"""
    preprocessor = ImagePreprocessor(
        enable_enhancement=True,
        sharpness_factor=2.0,
    )

    img = Image.new("RGB", (100, 100), color="white")
    result = preprocessor.preprocess(img)

    assert result.size == img.size


def test_brightness_adjustment():
    """测试亮度调整"""
    preprocessor = ImagePreprocessor(
        enable_enhancement=True,
        brightness_factor=1.2,
    )

    img = Image.new("RGB", (100, 100), color="white")
    result = preprocessor.preprocess(img)

    assert result.size == img.size


def test_denoise_enabled():
    """测试降噪功能"""
    preprocessor = ImagePreprocessor(
        enable_enhancement=True,
        apply_denoise=True,
    )

    img = Image.new("RGB", (100, 100), color="white")
    result = preprocessor.preprocess(img)

    assert result.size == img.size


def test_batch_preprocessing(tmp_path):
    """测试批量预处理"""
    from pathlib import Path

    # 创建测试图片
    image_paths = []
    for i in range(3):
        img_path = tmp_path / f"test_{i}.png"
        img = Image.new("RGB", (100, 100), color="white")
        img.save(img_path)
        image_paths.append(img_path)

    preprocessor = ImagePreprocessor(enable_enhancement=True)
    results = preprocessor.preprocess_batch(image_paths)

    assert len(results) == 3
    assert all(isinstance(img, Image.Image) for img in results)


def test_all_enhancements_together():
    """测试所有增强功能同时启用"""
    preprocessor = ImagePreprocessor(
        enable_enhancement=True,
        contrast_factor=1.2,
        sharpness_factor=1.5,
        brightness_factor=1.1,
        apply_denoise=True,
    )

    img = Image.new("RGB", (100, 100), color="white")
    result = preprocessor.preprocess(img)

    assert result.size == img.size
    assert result.mode == img.mode

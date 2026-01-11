"""提示词模板模块测试"""

import pytest
from ocrbyme.core.prompt_templates import OCRMode, PromptTemplate


def test_get_academic_prompt():
    """测试获取学术模式提示词"""
    prompt = PromptTemplate.get_prompt(OCRMode.ACADEMIC)
    assert "qwenvl markdown" in prompt
    assert "学术文档" in prompt
    assert "公式" in prompt
    assert "LaTeX" in prompt


def test_get_document_prompt():
    """测试获取文档模式提示词"""
    prompt = PromptTemplate.get_prompt(OCRMode.DOCUMENT)
    assert "qwenvl markdown" in prompt
    assert "Markdown 格式" in prompt


def test_get_table_prompt():
    """测试获取表格模式提示词"""
    prompt = PromptTemplate.get_prompt(OCRMode.TABLE)
    assert "qwenvl markdown" in prompt
    assert "表格" in prompt
    assert "表头" in prompt


def test_get_formula_prompt():
    """测试获取公式模式提示词"""
    prompt = PromptTemplate.get_prompt(OCRMode.FORMULA)
    assert "qwenvl markdown" in prompt
    assert "LaTeX" in prompt
    assert "单美元号 $公式$" in prompt
    assert "双美元号 $$公式$$" in prompt
    assert r"\frac" in prompt


def test_get_mixed_prompt():
    """测试获取混合模式提示词"""
    prompt = PromptTemplate.get_prompt(OCRMode.MIXED)
    assert "qwenvl markdown" in prompt
    assert "自动处理" in prompt


def test_custom_instruction():
    """测试自定义指令"""
    custom = "请特别注意识别数字"
    prompt = PromptTemplate.get_prompt(
        OCRMode.DOCUMENT,
        custom_instruction=custom
    )
    assert custom in prompt
    assert "额外要求" in prompt


def test_from_config():
    """测试从配置字符串获取提示词"""
    prompt = PromptTemplate.from_config("academic")
    assert "学术" in prompt

    prompt = PromptTemplate.from_config("custom instruction here")
    assert "custom instruction here" in prompt


def test_default_mode_is_academic():
    """测试默认模式是学术模式"""
    prompt = PromptTemplate.get_prompt()
    assert "学术文档" in prompt

"""提示词模板管理模块

提供针对不同文档类型和场景的优化提示词。
"""

from enum import Enum
from typing import Literal


class OCRMode(str, Enum):
    """OCR 模式枚举"""

    DOCUMENT = "document"  # 通用文档模式
    ACADEMIC = "academic"  # 学术论文模式 (包含公式、引用)
    TABLE = "table"  # 表格密集模式
    FORMULA = "formula"  # 数学公式密集模式
    MIXED = "mixed"  # 混合模式 (自动检测)


class PromptTemplate:
    """提示词模板类

    提供针对不同场景优化的提示词,遵循 Qwen VL Markdown 格式规范。
    """

    # 基础 Markdown 模式触发词
    BASE_MARKDOWN = "qwenvl markdown"

    # 学术论文模式 (针对复杂学术文档) - **默认模式**
    ACADEMIC_PROMPT = """请将这个学术文档页面转换为高质量的 Markdown 格式。

特别要求:
1. **完整识别**: 识别所有文字内容,包括脚注、页眉、页脚
2. **公式处理**: 数学公式使用 LaTeX 格式,区分行内公式 ($...$) 和独立公式 ($$...$$)
3. **引用格式**: 保留参考文献的编号和格式
4. **图表说明**: 保留图表标题和说明文字
5. **结构层次**: 准确识别章节标题、附录、参考文献等结构
6. **多语言**: 准确识别中英文混合内容
7. **特殊符号**: 保留特殊符号、上下标、希腊字母等

{base_mode}

输出格式要求:
- 使用标准的 Markdown 语法
- 表格转换为 Markdown 表格格式
- 代码块使用 ```语言 标记
- 不要遗漏任何内容,即使内容模糊也要尝试识别
"""

    # 通用文档模式
    DOCUMENT_PROMPT = """请将这个文档页面转换为 Markdown 格式。

要求:
1. 保留原始文档结构 (标题层级、段落、列表)
2. 准确识别所有文字内容,包括中英文混合
3. 保留表格格式为 Markdown 表格
4. 数学公式使用 LaTeX 格式 ($...$ 或 $$...$$)
5. 图片使用 ![描述](路径) 格式标记
6. 不要遗漏任何文字内容

{base_mode}
"""

    # 表格密集模式
    TABLE_PROMPT = """请将这个包含大量表格的文档页面转换为 Markdown 格式。

重点关注:
1. **表格结构**: 准确识别表格行列,合并单元格
2. **表头**: 正确识别表头行
3. **数据完整性**: 不遗漏任何单元格的数据
4. **表格标题**: 保留表格编号和标题
5. **表格注释**: 保留表格下方的注释和说明

{base_mode}

对于复杂表格:
- 使用 Markdown 表格格式
- 如无法用 Markdown 表示,使用 HTML 表格
- 空单元格标记为空或 "-"
"""

    # 数学公式密集模式
    FORMULA_PROMPT = """请将这个包含大量数学公式的文档页面转换为 LaTeX + Markdown 混合格式。

公式处理规则:
1. **行内公式**: 使用单美元号 $公式$
2. **独立公式**: 使用双美元号 $$公式$$ (独立成行)
3. **矩阵**: 使用 \\begin{{matrix}}...\\end{{matrix}} 或 \\begin{{bmatrix}}...\\end{{bmatrix}}
4. **分式**: 使用 \\frac{{分子}}{{分母}}
5. **上下标**: 使用 ^ (上标) 和 _ (下标)
6. **希腊字母**: 转换为 LaTeX 命令 (如 \\alpha, \\beta, \\sum)
7. **特殊符号**: \\int (积分), \\partial (偏微分), \\infty (无穷) 等
8. **括号**: 使用 \\left( ... \\right) 自动调整大小

{base_mode}

文字说明部分使用标准 Markdown 格式。
"""

    # 混合模式 (自动检测)
    MIXED_PROMPT = """请将这个文档页面转换为 Markdown 格式,自动处理各种元素。

处理规则:
1. **文字**: 标准 Markdown 格式
2. **表格**: Markdown 表格或 HTML 表格
3. **公式**: LaTeX 格式 ($...$ 或 $$...$$)
4. **图片**: ![描述](路径)
5. **代码块**: ```语言 ... ```
6. **列表**: 保留有序/无序列表结构

{base_mode}

优先保证内容的完整性和准确性,不要遗漏任何可见文字。
"""

    @classmethod
    def get_prompt(
        cls,
        mode: OCRMode | str = OCRMode.ACADEMIC,  # **用户选择: 默认 academic**
        custom_instruction: str | None = None,
    ) -> str:
        """获取指定模式的提示词

        Args:
            mode: OCR 模式
            custom_instruction: 自定义指令 (会追加到提示词末尾)

        Returns:
            完整的提示词字符串
        """
        mode = OCRMode(mode) if isinstance(mode, str) else mode

        # 根据模式选择模板
        prompt_map = {
            OCRMode.DOCUMENT: cls.DOCUMENT_PROMPT,
            OCRMode.ACADEMIC: cls.ACADEMIC_PROMPT,
            OCRMode.TABLE: cls.TABLE_PROMPT,
            OCRMode.FORMULA: cls.FORMULA_PROMPT,
            OCRMode.MIXED: cls.MIXED_PROMPT,
        }

        template = prompt_map.get(mode, cls.ACADEMIC_PROMPT)

        # 替换基础模式标记
        prompt = template.format(base_mode=cls.BASE_MARKDOWN)

        # 追加自定义指令
        if custom_instruction:
            prompt = f"{prompt}\n\n额外要求:\n{custom_instruction}"

        return prompt

    @classmethod
    def from_config(cls, mode_name: str) -> str:
        """从配置字符串获取提示词 (兼容性方法)

        Args:
            mode_name: 模式名称 ("academic", "table", "formula", "mixed", "document")

        Returns:
            提示词字符串
        """
        try:
            mode = OCRMode(mode_name.lower())
            return cls.get_prompt(mode)
        except ValueError:
            # 如果不是预定义模式,返回自定义指令
            return f"{cls.BASE_MARKDOWN}\n\n{mode_name}"

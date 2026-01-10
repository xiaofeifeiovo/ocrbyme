@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: 设置颜色和标题
color 0A
title OCRByMe - PDF 转 Markdown 工具

echo.
echo ================================================
echo        OCRByMe - PDF 转 Markdown 工具
echo ================================================
echo.

:: 检查虚拟环境
if not exist "venv\Scripts\activate.bat" (
    echo ❌ 错误: 虚拟环境未找到！
    echo 请先运行安装脚本或手动创建虚拟环境
    echo.
    pause
    exit /b 1
)

:: 激活虚拟环境
call "venv\Scripts\activate.bat"

:: 创建输出文件夹
if not exist "out" mkdir "out"

:: 查找 PDF 文件（排除测试文件）
set "pdf_found=0"
set "pdf_file="

:: 遍历当前目录的 PDF 文件
for %%f in (*.pdf) do (
    :: 排除测试文件
    echo %%f | findstr /i "test_document enriched_test" >nul
    if errorlevel 1 (
        set "pdf_file=%%f"
        set "pdf_found=1"
        goto :found_pdf
    )
)

if "%pdf_found%"=="0" (
    echo.
    echo ❌ 未找到 PDF 文件！
    echo.
    echo 使用方法:
    echo   1. 将要转换的 PDF 文件复制到此文件夹
    echo   2. 双击运行此批处理文件
    echo   3. 生成的 Markdown 文件将保存在 out 文件夹中
    echo   4. 内容将自动复制到剪贴板
    echo.
    pause
    exit /b 1
)

:found_pdf
echo.
echo ✅ 找到 PDF 文件: %pdf_file%
echo.

:: 获取文件名（不含扩展名）
for %%i in ("%pdf_file%") do set "filename=%%~ni"

:: 设置输出路径
set "output_md=out\%filename%.md"

:: 运行 OCR 转换
echo 🚀 开始处理...
echo.
echo 输入文件: %pdf_file%
echo 输出文件: %output_md%
echo.

ocrbyme "%pdf_file%" -o "%output_md%"

:: 检查处理结果
if exist "%output_md%" (
    echo.
    echo ✅ 转换成功！
    echo.
    echo 📁 输出文件: %output_md%
    echo.

    :: 复制到剪贴板
    echo 📋 正在复制到剪贴板...
    powershell -Command "Get-Content '%output_md%' -Raw | Set-Clipboard"

    if errorlevel 1 (
        echo ⚠️  剪贴板复制失败（可能需要管理员权限）
    ) else (
        echo ✅ 内容已复制到剪贴板！
        echo.
        echo 💡 提示: 按 Ctrl+V 可以直接粘贴
    )

    :: 打开输出文件夹
    echo.
    echo 📂 正在打开输出文件夹...
    explorer "out"

) else (
    echo.
    echo ❌ 转换失败！
    echo 请检查错误信息
)

echo.
echo ================================================
echo 按任意键退出...
pause >nul

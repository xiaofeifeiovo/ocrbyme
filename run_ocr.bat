@echo off
setlocal enabledelayedexpansion

:: ========================================
:: OCRByMe - PDF to Markdown Converter
:: ========================================

color 0A
title OCRByMe - PDF to Markdown Converter

echo.
echo ================================================
echo        OCRByMe - PDF to Markdown Converter
echo ================================================
echo.

:: Check virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please install the project first.
    echo.
    pause
    exit /b 1
)

:: Activate virtual environment
call "venv\Scripts\activate.bat"

:: Create output folder
if not exist "out" mkdir "out"

:: ========================================
:: Parameter Handling
:: ========================================

set "pdf_file="

:: Method 1: Check command line argument
if not "%~1"=="" (
    set "pdf_file=%~1"
    echo [INFO] Using command line argument: %pdf_file%
    goto :validate_file
)

:: Method 2: Try to read from clipboard
echo [INFO] No command line argument provided.
echo [INFO] Attempting to read file path from clipboard...
echo.

for /f "usebackq delims=" %%p in (`powershell -NoProfile -Command "try { Get-Clipboard } catch { '' }"`) do (
    set "clipboard_content=%%p"
)

:: Remove quotes and trim
set "pdf_file=!clipboard_content!"
set "pdf_file=!pdf_file:"=!"

:: Check if clipboard contains a file path
if not "!pdf_file!"=="" (
    echo [INFO] Clipboard content: !pdf_file!

    :: Check if it ends with .pdf
    for %%i in ("!pdf_file!") do set "ext=%%~xi"
    if /i "!ext!"==".pdf" (
        echo [INFO] Clipboard contains PDF path, attempting to use it...
        goto :validate_file
    )
)

:: Method 3: Search in current directory
echo [INFO] No valid PDF path in clipboard.
echo [INFO] Searching in current directory...
echo.

for %%f in (*.pdf) do (
    set "testname=%%f"
    set "pdf_file=%%f"

    :: Check if filename contains test keywords
    set "exclude=0"

    echo !testname! | findstr /i "test_document" >nul
    if not errorlevel 1 set "exclude=1"

    echo !testname! | findstr /i "enriched_test" >nul
    if not errorlevel 1 set "exclude=1"

    echo !testname! | findstr /i "demo_sample" >nul
    if not errorlevel 1 set "exclude=1"

    if "!exclude!"=="0" (
        echo [INFO] Found PDF: !pdf_file!
        echo.
        goto :validate_file
    )
)

:: If we get here, no PDF was found
echo.
echo [ERROR] No PDF file found!
echo.
echo Please use one of these methods:
echo   Method 1: Copy PDF file path to clipboard, then run this batch file
echo   Method 2: Run: run_ocr.bat "path\to\file.pdf"
echo   Method 3: Copy PDF to this folder and double-click this batch file
echo.
pause
exit /b 1

:validate_file
:: ========================================
:: Validate File
:: ========================================

echo.
echo [INFO] Validating file...

:: Check if file exists
if not exist "!pdf_file!" (
    echo [ERROR] File not found: !pdf_file!
    echo.
    echo Please check the file path and try again.
    echo.
    pause
    exit /b 1
)

echo [OK] File exists: !pdf_file!

:: Check if it's a PDF
for %%i in ("!pdf_file!") do set "ext=%%~xi"
if /i not "!ext!"==".pdf" (
    echo [ERROR] Not a PDF file: !pdf_file!
    echo.
    pause
    exit /b 1
)

echo [OK] File is a PDF.
echo.

:: ========================================
:: Run OCR Conversion
:: ========================================

:: Get filename without extension
for %%i in ("%pdf_file%") do set "filename=%%~ni"

:: Set output path
set "output_md=out\%filename%.md"

echo [INFO] Starting conversion...
echo   Input:  !pdf_file!
echo   Output: !output_md!
echo.

ocrbyme "!pdf_file!" -o "!output_md!"

:: Check conversion result
set "conversion_success=0"
if exist "!output_md!" (
    set "conversion_success=1"
)

:: ========================================
:: Post-Processing
:: ========================================

if "!conversion_success!"=="1" (
    echo.
    echo [SUCCESS] Conversion completed!
    echo   Output: !output_md!
    echo.

    :: Copy to clipboard with proper encoding (compatible with old PowerShell)
    echo [INFO] Copying to clipboard...

    :: Use compatible method for older PowerShell versions
    powershell -NoProfile -Command ^
        "$content = [System.IO.File]::ReadAllText('!output_md!'); " ^
        "$bytes = [System.Text.Encoding]::UTF8.GetBytes($content); " ^
        "$stream = [System.IO.MemoryStream]::new(); " ^
        "$stream.Write($bytes, 0, $bytes.Length); " ^
        "$stream.Position = 0; " ^
        "$reader = [System.IO.StreamReader]::new($stream); " ^
        "$text = $reader.ReadToEnd(); " ^
        "$reader.Close(); " ^
        "$stream.Close(); " ^
        "$text | Set-Clipboard"

    if errorlevel 1 (
        echo [WARNING] UTF-8 copy failed, trying simple method...
        powershell -NoProfile -Command "[System.IO.File]::ReadAllText('!output_md!') | Set-Clipboard"
        if errorlevel 1 (
            echo [ERROR] Clipboard copy failed. Please manually copy from: !output_md!
        ) else (
            echo [OK] Copied to clipboard!
        )
    ) else (
        echo [OK] Copied to clipboard with UTF-8 encoding!
    )

    echo.
    echo [TIP] Press Ctrl+V to paste the Markdown content
    echo.

    :: Open output folder
    echo [INFO] Opening output folder...
    start "" "out"

) else (
    echo.
    echo [ERROR] Conversion failed!
    echo Please check error messages above.
)

echo.
echo ================================================
echo Press any key to exit...
pause >nul

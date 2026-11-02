@echo off
chcp 65001 >nul
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)
python build_docx_report.py %*
if %errorlevel% neq 0 pause


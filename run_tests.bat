@echo off
chcp 65001 >nul
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)
echo ======================================================================
echo  Запуск автоматических тестов (pytest)
echo ======================================================================
python -m pytest %*
if %errorlevel% neq 0 pause


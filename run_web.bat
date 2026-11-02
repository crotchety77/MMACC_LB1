@echo off
chcp 65001 >nul
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)
echo ======================================================================
echo  Запуск FastAPI Web-сервера (http://127.0.0.1:8000)
echo  Для остановки сервера нажмите Ctrl+C
echo ======================================================================
python -m api.main
if %errorlevel% neq 0 pause


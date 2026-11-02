@echo off
chcp 65001 >nul
echo ======================================================================
echo    MMACC_LB1: Автоматическая установка окружения и зависимостей
echo ======================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ОШИБКА] Python не найден в PATH!
    echo Установите Python 3.10+ с сайта https://www.python.org/ и отметьте галочку "Add Python to PATH".
    pause
    exit /b 1
)

python --version
echo.

if not exist ".venv" (
    echo [1/3] Создание виртуального окружения .venv...
    python -m venv .venv
    if %errorlevel% neq 0 (
        echo [ОШИБКА] Не удалось создать виртуальное окружение .venv.
        pause
        exit /b 1
    )
) else (
    echo [1/3] Виртуальное окружение .venv уже существует.
)

echo [2/3] Установка / обновление зависимостей из requirements.txt...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ОШИБКА] Ошибка при установке пакетов через pip.
    pause
    exit /b 1
)

echo [3/3] Запуск автоматических тестов для проверки ядра...
python -m pytest
if %errorlevel% neq 0 (
    echo [ПРЕДУПРЕЖДЕНИЕ] Некоторые тесты завершились с ошибкой.
) else (
    echo.
    echo ======================================================================
    echo  Все зависимости успешно установлены, тесты пройдены на 100%!
    echo ======================================================================
    echo.
    echo Для запуска программы используйте:
    echo   run_cli.bat      - Интерактивное консольное меню (CLI)
    echo   run_report.bat   - Генерация чистового отчёта Word (.docx)
    echo   run_web.bat      - Запуск FastAPI Web-сервера
    echo.
)

pause


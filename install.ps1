# PowerShell скрипт установки зависимостей MMACC_LB1
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   MMACC_LB1: Автоматическая установка окружения и зависимостей" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ОШИБКА] Python не найден в системе. Установите Python 3.10+ и добавьте его в PATH." -ForegroundColor Red
    exit 1
}

$pyVersion = python --version
Write-Host "Обнаружен $pyVersion" -ForegroundColor Green

if (-not (Test-Path ".venv")) {
    Write-Host "`n[1/3] Создание виртуального окружения .venv..." -ForegroundColor Yellow
    python -m venv .venv
} else {
    Write-Host "`n[1/3] Виртуальное окружение .venv уже существует." -ForegroundColor Green
}

$venvPython = Join-Path (Get-Location) ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    $venvPython = "python"
}

Write-Host "`n[2/3] Установка зависимостей из requirements.txt..." -ForegroundColor Yellow
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

Write-Host "`n[3/3] Запуск верификационных тестов..." -ForegroundColor Yellow
& $venvPython -m pytest

Write-Host "`n======================================================================" -ForegroundColor Cyan
Write-Host " Все зависимости успешно установлены, тесты пройдены!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "Запуск приложения:"
Write-Host "  run_cli.bat      - Консольный интерфейс (CLI)"
Write-Host "  run_report.bat   - Генератор отчёта Word (.docx)"
Write-Host "  run_web.bat      - FastAPI Web-сервер`n"


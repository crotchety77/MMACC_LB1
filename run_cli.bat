@echo off
chcp 65001 >nul
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)
python -m expert_estimate.algorithm %*
if %errorlevel% neq 0 pause


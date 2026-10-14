@echo off
setlocal
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not found in PATH.
    echo Please install Python 3.10 or higher from https://www.python.org/downloads/
    pause
    exit /b 1
)

python start.py %*
if errorlevel 1 (
    echo.
    echo Agent exited with an error.
    pause
)

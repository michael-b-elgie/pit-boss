@echo off
echo ================================================
echo    Pit Boss Poker Timer - Setup & Installation
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.6+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python detected:
python --version
echo.

REM Install PyInstaller if needed
echo Checking for PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    pip install pyinstaller
) else (
    echo PyInstaller is already installed.
)

echo.
echo ================================================
echo Setup complete! You can now:
echo.
echo 1. Run the application directly:
echo    - Double-click "run.bat" 
echo    - OR run: python poker_timer.py
echo.
echo 2. Build a standalone executable:
echo    - Double-click "build.bat"
echo    - Executable will be in the "dist" folder
echo.
echo 3. Customize your tournament:
echo    - Edit poker_config.json after first run
echo    - Or use the built-in configuration editors
echo.
echo ================================================
pause
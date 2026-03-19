@echo off
echo Building Pit Boss Poker Timer executable...

REM Install pyinstaller if not already installed
pip install pyinstaller

REM Check if icon exists, if not create a simple one
if not exist poker_icon.ico (
    echo Creating default icon...
    python -c "
import tkinter as tk
root = tk.Tk()
root.withdraw()
try:
    from PIL import Image
    # Create a simple poker-themed icon if PIL is available
    img = Image.new('RGB', (32, 32), color='red')
    img.save('poker_icon.ico')
    print('Created simple icon')
except:
    print('PIL not available, building without custom icon')
    pass
root.destroy()
"
)

REM Build the executable with or without icon
if exist poker_icon.ico (
    echo Building with custom icon...
    pyinstaller --onefile --windowed --name "PitBoss" --icon=poker_icon.ico poker_timer.py
) else (
    echo Building without custom icon...
    pyinstaller --onefile --windowed --name "PitBoss" poker_timer.py
)

REM Copy config template to dist folder
if exist dist\poker_config.json (
    echo Config file already exists in dist folder
) else (
    echo Creating default config file in dist folder...
    copy poker_config_template.json dist\poker_config.json
)

echo.
echo Build complete! Executable is in the 'dist' folder.
echo You can run PitBoss.exe from the dist folder.
pause
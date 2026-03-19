# Pit Boss - Poker Timer Application

A comprehensive poker tournament timer application built with Python and tkinter that5. **Visual Features**
   - **Live Prize Display**: Always see what each position pays out
   - **Theme Selection**: Switch between Classic, Dark, Vegas, or Royal themes
   - **Status Indicators**: Clear display of timer status and game state
   - **Organized Layout**: Three-panel design keeps all information visible
   - **Custom Icons**: Add your poker night image as the application icon (works in Python too!)

6. **State Persistence** compiled into a Windows executable.

## 🎯 Features

### 🎲 **Game Timer**
- Configurable game duration (default: 20 minutes)
- Automatic break timer when game time expires
- Pause/resume functionality
- Visual timer display with MM:SS format
- Clear status indicators (Running/Paused/Break)

### 🕐 **Break Timer** 
- Configurable break duration (default: 10 minutes)
- Manual break activation
- Automatic return to game timer after break

### 💰 **Blind Level Management**
- Automatic blind level increases based on configurable intervals
- Manual blind level control (next/previous)
- Fully customizable blind structure
- Support for antes
- Visual display of current level, small/big blinds, and ante

### 👥 **Player Management**
- **Add/Remove Players**: Simple UI to manage active players
- **Elimination System**: Double-click any active player to eliminate them
- **Reactivation Feature**: Double-click eliminated player to move back to active
- **Mistake Recovery**: Right-click eliminated players for reactivation menu
- **Automatic Positioning**: Eliminated players get correct finishing position
- **Position Reordering**: When players are reactivated, positions automatically adjust
- **Clear Instructions**: Visual hints show how to eliminate/reactivate players

### 🏆 **Prize Structure & Display**
- **Live Prize Display**: Prize structure shown on main screen at all times
- Configurable prize structure with positions (1st, 2nd, 3rd, etc.)
- Support for percentage-based or fixed amount prizes
- Automatic prize calculation when players are eliminated
- Visual display of eliminated players with their finishing position and prize
- Total prize pool prominently displayed

### 🎨 **Themes & Customization**
- **Multiple Themes**: 
  - **Classic**: Traditional clean interface
  - **Dark**: Modern dark theme with white text
  - **Vegas**: Casino green with gold accents
  - **Royal**: Royal blue with gold highlights
- **Custom Tournament Titles**: Add your own tournament name
- **Flexible Layout**: Three-panel design for optimal information display

### ⚙️ **Configuration**
- All settings stored in JSON file (`poker_config.json`)
- Automatic state persistence - resume exactly where you left off
- Configurable timers, blinds, and prize structures
- Auto-save every 30 seconds
- Theme preferences saved

## Installation & Setup

### Option 1: Run Python Script Directly
1. Ensure Python 3.6+ is installed
2. Clone or download this repository
3. Run: `python poker_timer.py`

### Option 2: Build Windows Executable
1. Install PyInstaller: `pip install pyinstaller`
2. Run the build script: `build.bat`
3. Find the executable in the `dist` folder
4. Copy `poker_config.json` to the same folder as the executable

## Configuration

### Timer Settings
- **Game Duration**: Length of each game level (minutes)
- **Break Duration**: Length of breaks (minutes) 
- **Blind Increase Interval**: How often blinds automatically increase (minutes)

### Blind Structure
The application comes with a default tournament blind structure, but you can fully customize it:
- Small blind amounts
- Big blind amounts  
- Ante amounts (optional)
- Add/remove blind levels as needed

### Prize Structure
Configure your tournament's payout structure:
- Set total prize pool amount
- Define positions (1st, 2nd, 3rd, etc.)
- Use percentage-based or fixed amount prizes
- Automatic calculation when players are eliminated

## Usage

### 🎨 **Customization**
1. **Set Tournament Title**: Click "Edit Title" to customize your tournament name
2. **Choose Theme**: Click "Theme" button to select from 4 different visual themes
3. **Configure Layout**: The three-panel layout shows:
   - **Left Panel**: Timer, blinds, and configuration controls
   - **Middle Panel**: Active and eliminated players
   - **Right Panel**: Live prize structure and prize pool

### 🎯 **Setup Tournament**
   - Add all players using the "Add Player" button
   - Configure timer settings, blinds, and prizes as needed
   - Set the total prize pool amount
   - Choose your preferred theme and tournament title

2. **Run Tournament**
   - Click "Start Game" to begin the timer
   - Blinds will automatically increase based on your interval setting
   - Use "Start Break" to pause game and run break timer
   - Use manual blind level controls if needed

3. **Eliminate Players**
   - Double-click on any player in the Active Players list
   - They'll automatically be moved to eliminated list with correct position and prize
   - Position is based on order of elimination

4. **Reactivate Players (New!)**
   - **Made a mistake?** Double-click any eliminated player to reactivate them
   - **Right-click menu**: Right-click eliminated players for reactivation option
   - **Smart reordering**: Remaining eliminated players automatically get new positions
   - **Button option**: Use "Reactivate Selected" button for easy access

5. **Visual Features**
   - **Live Prize Display**: Always see what each position pays out
   - **Theme Selection**: Switch between Classic, Dark, Vegas, or Royal themes
   - **Status Indicators**: Clear display of timer status and game state
   - **Organized Layout**: Three-panel design keeps all information visible

5. **State Persistence**
   - Configuration automatically saves every 30 seconds
   - Close and reopen the application to resume exactly where you left off
   - All timer states, blind levels, and player information preserved

## Adding Your Custom Icon

Your poker night image will appear **prominently in the application interface** for everyone to see!

### 🖼️ **How to Add Your Icon:**

1. **Save your poker night image** in the project folder with one of these names:
   - `poker_icon.png` (recommended - best quality)
   - `poker_icon.gif` (animated images supported!)
   - `poker_icon.jpg` or `poker_icon.jpeg`

2. **Image Guidelines**:
   - **Size**: Works best with square images (same width and height)
   - **Recommended dimensions**: 128x128 to 512x512 pixels
   - **Format**: PNG, GIF, or JPEG
   - **The app will automatically resize large images**

3. **Where Your Icon Appears**:
   - **Window title bar** (small icon)
   - **Main interface** (large display in left panel for everyone to see!)
   - **Tournament branding** - perfect for "Kyle's 35th Birthday Poker Night"

4. **No icon?** The application works perfectly without one - just add it anytime!

### 📱 **Icon Display Features:**
- **Automatic Loading**: Detects and loads your icon when the app starts
- **Smart Sizing**: Large icons are automatically resized to fit perfectly  
- **Graceful Fallback**: App works normally if no icon is found
- **Live Display**: Icon appears prominently on the main screen during play
- **Tournament Branding**: Perfect for showing your event theme/logo

**💡 Pro Tip**: Use your poker night photo as the icon so everyone can see the theme throughout the tournament!

## File Structure

```
pit-boss/
├── poker_timer.py              # Main application
├── requirements.txt            # Python dependencies
├── build.bat                   # Windows build script
├── run.bat                     # Quick run script
├── setup.bat                   # Installation helper
├── create_icon.py              # Icon creation utility
├── poker_config_template.json  # Default configuration template
└── README.md                   # This file
```

## Building Executable

To create a standalone Windows executable:

1. Install PyInstaller: `pip install pyinstaller`
2. Run: `build.bat`
3. Executable will be created in `dist/PitBoss.exe`
4. Copy the executable anywhere - it includes all dependencies

## Customization

The application is highly configurable through the JSON config file and built-in editors:

### Themes
- **Classic**: Clean, traditional Windows appearance
- **Dark**: Modern dark mode with white text on dark backgrounds  
- **Vegas**: Casino-style green felt with gold accents
- **Royal**: Elegant royal blue with gold highlights

### Tournament Titles
- Add custom tournament names (e.g., "Kyle's 35th Birthday Poker Night")
- Titles appear in window title bar and can be displayed on main screen
- Perfect for special events and themed tournaments

### Prize Structure Customization

### Prize Structure Customization
- Modify default blind structures for different tournament types
- Adjust timer durations for your preferred pace
- Customize prize structures for different player counts
- Add more blind levels for longer tournaments
- Set percentage-based or fixed dollar amount prizes

### Visual Customization
- **Live Prize Display**: Prizes shown prominently on main screen
- **Three-Panel Layout**: Optimal information organization
- **Theme Integration**: All themes include coordinated colors for labels, buttons, and backgrounds

## Technical Details

- Built with Python 3 and tkinter (no external dependencies for core functionality)
- Multi-threaded timer system for accurate timing
- JSON-based configuration for easy customization and portability
- Cross-platform compatible (primarily designed for Windows)
- Automatic state persistence and recovery

## Tips

- **Backup your config**: The `poker_config.json` file contains all your tournament data
- **Test settings**: Try different timer and blind configurations to find what works for your group
- **Player management**: You can add/remove players even after the tournament starts
- **Manual control**: All automatic features can be overridden manually if needed

## Support

For issues or feature requests, please check the project repository or contact the developer.

---

**Pit Boss** - Professional poker tournament management made simple.
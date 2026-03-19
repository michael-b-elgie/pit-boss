"""
Simple icon extraction utility for the poker timer application.
This script helps convert the provided poker image into an icon format.
"""

import base64
import os

# This would contain the base64 encoded version of your poker image
# For now, we'll create a placeholder that you can replace with the actual image data
def create_poker_icon():
    """
    Creates a poker-themed icon for the application.
    Replace this with the actual image data from your poker night image.
    """
    
    # Instructions for the user
    instructions = """
    TO USE YOUR POKER NIGHT IMAGE AS AN ICON:
    
    1. Save your poker night image as 'poker_icon.png' in this directory
    2. For best results, make it square (e.g., 256x256 or 512x512 pixels)
    3. Run the build script - it will automatically use poker_icon.png
    4. If you want an .ico file, you can use online converters to convert PNG to ICO
    
    Alternatively, place your image file in this directory and rename it to:
    - poker_icon.png (for PNG format)
    - poker_icon.ico (for ICO format)
    
    The build script will automatically detect and use it.
    """
    
    print(instructions)
    
    # Check if user has already placed an icon file
    for icon_file in ['poker_icon.png', 'poker_icon.ico', 'poker_icon.jpg', 'poker_icon.jpeg']:
        if os.path.exists(icon_file):
            print(f"✓ Found icon file: {icon_file}")
            print("Your icon is ready to use!")
            return True
    
    print("No icon file found. Please follow the instructions above.")
    return False

if __name__ == "__main__":
    create_poker_icon()
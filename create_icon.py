import tkinter as tk
from tkinter import filedialog, messagebox
import os

def create_icon():
    """Simple utility to help create an icon file for the application"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    # Ask user to select an image file
    image_path = filedialog.askopenfilename(
        title="Select Image for Icon",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.ico"),
            ("All files", "*.*")
        ]
    )
    
    if image_path:
        try:
            # For now, just copy the file as poker_icon.png
            import shutil
            output_path = "poker_icon.png"
            shutil.copy2(image_path, output_path)
            
            print(f"Icon saved as {output_path}")
            print("You can use this file as an icon for the application.")
            print("To use it with PyInstaller, add --icon=poker_icon.ico to the build command.")
            
        except Exception as e:
            print(f"Error processing icon: {e}")
    
    root.destroy()

if __name__ == "__main__":
    create_icon()
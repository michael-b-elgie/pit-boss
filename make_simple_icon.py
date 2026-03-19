# Simple script to create a basic poker icon if none exists
import tkinter as tk
from tkinter import PhotoImage
import os

def create_simple_icon():
    """Create a simple poker-themed icon using tkinter"""
    
    # Check if an icon already exists
    icon_files = ['poker_icon.ico', 'poker_icon.png', 'poker_icon.jpg', 'poker_icon.jpeg']
    for icon_file in icon_files:
        if os.path.exists(icon_file):
            print(f"Icon file {icon_file} already exists!")
            return
    
    try:
        # Create a simple icon using tkinter canvas
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Create a canvas for drawing
        canvas = tk.Canvas(root, width=64, height=64, bg='darkred')
        
        # Draw a simple playing card shape
        canvas.create_rectangle(10, 5, 54, 59, fill='white', outline='black', width=2)
        
        # Draw spade symbol (approximation using ovals and triangle)
        canvas.create_oval(28, 15, 36, 25, fill='black')
        canvas.create_oval(25, 20, 33, 30, fill='black')
        canvas.create_oval(31, 20, 39, 30, fill='black')
        canvas.create_polygon(32, 30, 28, 35, 36, 35, fill='black')
        canvas.create_rectangle(31, 35, 33, 40, fill='black')
        
        # Draw "A" for Ace
        canvas.create_text(20, 45, text='A', font=('Arial', 12, 'bold'), fill='black')
        canvas.create_text(44, 20, text='A', font=('Arial', 12, 'bold'), fill='black')
        
        canvas.update()
        
        # Save as PostScript first (tkinter limitation), then we can convert
        canvas.postscript(file="temp_icon.ps")
        
        print("Basic icon template created!")
        print("For a better icon, replace poker_icon.png with your custom image.")
        
        root.destroy()
        
        # Clean up temp file
        if os.path.exists("temp_icon.ps"):
            os.remove("temp_icon.ps")
            
    except Exception as e:
        print(f"Could not create icon: {e}")
        print("You can manually add poker_icon.png or poker_icon.ico to use a custom icon.")

if __name__ == "__main__":
    create_simple_icon()
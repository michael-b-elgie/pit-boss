import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_poker_icon():
    """Create a sample poker icon for demonstration"""
    
    # Check if PIL is available
    try:
        # Create a 256x256 image with a poker theme
        size = 256
        img = Image.new('RGBA', (size, size), (139, 0, 0, 255))  # Dark red background
        draw = ImageDraw.Draw(img)
        
        # Draw a playing card background
        card_margin = 30
        card_rect = [card_margin, card_margin, size - card_margin, size - card_margin]
        draw.rectangle(card_rect, fill='white', outline='black', width=4)
        
        # Draw spade symbols
        center_x, center_y = size // 2, size // 2
        
        # Large center spade (approximation with polygons)
        spade_points = [
            (center_x, center_y - 30),
            (center_x - 25, center_y),
            (center_x - 15, center_y + 15),
            (center_x - 5, center_y + 25),
            (center_x + 5, center_y + 25),
            (center_x + 15, center_y + 15),
            (center_x + 25, center_y),
        ]
        draw.polygon(spade_points, fill='black')
        
        # Spade stem
        draw.rectangle([center_x - 3, center_y + 25, center_x + 3, center_y + 40], fill='black')
        
        # Corner symbols
        try:
            # Try to add text (may not work if font not available)
            font_size = 24
            font = ImageFont.load_default()
            draw.text((50, 50), 'A', fill='black', font=font)
            draw.text((size - 70, size - 70), 'A', fill='black', font=font)
        except:
            pass
        
        # Add some poker chips around the card
        chip_color = (0, 100, 0)  # Green
        chip_positions = [(60, 200), (200, 60), (200, 200)]
        for x, y in chip_positions:
            draw.ellipse([x-15, y-15, x+15, y+15], fill=chip_color, outline='white', width=2)
        
        # Save the image
        img.save('poker_icon.png', 'PNG')
        print("Created sample poker icon: poker_icon.png")
        print("You can replace this with your custom poker night image!")
        
        return True
        
    except ImportError:
        print("PIL (Python Imaging Library) not available.")
        print("Install with: pip install Pillow")
        return False
    except Exception as e:
        print(f"Error creating icon: {e}")
        return False

def create_simple_tkinter_icon():
    """Create a very simple icon using tkinter (fallback method)"""
    try:
        # This creates a very basic icon using tkinter
        root = tk.Tk()
        root.withdraw()
        
        # Create a simple red square icon (64x64)
        # This is very basic but will show the icon display feature
        canvas = Canvas(root, width=64, height=64, bg='darkred')
        canvas.create_rectangle(5, 5, 59, 59, fill='white', outline='black', width=2)
        canvas.create_text(32, 20, text='♠', font=('Arial', 20), fill='black')
        canvas.create_text(15, 45, text='A', font=('Arial', 12, 'bold'), fill='black')
        canvas.create_text(50, 45, text='A', font=('Arial', 12, 'bold'), fill='black')
        
        # Save as postscript (limited but works)
        canvas.update()
        canvas.postscript(file="simple_icon.eps")
        
        root.destroy()
        
        print("Created basic icon template.")
        print("For better results, save your poker image as poker_icon.png")
        return True
        
    except Exception as e:
        print(f"Could not create simple icon: {e}")
        return False

if __name__ == "__main__":
    # Check if icon already exists
    if os.path.exists('poker_icon.png'):
        print("poker_icon.png already exists!")
    else:
        print("Creating sample poker icon...")
        if not create_sample_poker_icon():
            create_simple_tkinter_icon()
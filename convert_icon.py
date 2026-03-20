"""
Convert poker_icon.jpeg to poker_icon.png for use with the poker timer
"""
import os
from PIL import Image

def convert_jpeg_to_png():
    """Convert JPEG icon to PNG format"""
    
    # Check for JPEG files
    jpeg_files = ['poker_icon.jpeg', 'poker_icon.jpg']
    
    for jpeg_file in jpeg_files:
        if os.path.exists(jpeg_file):
            try:
                print(f"Found {jpeg_file}, converting to PNG...")
                
                # Open and convert the image
                with Image.open(jpeg_file) as img:
                    # Convert to RGB if needed (in case of RGBA mode)
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Convert to RGB for better compatibility
                        rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                        img = rgb_img
                    
                    # Save as PNG
                    img.save('poker_icon.png', 'PNG', optimize=True)
                    print(f"Successfully converted {jpeg_file} to poker_icon.png")
                    print(f"Image size: {img.size[0]}x{img.size[1]} pixels")
                    return True
                    
            except Exception as e:
                print(f"Error converting {jpeg_file}: {e}")
                continue
    
    print("No JPEG icon files found.")
    return False

def create_fallback_icon():
    """Create a simple fallback icon if conversion fails"""
    try:
        # Create a simple poker-themed icon
        img = Image.new('RGB', (128, 128), color='darkred')
        
        # We'll create a simple colored square since we can't draw complex shapes easily
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        # Draw a white card shape
        draw.rectangle([20, 10, 108, 118], fill='white', outline='black', width=2)
        
        # Try to add text (may fail if font not available)
        try:
            # Draw suit symbols (approximated)
            draw.text((50, 40), '♠', fill='black', anchor='mm')
            draw.text((35, 100), 'A', fill='black', anchor='mm') 
            draw.text((85, 25), 'A', fill='black', anchor='mm')
        except:
            # If text drawing fails, just make a solid icon
            draw.rectangle([30, 20, 98, 108], fill='red', outline='black', width=2)
        
        img.save('poker_icon.png', 'PNG')
        print("Created fallback poker icon")
        return True
        
    except ImportError:
        print("PIL not available. Please install with: pip install Pillow")
        return False
    except Exception as e:
        print(f"Error creating fallback icon: {e}")
        return False

if __name__ == "__main__":
    print("Poker Icon Converter")
    print("===================")
    
    # First try to convert existing JPEG
    if convert_jpeg_to_png():
        print("\n✓ Conversion successful! Restart poker_timer.py to see your icon.")
    else:
        print("\nNo JPEG found, trying to create a simple fallback icon...")
        if create_fallback_icon():
            print("\n✓ Fallback icon created! Restart poker_timer.py to see it.")
        else:
            print("\n✗ Could not create icon. You can manually convert your JPEG to PNG format.")
            print("   Online converters: jpeg-to-png.com or similar")
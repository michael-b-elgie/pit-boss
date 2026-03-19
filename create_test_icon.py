import tkinter as tk
import base64

def create_test_icon():
    """Create a simple test icon using base64 encoded PNG data"""
    
    # This is a tiny 32x32 PNG image (red square with black border and spade symbol)
    png_data = """
iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAYAAABzenr0AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAA2SURBVFhH7c4xAQAgDMSwwL/z4MJJqKbMQIAAAQIECBAgQIAAAQIECBAgQIAAAQIECBAgQKAAAFABASBDHGwAAAAASUVORK5CYII=
"""
    
    try:
        # Decode the base64 data and write to file
        import binascii
        png_bytes = base64.b64decode(png_data.strip())
        
        with open('poker_icon.png', 'wb') as f:
            f.write(png_bytes)
        
        print("Created test poker_icon.png")
        return True
        
    except Exception as e:
        print(f"Could not create test icon: {e}")
        
        # Alternative: Create a simple GIF using tkinter
        try:
            root = tk.Tk()
            root.withdraw()
            
            # Create a simple pattern
            # This creates a basic image that tkinter can handle
            gif_data = "R0lGODlhIAAgAPIAAP8AAP////8A/wAA/wD/AP//AAAAAAAAACH5BAAAAAAALAAAAAAgACAAAAM2CLrc/jDKSau9OOvNu/9gKI5kaZ5oqq5s675wLM90bd94ru987//AoHBILBqPyKRyyWw6n9BI"
            
            # Write as a simple text placeholder instead
            with open('poker_icon_data.txt', 'w') as f:
                f.write("Save your poker image as poker_icon.png or poker_icon.gif")
            
            print("Created placeholder - add your poker_icon.png manually")
            root.destroy()
            return True
            
        except Exception as e2:
            print(f"Could not create any icon: {e2}")
            return False

if __name__ == "__main__":
    create_test_icon()
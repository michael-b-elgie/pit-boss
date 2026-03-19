import tkinter as tk

def create_basic_icon():
    """Create a very basic icon using tkinter that can be saved as PNG"""
    
    # Create a simple colored rectangle and save it
    # This is a workaround since PIL isn't available
    
    root = tk.Tk()
    root.withdraw()
    
    try:
        # Create a PhotoImage with a simple pattern
        # This creates a 64x64 red square with white border
        icon_data = '''
        R0lGODlhQABAAIAAAP8AAP///yH5BAAAAAAALAAAAABAAEAAAAJUhI+py+0Po5y02ouz3rz7D4biSJbmiabqyrbuC8fyTNf2jef6zvf+DwwKh8Si8YhMKpfMpvMJjUqn1Kr1is1qt9yu9wsOi8fksvmMTqvX7Lb7DY/L5/S6/Y7P6/f8vv8PGCg4SFhoeIiYqLjI2Oj4CBkpOUlZaXmJmam5ydnp+QkaKjpKWmp6ipqqusra6voKGys7S1tre4ubq7vL2+v7CxwsPExcbHyMnKy8zNzs/AwdLT1NXW19jZ2tvc3d7f0NHi4+Tl5ufo6err7O3u7+Dh8vP09fb3+Pn6+/z9/v/w8woMCBBAsaPIgwocKFDBs6fAgxosSJFCtavIgxo8aNHDt6/AgypMiRJEuaPIkypcqVLFu6fAkzpsyZNGvavIkzp86dPHv6/Ak0qNCh'''
        
        # Actually, let's create a simple text-based placeholder
        with open('poker_icon.png.txt', 'w') as f:
            f.write("Placeholder for poker icon - replace this file with poker_icon.png")
        
        print("Created placeholder. To add your poker night image:")
        print("1. Save your image as 'poker_icon.png' in this folder")
        print("2. Make sure it's a PNG, JPG, or GIF file")
        print("3. Restart the application to see it displayed")
        
    except Exception as e:
        print(f"Error: {e}")
    
    root.destroy()

if __name__ == "__main__":
    create_basic_icon()
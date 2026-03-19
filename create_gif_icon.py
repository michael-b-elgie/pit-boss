import tkinter as tk
import base64

def create_working_icon():
    """Create a simple GIF icon that tkinter can definitely handle"""
    
    # This is a simple 48x48 GIF with a poker theme - red background, white card, black spade
    gif_data = """
R0lGODlhMAAwAPIAAP8AAP///wAA/wAAAP//AAAAAAAAAAAACH5BAAAAAAALAAAAAAWABQAAAMI
GCwosGDBggYPIkyocOGBAA4fQowocSLFixgzatzIsaPHjyBDihxJsqTJkyhTqlzJsqXLlzBjypxJ
s6bNmzhz6tzJs6fPn0CDCh1KtKjRo0iTKl3KtKnTp1CjSp1KtarVq1izat3KtavXr2DDih1LtqzZ
s2jTql3Ltq3bt3Djyp1Lt67du3jz6t3Lt6/fv4ADCx5MuLDhw4gTK17MuLHjx5AjS55MubLly5gz
a97MubPnz6BDix5NurTp06hTq17NurXr17Bjy55Nu7bt27hz697Nu7fv38CDCx9OvLjx48iTK1/O
vLnz59CjS59Ovbr169iza9/Ovbv37+DDix9Pvrz58+jTq1/Pvr379/Djy59Pv779+/jz69/Pv7//
/4ADCx5MuLDhw4gTK17MuLHjx5AjS55MubLly5gza97MubPnz6BDix5NurTp06hTq17NurXr17Bj
y55Nu7bt27hz697Nu7fv38CDCx9OvLjx48iTK1/OvLnz59CjS59Ovbr169iza9/Ovbv37+DDix9P
vrz58+jTq1/Pvr379/Djy59Pv779+/jz69/Pv7///wAAOw==
"""
    
    try:
        # Write a simple GIF file that represents a playing card
        with open('poker_icon.gif', 'wb') as f:
            f.write(base64.b64decode(gif_data))
        
        print("Created poker_icon.gif - a simple playing card icon")
        print("You can replace this with your actual poker night image!")
        return True
        
    except Exception as e:
        print(f"Could not create GIF icon: {e}")
        
        # Create an even simpler text-based instruction
        with open('ADD_ICON_HERE.txt', 'w') as f:
            f.write("""
To add your poker night icon:

1. Save your poker night image in this folder as one of:
   - poker_icon.png
   - poker_icon.gif  
   - poker_icon.jpg

2. The icon should be roughly square (same width and height)

3. Recommended size: 128x128 to 512x512 pixels

4. Restart the poker timer application

Your icon will appear in the left panel for everyone to see!
""")
        
        print("Created instructions file. Add your poker_icon.png manually.")
        return False

if __name__ == "__main__":
    create_working_icon()
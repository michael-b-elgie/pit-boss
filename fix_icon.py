"""
Simple Icon Converter for Poker Timer
Converts JPEG images to PNG format without external dependencies
"""

def show_conversion_instructions():
    """Show instructions for converting JPEG to PNG"""
    
    print("🃏 POKER ICON CONVERTER")
    print("=" * 50)
    print()
    print("❌ JPEG FORMAT NOT SUPPORTED")
    print("   Your poker_icon.jpeg cannot be loaded by the poker timer")  
    print("   because tkinter only supports PNG and GIF formats.")
    print()
    print("✅ SOLUTION: Convert to PNG format")
    print()
    print("METHOD 1 - Online Converter (Recommended):")
    print("   1. Go to: https://convertio.co/jpeg-png/")
    print("   2. Upload your poker_icon.jpeg file") 
    print("   3. Download the converted file")
    print("   4. Rename it to 'poker_icon.png'")
    print("   5. Place it in this folder")
    print("   6. Restart poker_timer.py")
    print()
    print("METHOD 2 - Windows Paint:")
    print("   1. Right-click poker_icon.jpeg → 'Open with' → 'Paint'")
    print("   2. Click 'File' → 'Save As' → 'PNG picture'") 
    print("   3. Name it 'poker_icon.png'")
    print("   4. Restart poker_timer.py")
    print()
    print("METHOD 3 - Install PIL/Pillow (Advanced):")
    print("   1. Run: pip install Pillow")
    print("   2. Run this script again")
    print()
    print("📁 Current folder:", __file__.replace('\\convert_icon.py', ''))
    print()

def check_for_supported_icons():
    """Check what icon files exist"""
    import os
    
    supported_files = ['poker_icon.png', 'poker_icon.gif']
    unsupported_files = ['poker_icon.jpeg', 'poker_icon.jpg']
    
    print("📋 ICON FILE STATUS:")
    print("-" * 30)
    
    found_supported = False
    found_unsupported = False
    
    for file in supported_files:
        if os.path.exists(file):
            print(f"✅ {file} - Supported format, ready to use!")
            found_supported = True
        else:
            print(f"❌ {file} - Not found")
    
    for file in unsupported_files:
        if os.path.exists(file):
            print(f"⚠️  {file} - Found but needs conversion to PNG")
            found_unsupported = True
        else:
            print(f"❌ {file} - Not found") 
    
    print()
    
    if found_supported:
        print("🎉 You have supported icon files! Restart poker_timer.py")
    elif found_unsupported:
        print("🔧 You have JPEG files that need conversion (see instructions above)")
    else:
        print("📷 No icon files found. Add poker_icon.png or poker_icon.gif")
    
    return found_supported, found_unsupported

if __name__ == "__main__":
    supported, unsupported = check_for_supported_icons()
    
    if unsupported and not supported:
        print()
        show_conversion_instructions()
    elif supported:
        print("✨ All set! Your icon should work with the poker timer.")
    else:
        print()
        print("💡 TIP: Add your poker night photo as 'poker_icon.png'")
        print("   It will appear prominently during your tournament!")
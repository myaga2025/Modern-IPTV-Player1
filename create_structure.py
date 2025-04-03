import os
import sys
import shutil
from PIL import Image, ImageDraw

def create_directory_structure():
    """Create the required directory structure for the IPTV application"""
    print("Creating directory structure for Modern IPTV Player...")
    
    # Get the root directory
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define required directories
    required_dirs = [
        os.path.join(root_dir, "resources"),
        os.path.join(root_dir, "resources", "icons"),
        os.path.join(root_dir, "translations"),
    ]
    
    # Create directories if they don't exist
    for directory in required_dirs:
        if not os.path.exists(directory):
            print(f"Creating directory: {directory}")
            os.makedirs(directory, exist_ok=True)
    
    # Create default app icon if it doesn't exist
    icon_png_path = os.path.join(root_dir, "resources", "icons", "app_icon.png")
    if not os.path.exists(icon_png_path):
        print(f"Creating default app icon: {icon_png_path}")
        create_default_icon(icon_png_path)
    
    # Convert PNG to ICO if ICO doesn't exist
    icon_ico_path = os.path.join(root_dir, "resources", "icons", "app_icon.ico")
    if not os.path.exists(icon_ico_path) and os.path.exists(icon_png_path):
        print(f"Converting PNG to ICO: {icon_ico_path}")
        try:
            img = Image.open(icon_png_path)
            img.save(icon_ico_path, format="ICO")
        except Exception as e:
            print(f"Error converting icon: {e}")
    
    # Create empty translation files if they don't exist
    for lang in ["en", "ar"]:
        trans_path = os.path.join(root_dir, "translations", f"{lang}.qm")
        if not os.path.exists(trans_path):
            print(f"Creating empty translation file: {trans_path}")
            open(trans_path, "wb").close()
    
    print("Directory structure creation complete!")

def create_default_icon(filepath):
    """Create a default app icon"""
    try:
        # Create a blue square image
        img = Image.new('RGB', (256, 256), color=(65, 105, 225))
        draw = ImageDraw.Draw(img)
        
        # Draw TV-like shape
        draw.rectangle((50, 70, 206, 170), fill=(20, 20, 80))
        draw.rectangle((60, 80, 196, 160), fill=(200, 200, 255))
        
        # Draw stand
        draw.rectangle((110, 170, 146, 200), fill=(40, 40, 100))
        draw.rectangle((80, 200, 176, 210), fill=(40, 40, 100))
        
        # Draw "IPTV" text
        draw.text((90, 110), "IPTV", fill=(0, 0, 100), stroke_width=2)
        
        # Save the image
        img.save(filepath)
        print(f"Default icon created successfully at {filepath}")
    except Exception as e:
        print(f"Error creating default icon: {e}")
        # Create an empty file as fallback
        open(filepath, 'wb').close()

if __name__ == "__main__":
    create_directory_structure()

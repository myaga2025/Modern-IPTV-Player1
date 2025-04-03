import os
import sys
from PIL import Image

def convert_to_ico():
    """Check if app icon exists and convert to .ico if needed"""
    resources_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resources', 'icons')
    
    if not os.path.exists(resources_dir):
        print(f"Creating resources directory: {resources_dir}")
        os.makedirs(resources_dir, exist_ok=True)
    
    png_path = os.path.join(resources_dir, 'app_icon.png')
    ico_path = os.path.join(resources_dir, 'app_icon.ico')
    
    if not os.path.exists(png_path):
        print("Warning: app_icon.png not found. Creating a default icon.")
        create_default_icon(png_path)
    
    if not os.path.exists(ico_path):
        print(f"Converting {png_path} to {ico_path}")
        try:
            img = Image.open(png_path)
            img.save(ico_path, format='ICO')
            print("Icon conversion successful.")
        except Exception as e:
            print(f"Error converting icon: {e}")
            return False
    else:
        print("Icon file already exists.")
    
    return True

def create_default_icon(filepath):
    """Create a simple default icon"""
    try:
        img = Image.new('RGB', (256, 256), color=(65, 105, 225))
        img.save(filepath)
    except Exception as e:
        print(f"Error creating default icon: {e}")

if __name__ == "__main__":
    convert_to_ico()
    print("Icon check complete.")

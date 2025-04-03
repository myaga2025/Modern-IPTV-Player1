import os
import sys
import shutil
import subprocess

def check_environment():
    """Check that required environment variables and paths are set up correctly"""
    print("Checking environment...")
    
    # Check if Python is in path
    try:
        subprocess.run(["python", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Error: Python not found in PATH or not working correctly.")
        return False
    
    # Check if pip is in path
    try:
        subprocess.run(["pip", "--version"], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("Error: pip not found in PATH or not working correctly.")
        return False
    
    # Check if required directories exist and create them if they don't
    root_dir = os.path.dirname(os.path.abspath(__file__))
    required_dirs = [
        "resources",
        "resources/icons",
        "translations"
    ]
    
    for dir_name in required_dirs:
        dir_path = os.path.join(root_dir, dir_name)
        if not os.path.exists(dir_path):
            print(f"Creating required directory: {dir_path}")
            os.makedirs(dir_path, exist_ok=True)
    
    # Create default translation files if they don't exist
    create_default_translations()
    
    # Check if main.py exists
    if not os.path.exists(os.path.join(root_dir, "main.py")):
        print("Error: main.py not found. Make sure you're running this script from the project root.")
        return False
    
    print("Environment check completed successfully.")
    return True

def create_default_translations():
    """Create default translation files if they don't exist"""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    translations_dir = os.path.join(root_dir, "translations")
    
    # Create Arabic translation file if it doesn't exist
    ar_file = os.path.join(translations_dir, "ar.qm")
    if not os.path.exists(ar_file):
        print(f"Creating empty Arabic translation file: {ar_file}")
        open(ar_file, 'wb').close()
    
    # Create English translation file if it doesn't exist
    en_file = os.path.join(translations_dir, "en.qm")
    if not os.path.exists(en_file):
        print(f"Creating empty English translation file: {en_file}")
        open(en_file, 'wb').close()

def prepare_for_build():
    """Prepare the environment for building the application"""
    if not check_environment():
        return False
    
    # Check and convert icon
    print("Checking app icon...")
    try:
        # Create default icon if needed
        root_dir = os.path.dirname(os.path.abspath(__file__))
        icon_dir = os.path.join(root_dir, "resources", "icons")
        ico_path = os.path.join(icon_dir, "app_icon.ico")
        png_path = os.path.join(icon_dir, "app_icon.png")
        
        if not os.path.exists(png_path):
            # We need to create a default app icon
            print(f"Creating default app icon at {png_path}")
            try:
                from PIL import Image, ImageDraw
                # Create a blue square image
                img = Image.new('RGB', (256, 256), color=(65, 105, 225))
                draw = ImageDraw.Draw(img)
                # Draw TV-like shape
                draw.rectangle((50, 70, 206, 170), fill=(20, 20, 80))
                draw.rectangle((60, 80, 196, 160), fill=(200, 200, 255))
                # Draw stand
                draw.rectangle((110, 170, 146, 200), fill=(40, 40, 100))
                draw.rectangle((80, 200, 176, 210), fill=(40, 40, 100))
                # Save the image
                img.save(png_path)
                print("Default app icon created successfully.")
            except Exception as e:
                print(f"Error creating default icon: {e}")
                # Create an empty file as fallback
                open(png_path, 'wb').close()
        
        if not os.path.exists(ico_path) and os.path.exists(png_path):
            print(f"Converting {png_path} to {ico_path}")
            try:
                from PIL import Image
                img = Image.open(png_path)
                img.save(ico_path, format='ICO')
                print("Icon conversion successful.")
            except Exception as e:
                print(f"Error converting icon: {e}")
    except ImportError:
        print("Warning: PIL not found. Cannot create/convert icons.")
        
    print("Build preparation complete.")
    return True

if __name__ == "__main__":
    result = prepare_for_build()
    sys.exit(0 if result else 1)

#!/usr/bin/env python3
"""
Setup script for IPTV Player application
This script:
1. Creates the required directory structure
2. Downloads basic icons (if requests is installed)
3. Tests VLC availability
"""
import os
import sys
import platform
import subprocess
import importlib.util

def check_module_installed(module_name):
    """Check if a Python module is installed"""
    return importlib.util.find_spec(module_name) is not None

def create_directory_structure():
    """Create the necessary directory structure for the IPTV player"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define directories to create
    directories = [
        "resources/icons",
        "resources/styles",
        "playlists",
    ]
    
    for directory in directories:
        dir_path = os.path.join(base_dir, directory)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"Created directory: {dir_path}")
        else:
            print(f"Directory already exists: {dir_path}")
    
    return base_dir

def download_icons():
    """Download basic icons for the application"""
    if check_module_installed("requests"):
        try:
            print("\nDownloading application icons...")
            # Attempt to run Arabic logo download script
            try:
                from download_arabic_logo import download_icons
                success = download_icons()
                if success:
                    print("✓ All icons downloaded successfully")
                    return True
            except Exception as e:
                print(f"Error with arabic icons: {e}")
            
            # If failed, attempt to create default icons
            try:
                print("\nCreating default icons...")
                import subprocess
                result = subprocess.run([sys.executable, "create_default_icons.py"], 
                                       capture_output=True, text=True)
                if result.returncode == 0:
                    print("✓ Default icons created successfully")
                    return True
                else:
                    print(f"Error creating default icons: {result.stderr}")
            except Exception as e:
                print(f"Error creating default icons: {e}")
            
            # If all attempts fail, fallback to old method
            import requests
            
            icons = {
                "play": "https://raw.githubusercontent.com/feathericons/feather/master/icons/play.svg",
                "pause": "https://raw.githubusercontent.com/feathericons/feather/master/icons/pause.svg",
                "stop": "https://raw.githubusercontent.com/feathericons/feather/master/icons/square.svg",
                "volume": "https://raw.githubusercontent.com/feathericons/feather/master/icons/volume-2.svg",
                "app_icon": "https://raw.githubusercontent.com/feathericons/feather/master/icons/tv.svg",
                "logo": "https://raw.githubusercontent.com/feathericons/feather/master/icons/play-circle.svg",
            }
            
            base_dir = os.path.dirname(os.path.abspath(__file__))
            icons_dir = os.path.join(base_dir, "resources", "icons")
            
            for name, url in icons.items():
                file_path = os.path.join(icons_dir, f"{name}.svg")
                
                if not os.path.exists(file_path):
                    print(f"Downloading {name} icon...")
                    response = requests.get(url)
                    if response.status_code == 200:
                        with open(file_path, "wb") as f:
                            f.write(response.content)
                        print(f"Downloaded {name}.svg")
                    else:
                        print(f"Failed to download {name} icon: HTTP {response.status_code}")
            
            # Create a simple PNG app icon if not present
            app_icon_path = os.path.join(icons_dir, "app_icon.png")
            if not os.path.exists(app_icon_path) and check_module_installed("PIL"):
                try:
                    from PIL import Image, ImageDraw
                    img = Image.new('RGB', (128, 128), color=(30, 30, 30))
                    d = ImageDraw.Draw(img)
                    d.text((20, 50), "IPTV", fill=(255, 255, 255))
                    img.save(app_icon_path)
                    print(f"Created simple app_icon.png")
                except Exception as e:
                    print(f"Could not create app_icon.png: {e}")
            
            print("Icons downloaded to resources/icons directory.")
            print("Note: If icons don't appear, run the create_default_icons.py script.")
            return True
            
        except Exception as e:
            print(f"Error downloading icons: {e}")
            print("App will work without icons. To add icons later, run create_default_icons.py")
    else:
        print("Requests module not installed. Skipping icon download.")
        print("You will need to manually add icons to the resources/icons directory.")
        print("To create default icons, install required modules and run create_default_icons.py")
    
    return False

def create_style_file():
    """Create the stylesheet file if it doesn't exist"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    style_path = os.path.join(base_dir, "resources", "styles", "dark_theme.qss")
    
    if not os.path.exists(style_path):
        print("Creating dark theme stylesheet...")
        with open(style_path, "w", encoding="utf-8") as f:
            f.write("""/* Modern Dark Theme for IPTV Player */

/* Main Application */
QMainWindow, QDialog {
    background-color: #121212;
    color: #f0f0f0;
}

QWidget {
    color: #f0f0f0;
    background-color: #121212;
}

/* Menu and Status Bar */
QMenuBar {
    background-color: #1e1e1e;
    color: #f0f0f0;
}

QMenuBar::item {
    background-color: transparent;
}

QMenuBar::item:selected {
    background-color: #3a3a3a;
}

QMenu {
    background-color: #1e1e1e;
    border: 1px solid #2a2a2a;
}

QMenu::item {
    padding: 5px 20px;
}

QMenu::item:selected {
    background-color: #3a3a3a;
}

QStatusBar {
    background-color: #1e1e1e;
    color: #b0b0b0;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #2a2a2a;
    background-color: #121212;
}

QTabBar::tab {
    background-color: #1e1e1e;
    color: #b0b0b0;
    padding: 8px 15px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #3a3a3a;
    color: #f0f0f0;
}

/* Lists */
QListWidget {
    background-color: #1e1e1e;
    border: 1px solid #2a2a2a;
    border-radius: 4px;
}

QListWidget::item {
    padding: 5px;
    border-radius: 2px;
}

QListWidget::item:selected {
    background-color: #3778b7;
    color: #f0f0f0;
}

QListWidget::item:hover:!selected {
    background-color: #2a2a2a;
}

/* Buttons */
QPushButton {
    background-color: #2a2a2a;
    color: #f0f0f0;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    padding: 6px 12px;
}

QPushButton:hover {
    background-color: #3a3a3a;
}

QPushButton:pressed {
    background-color: #444444;
}

QPushButton:flat {
    border: none;
    background-color: transparent;
}

/* Line Edit */
QLineEdit {
    background-color: #1e1e1e;
    color: #f0f0f0;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    padding: 5px;
}

QLineEdit:focus {
    border: 1px solid #3778b7;
}

/* ComboBox */
QComboBox {
    background-color: #1e1e1e;
    color: #f0f0f0;
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    padding: 5px;
}

QComboBox:hover {
    border: 1px solid #3778b7;
}

QComboBox::drop-down {
    width: 20px;
    border-left: 1px solid #3a3a3a;
}

QComboBox QAbstractItemView {
    border: 1px solid #3a3a3a;
    background-color: #1e1e1e;
    selection-background-color: #3778b7;
}

/* Sliders */
QSlider::groove:horizontal {
    height: 8px;
    background: #2a2a2a;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: #3778b7;
    width: 16px;
    margin: -4px 0;
    border-radius: 8px;
}

QSlider::sub-page:horizontal {
    background: #3778b7;
    border-radius: 4px;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #1e1e1e;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #3a3a3a;
    min-height: 30px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #4a4a4a;
}

QScrollBar:horizontal {
    border: none;
    background: #1e1e1e;
    height: 10px;
    margin: 0px;
}

QScrollBar::handle:horizontal {
    background: #3a3a3a;
    min-width: 30px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal:hover {
    background: #4a4a4a;
}

QScrollBar::add-line, QScrollBar::sub-line {
    border: none;
    background: none;
}

QScrollBar::add-page, QScrollBar::sub-page {
    background: none;
}

/* Labels */
QLabel {
    color: #f0f0f0;
}

/* Frame */
QFrame {
    border-radius: 4px;
}
""")
        print("Created dark theme stylesheet.")
    else:
        print("Style file already exists.")

def check_dependencies():
    """Check if all required Python packages are installed"""
    required_modules = ["PyQt6", "requests"]
    optional_modules = ["python-vlc"]
    
    print("\nChecking dependencies...")
    
    all_required_installed = True
    for module in required_modules:
        if check_module_installed(module):
            print(f"✓ {module} is installed")
        else:
            print(f"✗ {module} is NOT installed")
            all_required_installed = False
    
    for module in optional_modules:
        if check_module_installed("vlc"):
            print(f"✓ {module} is installed")
        else:
            print(f"! {module} is NOT installed (required for video playback)")
    
    if not all_required_installed:
        print("\nSome required packages are missing. Install them using:")
        print("pip install -r requirements.txt")

def check_vlc_installation():
    """Check if VLC is installed on the system"""
    print("\nChecking for VLC installation...")
    
    system = platform.system()
    vlc_found = False
    
    if system == "Windows":
        paths = [
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'VideoLAN', 'VLC'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', ''), 'VideoLAN', 'VLC'),
            r"C:\Program Files\VideoLAN\VLC",
            r"C:\Program Files (x86)\VideoLAN\VLC",
        ]
        
        for path in paths:
            if os.path.exists(path):
                print(f"✓ VLC found at: {path}")
                vlc_found = True
                break
    
    elif system == "Darwin":  # macOS
        paths = [
            '/Applications/VLC.app/Contents/MacOS/',
            '/Applications/VLC.app/Contents/MacOS/lib',
        ]
        
        for path in paths:
            if os.path.exists(path):
                print(f"✓ VLC found at: {path}")
                vlc_found = True
                break
    
    else:  # Linux
        try:
            result = subprocess.run(['which', 'vlc'], capture_output=True, text=True, check=False)
            if result.returncode == 0:
                print(f"✓ VLC found at: {result.stdout.strip()}")
                vlc_found = True
        except Exception:
            pass
    
    if not vlc_found:
        print("✗ VLC not found in standard locations")
        print("  Please install VLC from: https://www.videolan.org/vlc/")
        print("  Video playback will not work without VLC")

def main():
    """Main setup function"""
    print("=" * 60)
    print("IPTV Player Setup")
    print("=" * 60)
    
    # Create directory structure
    base_dir = create_directory_structure()
    
    # Create style file
    create_style_file()
    
    # Download icons if possible
    download_icons()
    
    # Check dependencies
    check_dependencies()
    
    # Check VLC installation
    check_vlc_installation()
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("You can now run the application using: python main.py")
    print("=" * 60)

if __name__ == "__main__":
    main()

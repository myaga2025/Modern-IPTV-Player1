import os
import sys
import shutil
import subprocess
import PyInstaller.__main__

def ensure_directories_exist():
    """Ensure that all required directories exist"""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    required_dirs = [
        os.path.join(root_dir, "resources"),
        os.path.join(root_dir, "resources", "icons"),
        os.path.join(root_dir, "translations")
    ]
    
    for directory in required_dirs:
        if not os.path.exists(directory):
            print(f"Creating required directory: {directory}")
            os.makedirs(directory, exist_ok=True)

def build_executable():
    """Build the executable using PyInstaller"""
    print("Building Modern IPTV Player executable...")
    
    # Ensure required directories exist
    ensure_directories_exist()
    
    # Define paths
    root_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(root_dir, 'dist')
    build_dir = os.path.join(root_dir, 'build')
    
    # Clean previous build files if exist
    if os.path.exists(dist_dir):
        print("Cleaning previous distribution files...")
        shutil.rmtree(dist_dir)
    if os.path.exists(build_dir):
        print("Cleaning previous build files...")
        shutil.rmtree(build_dir)
    
    # Resources to include (use relative paths)
    resources_path = os.path.join('.', 'resources')
    translations_path = os.path.join('.', 'translations')
    
    # Define PyInstaller command arguments
    args = [
        'main.py',  # Entry point script
        '--name=Modern_IPTV_Player',
        '--windowed',  # No console window
        '--onedir',  # Create a directory with executables
        '--clean',
        '--noconfirm',
    ]
    
    # Add icon if it exists
    icon_path = os.path.join(resources_path, 'icons', 'app_icon.ico')
    if os.path.exists(os.path.join(root_dir, icon_path)):
        args.append(f'--icon={icon_path}')
    
    # Add data files with correct path separators based on OS
    separator = ';' if sys.platform.startswith('win') else ':'
    args.append(f'--add-data={resources_path}{separator}resources')
    args.append(f'--add-data={translations_path}{separator}translations')
    
    # Add hidden imports
    args.extend([
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=PyQt6.QtGui',
        '--hidden-import=python-vlc',
        '--hidden-import=chardet',
    ])
    
    # Run PyInstaller
    PyInstaller.__main__.run(args)
    
    print("\nBuild completed!")
    print(f"Executable created at: {os.path.join(dist_dir, 'Modern_IPTV_Player', 'Modern_IPTV_Player.exe')}")

if __name__ == "__main__":
    build_executable()

#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from pathlib import Path
import argparse
import datetime

def build_deb_package(version="1.0.0"):
    """Build a Debian package for the Modern IPTV Player application"""
    print(f"Building Modern IPTV Player DEB package v{version}...")
    
    # Define paths
    root_dir = os.path.dirname(os.path.abspath(__file__))
    deb_build_dir = os.path.join(root_dir, 'deb_build')
    dist_dir = os.path.join(root_dir, 'dist')
    
    # Clean previous build files if exist
    if os.path.exists(deb_build_dir):
        print("Cleaning previous DEB build files...")
        shutil.rmtree(deb_build_dir)
    
    # Create package directory structure
    package_name = "modern-iptv-player"
    package_dir = os.path.join(deb_build_dir, package_name)
    
    # Create directories
    dirs = [
        os.path.join(package_dir, "DEBIAN"),
        os.path.join(package_dir, "usr", "bin"),
        os.path.join(package_dir, "usr", "share", package_name),
        os.path.join(package_dir, "usr", "share", "applications"),
        os.path.join(package_dir, "usr", "share", "icons", "hicolor", "128x128", "apps"),
        os.path.join(package_dir, "usr", "share", "doc", package_name),
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    
    # Copy application files
    app_files = [
        ("main.py", os.path.join(package_dir, "usr", "share", package_name, "main.py")),
    ]
    
    # Copy Python source files
    for root, dirs, files in os.walk(root_dir):
        # Skip build directories and hidden folders
        if any(x in root for x in ['.git', '__pycache__', 'deb_build', 'dist', 'build']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                src_file = os.path.join(root, file)
                # Get relative path from project root
                rel_path = os.path.relpath(os.path.join(root, file), root_dir)
                dest_file = os.path.join(package_dir, "usr", "share", package_name, rel_path)
                
                # Create destination directory if it doesn't exist
                os.makedirs(os.path.dirname(dest_file), exist_ok=True)
                
                # Copy file
                shutil.copy2(src_file, dest_file)
                print(f"Copied: {rel_path}")
    
    # Copy resources
    resources_dir = os.path.join(root_dir, "resources")
    if os.path.exists(resources_dir):
        dest_resources = os.path.join(package_dir, "usr", "share", package_name, "resources")
        shutil.copytree(resources_dir, dest_resources)
        print("Copied: resources/")
    
    # Copy translations
    translations_dir = os.path.join(root_dir, "translations")
    if os.path.exists(translations_dir):
        dest_translations = os.path.join(package_dir, "usr", "share", package_name, "translations")
        shutil.copytree(translations_dir, dest_translations)
        print("Copied: translations/")
    
    # Copy icon to icons directory
    icon_path = os.path.join(root_dir, "resources", "icons", "app_icon.png")
    if os.path.exists(icon_path):
        icon_dest = os.path.join(package_dir, "usr", "share", "icons", "hicolor", "128x128", "apps", f"{package_name}.png")
        shutil.copy2(icon_path, icon_dest)
        print("Copied: app icon to icons directory")
    
    # Copy README
    readme_path = os.path.join(root_dir, "README.md")
    if os.path.exists(readme_path):
        readme_dest = os.path.join(package_dir, "usr", "share", "doc", package_name, "README.md")
        shutil.copy2(readme_path, readme_dest)
        print("Copied: README.md")
    
    # Create the launcher script
    launcher_path = os.path.join(package_dir, "usr", "bin", package_name)
    with open(launcher_path, 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('cd /usr/share/modern-iptv-player\n')
        f.write('python3 main.py "$@"\n')
    os.chmod(launcher_path, 0o755)
    print("Created: launcher script")
    
    # Create desktop entry
    desktop_entry_path = os.path.join(package_dir, "usr", "share", "applications", f"{package_name}.desktop")
    with open(desktop_entry_path, 'w') as f:
        f.write('[Desktop Entry]\n')
        f.write(f'Name=Modern IPTV Player\n')
        f.write(f'Comment=Play IPTV channels from M3U playlists\n')
        f.write(f'Exec={package_name}\n')
        f.write(f'Icon={package_name}\n')
        f.write('Terminal=false\n')
        f.write('Type=Application\n')
        f.write('Categories=AudioVideo;Video;TV;\n')
        f.write('Keywords=iptv;streaming;tv;player;\n')
    print("Created: desktop entry file")
    
    # Create control file
    control_file_path = os.path.join(package_dir, "DEBIAN", "control")
    with open(control_file_path, 'w') as f:
        f.write(f'Package: {package_name}\n')
        f.write(f'Version: {version}\n')
        f.write('Section: video\n')
        f.write('Priority: optional\n')
        f.write('Architecture: all\n')  # Using 'all' for Python packages
        f.write('Maintainer: IPTV Player Development Team <admin@aljup.com>\n')
        f.write('Depends: python3 (>= 3.8), python3-pip, python3-pyqt6, vlc (>= 3.0.0)\n')
        f.write('Homepage: https://www.aljup.com\n')
        f.write('Description: Modern IPTV Player\n')
        f.write(' A modern IPTV player supporting M3U playlists with an elegant graphical interface.\n')
        f.write(' .\n')  # Empty line before bullet points in Debian control files
        f.write(' * Support for local and remote M3U playlists\n')
        f.write(' * Search and categorization by groups\n')
        f.write(' * Create and manage custom playlists\n')
        f.write(' * Modern and user-friendly interface\n')
        f.write(' * Support for Arabic and English languages\n')
    print("Created: control file")
    
    # Create postinst script (runs after installation)
    postinst_path = os.path.join(package_dir, "DEBIAN", "postinst")
    with open(postinst_path, 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('set -e\n\n')
        f.write('# Install required Python packages\n')
        f.write('pip3 install PyQt6 requests chardet python-vlc pillow\n\n')
        f.write('# Update desktop database\n')
        f.write('if [ -x "$(command -v update-desktop-database)" ]; then\n')
        f.write('    update-desktop-database\n')
        f.write('fi\n')
    os.chmod(postinst_path, 0o755)
    print("Created: postinst script")
    
    # Create prerm script (runs before removal)
    prerm_path = os.path.join(package_dir, "DEBIAN", "prerm")
    with open(prerm_path, 'w') as f:
        f.write('#!/bin/bash\n')
        f.write('set -e\n\n')
        f.write('# Cleanup actions before removal can be added here\n')
    os.chmod(prerm_path, 0o755)
    print("Created: prerm script")
    
    # Build the package
    os.makedirs(dist_dir, exist_ok=True)
    deb_file = os.path.join(dist_dir, f"{package_name}_{version}_all.deb")
    
    try:
        print("\nBuilding DEB package...")
        subprocess.run(['dpkg-deb', '--build', package_dir, deb_file], check=True)
        print(f"\nDEB package created successfully at: {deb_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error building DEB package: {e}")
        print("Make sure you have dpkg-deb installed (sudo apt-get install dpkg)")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Build DEB package for Modern IPTV Player')
    parser.add_argument('--version', default="1.0.0", help='Package version (default: 1.0.0)')
    args = parser.parse_args()
    
    success = build_deb_package(args.version)
    sys.exit(0 if success else 1)

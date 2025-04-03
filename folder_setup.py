#!/usr/bin/env python3
"""
Set up folder structure for IPTV Player application
"""
import os
import sys

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
    
    # Check if icons exist, create placeholder if not
    icons_placeholder_path = os.path.join(base_dir, "resources/icons/place_icons_here.txt")
    if not os.path.exists(icons_placeholder_path):
        with open(icons_placeholder_path, "w", encoding="utf-8") as f:
            f.write("""Place the following icons here:
- play.png
- pause.png
- stop.png
- volume.png

You can download free icons from sources like:
- Material Design Icons (https://materialdesignicons.com/)
- Feather Icons (https://feathericons.com/)
- Font Awesome (https://fontawesome.com/)
""")
    
    # Create an empty dark_theme.qss if it doesn't exist
    styles_path = os.path.join(base_dir, "resources/styles/dark_theme.qss")
    if not os.path.exists(styles_path):
        print("Creating empty dark_theme.qss file...")
        with open(styles_path, "w", encoding="utf-8") as f:
            f.write("/* Modern Dark Theme for IPTV Player */\n")

if __name__ == "__main__":
    print("Setting up directory structure for IPTV Player...")
    create_directory_structure()
    print("Done!")

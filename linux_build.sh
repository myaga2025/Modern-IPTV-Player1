#!/bin/bash

# Script to build DEB package for Modern IPTV Player
echo "Building Modern IPTV Player for Linux..."

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 is not installed. Please install it first."
    exit 1
fi

# Check if required packages are installed
if ! command -v dpkg-deb &> /dev/null; then
    echo "Warning: dpkg-deb not found. Installing it now..."
    sudo apt-get update && sudo apt-get install -y dpkg
fi

# Install required Python packages
echo "Installing required Python packages..."
pip3 install PyQt6 requests chardet python-vlc pillow

# Create directories and resources
echo "Preparing directory structure..."
python3 create_structure.py

# Build DEB package
echo "Building DEB package..."
VERSION="1.0.0"

# Get version from arguments if provided
if [ "$1" != "" ]; then
    VERSION="$1"
fi

python3 build_deb.py --version "$VERSION"

echo "Build process complete."
echo "You can find the DEB package in the dist directory."
echo "To install on a Debian-based system: sudo dpkg -i dist/modern-iptv-player_${VERSION}_all.deb"

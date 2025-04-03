#!/bin/bash

# Script to install dependencies for Modern IPTV Player on Linux
echo "Installing dependencies for Modern IPTV Player..."

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo "Cannot detect Linux distribution. Please install dependencies manually."
    exit 1
fi

# Install common dependencies based on distribution
case $DISTRO in
    ubuntu|debian|linuxmint|pop)
        echo "Detected Debian-based distribution: $DISTRO"
        sudo apt update
        sudo apt install -y python3 python3-pip python3-pyqt6 vlc python3-dev build-essential
        ;;
    fedora)
        echo "Detected Fedora"
        sudo dnf install -y python3 python3-pip python3-qt6 vlc python3-devel gcc
        ;;
    arch|manjaro)
        echo "Detected Arch-based distribution: $DISTRO"
        sudo pacman -Syu --noconfirm python python-pip python-pyqt6 vlc
        ;;
    *)
        echo "Unsupported distribution: $DISTRO"
        echo "Please install the following packages manually:"
        echo "- Python 3.8 or newer"
        echo "- pip for Python 3"
        echo "- PyQt6"
        echo "- VLC media player"
        exit 1
        ;;
esac

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --user PyQt6 requests chardet python-vlc pillow

echo "Dependencies installed successfully."
echo "You can now run the application with: python3 main.py"

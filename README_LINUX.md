# Modern IPTV Player - Linux Installation Guide

This document provides guidance on installing and using Modern IPTV Player on Linux systems.

## Table of Contents
- [Installation Methods](#installation-methods)
  - [Using DEB Package (Debian/Ubuntu/Mint)](#using-deb-package-debianubuntumint)
  - [Manual Installation](#manual-installation)
- [Building from Source](#building-from-source)
  - [Building a DEB Package](#building-a-deb-package)
- [Troubleshooting](#troubleshooting)

## Installation Methods

### Using DEB Package (Debian/Ubuntu/Mint)

The easiest way to install on Debian-based distributions:

1. Download the latest DEB package from the releases page
2. Install the package:
   ```
   sudo dpkg -i modern-iptv-player_1.0.0_all.deb
   sudo apt-get install -f  # To resolve any dependencies
   ```
3. Launch the application from your applications menu or run:
   ```
   modern-iptv-player
   ```

### Manual Installation

For other Linux distributions:

1. Install the required dependencies:
   ```
   # On Debian/Ubuntu:
   sudo apt install python3 python3-pip python3-pyqt6 vlc

   # On Fedora:
   sudo dnf install python3 python3-pip python3-qt6 vlc

   # On Arch:
   sudo pacman -S python python-pip python-pyqt6 vlc
   ```

2. Clone the repository or download the source code:
   ```
   git clone https://github.com/your-username/modern-iptv-player.git
   cd modern-iptv-player
   ```

3. Install Python dependencies:
   ```
   pip3 install --user -r requirements.txt
   ```

4. Run the application:
   ```
   python3 main.py
   ```

## Building from Source

### Building a DEB Package

To build a DEB package for Debian-based distributions:

1. Make sure you have the required build dependencies:
   ```
   sudo apt install python3 python3-pip dpkg build-essential
   ```

2. Run the build script:
   ```
   ./linux_build.sh
   ```
   
   Or with a specific version:
   ```
   ./linux_build.sh 1.1.0
   ```

3. The DEB package will be created in the `dist` directory

## Troubleshooting

### VLC Issues

If you encounter issues with VLC:

1. Make sure the correct version of VLC is installed:
   ```
   vlc --version
   ```

2. Try setting the VLC path manually:
   ```
   python3 force_vlc_path.py
   ```

### Audio/Video Issues

If channels don't play or you experience audio/video issues:

1. Install additional codecs:
   ```
   # On Debian/Ubuntu:
   sudo apt install vlc-plugin-access-extra vlc-plugin-video-output
   ```

2. Check your firewall settings to ensure the application can access the internet

### Application Crashes

If the application crashes:

1. Try running from the terminal to see error messages:
   ```
   modern-iptv-player
   ```

2. Check if all dependencies are properly installed:
   ```
   pip3 list | grep -E 'PyQt6|requests|chardet|python-vlc'
   ```

3. Update all packages:
   ```
   pip3 install --user --upgrade PyQt6 requests chardet python-vlc
   ```

For further assistance, please file an issue on our GitHub repository.

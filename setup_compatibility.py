#!/usr/bin/env python3
"""
Compatibility check script for IPTV Player
This script verifies the system configuration and provides guidance on compatibility issues
"""
import os
import sys
import platform
import ctypes
import struct

def get_python_arch():
    """Get Python architecture"""
    return "64-bit" if sys.maxsize > 2**32 else "32-bit"

def get_os_arch():
    """Get OS architecture"""
    if platform.system() == "Windows":
        if 'PROGRAMFILES(X86)' in os.environ:
            return "64-bit"
        else:
            return "32-bit"
    elif platform.system() == "Linux":
        return platform.architecture()[0]
    elif platform.system() == "Darwin":
        return "64-bit"  # macOS has been 64-bit for a while
    else:
        return "Unknown"

def check_dll_arch(file_path):
    """Check if a DLL is 32-bit or 64-bit"""
    try:
        with open(file_path, 'rb') as f:
            # Read DOS header
            dos_header = f.read(64)
            if len(dos_header) != 64 or dos_header[0:2] != b'MZ':
                return "Invalid PE file"
            
            # Get PE header offset
            pe_offset = struct.unpack('<I', dos_header[60:64])[0]
            f.seek(pe_offset)
            
            # Read PE signature
            pe_sig = f.read(4)
            if pe_sig != b'PE\x00\x00':
                return "Invalid PE signature"
            
            # Read machine type (offset 4 from PE signature)
            f.seek(pe_offset + 4)
            machine_type = struct.unpack('<H', f.read(2))[0]
            
            if machine_type == 0x8664:  # AMD64
                return "64-bit"
            elif machine_type == 0x014c:  # i386
                return "32-bit"
            else:
                return f"Unknown machine type: 0x{machine_type:04x}"
    except Exception as e:
        return f"Error: {e}"

def check_vlc_installations():
    """Check all VLC installations"""
    results = []
    
    # Check common VLC install locations
    vlc_paths = [
        r"C:\Program Files\VideoLAN\VLC",
        r"C:\Program Files (x86)\VideoLAN\VLC",
    ]
    
    for path in vlc_paths:
        if os.path.exists(path):
            libvlc_path = os.path.join(path, "libvlc.dll")
            if os.path.exists(libvlc_path):
                arch = check_dll_arch(libvlc_path)
                results.append((path, arch))
    
    return results

def main():
    """Main function"""
    print("=" * 60)
    print("IPTV Player Compatibility Check")
    print("=" * 60)
    
    # System information
    print("\nSystem Information:")
    print(f"Operating System: {platform.system()} {platform.release()}")
    print(f"OS Architecture: {get_os_arch()}")
    print(f"Python Version: {platform.python_version()}")
    print(f"Python Architecture: {get_python_arch()}")
    
    # VLC installations
    print("\nVLC Installations:")
    vlc_installs = check_vlc_installations()
    
    if not vlc_installs:
        print("No VLC installations found.")
        print("Please download and install VLC from: https://www.videolan.org/vlc/")
    else:
        for path, arch in vlc_installs:
            print(f"- {path}: {arch}")
    
    # Compatibility assessment
    print("\nCompatibility Assessment:")
    python_arch = get_python_arch()
    
    # Check if we have a matching VLC architecture
    matching_vlc = False
    for path, arch in vlc_installs:
        if arch == python_arch:
            matching_vlc = True
            print(f"✓ Found matching VLC installation: {path} ({arch})")
    
    if not matching_vlc and vlc_installs:
        print(f"✗ No VLC installation matching Python's architecture ({python_arch}) found.")
        print(f"  This will likely cause compatibility issues.")
        print(f"  Please install the {python_arch} version of VLC.")
    
    print("\nRecommendation:")
    if python_arch == "64-bit":
        print("- Use 64-bit VLC installed in: C:\\Program Files\\VideoLAN\\VLC")
    else:
        print("- Use 32-bit VLC installed in: C:\\Program Files (x86)\\VideoLAN\\VLC")
    print("\nTo force a specific VLC path, run: python force_vlc_path.py")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")

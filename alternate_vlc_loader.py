#!/usr/bin/env python3
"""
Alternative VLC loader for cases where the standard approach fails.
This script:
1. Attempts to find VLC installation
2. Explicitly loads libvlc.dll using ctypes
3. Creates a wrapper module for python-vlc
"""
import os
import sys
import platform
import ctypes
from ctypes.util import find_library

def get_architecture():
    """Get system architecture (32 or 64 bit)"""
    return "64bit" if sys.maxsize > 2**32 else "32bit"

def find_vlc():
    """Find VLC installation directory"""
    system = platform.system()
    arch = get_architecture()
    print(f"System: {system}, Architecture: {arch}")
    
    if system == "Windows":
        # Use C:\Program Files (x86)\VideoLAN\VLC directly
        vlc_dir = r"C:\Program Files (x86)\VideoLAN\VLC"
        libvlc_path = os.path.join(vlc_dir, 'libvlc.dll')
        
        if os.path.exists(libvlc_path):
            return vlc_dir, libvlc_path
        
        # Fallbacks in case the direct path doesn't work
        program_files = os.environ.get('PROGRAMFILES', 'C:\\Program Files')
        program_files_x86 = os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')
        
        vlc_dirs = [
            os.path.join(program_files_x86, 'VideoLAN', 'VLC'),
            os.path.join(program_files, 'VideoLAN', 'VLC')
        ]
        
        for directory in vlc_dirs:
            if not os.path.isdir(directory):
                continue
                
            libvlc_path = os.path.join(directory, 'libvlc.dll')
            if os.path.exists(libvlc_path):
                return directory, libvlc_path
    elif system == "Darwin":  # macOS
        vlc_dirs = [
            '/Applications/VLC.app/Contents/MacOS/',
            '/Applications/VLC.app/Contents/MacOS/lib',
            os.path.expanduser('~/Applications/VLC.app/Contents/MacOS/')
        ]
        for directory in vlc_dirs:
            if not os.path.isdir(directory):
                continue
                
            libvlc_path = os.path.join(directory, 'lib', 'libvlc.dylib')
            if not os.path.exists(libvlc_path):
                libvlc_path = os.path.join(directory, 'libvlc.dylib')
            if os.path.exists(libvlc_path):
                return directory, libvlc_path
    elif system == "Linux":
        # On Linux, VLC libraries are typically in the library path
        lib_path = find_library("vlc")
        if lib_path:
            vlc_dirs = [os.path.dirname(lib_path)]
        else:
            vlc_dirs = [
                '/usr/lib',
                '/usr/local/lib',
                '/usr/lib/x86_64-linux-gnu'
            ]
        for directory in vlc_dirs:
            if not os.path.isdir(directory):
                continue
                
            libvlc_path = os.path.join(directory, 'libvlc.so')
            if os.path.exists(libvlc_path):
                return directory, libvlc_path
    
    return None, None

def load_vlc_library():
    """Load VLC library directly"""
    vlc_dir, libvlc_path = find_vlc()
    
    if not libvlc_path:
        print("Could not find VLC library.")
        return None
    
    print(f"Found VLC at: {vlc_dir}")
    print(f"Library path: {libvlc_path}")
    
    # Add VLC directory to PATH
    os.environ['PATH'] = vlc_dir + os.pathsep + os.environ.get('PATH', '')
    
    # Add to Python path
    if vlc_dir not in sys.path:
        sys.path.append(vlc_dir)
    
    try:
        # Try to load the library
        libvlc = ctypes.CDLL(libvlc_path)
        print("Successfully loaded VLC library!")
        return libvlc
    except Exception as e:
        print(f"Failed to load VLC library: {e}")
        return None

def create_vlc_path_file():
    """Create a file with VLC path for future use"""
    vlc_dir, _ = find_vlc()
    
    if vlc_dir:
        try:
            with open("vlc_path.txt", "w") as f:
                f.write(vlc_dir)
            print(f"Saved VLC path to vlc_path.txt: {vlc_dir}")
        except Exception as e:
            print(f"Error saving VLC path: {e}")

def main():
    """Main function"""
    print("=" * 60)
    print("Alternative VLC Loader")
    print("=" * 60)
    
    # Try to load VLC directly
    libvlc = load_vlc_library()
    
    if libvlc:
        # Create path file for future use
        create_vlc_path_file()
        print("\nVLC loaded successfully! The application should now work properly.")
    else:
        print("\nFailed to load VLC. Please make sure VLC is installed correctly.")
        print("You may need to:")
        print("1. Install VLC from https://www.videolan.org/vlc/")
        print("2. Make sure the VLC architecture (32/64-bit) matches your Python installation")
        print(f"   Your Python is: {get_architecture()}")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()

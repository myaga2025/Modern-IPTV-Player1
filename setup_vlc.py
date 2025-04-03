#!/usr/bin/env python3
"""
أداة تكوين VLC لتطبيق مشغل IPTV
تساعد هذه الأداة في تشخيص وإصلاح مشاكل تكوين VLC
"""
import os
import sys
import platform
import ctypes
import subprocess
from pathlib import Path

def is_admin():
    """Check if script is running with admin privileges"""
    try:
        return os.name == 'nt' and ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_python_arch():
    """Returns the Python architecture (32bit or 64bit)"""
    return "64bit" if sys.maxsize > 2**32 else "32bit"

def get_file_arch(file_path):
    """Try to determine if a Windows DLL is 32-bit or 64-bit"""
    if not os.path.exists(file_path):
        return "Unknown"
        
    try:
        with open(file_path, 'rb') as f:
            # Read DOS header
            dos_header = f.read(64)
            if len(dos_header) != 64 or dos_header[0:2] != b'MZ':
                return "Unknown"
            
            # Get PE header offset
            pe_offset = int.from_bytes(dos_header[60:64], byteorder='little')
            f.seek(pe_offset)
            
            # Read PE signature
            pe_sig = f.read(4)
            if pe_sig != b'PE\x00\x00':
                return "Unknown"
            
            # Read machine type
            machine_type = f.read(2)
            machine_type_value = int.from_bytes(machine_type, byteorder='little')
            
            if machine_type_value == 0x8664:  # AMD64
                return "64bit"
            elif machine_type_value == 0x014c:  # i386
                return "32bit"
            else:
                return "Unknown"
    except Exception as e:
        print(f"Error checking file architecture: {e}")
        return "Unknown"

def find_vlc_paths():
    """البحث عن جميع مسارات تثبيت VLC الممكنة"""
    system = platform.system()
    python_arch = get_python_arch()
    possible_paths = []
    found_paths = []
    
    print(f"بنية Python: {python_arch}")
    
    if system == "Windows":
        # استخدام إصدار 64 بت أولاً دائماً
        possible_paths = [
            os.path.join(os.environ.get('PROGRAMFILES', ''), 'VideoLAN', 'VLC'),
            r"C:\Program Files\VideoLAN\VLC",
            # مسار 32 بت كخيار ثانوي
            r"C:\Program Files (x86)\VideoLAN\VLC",
        ]
    elif system == "Darwin":  # macOS
        possible_paths = [
            '/Applications/VLC.app/Contents/MacOS/',
            '/Applications/VLC.app/Contents/MacOS/lib',
            os.path.expanduser('~/Applications/VLC.app/Contents/MacOS/'),
        ]
    else:  # Linux
        possible_paths = [
            '/usr/bin',
            '/usr/local/bin',
            '/usr/lib',
            '/usr/local/lib',
        ]
    
    for path in possible_paths:
        if os.path.exists(path):
            if system == "Windows":
                libvlc_path = os.path.join(path, "libvlc.dll")
                if os.path.exists(libvlc_path):
                    vlc_arch = get_file_arch(libvlc_path)
                    found_paths.append((path, vlc_arch))
                    # إعطاء الأولوية للإصدار 64 بت
                    if vlc_arch == "64bit":
                        # وضع المسارات ذات البنية 64 بت في بداية القائمة
                        found_paths.insert(0, found_paths.pop(-1))
            elif system == "Darwin":
                if os.path.exists(os.path.join(path, "lib", "libvlc.dylib")) or \
                   os.path.exists(os.path.join(path, "libvlc.dylib")):
                    found_paths.append((path, "Unknown"))
            else:  # Linux
                if os.path.exists(os.path.join(path, "libvlc.so")) or \
                   os.path.exists("/usr/lib/libvlc.so") or \
                   os.path.exists("/usr/local/lib/libvlc.so"):
                    found_paths.append((path, "Unknown"))
    
    return found_paths

def set_environment_variables(vlc_path):
    """Set environment variables for VLC"""
    system = platform.system()
    
    # Clear problematic environment variables
    if 'PYTHON_VLC_MODULE_PATH' in os.environ:
        del os.environ['PYTHON_VLC_MODULE_PATH']
    if 'PYTHON_VLC_LIB_PATH' in os.environ:
        del os.environ['PYTHON_VLC_LIB_PATH']
    
    if system == "Windows":
        os.environ['PATH'] = vlc_path + os.pathsep + os.environ.get('PATH', '')
    elif system == "Darwin":
        os.environ['PATH'] = vlc_path + os.pathsep + os.environ.get('PATH', '')
        os.environ['DYLD_LIBRARY_PATH'] = vlc_path + os.pathsep + os.environ.get('DYLD_LIBRARY_PATH', '')
    
    # Add to Python path
    if vlc_path not in sys.path:
        sys.path.append(vlc_path)
    
    print(f"Environment variables set for VLC path: {vlc_path}")

def check_vlc_python_module():
    """Check if python-vlc module is installed"""
    try:
        import vlc
        print("✓ python-vlc module is installed")
        print(f"  Module location: {vlc.__file__}")
        return True
    except ImportError:
        print("✗ python-vlc module is NOT installed")
        print("  To install: pip install python-vlc")
        return False
    except Exception as e:
        print(f"✗ Error importing vlc module: {e}")
        return False

def test_vlc_import(vlc_path=None):
    """Test VLC import with specific path"""
    if vlc_path:
        set_environment_variables(vlc_path)
    
    try:
        import vlc
        print("✓ Successfully imported VLC module")
        
        # Try to create a VLC instance
        try:
            instance = vlc.Instance('--no-xlib')
            player = instance.media_player_new()
            print("✓ Successfully created VLC instance and player")
            return True
        except Exception as e:
            print(f"✗ Error creating VLC instance: {e}")
            return False
    except ImportError:
        print("✗ Failed to import VLC module")
        return False
    except Exception as e:
        print(f"✗ Error during VLC import: {e}")
        return False

def create_path_file(vlc_path):
    """Create a file with VLC path for the application to use"""
    try:
        with open("vlc_path.txt", "w") as f:
            f.write(vlc_path)
        print(f"VLC path saved to vlc_path.txt: {vlc_path}")
    except Exception as e:
        print(f"Error saving VLC path: {e}")

def main():
    """Main function"""
    print("=" * 60)
    print("VLC Setup and Diagnosis Tool for IPTV Player")
    print("=" * 60)
    
    # Check for python-vlc module
    print("\nChecking for python-vlc module...")
    check_vlc_python_module()
    
    # Try hardcoded path first if on Windows
    if platform.system() == "Windows":
        hardcoded_path = r"C:\Program Files (x86)\VideoLAN\VLC"
        if os.path.exists(hardcoded_path):
            print(f"\nTrying hardcoded VLC path: {hardcoded_path}")
            if test_vlc_import(hardcoded_path):
                print("✓ Hardcoded VLC path works!")
                create_path_file(hardcoded_path)
                print("\nSetup complete! VLC is properly configured.")
                print("You can now run the IPTV Player application.")
                return
    
    # Find VLC paths
    print("\nSearching for VLC installation...")
    found_paths = find_vlc_paths()
    
    if not found_paths:
        print("✗ No VLC installation found in standard locations")
        print("\nPlease install VLC from https://www.videolan.org/vlc/")
        python_arch = get_python_arch()
        print(f"Make sure to download the {python_arch} version to match your Python architecture.")
        print("After installation, run this script again.")
        return
    
    print(f"Found {len(found_paths)} potential VLC installation(s):")
    compatible_paths = []
    for i, (path, arch) in enumerate(found_paths):
        print(f"{i+1}. {path} [Architecture: {arch}]")
        if arch == get_python_arch() or arch == "Unknown":
            compatible_paths.append(path)
    
    # Check for architecture mismatch
    python_arch = get_python_arch()
    if not compatible_paths:
        print(f"\n⚠️ Architecture mismatch detected: Your Python is {python_arch}!")
        print(f"You need to install the {python_arch} version of VLC.")
        print("The application may not work until you install the correct VLC version.")
    
    # Try compatible paths first, then all paths
    paths_to_try = compatible_paths if compatible_paths else [path for path, _ in found_paths]
    
    # Try each path
    print("\nTesting VLC paths...")
    for i, path in enumerate(paths_to_try):
        print(f"\nTrying VLC path: {path}")
        if test_vlc_import(path):
            print("✓ This VLC path works!")
            create_path_file(path)
            
            print("\nSetup complete! VLC is properly configured.")
            print("You can now run the IPTV Player application.")
            return
    
    print("\n✗ None of the found VLC paths worked correctly")
    print("This could be due to one of the following issues:")
    print("1. VLC installation is incomplete or corrupted")
    print("2. Required DLLs/shared libraries are missing")
    print("3. Python architecture (32/64-bit) doesn't match VLC architecture")
    print(f"\nYour Python is {python_arch}. You need the {python_arch} version of VLC.")
    print("\nTry reinstalling VLC and make sure to:")
    print(f"- Download the {python_arch} version of VLC to match your Python")
    print("- Install VLC in the default location")
    print("- Restart your computer after installation")

if __name__ == "__main__":
    # Check for admin privileges on Windows
    if platform.system() == "Windows" and not is_admin():
        print("Note: For best results, run this script as administrator")
        print("Some diagnostics might be limited without admin privileges\n")
    
    main()

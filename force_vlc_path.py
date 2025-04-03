#!/usr/bin/env python3
"""
أداة تكوين مسار VLC لمشغل IPTV
هذه الأداة تقوم بإنشاء ملف لتعيين مسار تثبيت VLC للتطبيق
"""
import os
import sys
import ctypes
import platform

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

def main():
    """الوظيفة الرئيسية"""
    print("=" * 60)
    print("أداة تكوين مسار VLC")
    print("=" * 60)
    
    python_arch = get_python_arch()
    print(f"بنية Python: {python_arch}")
    
    # تحديد المسارات الموصى بها بناءً على بنية Python
    # نعطي الأولوية دائماً لإصدار 64 بت
    recommended_paths = [
        os.path.join(os.environ.get('PROGRAMFILES', ''), 'VideoLAN', 'VLC'),
        r"C:\Program Files\VideoLAN\VLC"
    ]
    fallback_path = r"C:\Program Files (x86)\VideoLAN\VLC"
    
    # Check for existing VLC installations
    found_paths = []
    for path in recommended_paths + [fallback_path]:
        if os.path.exists(path):
            libvlc_path = os.path.join(path, 'libvlc.dll')
            if os.path.exists(libvlc_path):
                arch = get_file_arch(libvlc_path)
                found_paths.append((path, arch))
    
    # تفضيل المسارات ذات البنية 64 بت
    if found_paths:
        # إعادة ترتيب المسارات ليكون إصدار 64 بت في المقدمة
        found_paths.sort(key=lambda x: x[1] != "64bit")
    
    # Print found paths
    if found_paths:
        print("\nDetected VLC installations:")
        for i, (path, arch) in enumerate(found_paths):
            print(f"{i+1}. {path} [{arch}]")
            if arch == python_arch:
                print(f"   ✓ RECOMMENDED - Matches Python architecture")
            else:
                print(f"   ⚠️ WARNING - Architecture mismatch with Python")
    else:
        print("\nNo VLC installations detected.")
        print(f"Please install VLC ({python_arch}) from https://www.videolan.org/vlc/")
        input("\nPress Enter to exit...")
        return
    
    # Ask user to select path or provide custom path
    print("\nPlease choose a VLC path:")
    for i, (path, arch) in enumerate(found_paths):
        print(f"{i+1}. {path} [{arch}]")
    print(f"{len(found_paths) + 1}. Specify a custom path")
    
    while True:
        try:
            choice = int(input("\nEnter your choice (number): ").strip())
            if 1 <= choice <= len(found_paths):
                selected_path = found_paths[choice - 1][0]
                selected_arch = found_paths[choice - 1][1]
                break
            elif choice == len(found_paths) + 1:
                custom_path = input("Enter the full path to VLC installation directory: ").strip()
                if os.path.exists(custom_path):
                    libvlc_path = os.path.join(custom_path, 'libvlc.dll')
                    if os.path.exists(libvlc_path):
                        selected_path = custom_path
                        selected_arch = get_file_arch(libvlc_path)
                        break
                    else:
                        print(f"❌ Error: {custom_path} does not contain libvlc.dll!")
                else:
                    print(f"❌ Error: The path {custom_path} does not exist!")
            else:
                print("Invalid choice, please try again.")
        except ValueError:
            print("Please enter a number.")
    
    # Warn if architecture mismatch
    if selected_arch != python_arch:
        print(f"\n⚠️ WARNING: Architecture mismatch between Python ({python_arch}) and VLC ({selected_arch}).")
        print("This may cause issues with video playback.")
        confirm = input("Continue anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Operation cancelled.")
            return
    
    # Create the configuration file
    try:
        with open("vlc_path.txt", "w") as f:
            f.write(selected_path)
        
        print("\n✅ Configuration successful!")
        print(f"VLC path set to: {selected_path}")
        print("\nYou can now run the application using: python main.py")
    except Exception as e:
        print(f"❌ Error creating configuration file: {e}")

if __name__ == "__main__":
    # Check for admin privileges on Windows
    if platform.system() == "Windows" and not is_admin():
        print("Note: For best results, run this script as administrator")
        print("Some operations might be limited without admin privileges\n")
    
    main()
    
    input("\nPress Enter to exit...")

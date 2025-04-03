#!/usr/bin/env python3
import sys
import os
import platform
import ctypes
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QDir, QTranslator
from PyQt6.QtGui import QIcon

# Import our new playlist loader
from playlist_loader import load_playlist_from_url, load_playlist_from_file
from core.language_manager import LanguageManager, tr  # Fix: Import tr function here
# Fix import error - use the correct module name
from core.url_history import PlaylistURLManager
from core.playlist_history import PlaylistHistory
from core.theme_manager import ThemeManager

# Import Xtream client
from core.xtream_client import XtreamClient

# Add error handling utilities
import traceback

# Global exception handler to prevent app crashes
def global_exception_handler(exctype, value, tb):
    """Global exception handler to prevent crashes"""
    error_msg = ''.join(traceback.format_exception(exctype, value, tb))
    print(f"Error occurred:\n{error_msg}")
    
    # If we have a UI, show error dialog
    if QApplication.instance():
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("خطأ في التطبيق")
        msg.setText("حدث خطأ غير متوقع في التطبيق")
        msg.setDetailedText(error_msg)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    # Don't exit the app, just log the error
    # The original handler would be: sys.__excepthook__(exctype, value, tb)

# Set the global exception handler
sys.excepthook = global_exception_handler

def get_python_arch():
    """Returns the Python architecture (32bit or 64bit)"""
    return "64bit" if sys.maxsize > 2**32 else "32bit"

def setup_vlc_path():
    """Setup VLC library path based on platform"""
    system = platform.system()
    python_arch = get_python_arch()
    
    print(f"Python architecture: {python_arch}")
    
    if system == "Windows":
        # Check if we have a saved VLC path from previous runs
        if os.path.exists("vlc_path.txt"):
            with open("vlc_path.txt", "r") as f:
                custom_path = f.read().strip()
                if custom_path and os.path.exists(custom_path):
                    print(f"استخدام مسار VLC من ملف التكوين: {custom_path}")
                    
                    # Validate that the architecture matches
                    libvlc_path = os.path.join(custom_path, 'libvlc.dll')
                    if os.path.exists(libvlc_path):
                        try:
                            # Try to load the DLL directly to make sure it works with this Python
                            ctypes.CDLL(libvlc_path)
                            print(f"تم تحميل libvlc.dll بنجاح من المسار المخصص")
                            
                            # Add VLC directory to PATH and Python path
                            if custom_path not in sys.path:
                                sys.path.append(custom_path)
                            
                            os.environ['PATH'] = custom_path + os.pathsep + os.environ.get('PATH', '')
                            
                            # Remove problematic environment variables
                            if 'PYTHON_VLC_MODULE_PATH' in os.environ:
                                del os.environ['PYTHON_VLC_MODULE_PATH']
                            if 'PYTHON_VLC_LIB_PATH' in os.environ:
                                del os.environ['PYTHON_VLC_LIB_PATH']
                                
                            return custom_path
                        except Exception as e:
                            print(f"خطأ في تحميل libvlc.dll من المسار المخصص: {e}")
                            # Continue to try other paths if custom path fails
        
        # Define VLC paths based on Python architecture
        vlc_paths = []
        
        # Always try the architecture that matches Python first
        if python_arch == "64bit":
            vlc_paths = [
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'VideoLAN', 'VLC'),
                r"C:\Program Files\VideoLAN\VLC",
                # Fallback to 32-bit as last resort
                r"C:\Program Files (x86)\VideoLAN\VLC",
            ]
        else:  # 32-bit Python
            vlc_paths = [
                r"C:\Program Files (x86)\VideoLAN\VLC",
                # Fallback to 64-bit as last resort (but unlikely to work)
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'VideoLAN', 'VLC'),
                r"C:\Program Files\VideoLAN\VLC",
            ]
        
        for path in vlc_paths:
            if os.path.exists(path):
                print(f"تم العثور على VLC في: {path}")
                
                # Try to load the DLL directly
                libvlc_path = os.path.join(path, 'libvlc.dll')
                if os.path.exists(libvlc_path):
                    try:
                        # Try to load the DLL directly to make sure it works
                        ctypes.CDLL(libvlc_path)
                        print("تم تحميل libvlc.dll بنجاح")
                        
                        # Add VLC directory to PATH and Python path
                        if path not in sys.path:
                            sys.path.append(path)
                        
                        os.environ['PATH'] = path + os.pathsep + os.environ.get('PATH', '')
                        
                        # Remove problematic environment variables
                        if 'PYTHON_VLC_MODULE_PATH' in os.environ:
                            del os.environ['PYTHON_VLC_MODULE_PATH']
                        if 'PYTHON_VLC_LIB_PATH' in os.environ:
                            del os.environ['PYTHON_VLC_LIB_PATH']
                            
                        # Save this as our preferred path for future runs
                        with open("vlc_path.txt", "w") as f:
                            f.write(path)
                            
                        return path
                    except Exception as e:
                        print(f"خطأ في تحميل libvlc.dll: {e}")
        
        print("تحذير: لم يتم العثور على تثبيت VLC متوافق.")
        return None
    
    elif system == "Darwin":  # macOS
        vlc_paths = [
            '/Applications/VLC.app/Contents/MacOS/',
            '/Applications/VLC.app/Contents/MacOS/lib',
        ]
        
        for path in vlc_paths:
            if os.path.exists(path):
                print(f"Found VLC at: {path}")
                if path not in sys.path:
                    sys.path.append(path)
                os.environ['PATH'] = path + os.pathsep + os.environ.get('PATH', '')
                os.environ['DYLD_LIBRARY_PATH'] = path + os.pathsep + os.environ.get('DYLD_LIBRARY_PATH', '')
                return path
        
        print("Warning: Could not find VLC installation path.")
        return None
    
    # Linux doesn't need path setup as libraries should be in system paths
    return None

def check_vlc():
    """Check if VLC is available on the system"""
    # First try to set up the path
    vlc_path = setup_vlc_path()
    
    # Remove problematic environment variables
    if 'PYTHON_VLC_MODULE_PATH' in os.environ:
        del os.environ['PYTHON_VLC_MODULE_PATH']
    if 'PYTHON_VLC_LIB_PATH' in os.environ:
        del os.environ['PYTHON_VLC_LIB_PATH']
    
    try:
        # Try to import the VLC module
        import vlc
        return True, vlc_path
    except (ImportError, OSError, FileNotFoundError) as e:
        print(f"Error importing VLC: {e}")
        return False, vlc_path

def find_vlc_install():
    """Try to find VLC installation"""
    system = platform.system()
    python_arch = get_python_arch()
    paths = []
    
    if system == "Windows":
        if python_arch == "64bit":
            paths = [
                os.path.join(os.environ.get('PROGRAMFILES', ''), 'VideoLAN', 'VLC'),
                r"C:\Program Files\VideoLAN\VLC",
            ]
        else:
            paths = [
                r"C:\Program Files (x86)\VideoLAN\VLC",
            ]
    elif system == "Darwin":  # macOS
        paths = ['/Applications/VLC.app/Contents/MacOS/']
    else:  # Linux
        # VLC is typically in the PATH on Linux if installed
        return "Please install VLC using your package manager."
    
    for path in paths:
        if os.path.exists(path):
            return path
    
    # Suggest download link if not found
    return f"https://www.videolan.org/vlc/ (Please download the {'64-bit' if python_arch == '64bit' else '32-bit'} version)"

def main():
    """Main application entry point"""
    # Create application
    app = QApplication(sys.argv)
    
    # تعيين أيقونة التطبيق إذا كانت متاحة
    app_icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "resources", "icons", "app_icon.png")
    
    if os.path.exists(app_icon_path):
        app_icon = QIcon(app_icon_path)
        app.setWindowIcon(app_icon)
        # تعيين الأيقونة للاستخدام في شريط المهام في ويندوز
        if platform.system() == "Windows":
            import ctypes
            myappid = 'mycompany.iptvplayer.v1.0'  # أي معرف فريد
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    
    # الحصول على مسار مناسب لتخزين بيانات التطبيق (مسار قابل للكتابة)
    if getattr(sys, 'frozen', False):
        # تشغيل كتطبيق مجمّد (exe)
        app_path = os.path.dirname(sys.executable)
        # استخدام مسار AppData للمستخدم بدلاً من مجلد البرنامج
        data_dir = os.path.join(os.environ['APPDATA'], 'Modern-IPTV-Player', 'data')
    else:
        # تشغيل كمصدر Python
        app_path = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(app_path, 'data')
    
    os.makedirs(data_dir, exist_ok=True)
    
    # Initialize language first (before any UI operations that need translations)
    translator = QTranslator()
    app.installTranslator(translator)
    lang_manager = LanguageManager()
    
    # إنشاء مدير قفل التطبيق
    from core.pin_lock_manager import PinLockManager
    pin_manager = PinLockManager(data_dir)
    
    # التحقق من وجود قفل نشط (بعد تهيئة إدارة اللغة)
    if pin_manager.is_pin_enabled():
        # إظهار مربع حوار الرمز السري
        from ui.pin_dialog import PinDialog
        
        max_attempts = 3
        attempts = 0
        pin_verified = False
        
        while attempts < max_attempts and not pin_verified:
            pin_dialog = PinDialog(verification_mode=True)
            
            if pin_dialog.exec():
                entered_pin = pin_dialog.get_pin()
                if pin_manager.verify_pin(entered_pin):
                    pin_verified = True
                else:
                    attempts += 1
                    remaining = max_attempts - attempts
                    
                    if remaining > 0:
                        QMessageBox.warning(
                            None, 
                            tr("PIN Verification Failed"), 
                            tr("Incorrect PIN. {attempts_left} attempts remaining.").format(attempts_left=remaining)
                        )
                    else:
                        QMessageBox.critical(
                            None, 
                            tr("PIN Verification Failed"), 
                            tr("Incorrect PIN. Application will close.")
                        )
            else:
                # تم إغلاق نافذة الرمز السري، إنهاء التطبيق
                return
        
        # إنهاء التطبيق إذا لم يتم التحقق من الرمز السري بعد المحاولات المسموح بها
        if not pin_verified:
            return
    
    # عرض نافذة فحص المتطلبات (سيتم انشاؤها فقط إذا كانت أول مرة)
    show_requirements_check = True
    
    # التحقق مما إذا كانت هذه هي أول مرة لفتح التطبيق
    first_run_file = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')),
                             'Modern-IPTV-Player', 'first_run.txt')
    
    if os.path.exists(first_run_file):
        show_requirements_check = False
    else:
        # إنشاء ملف لتسجيل أن التطبيق قد تم تشغيله من قبل
        os.makedirs(os.path.dirname(first_run_file), exist_ok=True)
        with open(first_run_file, 'w') as f:
            f.write('1')
    
    if show_requirements_check:
        try:
            # استدعاء نافذة فحص المتطلبات
            from core.requirements_checker import RequirementsDialog
            req_dialog = RequirementsDialog()
            req_dialog.show_and_wait()
        except Exception as e:
            print(f"خطأ في عرض نافذة فحص المتطلبات: {e}")
    
    # إنشاء المكونات مع تمرير مسار البيانات
    url_manager = PlaylistURLManager(data_dir)
    playlist_history = PlaylistHistory(data_dir)
    theme_manager = ThemeManager(data_dir=data_dir)
    
    # Check for VLC 
    vlc_available, vlc_path = check_vlc()
    if not vlc_available:
        python_arch = get_python_arch()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("VLC Not Found")
        msg.setText("VLC media player appears to be missing or not properly configured.")
        
        # Add detailed instructions
        details = ("The application will start, but video playback will not be available.\n\n"
                  "To fix this issue:\n"
                  f"1. Make sure VLC media player ({python_arch}) is installed\n"
                  "2. If VLC is already installed, it might be the wrong architecture\n\n")
                  
        # Add installation suggestion
        vlc_install_path = find_vlc_install()
        if vlc_install_path.startswith("http"):
            details += f"Download VLC from: {vlc_install_path}"
        else:
            details += f"VLC should be installed at: {vlc_install_path}"
        
        msg.setDetailedText(details)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    # Import MainWindow here to avoid potential import errors with VLC
    from ui.main_window import MainWindow
    
    try:
        # إنشاء النافذة الرئيسية مع تمرير المكونات التي تم إنشاؤها
        window = MainWindow(url_manager, playlist_history, theme_manager, lang_manager, pin_manager)
        
        # عرض الملاحظة إذا كان التطبيق يُفتح لأول مرة - قبل إظهار النافذة الرئيسية
        try:
            from core.first_run_notice import NoticeManager
            notice_manager = NoticeManager()
            notice_manager.show_notice_if_needed(window)
        except Exception as e:
            print(f"خطأ في عرض الملاحظة: {e}")
        
        # Show the main window
        window.showMaximized()
        
        # Run application
        sys.exit(app.exec())
    except Exception as e:
        error_msg = traceback.format_exc()
        print(f"خطأ في تشغيل التطبيق: {e}\n{error_msg}")
        
        # Show error dialog
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("خطأ في التطبيق")
        msg.setText("حدث خطأ عند محاولة تشغيل التطبيق")
        msg.setDetailedText(error_msg)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        
        sys.exit(1)

if __name__ == "__main__":
    main()

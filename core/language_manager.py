import json
import os
import locale
from PyQt6.QtCore import QObject, QTranslator, QCoreApplication

# Default translations
_translations = {
    "en": {
        "Modern IPTV Player": "Modern IPTV Player",
        "Search channels...": "Search channels...",
        "All Channels": "All Channels",
        "Category:": "Category:",
        "All": "All",
        "Ready": "Ready",
        "&File": "&File",
        "&Open Playlist...": "&Open Playlist...",
        "Open Playlist from &URL...": "Open Playlist from &URL...",
        "E&xit": "E&xit",
        "&Playback": "&Playback",
        "&Play/Pause": "&Play/Pause",
        "&Stop": "&Stop",
        "&Settings": "&Settings",
        "Language": "Language",
        "English": "English",
        "العربية": "العربية",
        "&Help": "&Help",
        "About App": "About App",
        "About Developer": "About Developer",
        "Check for Updates": "Check for Updates",
        "Language Changed": "Language Changed",
        "The language has been changed. Please restart the application for the changes to take effect.": "The language has been changed. Please restart the application for the changes to take effect.",
        "Updates": "Updates",
        "App Logo": "App Logo",
        "Manage Settings": "Manage Settings",
        "Recent URLs:": "Recent URLs:",
        "Welcome": "Welcome",
        "Welcome to Modern IPTV Player": "Welcome to Modern IPTV Player",
    },
    "ar": {
        "Modern IPTV Player": "مشغل IPTV الحديث",
        "Search channels...": "بحث عن القنوات...",
        "All Channels": "كل القنوات",
        "Category:": "التصنيف:",
        "All": "الكل",
        "Ready": "جاهز",
        "&File": "&ملف",
        "&Open Playlist...": "&فتح قائمة تشغيل...",
        "Open Playlist from &URL...": "فتح قائمة تشغيل من &رابط...",
        "E&xit": "&خروج",
        "&Playback": "&تشغيل",
        "&Play/Pause": "&تشغيل/إيقاف مؤقت",
        "&Stop": "إي&قاف",
        "&Settings": "الإ&عدادات",
        "Language": "اللغة",
        "English": "English",
        "العربية": "العربية",
        "&Help": "م&ساعدة",
        "About App": "حول التطبيق",
        "About Developer": "عن المطور",
        "Check for Updates": "التحقق من التحديثات",
        "Language Changed": "تم تغيير اللغة",
        "The language has been changed. Please restart the application for the changes to take effect.": "تم تغيير اللغة. الرجاء إعادة تشغيل التطبيق لتطبيق التغييرات.",
        "Updates": "التحديثات",
        "Play": "تشغيل",
        "Add to Playlist": "إضافة إلى قائمة التشغيل",
        "No channel selected": "لم يتم اختيار قناة",
        "Playing: {channel_name}": "يتم تشغيل: {channel_name}",
        "Loading playlist: {file_path}...": "جاري تحميل قائمة التشغيل: {file_path}...",
        "Loading playlist from URL...": "جاري تحميل قائمة التشغيل من الرابط...",
        "Loaded {count} channels": "تم تحميل {count} قناة",
        "Error": "خطأ",
        "Failed to load playlist": "فشل تحميل قائمة التشغيل",
        "Failed to load playlist from URL": "فشل تحميل قائمة التشغيل من الرابط",
        "M3U Playlists (*.m3u *.m3u8);;All Files (*)": "قوائم تشغيل M3U (*.m3u *.m3u8);;جميع الملفات (*)",
        "Open Playlist": "فتح قائمة التشغيل",
        "Open Playlist URL": "فتح قائمة التشغيل من رابط",
        "Enter playlist URL:": "أدخل رابط قائمة التشغيل:",
        "Add New Playlist": "إضافة قائمة تشغيل جديدة",
        "Name:": "الاسم:",
        "OK": "موافق",
        "Cancel": "إلغاء",
        "VLC is not available. Please install the correct version of VLC media player.": "برنامج VLC غير متوفر. الرجاء تثبيت الإصدار الصحيح من مشغل VLC.",
        "VLC is not available. Please install VLC media player.": "برنامج VLC غير متوفر. الرجاء تثبيت مشغل VLC.",
        "You are using the latest version (1.0).\nNo updates are currently available.": "أنت تستخدم أحدث إصدار من البرنامج (1.0).\nلا توجد تحديثات متوفرة حاليًا.",
        # Playlist management related translations
        "Manage Playlists...": "إدارة قوائم التشغيل...",
        "Playlist Manager": "إدارة قوائم التشغيل",
        "New Playlist": "قائمة تشغيل جديدة",
        "Rename": "إعادة تسمية",
        "Delete": "حذف",
        "Playlists": "قوائم التشغيل",
        "History": "السجل",
        "Channels": "القنوات",
        "Created": "تم الإنشاء",
        "Last Updated": "آخر تحديث",
        "Name": "الاسم",
        "Enter playlist name:": "أدخل اسم قائمة التشغيل:",
        "Duplicate Name": "اسم مكرر",
        "A playlist with this name already exists.": "توجد بالفعل قائمة تشغيل بهذا الاسم.",
        "Rename Playlist": "إعادة تسمية قائمة التشغيل",
        "Enter new name:": "أدخل الاسم الجديد:",
        "Confirm Delete": "تأكيد الحذف",
        "Are you sure you want to delete playlist '{name}'?": "هل أنت متأكد أنك تريد حذف قائمة التشغيل '{name}'؟",
        "Added '{channel}' to playlist '{playlist}'": "تمت إضافة '{channel}' إلى قائمة التشغيل '{playlist}'",
        "Created new playlist '{playlist}' with channel '{channel}'": "تم إنشاء قائمة تشغيل جديدة '{playlist}' مع القناة '{channel}'",
        "Add to Playlist": "إضافة إلى قائمة التشغيل",
        "New Playlist...": "قائمة تشغيل جديدة...",
        "Channel": "القناة",
        "Select playlist:": "اختر قائمة التشغيل:",
        "Create New Playlist": "إنشاء قائمة تشغيل جديدة",
        "Xtream (Soon)": "Xtream (قريباً)",
        "App Logo": "شعار التطبيق",
        "Manage Settings": "إدارة الإعدادات",
        "Recent URLs:": "الروابط الأخيرة:",
        "Welcome": "مرحباً",
        "Welcome to Modern IPTV Player": "مرحباً بك في مشغل IPTV الحديث",
    }
}

# Global translator
_translator = None
_current_language = "en"

def tr(text):
    """Translate text using the translation dictionary"""
    global _translations, _current_language
    if text in _translations[_current_language]:
        return _translations[_current_language][text]
    return text

class LanguageManager(QObject):
    """Language manager for the application"""
    
    def __init__(self):
        super().__init__()
        global _current_language
        
        self.languages = {
            "en": "English",
            "ar": "العربية"
        }
        
        # Load user preference or use system locale
        self.current_language = self._load_language_preference()
        _current_language = self.current_language
        
    def _load_language_preference(self):
        """Load language preference from file"""
        language_file = "language.txt"
        
        if os.path.exists(language_file):
            try:
                with open(language_file, "r") as f:
                    lang = f.read().strip()
                    if lang in self.languages:
                        return lang
            except:
                pass
        
        # Default based on system or fall back to English
        try:
            system_lang = locale.getdefaultlocale()[0][:2]
            if system_lang in self.languages:
                return system_lang
        except:
            pass
            
        return "en"  # Default to English
    
    def change_language(self, language):
        """Change the application language"""
        if language in self.languages:
            global _current_language
            
            self.current_language = language
            _current_language = language
            
            # Save preference
            try:
                with open("language.txt", "w") as f:
                    f.write(language)
            except:
                pass

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
        # PIN Lock related translations
        "App Lock": "App Lock",
        "Create PIN Code": "Create PIN Code",
        "Enter PIN code to continue": "Enter PIN code to continue",
        "Create new PIN code": "Create new PIN code",
        "Please enter a 4-digit PIN code:": "Please enter a 4-digit PIN code:",
        "Confirm PIN code:": "Confirm PIN code:",
        "Please enter a 4-digit PIN code": "Please enter a 4-digit PIN code",
        "Please confirm your PIN code": "Please confirm your PIN code",
        "PIN codes do not match! Try again.": "PIN codes do not match! Try again.",
        "Unlock": "Unlock",
        "Create PIN": "Create PIN",
        "Cancel": "Cancel",
        "App Lock Settings": "App Lock Settings",
        "Lock the app with a PIN code to prevent unauthorized access. You will be asked to enter your PIN each time you open the app.": "Lock the app with a PIN code to prevent unauthorized access. You will be asked to enter your PIN each time you open the app.",
        "Enable PIN Lock": "Enable PIN Lock",
        "Change PIN": "Change PIN",
        "Disable PIN Lock": "Disable PIN Lock",
        "⚠️ Security Note: If you forget your PIN, you will need to reinstall the application.": "⚠️ Security Note: If you forget your PIN, you will need to reinstall the application.",
        "PIN verification": "PIN verification",
        "Incorrect PIN. Application will close.": "Incorrect PIN. Application will close.",
        "Success": "Success",
        "PIN lock enabled and new PIN created.": "PIN lock enabled and new PIN created.",
        "Error": "Error",
        "Error enabling PIN lock.": "Error enabling PIN lock.",
        "Current PIN is incorrect.": "Current PIN is incorrect.",
        "PIN changed successfully.": "PIN changed successfully.",
        "Error changing PIN.": "Error changing PIN.",
        "PIN lock disabled.": "PIN lock disabled.",
        "Error disabling PIN lock.": "Error disabling PIN lock.",
        "Close": "Close",
        "PIN Verification Failed": "PIN Verification Failed",
        "Incorrect PIN. {attempts_left} attempts remaining.": "Incorrect PIN. {attempts_left} attempts remaining.",
        # Xtream API related translations
        "Xtream Connection": "Xtream Connection",
        "Xtream Connection Info": "Xtream Connection Info",
        "Connect to Xtream Provider": "Connect to Xtream Provider",
        "Server URL:": "Server URL:",
        "Username:": "Username:",
        "Password:": "Password:",
        "Remember credentials": "Remember credentials",
        "Connect": "Connect",
        "Cancel": "Cancel",
        "Please fill in all fields": "Please fill in all fields",
        "Connecting...": "Connecting...",
        "Connected, but no streams were found": "Connected, but no streams were found",
        "Connection Information": "Connection Information",
        "Server:": "Server:",
        "Status:": "Status:",
        "Expiration:": "Expiration:",
        "Error connecting to Xtream service: {error}": "Error connecting to Xtream service: {error}",
        "Error processing Xtream data: {error}": "Error processing Xtream data: {error}",
        "Connected to Xtream service. Loaded {count} channels.": "Connected to Xtream service. Loaded {count} channels.",
        # Movies & Series related translations
        "Movies": "Movies",
        "Series": "Series",
        "Search...": "Search...",
        "No results found": "No results found",
        "Playing: {movie_name}": "Playing: {movie_name}",
        "Loaded {count} movies": "Loaded {count} movies",
        "Loaded {count} series": "Loaded {count} series",
        "Director:": "Director:",
        "Cast:": "Cast:",
        "Genre:": "Genre:",
        "Released:": "Released:",
        "Rating:": "Rating:",
        "Duration:": "Duration:",
        "Seasons": "Seasons",
        "Episodes": "Episodes",
        "Season": "Season",
        "Episode": "Episode",
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
        # PIN Lock related translations
        "App Lock": "قفل التطبيق",
        "Create PIN Code": "إنشاء رمز سري",
        "Enter PIN code to continue": "أدخل الرمز السري للمتابعة",
        "Create new PIN code": "أنشئ رمز سري جديد",
        "Please enter a 4-digit PIN code:": "الرجاء إدخال الرمز السري المكون من 4 أرقام:",
        "Confirm PIN code:": "تأكيد الرمز السري:",
        "Please enter a 4-digit PIN code": "الرجاء إدخال رمز سري من 4 أرقام",
        "Please confirm your PIN code": "الرجاء تأكيد الرمز السري",
        "PIN codes do not match! Try again.": "الرمز غير متطابق! حاول مرة أخرى.",
        "Unlock": "فتح القفل",
        "Create PIN": "إنشاء الرمز",
        "Cancel": "إلغاء",
        "App Lock Settings": "إعدادات قفل التطبيق",
        "Lock the app with a PIN code to prevent unauthorized access. You will be asked to enter your PIN each time you open the app.": "قفل التطبيق برمز سري يمنع الدخول غير المصرح به إلى التطبيق. سيُطلب منك إدخال الرمز السري في كل مرة تفتح فيها التطبيق.",
        "Enable PIN Lock": "تفعيل قفل التطبيق برمز سري",
        "Change PIN": "تغيير الرمز السري",
        "Disable PIN Lock": "إلغاء تفعيل الرمز السري",
        "⚠️ ملاحظة أمان: إذا نسيت الرمز السري، ستحتاج إلى إعادة تثبيت التطبيق.": "⚠️ ملاحظة أمان: إذا نسيت الرمز السري، ستحتاج إلى إعادة تثبيت التطبيق.",
        "PIN verification": "التحقق من الرمز السري",
        "Incorrect PIN. Application will close.": "الرمز السري غير صحيح. سيتم إغلاق التطبيق.",
        "Success": "نجاح",
        "PIN lock enabled and new PIN created.": "تم تفعيل قفل التطبيق وإنشاء رمز سري جديد.",
        "Error": "خطأ",
        "Error enabling PIN lock.": "حدث خطأ أثناء تفعيل قفل التطبيق.",
        "Current PIN is incorrect.": "الرمز السري الحالي غير صحيح.",
        "PIN changed successfully.": "تم تغيير الرمز السري بنجاح.",
        "Error changing PIN.": "حدث خطأ أثناء تغيير الرمز السري.",
        "PIN lock disabled.": "تم تعطيل قفل التطبيق.",
        "Error disabling PIN lock.": "حدث خطأ أثناء تعطيل قفل التطبيق.",
        "Close": "إغلاق",
        "PIN Verification Failed": "فشل التحقق من الرمز السري",
        "Incorrect PIN. {attempts_left} attempts remaining.": "الرمز السري غير صحيح. متبقي {attempts_left} محاولات.",
        # Xtream API related translations
        "Xtream Connection": "اتصال Xtream",
        "Xtream Connection Info": "معلومات اتصال Xtream",
        "Connect to Xtream Provider": "الاتصال بمزود Xtream",
        "Server URL:": "عنوان الخادم:",
        "Username:": "اسم المستخدم:",
        "Password:": "كلمة المرور:",
        "Remember credentials": "تذكر بيانات الدخول",
        "Connect": "اتصال",
        "Cancel": "إلغاء",
        "Please fill in all fields": "الرجاء ملء جميع الحقول",
        "Connecting...": "جاري الاتصال...",
        "Connected, but no streams were found": "تم الاتصال، لكن لم يتم العثور على أي قنوات",
        "Connection Information": "معلومات الاتصال",
        "Server:": "الخادم:",
        "Status:": "الحالة:",
        "Expiration:": "تاريخ انتهاء الصلاحية:",
        "Error connecting to Xtream service: {error}": "خطأ في الاتصال بخدمة Xtream: {error}",
        "Error processing Xtream data: {error}": "خطأ في معالجة بيانات Xtream: {error}",
        "Connected to Xtream service. Loaded {count} قناة.": "تم الاتصال بخدمة Xtream. تم تحميل {count} قناة.",
        # Movies & Series related translations
        "Movies": "الأفلام",
        "Series": "المسلسلات",
        "Search...": "بحث...",
        "No results found": "لم يتم العثور على نتائج",
        "Playing: {movie_name}": "يتم تشغيل: {movie_name}",
        "Loaded {count} movies": "تم تحميل {count} فيلم",
        "Loaded {count} series": "تم تحميل {count} مسلسل",
        "Director:": "المخرج:",
        "Cast:": "طاقم التمثيل:",
        "Genre:": "النوع:",
        "Released:": "تاريخ الإصدار:",
        "Rating:": "التقييم:",
        "Duration:": "المدة:",
        "Seasons": "المواسم",
        "Episodes": "الحلقات",
        "Season": "الموسم",
        "Episode": "الحلقة",
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

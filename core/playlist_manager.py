import os
import sys
import json
import logging
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 
                                         'Modern-IPTV-Player', 'logs', 'playlist_manager.log')),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('PlaylistManager')

class PlaylistManager(QObject):
    """
    مدير قوائم التشغيل - يتعامل مع حفظ وتحميل قوائم التشغيل
    """
    playlist_saved = pyqtSignal(str)  # إشارة للإشعار بحفظ قائمة تشغيل
    playlist_loaded = pyqtSignal(str, list)  # إشارة للإشعار بتحميل قائمة تشغيل
    
    def __init__(self, data_dir):
        super().__init__()
        self.data_dir = data_dir
        self.playlists_dir = os.path.join(data_dir, 'playlists')
        os.makedirs(self.playlists_dir, exist_ok=True)
        logger.info(f"تم تهيئة مدير قوائم التشغيل. المسار: {self.playlists_dir}")

    def save_playlist(self, name, channels, overwrite=False):
        """
        حفظ قائمة تشغيل في ملف
        """
        try:
            # تنظيف اسم الملف
            safe_name = self._sanitize_filename(name)
            if not safe_name.endswith('.json'):
                safe_name += '.json'
            
            # إنشاء المسار الكامل
            file_path = os.path.join(self.playlists_dir, safe_name)
            
            # التحقق من وجود الملف
            if os.path.exists(file_path) and not overwrite:
                logger.warning(f"محاولة الكتابة فوق ملف موجود: {file_path}")
                return False, "قائمة التشغيل موجودة بالفعل. الرجاء اختيار اسم آخر أو تأكيد الاستبدال."
            
            # إعداد البيانات للحفظ
            playlist_data = {
                'name': name,
                'channels': channels,
                'version': '1.0'
            }
            
            # كتابة البيانات
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(playlist_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"تم حفظ قائمة التشغيل بنجاح: {file_path}")
            self.playlist_saved.emit(name)
            return True, "تم حفظ قائمة التشغيل بنجاح."
            
        except Exception as e:
            error_msg = f"خطأ في حفظ قائمة التشغيل: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    def load_playlist(self, name):
        """
        تحميل قائمة تشغيل من ملف
        """
        try:
            # التحقق من امتداد الملف
            if not name.endswith('.json'):
                name += '.json'
            
            # إنشاء المسار الكامل
            file_path = os.path.join(self.playlists_dir, name)
            
            # التحقق من وجود الملف
            if not os.path.exists(file_path):
                logger.warning(f"محاولة تحميل ملف غير موجود: {file_path}")
                return False, [], "قائمة التشغيل غير موجودة."
            
            # قراءة البيانات
            with open(file_path, 'r', encoding='utf-8') as f:
                playlist_data = json.load(f)
            
            name = playlist_data.get('name', os.path.splitext(name)[0])
            channels = playlist_data.get('channels', [])
            
            logger.info(f"تم تحميل قائمة التشغيل بنجاح: {file_path}")
            self.playlist_loaded.emit(name, channels)
            return True, channels, "تم تحميل قائمة التشغيل بنجاح."
            
        except json.JSONDecodeError:
            error_msg = "الملف ليس بتنسيق JSON صالح."
            logger.error(error_msg)
            return False, [], error_msg
            
        except Exception as e:
            error_msg = f"خطأ في تحميل قائمة التشغيل: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, [], error_msg

    def get_all_playlists(self):
        """
        الحصول على قائمة بجميع قوائم التشغيل المخزنة
        """
        try:
            playlists = []
            for filename in os.listdir(self.playlists_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(self.playlists_dir, filename), 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            playlists.append({
                                'name': data.get('name', os.path.splitext(filename)[0]),
                                'filename': filename,
                                'channel_count': len(data.get('channels', []))
                            })
                    except Exception as e:
                        logger.error(f"خطأ في قراءة ملف قائمة التشغيل {filename}: {str(e)}")
            
            return playlists
        except Exception as e:
            logger.error(f"خطأ في الحصول على قائمة قوائم التشغيل: {str(e)}", exc_info=True)
            return []

    def delete_playlist(self, name):
        """
        حذف قائمة تشغيل
        """
        try:
            if not name.endswith('.json'):
                name += '.json'
                
            file_path = os.path.join(self.playlists_dir, name)
            
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"تم حذف قائمة التشغيل: {file_path}")
                return True, "تم حذف قائمة التشغيل بنجاح."
            else:
                logger.warning(f"محاولة حذف ملف غير موجود: {file_path}")
                return False, "قائمة التشغيل غير موجودة."
                
        except Exception as e:
            error_msg = f"خطأ في حذف قائمة التشغيل: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return False, error_msg

    def _sanitize_filename(self, filename):
        """
        تنظيف اسم الملف من الأحرف غير المسموح بها
        """
        # إزالة الأحرف غير المسموح بها في أسماء الملفات
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename

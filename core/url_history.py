import os
import json
from datetime import datetime

class PlaylistURLManager:
    """Manages history of loaded playlist URLs"""
    
    def __init__(self, data_dir=None):
        # استخدام المسار المُمرر أو الاعتماد على المسار الافتراضي
        if data_dir:
            self.data_dir = data_dir
        else:
            # استخدام مسار AppData للمستخدم كمسار افتراضي
            self.data_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')),
                                      'Modern-IPTV-Player', 'data')
        
        # التأكد من وجود المجلد
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.history_file = os.path.join(self.data_dir, 'url_history.json')
        self.urls = self._load_urls()
    
    def _load_urls(self):
        """تحميل سجل الروابط من ملف"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
            except Exception as e:
                print(f"خطأ في تحميل سجل الروابط: {e}")
        return []
    
    def save_history(self):
        """حفظ سجل الروابط إلى ملف"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.urls, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"خطأ في حفظ سجل الروابط: {e}")
    
    def add_url(self, url):
        """إضافة رابط جديد إلى السجل"""
        # تجنب التكرار - إذا كان الرابط موجود فإزالته أولاً ثم إضافته من جديد في المقدمة
        if url in self.urls:
            self.urls.remove(url)
        
        # إضافة الرابط في بداية القائمة (الأحدث أولاً)
        self.urls.insert(0, url)
        
        # الاحتفاظ بآخر 20 رابط فقط
        self.urls = self.urls[:20]
        
        # حفظ التغييرات
        self.save_history()
    
    def get_urls(self):
        """استرجاع قائمة الروابط المحفوظة"""
        return self.urls
    
    def clear_history(self):
        """مسح سجل الروابط"""
        self.urls = []
        self.save_history()

import os
import json
import requests
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextBrowser, QPushButton, QDialogButtonBox
from PyQt6.QtCore import Qt
from core.language_manager import tr, _current_language

class NoticeManager:
    """مدير عرض الملاحظات للمستخدم عند فتح التطبيق لأول مرة"""
    
    def __init__(self, config_file="app_config.json"):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self):
        """تحميل ملف التكوين"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"خطأ في تحميل ملف التكوين: {e}")
        
        # إذا لم يوجد ملف تكوين، أنشئ واحداً جديداً
        return {"first_run": True, "version": "1.0"}
    
    def _save_config(self):
        """حفظ ملف التكوين"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"خطأ في حفظ ملف التكوين: {e}")
    
    def is_first_run(self):
        """التحقق مما إذا كان هذا هو التشغيل الأول للتطبيق"""
        return self.config.get("first_run", True)
    
    def mark_as_run(self):
        """تعليم التطبيق على أنه تم تشغيله"""
        self.config["first_run"] = False
        self._save_config()
    
    def fetch_notice_text(self, language="en"):
        """جلب نص الملاحظة من الإنترنت"""
        # استخدام الروابط المقدمة بشكل مباشر
        url = f"https://aljup.com/app/note_{language}.txt"
        print(f"محاولة تنزيل الملاحظة من: {url}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"تم تنزيل الملاحظة بنجاح باللغة: {language}")
                return response.text
            else:
                print(f"فشل تنزيل الملاحظة باللغة {language}، كود الاستجابة: {response.status_code}")
                return None
        except Exception as e:
            print(f"خطأ في جلب الملاحظة من {url}: {e}")
            return None
    
    def show_notice_if_needed(self, parent=None):
        """عرض الملاحظة إذا كان التطبيق يُفتح لأول مرة"""
        if not self.is_first_run():
            print("ليس التشغيل الأول للتطبيق، تم تخطي عرض الملاحظة")
            return False
        
        print(f"التشغيل الأول للتطبيق، جاري محاولة عرض الملاحظة (اللغة الحالية: {_current_language})")
        
        # جلب نص الملاحظة بناءً على اللغة الحالية
        language = _current_language
        notice_text = self.fetch_notice_text(language)
        
        # محاولة احتياطية: إذا فشل تنزيل الملاحظة باللغة الحالية وكانت العربية، نجرب تنزيلها مع "ar"
        if not notice_text and language == "ar":
            print("محاولة تنزيل الملاحظة باللغة العربية (ar)")
            notice_text = self.fetch_notice_text("ar")
        
        # محاولة أخيرة: إذا فشلت جميع المحاولات السابقة، نجرب اللغة الإنجليزية
        if not notice_text:
            print("محاولة تنزيل الملاحظة باللغة الإنجليزية (en)")
            notice_text = self.fetch_notice_text("en")
        
        # إذا لم نتمكن من جلب الملاحظة، نستخدم نص افتراضي
        if not notice_text:
            print("لم نتمكن من تنزيل أي ملاحظة، سيتم استخدام نص افتراضي")
            if language == "ar":
                notice_text = """
                <div dir="rtl" style="text-align: right;">
                <h2>مرحباً بك في مشغل IPTV الحديث!</h2>
                <p>شكراً لاستخدامك تطبيقنا. نأمل أن يكون مفيداً لك.</p>
                <p>تم تطوير هذا التطبيق بهدف تقديم تجربة مشاهدة سهلة ومميزة.</p>
                <p>إذا كانت لديك أي اقتراحات أو ملاحظات، يرجى مراسلتنا.</p>
                <p><b>استمتع بالمشاهدة!</b></p>
                </div>
                """
            else:
                notice_text = """
                <h2>Welcome to Modern IPTV Player!</h2>
                <p>Thank you for using our application. We hope you find it useful.</p>
                <p>This application was developed to provide an easy and excellent viewing experience.</p>
                <p>If you have any suggestions or comments, please contact us.</p>
                <p><b>Enjoy watching!</b></p>
                """
        
        # عرض الملاحظة في نافذة منبثقة
        dialog = NoticeDialog(notice_text, parent)
        dialog.exec()
        
        # تعليم التطبيق كمستخدم
        self.mark_as_run()
        return True


class NoticeDialog(QDialog):
    """نافذة عرض الملاحظة"""
    
    def __init__(self, notice_text, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(tr("Welcome"))
        self.setMinimumSize(600, 450)
        
        # إنشاء التخطيط
        layout = QVBoxLayout(self)
        
        # إضافة عنوان
        title = QLabel(tr("Welcome to Modern IPTV Player"))
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # إضافة مربع نص لعرض الملاحظة
        self.notice_browser = QTextBrowser()
        self.notice_browser.setHtml(notice_text)
        
        # تعيين خصائص النص لتحسين العرض
        self.notice_browser.setOpenExternalLinks(True)
        self.notice_browser.setStyleSheet("font-size: 12pt;")
        layout.addWidget(self.notice_browser)
        
        # إضافة أزرار بنص مترجم
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        if _current_language == "ar":
            button_box.button(QDialogButtonBox.StandardButton.Ok).setText("موافق")
            
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
        
        # تعيين اتجاه النص بناءً على اللغة
        if _current_language == "ar":
            self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
            self.setWindowTitle("مرحباً")
            title.setText("مرحباً بك في مشغل IPTV الحديث")
        else:
            self.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

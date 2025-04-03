#!/usr/bin/env python3
"""
أداة إدارة إعدادات التطبيق
تتيح هذه الأداة تصدير واستيراد إعدادات التطبيق بما في ذلك:
- قوائم التشغيل المخصصة
- روابط قوائم التشغيل المستخدمة
- إعدادات اللغة
- مسار VLC
"""
import os
import sys
import json
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt

class SettingsManager(QMainWindow):
    """نافذة إدارة الإعدادات"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("إدارة الإعدادات")
        self.setMinimumSize(500, 400)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("إدارة إعدادات التطبيق")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "يمكنك من خلال هذه الأداة تصدير واستيراد إعدادات التطبيق."
            "\nتشمل الإعدادات: قوائم التشغيل المخصصة، روابط M3U المستخدمة، إعدادات اللغة، ومسار VLC."
        )
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        layout.addSpacing(20)
        
        # Export button
        self.export_btn = QPushButton("تصدير الإعدادات")
        self.export_btn.setMinimumHeight(40)
        self.export_btn.clicked.connect(self.export_settings)
        layout.addWidget(self.export_btn)
        
        # Import button
        self.import_btn = QPushButton("استيراد الإعدادات")
        self.import_btn.setMinimumHeight(40)
        self.import_btn.clicked.connect(self.import_settings)
        layout.addWidget(self.import_btn)
        
        # Reset button
        layout.addSpacing(40)
        self.reset_btn = QPushButton("إعادة تعيين جميع الإعدادات")
        self.reset_btn.setStyleSheet("color: red;")
        self.reset_btn.clicked.connect(self.reset_settings)
        layout.addWidget(self.reset_btn)
        
        layout.addStretch()
    
    def get_settings_files(self):
        """الحصول على قائمة ملفات الإعدادات"""
        files = []
        
        # قائمة بملفات الإعدادات
        if os.path.exists("language.txt"):
            files.append("language.txt")
        
        if os.path.exists("vlc_path.txt"):
            files.append("vlc_path.txt")
        
        if os.path.exists("playlist_urls.json"):
            files.append("playlist_urls.json")
        
        # إضافة مجلد قوائم التشغيل المخصصة إذا كان موجودًا
        if os.path.exists("playlists") and os.path.isdir("playlists"):
            for file in os.listdir("playlists"):
                if file.endswith(".json"):
                    files.append(os.path.join("playlists", file))
        
        return files
    
    def export_settings(self):
        """تصدير جميع الإعدادات إلى ملف مضغوط"""
        try:
            # اختيار مسار الحفظ
            file_path, _ = QFileDialog.getSaveFileName(
                self, "حفظ الإعدادات", "iptv_settings.json", "ملف إعدادات (*.json)"
            )
            
            if not file_path:
                return
            
            # جمع الإعدادات في قاموس
            settings = {}
            
            # قائمة الملفات
            files = self.get_settings_files()
            
            # إضافة كل ملف إلى القاموس
            for file_path in files:
                try:
                    if os.path.exists(file_path):
                        if file_path.endswith(".json"):
                            with open(file_path, "r", encoding="utf-8") as f:
                                key = os.path.basename(file_path)
                                if os.path.dirname(file_path) == "playlists":
                                    if "playlists" not in settings:
                                        settings["playlists"] = {}
                                    settings["playlists"][key] = json.load(f)
                                else:
                                    settings[key] = json.load(f)
                        else:
                            with open(file_path, "r", encoding="utf-8") as f:
                                settings[os.path.basename(file_path)] = f.read().strip()
                except Exception as e:
                    print(f"خطأ في قراءة الملف {file_path}: {e}")
            
            # حفظ الإعدادات
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(
                self,
                "نجاح",
                f"تم تصدير الإعدادات بنجاح إلى:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "خطأ",
                f"حدث خطأ أثناء تصدير الإعدادات:\n{str(e)}"
            )
    
    def import_settings(self):
        """استيراد الإعدادات من ملف"""
        try:
            # اختيار ملف الإعدادات
            file_path, _ = QFileDialog.getOpenFileName(
                self, "استيراد الإعدادات", "", "ملف إعدادات (*.json);;جميع الملفات (*)"
            )
            
            if not file_path:
                return
            
            # قراءة الإعدادات
            with open(file_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
            
            # استخراج الإعدادات وحفظها
            for key, value in settings.items():
                if key == "playlists" and isinstance(value, dict):
                    # إنشاء مجلد قوائم التشغيل إذا لم يكن موجودًا
                    os.makedirs("playlists", exist_ok=True)
                    
                    # حفظ كل ملف قائمة تشغيل
                    for playlist_file, playlist_data in value.items():
                        with open(os.path.join("playlists", playlist_file), "w", encoding="utf-8") as f:
                            json.dump(playlist_data, f, ensure_ascii=False, indent=2)
                elif key.endswith(".json"):
                    # الملفات ذات الصيغة JSON
                    with open(key, "w", encoding="utf-8") as f:
                        json.dump(value, f, ensure_ascii=False, indent=2)
                else:
                    # الملفات النصية البسيطة
                    with open(key, "w", encoding="utf-8") as f:
                        f.write(str(value))
            
            QMessageBox.information(
                self,
                "نجاح",
                "تم استيراد الإعدادات بنجاح.\nيرجى إعادة تشغيل التطبيق لتطبيق التغييرات."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "خطأ",
                f"حدث خطأ أثناء استيراد الإعدادات:\n{str(e)}"
            )
    
    def reset_settings(self):
        """إعادة تعيين جميع الإعدادات"""
        confirm = QMessageBox.question(
            self,
            "تأكيد",
            "هل أنت متأكد من رغبتك في إعادة تعيين جميع الإعدادات؟\nسيؤدي هذا إلى حذف جميع قوائم التشغيل المخصصة والإعدادات الأخرى.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # حذف ملفات الإعدادات
            files_to_delete = [
                "language.txt",
                "vlc_path.txt",
                "playlist_urls.json"
            ]
            
            for file in files_to_delete:
                if os.path.exists(file):
                    os.remove(file)
            
            # حذف مجلد قوائم التشغيل
            if os.path.exists("playlists") and os.path.isdir("playlists"):
                shutil.rmtree("playlists")
            
            QMessageBox.information(
                self,
                "نجاح",
                "تم إعادة تعيين جميع الإعدادات بنجاح.\nيرجى إعادة تشغيل التطبيق لتطبيق التغييرات."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "خطأ",
                f"حدث خطأ أثناء إعادة تعيين الإعدادات:\n{str(e)}"
            )

def main():
    """الدالة الرئيسية"""
    app = QApplication(sys.argv)
    window = SettingsManager()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

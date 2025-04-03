#!/usr/bin/env python3
"""
مدير شعار التطبيق 
يتيح هذا السكربت تطبيق الشعار على التطبيق وتعديله
"""
import os
import sys
import shutil
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel,
                           QPushButton, QFileDialog, QMessageBox)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import Qt

class LogoManagerWindow(QMainWindow):
    """نافذة إدارة شعار التطبيق"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("إدارة شعار التطبيق")
        self.setMinimumSize(500, 400)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create layout
        layout = QVBoxLayout(central_widget)
        
        # مسارات الأيقونات
        self.icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icons")
        self.backup_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icons_backup")
        
        self.logo_path = os.path.join(self.icons_dir, "logo.png")
        self.app_icon_path = os.path.join(self.icons_dir, "app_icon.png")
        
        # إنشاء المجلدات إذا لم تكن موجودة
        if not os.path.exists(self.icons_dir):
            os.makedirs(self.icons_dir, exist_ok=True)
        
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir, exist_ok=True)
        
        # عنوان
        title_label = QLabel("إدارة شعار التطبيق")
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # عرض الشعار الحالي
        logo_title = QLabel("الشعار الحالي:")
        logo_title.setStyleSheet("font-weight: bold; margin-top: 20px;")
        layout.addWidget(logo_title)
        
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.logo_label.setMinimumHeight(100)
        layout.addWidget(self.logo_label)
        
        # زر تغيير الشعار
        self.change_logo_btn = QPushButton("تغيير شعار التطبيق")
        self.change_logo_btn.clicked.connect(self.change_logo)
        layout.addWidget(self.change_logo_btn)
        
        # أيقونة التطبيق
        app_icon_title = QLabel("أيقونة التطبيق:")
        app_icon_title.setStyleSheet("font-weight: bold; margin-top: 20px;")
        layout.addWidget(app_icon_title)
        
        self.app_icon_label = QLabel()
        self.app_icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.app_icon_label.setMinimumHeight(64)
        layout.addWidget(self.app_icon_label)
        
        # زر تغيير أيقونة التطبيق
        self.change_app_icon_btn = QPushButton("تغيير أيقونة التطبيق")
        self.change_app_icon_btn.clicked.connect(self.change_app_icon)
        layout.addWidget(self.change_app_icon_btn)
        
        # زر استعادة الأيقونات الافتراضية
        self.restore_default_btn = QPushButton("استعادة الأيقونات الافتراضية")
        self.restore_default_btn.clicked.connect(self.restore_default_icons)
        layout.addWidget(self.restore_default_btn)
        
        # حالة الأيقونات
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: gray; font-style: italic;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # تحميل الشعارات الحالية
        self.load_current_icons()
    
    def load_current_icons(self):
        """تحميل وعرض الشعارات الحالية"""
        # تحميل شعار التطبيق
        if os.path.exists(self.logo_path):
            pixmap = QPixmap(self.logo_path)
            if not pixmap.isNull():
                self.logo_label.setPixmap(pixmap.scaledToHeight(100, Qt.TransformationMode.SmoothTransformation))
            else:
                self.logo_label.setText("(الشعار غير متوفر)")
        else:
            self.logo_label.setText("(الشعار غير متوفر)")
        
        # تحميل أيقونة التطبيق
        if os.path.exists(self.app_icon_path):
            pixmap = QPixmap(self.app_icon_path)
            if not pixmap.isNull():
                self.app_icon_label.setPixmap(pixmap.scaledToHeight(64, Qt.TransformationMode.SmoothTransformation))
            else:
                self.app_icon_label.setText("(الأيقونة غير متوفرة)")
        else:
            self.app_icon_label.setText("(الأيقونة غير متوفرة)")
        
        # عرض حالة الأيقونات (مخصصة أو افتراضية)
        if self._are_icons_customized():
            self.status_label.setText("* تم تخصيص الأيقونات *")
        else:
            self.status_label.setText("الأيقونات الافتراضية")
    
    def _are_icons_customized(self):
        """التحقق مما إذا كانت الأيقونات مخصصة أم لا"""
        # التحقق من وجود ملفات الأيقونات الافتراضية المحفوظة
        backup_logo = os.path.join(self.backup_dir, "logo.png")
        backup_app_icon = os.path.join(self.backup_dir, "app_icon.png")
        
        return os.path.exists(backup_logo) or os.path.exists(backup_app_icon)
    
    def _backup_icon(self, icon_name):
        """إنشاء نسخة احتياطية من الأيقونة الافتراضية"""
        original_path = os.path.join(self.icons_dir, f"{icon_name}.png")
        backup_path = os.path.join(self.backup_dir, f"{icon_name}.png")
        
        # إذا لم توجد نسخة احتياطية بالفعل وكانت الأيقونة موجودة، قم بإنشاء نسخة
        if not os.path.exists(backup_path) and os.path.exists(original_path):
            try:
                shutil.copy2(original_path, backup_path)
                return True
            except Exception as e:
                print(f"خطأ في إنشاء نسخة احتياطية من {icon_name}: {e}")
        
        return False
    
    def change_logo(self):
        """تغيير شعار التطبيق"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "اختر شعار التطبيق", "", "صور (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            try:
                # عمل نسخة احتياطية من الأيقونة الافتراضية
                self._backup_icon("logo")
                
                # نسخ الملف إلى مجلد الأيقونات
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    pixmap.save(self.logo_path)
                    self.load_current_icons()
                    QMessageBox.information(self, "نجاح", "تم تغيير شعار التطبيق بنجاح!")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تغيير الشعار: {str(e)}")
    
    def change_app_icon(self):
        """تغيير أيقونة التطبيق"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "اختر أيقونة التطبيق", "", "صور (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            try:
                # عمل نسخة احتياطية من الأيقونة الافتراضية
                self._backup_icon("app_icon")
                
                # نسخ الملف إلى مجلد الأيقونات
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    pixmap.save(self.app_icon_path)
                    self.load_current_icons()
                    QMessageBox.information(self, "نجاح", "تم تغيير أيقونة التطبيق بنجاح!")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تغيير الأيقونة: {str(e)}")
    
    def restore_default_icons(self):
        """استعادة الأيقونات الافتراضية"""
        try:
            # التحقق من وجود نسخ احتياطية للأيقونات الافتراضية
            backup_logo = os.path.join(self.backup_dir, "logo.png")
            backup_app_icon = os.path.join(self.backup_dir, "app_icon.png")
            
            restored = False
            
            # استعادة الأيقونات من النسخ الاحتياطية إن وجدت
            if os.path.exists(backup_logo):
                shutil.copy2(backup_logo, self.logo_path)
                os.remove(backup_logo)
                restored = True
            
            if os.path.exists(backup_app_icon):
                shutil.copy2(backup_app_icon, self.app_icon_path)
                os.remove(backup_app_icon)
                restored = True
            
            # إذا لم تتم الاستعادة، حاول إنشاء أيقونات افتراضية جديدة
            if not restored:
                # أولاً نحاول تنزيل الشعارات من الإنترنت
                try:
                    from download_arabic_logo import download_icons
                    if download_icons():
                        self.load_current_icons()
                        QMessageBox.information(self, "نجاح", "تم استعادة الأيقونات الافتراضية من الإنترنت بنجاح!")
                        return
                except Exception as e:
                    print(f"فشل تنزيل الأيقونات من الإنترنت: {e}")
                
                # إذا فشل التنزيل، نقوم بإنشاء أيقونات افتراضية
                try:
                    from create_default_icons import create_default_icons
                    if create_default_icons():
                        self.load_current_icons()
                        QMessageBox.information(self, "نجاح", "تم إنشاء أيقونات افتراضية جديدة بنجاح!")
                        return
                except Exception as e:
                    print(f"فشل إنشاء الأيقونات الافتراضية: {e}")
                
                # إذا فشلت جميع المحاولات السابقة
                QMessageBox.warning(self, "تحذير", "تعذر استعادة الأيقونات الافتراضية. تأكد من اتصال الإنترنت أو قم بتثبيت الحزم المطلوبة.")
            else:
                self.load_current_icons()
                QMessageBox.information(self, "نجاح", "تمت استعادة الأيقونات الافتراضية بنجاح!")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء استعادة الأيقونات الافتراضية: {str(e)}")

def main():
    """الدالة الرئيسية"""
    app = QApplication(sys.argv)
    window = LogoManagerWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

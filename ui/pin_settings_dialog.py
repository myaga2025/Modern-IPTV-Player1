from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QCheckBox, QMessageBox, QApplication)
from PyQt6.QtCore import Qt
from ui.pin_dialog import PinDialog
from core.language_manager import tr
import os

class PinSettingsDialog(QDialog):
    """مربع حوار إعدادات قفل التطبيق"""
    
    def __init__(self, pin_manager, parent=None):
        super().__init__(parent)
        self.pin_manager = pin_manager
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # تعيين العنوان والحجم
        self.setWindowTitle(tr("App Lock Settings"))
        self.setMinimumSize(500, 300)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        # الحصول على السمة الحالية للتطبيق
        app = QApplication.instance()
        is_dark_theme = app.styleSheet() and "background-color: #121212" in app.styleSheet()
        
        # تحديد الألوان بناءً على السمة
        text_color = "#FFFFFF" if is_dark_theme else "#000000"
        secondary_text = "#CCCCCC" if is_dark_theme else "#555555"
        border_color = "#555555" if is_dark_theme else "#AAAAAA"
        bg_color = "#333333" if is_dark_theme else "#F0F0F0"
        button_bg = "#444444" if is_dark_theme else "#E0E0E0"
        button_hover = "#555555" if is_dark_theme else "#D0D0D0"
        accent_color = "#0078D7"  # الأزرق لكلا السمتين
        warning_color = "#FF5252"
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # عنوان مربع الحوار
        title_label = QLabel(tr("App Lock Settings"))
        title_label.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {text_color};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # شرح الميزة
        description_label = QLabel(tr("Lock the app with a PIN code to prevent unauthorized access. "
                                  "You will be asked to enter your PIN each time you open the app."))
        description_label.setWordWrap(True)
        description_label.setStyleSheet(f"font-size: 15px; color: {secondary_text};")
        main_layout.addWidget(description_label)
        
        # خط فاصل بصري
        separator = QLabel("")
        separator.setStyleSheet(f"background-color: {border_color}; min-height: 1px; max-height: 1px;")
        main_layout.addWidget(separator)
        
        # خيار تفعيل/تعطيل القفل
        self.enable_checkbox = QCheckBox(tr("Enable PIN Lock"))
        self.enable_checkbox.setChecked(self.pin_manager.is_pin_enabled())
        self.enable_checkbox.toggled.connect(self.toggle_pin_lock)
        self.enable_checkbox.setStyleSheet(f"""
            QCheckBox {{
                font-size: 16px; 
                font-weight: bold;
                color: {text_color};
                spacing: 10px;
            }}
            QCheckBox::indicator {{
                width: 20px;
                height: 20px;
            }}
        """)
        main_layout.addWidget(self.enable_checkbox)
        
        # أزرار إدارة الرمز السري
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # زر إنشاء/تغيير الرمز
        self.change_pin_button = QPushButton(tr("Change PIN"))
        self.change_pin_button.setEnabled(self.pin_manager.is_pin_enabled())
        self.change_pin_button.clicked.connect(self.change_pin)
        
        # زر إلغاء تفعيل الرمز
        self.disable_pin_button = QPushButton(tr("Disable PIN Lock"))
        self.disable_pin_button.setEnabled(self.pin_manager.is_pin_enabled())
        self.disable_pin_button.clicked.connect(self.disable_pin)
        
        # تنسيق الأزرار
        button_style = f"""
            QPushButton {{
                background-color: {button_bg};
                color: {text_color};
                border: 1px solid {border_color};
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 15px;
            }}
            QPushButton:hover {{
                background-color: {button_hover};
            }}
            QPushButton:pressed {{
                background-color: {accent_color};
                color: white;
            }}
            QPushButton:disabled {{
                background-color: {button_bg};
                color: {border_color};
            }}
        """
        
        self.change_pin_button.setStyleSheet(button_style)
        self.disable_pin_button.setStyleSheet(button_style)
        
        buttons_layout.addWidget(self.change_pin_button)
        buttons_layout.addWidget(self.disable_pin_button)
        
        main_layout.addLayout(buttons_layout)
        
        # إضافة مساحة فارغة
        main_layout.addStretch()
        
        # تحذير أمان
        security_label = QLabel(tr("⚠️ Security Note: If you forget your PIN, you will need to reinstall the application."))
        security_label.setStyleSheet(f"font-size: 14px; color: {warning_color};")
        security_label.setWordWrap(True)
        main_layout.addWidget(security_label)
        
        # أزرار الإغلاق
        close_layout = QHBoxLayout()
        close_button = QPushButton(tr("Close"))
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: white;
                border: 1px solid {accent_color};
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 15px;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: #006cc1;
            }}
            QPushButton:pressed {{
                background-color: #005bb1;
            }}
        """)
        
        close_layout.addStretch()
        close_layout.addWidget(close_button)
        
        main_layout.addLayout(close_layout)
    
    def toggle_pin_lock(self, checked):
        """تفعيل أو تعطيل قفل التطبيق"""
        if checked:
            # تفعيل القفل - إنشاء رمز جديد
            self.create_new_pin()
        else:
            # تعطيل القفل - يتطلب التحقق من الرمز الحالي أولاً
            self.verify_then_disable()
            
        # تحديث حالة الأزرار
        self.update_button_states()
    
    def create_new_pin(self):
        """إنشاء رمز سري جديد"""
        # فتح مربع حوار إنشاء رمز جديد
        pin_dialog = PinDialog(self, verification_mode=False)
        if pin_dialog.exec():
            # تم إنشاء رمز جديد
            new_pin = pin_dialog.get_pin()
            if new_pin:
                success = self.pin_manager.set_pin(new_pin, True)
                if success:
                    QMessageBox.information(self, tr("Success"), tr("App lock has been enabled and a new PIN has been set."))
                else:
                    QMessageBox.critical(self, tr("Error"), tr("An error occurred while enabling app lock."))
                    self.enable_checkbox.setChecked(False)
        else:
            # تم إلغاء إنشاء الرمز
            self.enable_checkbox.setChecked(False)
    
    def change_pin(self):
        """تغيير الرمز السري"""
        # التحقق من الرمز الحالي أولاً
        verify_dialog = PinDialog(self, verification_mode=True)
        if verify_dialog.exec():
            current_pin = verify_dialog.get_pin()
            
            # التحقق من صحة الرمز الحالي
            if self.pin_manager.verify_pin(current_pin):
                # إنشاء رمز جديد
                new_pin_dialog = PinDialog(self, verification_mode=False)
                if new_pin_dialog.exec():
                    new_pin = new_pin_dialog.get_pin()
                    if self.pin_manager.change_pin(current_pin, new_pin):
                        QMessageBox.information(self, tr("Success"), tr("PIN has been changed successfully."))
                    else:
                        QMessageBox.critical(self, tr("Error"), tr("An error occurred while changing the PIN."))
            else:
                QMessageBox.warning(self, tr("Error"), tr("The current PIN is incorrect."))
    
    def verify_then_disable(self):
        """التحقق من الرمز الحالي قبل تعطيل القفل"""
        # إذا كان القفل مفعلاً بالفعل، فنحتاج إلى التحقق من الرمز أولاً
        if self.pin_manager.is_pin_enabled():
            verify_dialog = PinDialog(self, verification_mode=True)
            if verify_dialog.exec():
                current_pin = verify_dialog.get_pin()
                
                # التحقق من صحة الرمز
                if self.pin_manager.verify_pin(current_pin):
                    self.disable_pin()
                else:
                    QMessageBox.warning(self, tr("Error"), tr("The PIN is incorrect."))
                    self.enable_checkbox.setChecked(True)  # إعادة تحديد الخيار
            else:
                # تم إلغاء التحقق
                self.enable_checkbox.setChecked(True)  # إعادة تحديد الخيار
    
    def disable_pin(self):
        """تعطيل قفل التطبيق"""
        if self.pin_manager.disable_pin():
            QMessageBox.information(self, tr("Success"), tr("App lock has been disabled."))
            self.enable_checkbox.setChecked(False)
        else:
            QMessageBox.critical(self, tr("Error"), tr("An error occurred while disabling app lock."))
            self.enable_checkbox.setChecked(True)
            
        # تحديث حالة الأزرار
        self.update_button_states()
    
    def update_button_states(self):
        """تحديث حالة الأزرار بناءً على حالة تفعيل القفل"""
        is_enabled = self.pin_manager.is_pin_enabled()
        self.change_pin_button.setEnabled(is_enabled)
        self.disable_pin_button.setEnabled(is_enabled)

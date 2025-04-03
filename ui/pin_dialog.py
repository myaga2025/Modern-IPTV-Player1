from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QLineEdit, QApplication)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import os
from core.language_manager import tr

class PinDialog(QDialog):
    """مربع حوار إدخال الرمز السري"""
    
    def __init__(self, parent=None, verification_mode=True):
        """
        تهيئة مربع حوار الرمز السري
        verification_mode: إذا كان True، فسيكون للتحقق من الرمز. وإذا كان False، فسيكون لإنشاء رمز جديد.
        """
        super().__init__(parent)
        self.verification_mode = verification_mode
        self.pin = ""
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # تعيين العنوان والحجم
        title = tr("App Lock") if self.verification_mode else tr("Create PIN Code")
        self.setWindowTitle(title)
        self.setFixedSize(400, 240)  # تقليل الحجم للواجهة المبسطة
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        # الحصول على السمة الحالية للتطبيق
        app = QApplication.instance()
        is_dark_theme = app and app.styleSheet() and "background-color: #121212" in app.styleSheet()
        
        # تحديد الألوان بناءً على السمة
        text_color = "#FFFFFF" if is_dark_theme else "#000000"
        input_bg_color = "#444444" if is_dark_theme else "#FFFFFF"
        button_bg = "#444444" if is_dark_theme else "#E0E0E0"
        button_hover = "#555555" if is_dark_theme else "#D0D0D0"
        accent_color = "#0078D7"  # الأزرق لكلا السمتين
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(30, 30, 30, 30)
        
        # عنوان مربع الحوار
        title_text = tr("Enter PIN code to continue") if self.verification_mode else tr("Create new PIN code")
        title_label = QLabel(title_text)
        title_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {text_color};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # حقول إدخال الرقم السري
        pin_layout = QHBoxLayout()
        pin_layout.setSpacing(15)
        pin_layout.setContentsMargins(10, 5, 10, 5)
        
        self.pin_digits = []
        for i in range(4):
            digit_input = QLineEdit()
            digit_input.setMaxLength(1)
            digit_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
            digit_input.setFixedSize(60, 60)  # تصغير حجم حقول الإدخال
            digit_input.setStyleSheet(f"""
                QLineEdit {{
                    font-size: 26px;
                    font-weight: bold;
                    border: 2px solid {accent_color};
                    border-radius: 8px;
                    background-color: {input_bg_color};
                    color: {text_color};
                }}
                QLineEdit:focus {{
                    border: 3px solid {accent_color};
                }}
            """)
            
            self.pin_digits.append(digit_input)
            pin_layout.addWidget(digit_input)
            
            digit_input.textChanged.connect(lambda text, idx=i: self.on_digit_changed(text, idx))
        
        main_layout.addLayout(pin_layout)
        
        # رسائل الحالة
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("font-size: 14px; color: #FF5252; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setMinimumHeight(20)
        main_layout.addWidget(self.status_label)
        
        main_layout.addStretch()
        
        # أزرار التحكم
        button_layout = QHBoxLayout()
        
        # زر الإلغاء
        self.cancel_button = QPushButton(tr("Cancel"))
        self.cancel_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {button_bg};
                color: {text_color};
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {button_hover};
            }}
        """)
        self.cancel_button.clicked.connect(self.reject)
        
        # زر التأكيد
        button_text = tr("Unlock") if self.verification_mode else tr("Create PIN")
        self.ok_button = QPushButton(button_text)
        self.ok_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent_color};
                color: white;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: #006cc1;
            }}
        """)
        self.ok_button.clicked.connect(self.validate_pin)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        
        main_layout.addLayout(button_layout)
        
        # تركيز على الخانة الأولى
        if self.pin_digits:
            self.pin_digits[0].setFocus()
    
    def on_digit_changed(self, text, index):
        """معالجة تغيير رقم في الرمز السري"""
        # قبول الأرقام فقط
        if text and not text.isdigit():
            self.pin_digits[index].clear()
            return
            
        if text:
            # تحديث الرمز السري
            while len(self.pin) <= index:
                self.pin += " "
            
            self.pin = self.pin[:index] + text + self.pin[index+1:]
            
            # الانتقال إلى الخانة التالية إذا كان هناك خانة تالية
            if index < 3:
                self.pin_digits[index + 1].setFocus()
            else:
                # إذا كانت هذه آخر خانة، ننفذ التحقق مباشرة
                self.validate_pin()
        else:
            # عند المسح، نحدث الرمز
            if len(self.pin) > index:
                self.pin = self.pin[:index] + " " + self.pin[index+1:]
    
    def validate_pin(self):
        """التحقق من صحة الرمز السري المدخل"""
        pin = self.pin.strip()
        
        if len(pin) != 4:
            self.status_label.setText(tr("Please enter a 4-digit PIN code"))
            return
            
        # كل شيء بخير، نقبل الحوار
        self.pin = pin
        self.accept()
    
    def keyPressEvent(self, event):
        """معالجة أحداث الضغط على المفاتيح"""
        # معالجة زر Backspace للتنقل بين الخانات
        if event.key() == Qt.Key.Key_Backspace:
            focused_widget = self.focusWidget()
            if isinstance(focused_widget, QLineEdit):
                if not focused_widget.text():
                    if focused_widget in self.pin_digits:
                        current_index = self.pin_digits.index(focused_widget)
                        if current_index > 0:
                            self.pin_digits[current_index - 1].setFocus()
                            self.pin_digits[current_index - 1].clear()
        
        # معالجة مفاتيح الأسهم للتنقل بين الخانات
        elif event.key() == Qt.Key.Key_Left:
            focused_widget = self.focusWidget()
            if isinstance(focused_widget, QLineEdit) and focused_widget in self.pin_digits:
                current_index = self.pin_digits.index(focused_widget)
                if current_index > 0:
                    self.pin_digits[current_index - 1].setFocus()
        
        elif event.key() == Qt.Key.Key_Right:
            focused_widget = self.focusWidget()
            if isinstance(focused_widget, QLineEdit) and focused_widget in self.pin_digits:
                current_index = self.pin_digits.index(focused_widget)
                if current_index < 3:
                    self.pin_digits[current_index + 1].setFocus()
        
        # معالجة زر الإدخال
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.validate_pin()
        
        # معالجة زر الهروب
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        
        # معالجة الأرقام مباشرة
        elif event.key() >= Qt.Key.Key_0 and event.key() <= Qt.Key.Key_9:
            focused_widget = self.focusWidget()
            if isinstance(focused_widget, QLineEdit):
                digit = event.text()
                focused_widget.setText(digit)
        else:
            super().keyPressEvent(event)
    
    def get_pin(self):
        """استرجاع الرمز السري المدخل"""
        return self.pin.strip()

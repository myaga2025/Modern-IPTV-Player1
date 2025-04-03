from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QPixmap, QIcon
import os
from core.language_manager import tr

class ComingSoonWidget(QWidget):
    """واجهة عرض للميزات القادمة قريبًا مع علامة 'معطل'"""
    
    def __init__(self, feature_type="series", parent=None):
        """
        تهيئة واجهة الميزات القادمة
        
        Args:
            feature_type: نوع الميزة ("series", "movies", "generic")
            parent: العنصر الأصل
        """
        super().__init__(parent)
        self.feature_type = feature_type
        
        # إعداد واجهة المستخدم
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # الحصول على ألوان السمة
        app_stylesheet = self.parent().styleSheet() if self.parent() else ""
        is_dark_theme = "background-color: #121212" in app_stylesheet
        text_color = "#FFFFFF" if is_dark_theme else "#333333"
        
        # محاولة تحميل صورة معطل/قريبًا
        disabled_icon = None
        try:
            icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   "resources", "icons", "soon_badge.png")
            if os.path.exists(icon_path):
                self.disabled_image = QPixmap(icon_path)
            else:
                self.disabled_image = None
        except:
            self.disabled_image = None
            
        # ملصق قريباً (SOON)
        self.soon_label = QLabel(tr("COMING SOON"))
        font = QFont("Arial", 36, QFont.Weight.Bold)
        self.soon_label.setFont(font)
        self.soon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.soon_label.setStyleSheet(f"""
            color: #0078D7;
            font-weight: bold;
        """)
        main_layout.addWidget(self.soon_label)
        
        # ملصق معطل باللون الأحمر
        self.disabled_label = QLabel(tr("DISABLED"))
        disabled_font = QFont("Arial", 24, QFont.Weight.Bold)
        self.disabled_label.setFont(disabled_font)
        self.disabled_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.disabled_label.setStyleSheet("""
            color: #FF3333;
            font-weight: bold;
            background-color: rgba(255, 51, 51, 0.1);
            border: 2px solid #FF3333;
            border-radius: 10px;
            padding: 10px;
        """)
        main_layout.addWidget(self.disabled_label)
        
        # عنوان الميزة
        title = ""
        if self.feature_type == "series":
            title = tr("Series Feature is Currently Disabled")
        elif self.feature_type == "movies":
            title = tr("Movies Feature is Currently Disabled")
        else:
            title = tr("Feature is Currently Disabled")
            
        self.title_label = QLabel(title)
        title_font = QFont("Arial", 18)
        self.title_label.setFont(title_font)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(f"color: {text_color};")
        main_layout.addWidget(self.title_label)
        
        # وصف الميزة
        description = ""
        if self.feature_type == "series":
            description = tr("Series feature has been temporarily disabled. It will be available in a future update. Thank you for your patience.")
        elif self.feature_type == "movies":
            description = tr("Movies feature has been temporarily disabled. It will be available in a future update.")
        else:
            description = tr("This feature has been temporarily disabled. It will be available in a future update.")
        
        self.desc_label = QLabel(description)
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.desc_label.setStyleSheet(f"color: {text_color};")
        main_layout.addWidget(self.desc_label)
        
    def paintEvent(self, event):
        """رسم خلفية مخصصة للواجهة"""
        super().paintEvent(event)
        
        # رسم خلفية شفافة مميزة
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # رسم دوائر زينة في الخلفية
        painter.save()
        
        accent_color = QColor("#0078D7")
        accent_color.setAlpha(30)  # شفافية عالية
        
        # رسم بعض الدوائر بأحجام مختلفة
        painter.setBrush(accent_color)
        painter.setPen(Qt.PenStyle.NoPen)
        
        # دائرة علوية يمنى - استخدام QRectF لتمرير القيم العشرية بشكل صحيح
        circle_size = min(self.width(), self.height()) * 0.5
        top_right_rect = QRectF(
            self.width() - circle_size * 0.7, 
            -circle_size * 0.3, 
            circle_size, 
            circle_size
        )
        painter.drawEllipse(top_right_rect)
        
        # دائرة سفلية يسرى - استخدام QRectF لتمرير القيم العشرية بشكل صحيح
        circle_size = min(self.width(), self.height()) * 0.4
        bottom_left_rect = QRectF(
            -circle_size * 0.3, 
            self.height() - circle_size * 0.7, 
            circle_size, 
            circle_size
        )
        painter.drawEllipse(bottom_left_rect)
        
        # إذا كانت الصورة موجودة، نرسمها
        if hasattr(self, 'disabled_image') and self.disabled_image:
            badge_width = self.disabled_image.width()
            badge_height = self.disabled_image.height()
            painter.drawPixmap(
                int((self.width() - badge_width) // 2), 
                int((self.height() - badge_height) // 2 - 100), 
                self.disabled_image
            )
        
        painter.restore()

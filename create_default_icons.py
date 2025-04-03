#!/usr/bin/env python3
"""
أداة لإنشاء أيقونات افتراضية للتطبيق
في حالة عدم القدرة على تنزيل الأيقونات من الإنترنت
"""
import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QPainter, QBrush, QFont, QColor, QPen
from PyQt6.QtCore import Qt, QRect, QSize

def create_icon(filename, text, size=128, bg_color="#1e1e1e", text_color="#ffffff"):
    """إنشاء أيقونة بسيطة مع نص"""
    pixmap = QPixmap(size, size)
    pixmap.fill(QColor(bg_color))
    
    painter = QPainter(pixmap)
    painter.setPen(QPen(QColor(text_color)))
    painter.setBrush(QBrush(QColor(text_color)))
    
    # استخدم خط بحجم مناسب
    font = QFont("Arial", size // 4)
    font.setBold(True)
    painter.setFont(font)
    
    # رسم النص في وسط الأيقونة
    painter.drawText(QRect(0, 0, size, size), Qt.AlignmentFlag.AlignCenter, text)
    
    # إذا كان النص يحتوي على "play" أو "تشغيل"، ارسم مثلث
    if "play" in text.lower() or "تشغيل" in text:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(text_color)))
        
        # رسم مثلث التشغيل
        points = [
            (size//4, size//4),
            (size//4, size*3//4),
            (size*3//4, size//2)
        ]
        painter.drawPolygon([QPoint(x, y) for x, y in points])
    
    # إذا كان النص يحتوي على "pause" أو "إيقاف"، ارسم شريطين متوازيين
    elif "pause" in text.lower() or "إيقاف" in text:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(text_color)))
        
        # رسم شريطي الإيقاف المؤقت
        painter.drawRect(size//4, size//4, size//6, size//2)
        painter.drawRect(size*7//12, size//4, size//6, size//2)
    
    # إذا كان النص يحتوي على "stop" أو "إيقاف"، ارسم مربع
    elif "stop" in text.lower() or "إيقاف" in text:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(text_color)))
        
        # رسم مربع الإيقاف
        painter.drawRect(size//3, size//3, size//3, size//3)
    
    # إذا كان النص يحتوي على "volume" أو "صوت"، ارسم رمز الصوت
    elif "volume" in text.lower() or "صوت" in text:
        painter.setPen(QPen(QColor(text_color), 2))
        painter.setBrush(QBrush(QColor(text_color)))
        
        # رسم رمز السماعة
        points = [
            (size//4, size*2//5),
            (size*3//8, size*2//5),
            (size//2, size//3),
            (size//2, size*2//3),
            (size*3//8, size*3//5),
            (size//4, size*3//5)
        ]
        painter.drawPolygon([QPoint(x, y) for x, y in points])
        
        # رسم موجات الصوت
        painter.setPen(QPen(QColor(text_color), 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawArc(size//2, size//3, size//6, size//3, 60*16, 240*16)
        painter.drawArc(size*4//7, size//4, size//4, size//2, 60*16, 240*16)
    
    painter.end()
    
    # حفظ الصورة
    return pixmap.save(filename)

def create_default_icons():
    """إنشاء الأيقونات الافتراضية"""
    print("جاري إنشاء الأيقونات الافتراضية...")
    
    # تأكد من وجود المجلد
    icons_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "icons")
    os.makedirs(icons_dir, exist_ok=True)
    
    # قائمة الأيقونات التي يجب إنشاؤها
    icons = {
        "app_icon": "IPTV",
        "logo": "IPTV",
        "play": "▶",
        "pause": "⏸",
        "stop": "■",
        "volume": "🔊"
    }
    
    success_count = 0
    
    # إنشاء كل أيقونة
    for name, text in icons.items():
        icon_path = os.path.join(icons_dir, f"{name}.png")
        
        # تخطي الأيقونة إذا كانت موجودة بالفعل
        if os.path.exists(icon_path):
            print(f"الأيقونة {name}.png موجودة بالفعل، تم تخطيها.")
            success_count += 1
            continue
        
        try:
            # إنشاء أيقونة افتراضية
            size = 128
            if name == "app_icon":
                size = 256  # حجم أكبر لأيقونة التطبيق
            
            if create_icon(icon_path, text, size):
                print(f"تم إنشاء {name}.png بنجاح")
                success_count += 1
            else:
                print(f"فشل إنشاء {name}.png")
        except Exception as e:
            print(f"خطأ أثناء إنشاء {name}.png: {e}")
    
    return success_count == len(icons)

def main():
    """الدالة الرئيسية"""
    # إنشاء تطبيق PyQt (مطلوب لرسم الأيقونات)
    app = QApplication(sys.argv)
    
    success = create_default_icons()
    
    if success:
        print("\nتم إنشاء جميع الأيقونات بنجاح.")
    else:
        print("\nلم يتم إنشاء بعض الأيقونات.")
    
    print("\nيمكنك الآن تشغيل البرنامج وسترى الأيقونات الافتراضية.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

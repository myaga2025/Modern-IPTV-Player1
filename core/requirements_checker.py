import os
import sys
import time
import threading
import platform
from PyQt6.QtWidgets import (QDialog, QProgressBar, QLabel, QVBoxLayout,
                           QHBoxLayout, QPushButton, QApplication, QMessageBox)
from PyQt6.QtCore import QTimer, pyqtSignal, Qt
from PyQt6.QtGui import QPixmap, QIcon

class RequirementsChecker:
    """فحص توفر متطلبات التشغيل وعرض روابط التنزيل إذا لزم الأمر"""

    @staticmethod
    def check_vlc():
        """التحقق من وجود VLC"""
        try:
            import vlc
            return True, None
        except (ImportError, OSError) as e:
            # إرجاع رابط التنزيل المناسب حسب نظام التشغيل
            system = platform.system()
            if system == "Windows":
                python_arch = "64bit" if sys.maxsize > 2**32 else "32bit"
                vlc_arch = "64bit" if python_arch == "64bit" else "32bit"
                return False, f"https://www.videolan.org/vlc/download-windows.html (يجب تنزيل إصدار {vlc_arch})"
            elif system == "Darwin":  # macOS
                return False, "https://www.videolan.org/vlc/download-macosx.html"
            else:  # Linux
                return False, "استخدم مدير حزم النظام لديك لتثبيت VLC"

    @staticmethod
    def check_pyqt():
        """التحقق من توفر PyQt6"""
        try:
            # نحن نستخدم هذه المكتبة بالفعل لعرض النافذة، لذا يجب أن تكون موجودة
            return True, None
        except Exception:
            return False, "https://pypi.org/project/PyQt6/"

    @staticmethod
    def check_other_dependencies():
        """التحقق من المكتبات الأخرى المطلوبة"""
        # هنا يمكنك إضافة فحص لأي متطلبات أخرى للتطبيق
        # على سبيل المثال: requests, numpy, etc.
        dependencies = {
            "requests": "https://pypi.org/project/requests/",
            # يمكنك إضافة المزيد من المكتبات هنا
        }
        
        missing = {}
        for lib, url in dependencies.items():
            try:
                __import__(lib)
            except ImportError:
                missing[lib] = url
        
        if missing:
            return False, missing
        return True, None


class RequirementsDialog(QDialog):
    """نافذة تعرض تقدم فحص المتطلبات"""
    
    # إشارة لإخبار النافذة الرئيسية بنتائج الفحص
    check_complete = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("فحص متطلبات النظام")
        self.setMinimumWidth(500)
        self.setModal(True)
        self.checker = RequirementsChecker()
        
        # نتائج الفحص
        self.results = {}
        
        # إعداد واجهة المستخدم
        self._setup_ui()
        
        # بدء الفحص بعد فتح النافذة
        QTimer.singleShot(100, self.start_checks)
    
    def _setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QVBoxLayout(self)
        
        # إضافة شعار التطبيق إذا وجد
        try:
            logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                    "resources", "icons", "app_icon.png")
            if os.path.exists(logo_path):
                logo_label = QLabel()
                pixmap = QPixmap(logo_path)
                logo_label.setPixmap(pixmap.scaledToWidth(100, Qt.TransformationMode.SmoothTransformation))
                logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(logo_label)
        except Exception:
            pass
        
        # العنوان
        title_label = QLabel("جاري فحص متطلبات النظام...")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 15px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # مؤشر التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # حالة الفحص الحالي
        self.status_label = QLabel("بدء الفحص...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # زر الإغلاق (مخفي في البداية)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.close_button = QPushButton("إغلاق")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setVisible(False)  # سيظهر هذا الزر بعد اكتمال الفحص
        button_layout.addWidget(self.close_button)
        
        # زر التنزيل (مخفي في البداية)
        self.download_button = QPushButton("تنزيل المتطلبات")
        self.download_button.clicked.connect(self.open_download_links)
        self.download_button.setVisible(False)  # سيظهر هذا الزر إذا كانت هناك متطلبات مفقودة
        button_layout.addWidget(self.download_button)
        
        layout.addLayout(button_layout)
    
    def start_checks(self):
        """بدء فحوصات المتطلبات في خيط منفصل"""
        self.thread = threading.Thread(target=self.run_checks)
        self.thread.daemon = True
        self.thread.start()
    
    def run_checks(self):
        """تنفيذ فحوصات المتطلبات"""
        # فحص VLC
        self.update_status("جاري فحص توفر برنامج VLC...", 10)
        time.sleep(1)  # تأخير قصير للتأثير البصري
        vlc_ok, vlc_link = self.checker.check_vlc()
        self.results["VLC"] = {"ok": vlc_ok, "link": vlc_link}
        
        # فحص PyQt
        self.update_status("جاري فحص توفر PyQt6...", 40)
        time.sleep(0.5)
        pyqt_ok, pyqt_link = self.checker.check_pyqt()
        self.results["PyQt6"] = {"ok": pyqt_ok, "link": pyqt_link}
        
        # فحص المتطلبات الأخرى
        self.update_status("جاري فحص المتطلبات الأخرى...", 70)
        time.sleep(0.5)
        other_ok, other_links = self.checker.check_other_dependencies()
        self.results["other"] = {"ok": other_ok, "links": other_links}
        
        # إكمال الفحص
        self.update_status("اكتمل الفحص", 100)
        
        # التحقق من وجود أية متطلبات مفقودة
        self.missing_requirements = []
        
        if not self.results["VLC"]["ok"]:
            self.missing_requirements.append(("VLC", self.results["VLC"]["link"]))
        
        if not self.results["PyQt6"]["ok"]:
            self.missing_requirements.append(("PyQt6", self.results["PyQt6"]["link"]))
        
        if not self.results["other"]["ok"] and isinstance(self.results["other"]["links"], dict):
            for lib, link in self.results["other"]["links"].items():
                self.missing_requirements.append((lib, link))
        
        # تحديث واجهة المستخدم في الخيط الرئيسي
        QApplication.instance().postEvent(self, _UpdateUIEvent(self.missing_requirements))
        
        # إرسال النتائج للنافذة الرئيسية
        self.check_complete.emit(self.results)
    
    def update_status(self, message, progress):
        """تحديث حالة الفحص في واجهة المستخدم"""
        QApplication.instance().postEvent(self, _StatusUpdateEvent(message, progress))
    
    def open_download_links(self):
        """عرض روابط تنزيل المتطلبات المفقودة"""
        if not self.missing_requirements:
            return
        
        message = "المتطلبات التالية مفقودة. يرجى تثبيتها قبل استخدام التطبيق:\n\n"
        
        for req, link in self.missing_requirements:
            message += f"• {req}: {link}\n"
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("متطلبات مفقودة")
        msg_box.setText(message)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.exec()
    
    def show_and_wait(self):
        """عرض النافذة وانتظار اكتمال الفحص"""
        self.exec()
        return self.results
    
    def event(self, event):
        """معالجة الأحداث المخصصة"""
        if event.type() == _StatusUpdateEvent.TYPE:
            self.status_label.setText(event.message)
            self.progress_bar.setValue(event.progress)
            return True
        elif event.type() == _UpdateUIEvent.TYPE:
            self.close_button.setVisible(True)
            
            if event.missing_requirements:
                status = f"تم العثور على {len(event.missing_requirements)} متطلبات مفقودة"
                self.status_label.setText(status)
                self.download_button.setVisible(True)
            else:
                self.status_label.setText("جميع المتطلبات متوفرة")
            
            return True
        
        return super().event(event)


# أحداث مخصصة لتحديث واجهة المستخدم من الخيط الآخر
class _StatusUpdateEvent(QApplication.instance().Event):
    TYPE = QApplication.instance().registerEventType()
    
    def __init__(self, message, progress):
        super().__init__(_StatusUpdateEvent.TYPE)
        self.message = message
        self.progress = progress


class _UpdateUIEvent(QApplication.instance().Event):
    TYPE = QApplication.instance().registerEventType()
    
    def __init__(self, missing_requirements):
        super().__init__(_UpdateUIEvent.TYPE)
        self.missing_requirements = missing_requirements


def check_requirements(parent=None):
    """دالة للاستخدام المباشر للتحقق من المتطلبات"""
    dialog = RequirementsDialog(parent)
    results = dialog.show_and_wait()
    return results

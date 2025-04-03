from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                            QPushButton, QMessageBox, QListWidget, QListWidgetItem,
                            QDialogButtonBox, QTabWidget, QWidget, QComboBox)
from PyQt6.QtCore import Qt, pyqtSignal
import os
import sys
import traceback

class PlaylistDialog(QDialog):
    """مربع حوار حفظ وتحميل قوائم التشغيل"""
    
    playlist_selected = pyqtSignal(str)  # إشارة عند اختيار قائمة تشغيل
    
    def __init__(self, playlist_manager, parent=None, mode="save"):
        """
        تهيئة مربع حوار قوائم التشغيل
        mode: "save" للحفظ أو "load" للتحميل
        """
        super().__init__(parent)
        self.playlist_manager = playlist_manager
        self.mode = mode
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # تعيين عنوان مناسب للوضع
            if self.mode == "save":
                self.setWindowTitle("حفظ قائمة التشغيل")
            else:
                self.setWindowTitle("تحميل قائمة التشغيل")
                
            # إعداد الحجم
            self.resize(400, 300)
            
            # التخطيط الرئيسي
            main_layout = QVBoxLayout(self)
            
            # حقل الاسم (للحفظ فقط)
            if self.mode == "save":
                name_layout = QHBoxLayout()
                name_label = QLabel("اسم قائمة التشغيل:", self)
                self.name_edit = QLineEdit(self)
                name_layout.addWidget(name_label)
                name_layout.addWidget(self.name_edit)
                main_layout.addLayout(name_layout)
            
            # قائمة قوائم التشغيل المحفوظة
            playlists_label = QLabel("قوائم التشغيل المحفوظة:", self)
            main_layout.addWidget(playlists_label)
            
            self.playlists_list = QListWidget(self)
            main_layout.addWidget(self.playlists_list)
            
            # أزرار الإجراءات
            buttons_layout = QHBoxLayout()
            
            if self.mode == "save":
                self.save_button = QPushButton("حفظ", self)
                self.save_button.clicked.connect(self.save_playlist)
                buttons_layout.addWidget(self.save_button)
            else:
                self.load_button = QPushButton("تحميل", self)
                self.load_button.clicked.connect(self.load_playlist)
                buttons_layout.addWidget(self.load_button)
            
            self.delete_button = QPushButton("حذف", self)
            self.delete_button.clicked.connect(self.delete_playlist)
            buttons_layout.addWidget(self.delete_button)
            
            self.cancel_button = QPushButton("إلغاء", self)
            self.cancel_button.clicked.connect(self.reject)
            buttons_layout.addWidget(self.cancel_button)
            
            main_layout.addLayout(buttons_layout)
            
            # تحميل قائمة قوائم التشغيل
            self.load_playlists_list()
            
            # الاتصال بالإشارات
            self.playlists_list.itemClicked.connect(self.on_playlist_selected)
            
        except Exception as e:
            error_msg = traceback.format_exc()
            print(f"خطأ في إعداد واجهة المستخدم: {e}\n{error_msg}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء إعداد مربع الحوار: {str(e)}")
    
    def load_playlists_list(self):
        """تحميل قائمة قوائم التشغيل المحفوظة"""
        try:
            self.playlists_list.clear()
            
            playlists = self.playlist_manager.get_all_playlists()
            for playlist in playlists:
                item = QListWidgetItem(f"{playlist['name']} ({playlist['channel_count']} قناة)")
                item.setData(Qt.ItemDataRole.UserRole, playlist['filename'])
                self.playlists_list.addItem(item)
                
        except Exception as e:
            error_msg = traceback.format_exc()
            print(f"خطأ في تحميل قائمة قوائم التشغيل: {e}\n{error_msg}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل قوائم التشغيل: {str(e)}")
    
    def on_playlist_selected(self, item):
        """معالجة حدث اختيار قائمة تشغيل"""
        try:
            if item is None:
                return
                
            filename = item.data(Qt.ItemDataRole.UserRole)
            if self.mode == "save" and self.name_edit:
                # استخراج اسم قائمة التشغيل من الملف
                playlist_name = filename
                if playlist_name.endswith('.json'):
                    playlist_name = playlist_name[:-5]
                self.name_edit.setText(playlist_name)
                
        except Exception as e:
            error_msg = traceback.format_exc()
            print(f"خطأ في معالجة اختيار قائمة التشغيل: {e}\n{error_msg}")
    
    def save_playlist(self):
        """حفظ قائمة التشغيل"""
        try:
            if not hasattr(self, 'channels') or not self.channels:
                QMessageBox.warning(self, "تحذير", "لا توجد قنوات لحفظها!")
                return
                
            name = self.name_edit.text().strip()
            if not name:
                QMessageBox.warning(self, "تحذير", "الرجاء إدخال اسم لقائمة التشغيل!")
                return
                
            # التحقق مما إذا كانت قائمة التشغيل موجودة بالفعل
            selected_items = self.playlists_list.selectedItems()
            overwrite = False
            
            if selected_items and self.name_edit.text() == selected_items[0].text().split(" (")[0]:
                # تم تحديد قائمة موجودة بالفعل
                reply = QMessageBox.question(
                    self, 
                    "تأكيد الاستبدال", 
                    f"هل تريد استبدال قائمة التشغيل '{name}'؟",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    overwrite = True
                else:
                    return
            
            # حفظ قائمة التشغيل
            success, message = self.playlist_manager.save_playlist(name, self.channels, overwrite)
            
            if success:
                QMessageBox.information(self, "نجاح", message)
                self.load_playlists_list()  # تحديث القائمة
                self.accept()
            else:
                QMessageBox.warning(self, "خطأ", message)
                
        except Exception as e:
            error_msg = traceback.format_exc()
            print(f"خطأ في حفظ قائمة التشغيل: {e}\n{error_msg}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حفظ قائمة التشغيل: {str(e)}")
    
    def load_playlist(self):
        """تحميل قائمة التشغيل المحددة"""
        try:
            selected_items = self.playlists_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "تحذير", "الرجاء تحديد قائمة تشغيل!")
                return
                
            filename = selected_items[0].data(Qt.ItemDataRole.UserRole)
            
            # إرسال إشارة بإسم الملف المحدد
            self.playlist_selected.emit(filename)
            self.accept()
                
        except Exception as e:
            error_msg = traceback.format_exc()
            print(f"خطأ في تحميل قائمة التشغيل: {e}\n{error_msg}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء تحميل قائمة التشغيل: {str(e)}")
    
    def delete_playlist(self):
        """حذف قائمة التشغيل المحددة"""
        try:
            selected_items = self.playlists_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "تحذير", "الرجاء تحديد قائمة تشغيل للحذف!")
                return
                
            filename = selected_items[0].data(Qt.ItemDataRole.UserRole)
            playlist_name = selected_items[0].text().split(" (")[0]
            
            # تأكيد الحذف
            reply = QMessageBox.question(
                self, 
                "تأكيد الحذف", 
                f"هل أنت متأكد من حذف قائمة التشغيل '{playlist_name}'؟",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                success, message = self.playlist_manager.delete_playlist(filename)
                
                if success:
                    QMessageBox.information(self, "نجاح", message)
                    self.load_playlists_list()  # تحديث القائمة
                else:
                    QMessageBox.warning(self, "خطأ", message)
                
        except Exception as e:
            error_msg = traceback.format_exc()
            print(f"خطأ في حذف قائمة التشغيل: {e}\n{error_msg}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حذف قائمة التشغيل: {str(e)}")
    
    def set_channels(self, channels):
        """تعيين قائمة القنوات لحفظها"""
        self.channels = channels

import os
import json
import hashlib
from PyQt6.QtCore import QObject, pyqtSignal

class PinLockManager(QObject):
    """
    مدير قفل التطبيق بكود PIN - يتعامل مع حفظ وتحقق الرقم السري
    """
    pin_changed = pyqtSignal(bool)  # إشارة عند تغيير الرمز (تفعيل/إلغاء)
    
    def __init__(self, data_dir):
        super().__init__()
        self.data_dir = data_dir
        self.settings_dir = os.path.join(data_dir, 'settings')
        os.makedirs(self.settings_dir, exist_ok=True)
        self.pin_file = os.path.join(self.settings_dir, 'pin_lock.json')
    
    def _hash_pin(self, pin):
        """تشفير الرمز السري باستخدام SHA-256"""
        # تحويل الرمز السري إلى سلسلة نصية
        pin_str = str(pin)
        # إضافة salt ثابتة لزيادة الأمان
        salt = "ModernIPTV_PIN_SALT_2024"
        # دمج الرمز السري مع الـ salt
        salted_pin = pin_str + salt
        # إنشاء التشفير باستخدام SHA-256
        hash_object = hashlib.sha256(salted_pin.encode())
        # إرجاع قيمة التشفير كنص
        return hash_object.hexdigest()
    
    def is_pin_enabled(self):
        """التحقق مما إذا كان قفل التطبيق مفعل"""
        if not os.path.exists(self.pin_file):
            return False
            
        try:
            with open(self.pin_file, 'r') as f:
                data = json.load(f)
                return data.get('enabled', False)
        except Exception:
            return False
    
    def verify_pin(self, pin):
        """التحقق من صحة الرمز السري المدخل"""
        if not os.path.exists(self.pin_file):
            return False
            
        try:
            with open(self.pin_file, 'r') as f:
                data = json.load(f)
                if not data.get('enabled', False):
                    # إذا كان القفل غير مفعل، فلا داعي للتحقق
                    return True
                    
                stored_hash = data.get('pin_hash', '')
                input_hash = self._hash_pin(pin)
                
                return stored_hash == input_hash
        except Exception:
            return False
    
    def set_pin(self, pin, enabled=True):
        """تعيين رمز سري جديد وتفعيل/تعطيل القفل"""
        try:
            pin_hash = self._hash_pin(pin) if pin else ''
            
            data = {
                'enabled': enabled,
                'pin_hash': pin_hash
            }
            
            with open(self.pin_file, 'w') as f:
                json.dump(data, f)
                
            self.pin_changed.emit(enabled)
            return True
        except Exception:
            return False
    
    def disable_pin(self):
        """تعطيل قفل التطبيق"""
        return self.set_pin('', False)
    
    def change_pin(self, old_pin, new_pin):
        """تغيير الرمز السري بعد التحقق من الرمز القديم"""
        if self.verify_pin(old_pin):
            return self.set_pin(new_pin, True)
        return False

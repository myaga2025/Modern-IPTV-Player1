#!/usr/bin/env python3
"""
إنشاء ملفات الملاحظات المحلية للاستخدام عند فشل الوصول للإنترنت
"""
import os
import sys
import requests

def create_notice_files():
    """إنشاء ملفات الملاحظات المحلية"""
    notices_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources", "notices")
    os.makedirs(notices_dir, exist_ok=True)
    
    # الملاحظة الافتراضية بالعربية
    ar_notice = """
    <div dir="rtl" style="text-align: right;">
    <h2>مرحباً بك في مشغل IPTV الحديث!</h2>
    <p>شكراً لاستخدامك تطبيقنا. نأمل أن يكون مفيداً لك.</p>
    <p>تم تطوير هذا التطبيق بهدف تقديم تجربة مشاهدة سهلة ومميزة.</p>
    <p>يمكنك تحميل قوائم التشغيل من ملفات M3U المحلية أو من عناوين URL.</p>
    <p>للمزيد من المعلومات أو الدعم، يرجى زيارة <a href="https://aljup.com">موقعنا</a>.</p>
    <p><b>استمتع بالمشاهدة!</b></p>
    </div>
    """
    
    # الملاحظة الافتراضية بالإنجليزية
    en_notice = """
    <h2>Welcome to Modern IPTV Player!</h2>
    <p>Thank you for using our application. We hope you find it useful.</p>
    <p>This application was developed to provide an easy and excellent viewing experience.</p>
    <p>You can load playlists from local M3U files or from URLs.</p>
    <p>For more information or support, please visit <a href="https://aljup.com">our website</a>.</p>
    <p><b>Enjoy watching!</b></p>
    """
    
    # محاولة تنزيل الملاحظات من الإنترنت أولاً
    print("محاولة تنزيل الملاحظات من الإنترنت...")
    
    try:
        ar_response = requests.get("https://aljup.com/app/note_ar.txt", timeout=10)
        if ar_response.status_code == 200:
            ar_notice = ar_response.text
            print("✓ تم تنزيل الملاحظة العربية بنجاح")
        else:
            print("× فشل تنزيل الملاحظة العربية، سيتم استخدام النص الافتراضي")
    except Exception as e:
        print(f"× خطأ في تنزيل الملاحظة العربية: {e}")
    
    try:
        en_response = requests.get("https://aljup.com/app/note_en.txt", timeout=10)
        if en_response.status_code == 200:
            en_notice = en_response.text
            print("✓ تم تنزيل الملاحظة الإنجليزية بنجاح")
        else:
            print("× فشل تنزيل الملاحظة الإنجليزية، سيتم استخدام النص الافتراضي")
    except Exception as e:
        print(f"× خطأ في تنزيل الملاحظة الإنجليزية: {e}")
    
    # حفظ الملفات محلياً
    ar_path = os.path.join(notices_dir, "note_ar.txt")
    en_path = os.path.join(notices_dir, "note_en.txt")
    
    with open(ar_path, 'w', encoding='utf-8') as f:
        f.write(ar_notice)
    print(f"✓ تم حفظ الملاحظة العربية في: {ar_path}")
    
    with open(en_path, 'w', encoding='utf-8') as f:
        f.write(en_notice)
    print(f"✓ تم حفظ الملاحظة الإنجليزية في: {en_path}")
    
    print("\nتم إنشاء ملفات الملاحظات بنجاح!")

if __name__ == "__main__":
    create_notice_files()

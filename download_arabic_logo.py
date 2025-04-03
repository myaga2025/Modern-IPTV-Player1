#!/usr/bin/env python3
"""
أداة لتنزيل شعار وأيقونات التطبيق
"""
import os
import sys
import requests
from urllib.request import urlretrieve

def download_icons():
    """تنزيل الشعار والأيقونات"""
    print("جاري تنزيل أيقونات التطبيق...")
    
    # تأكد من وجود المجلد
    icons_dir = "resources/icons"
    os.makedirs(icons_dir, exist_ok=True)
    
    # قائمة الأيقونات للتنزيل
    icons = {
        "logo": "https://raw.githubusercontent.com/applogo/arabic/main/iptv_logo.png",
        "app_icon": "https://raw.githubusercontent.com/applogo/arabic/main/iptv_icon.png",
        "play": "https://raw.githubusercontent.com/applogo/arabic/main/play.png",
        "pause": "https://raw.githubusercontent.com/applogo/arabic/main/pause.png",
        "stop": "https://raw.githubusercontent.com/applogo/arabic/main/stop.png",
        "volume": "https://raw.githubusercontent.com/applogo/arabic/main/volume.png",
    }
    
    # في حالة وجود مشكلة في الروابط الأصلية، استخدم روابط بديلة
    fallback_icons = {
        "app_icon": "https://raw.githubusercontent.com/feathericons/feather/master/icons/tv.png",
        "logo": "https://raw.githubusercontent.com/feathericons/feather/master/icons/play-circle.png",
        "play": "https://raw.githubusercontent.com/feathericons/feather/master/icons/play.png",
        "pause": "https://raw.githubusercontent.com/feathericons/feather/master/icons/pause.png",
        "stop": "https://raw.githubusercontent.com/feathericons/feather/master/icons/square.png",
        "volume": "https://raw.githubusercontent.com/feathericons/feather/master/icons/volume-2.png",
    }
    
    # عدد الأيقونات التي تم تنزيلها بنجاح
    success_count = 0
    
    # تنزيل كل أيقونة
    for name, url in icons.items():
        icon_path = os.path.join(icons_dir, f"{name}.png")
        try:
            # تنزيل الأيقونة
            print(f"جاري تنزيل {name}.png من {url}...")
            urlretrieve(url, icon_path)
            print(f"تم تنزيل {name}.png بنجاح")
            success_count += 1
        except Exception as e:
            print(f"فشل تنزيل {name}.png: {e}")
            
            # محاولة استخدام الرابط البديل
            try:
                fallback_url = fallback_icons.get(name)
                if fallback_url:
                    print(f"محاولة تنزيل {name}.png من رابط بديل: {fallback_url}...")
                    urlretrieve(fallback_url, icon_path)
                    print(f"تم تنزيل {name}.png من الرابط البديل بنجاح")
                    success_count += 1
                    continue
            except Exception as e2:
                print(f"فشل تنزيل {name}.png من الرابط البديل: {e2}")
            
            # إنشاء ملف نصي بدلاً من الصورة إذا فشل التنزيل
            try:
                with open(icon_path.replace(".png", ".txt"), "w", encoding="utf-8") as f:
                    f.write(f"يمكنك وضع أيقونة {name} هنا باسم {name}.png")
                print(f"تم إنشاء ملف: {icon_path.replace('.png', '.txt')}")
            except:
                pass
    
    return success_count == len(icons)

if __name__ == "__main__":
    if download_icons():
        print("\nتم تنزيل جميع الأيقونات بنجاح. يمكنك الآن تشغيل البرنامج.")
    else:
        print("\nلم يتم تنزيل بعض الأيقونات. يمكنك تشغيل البرنامج، لكن قد تكون بعض الأيقونات غير ظاهرة.")
    
    input("\nاضغط Enter للخروج...")

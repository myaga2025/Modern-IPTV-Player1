# كيفية إنشاء ملف تنفيذي للبرنامج (How to Build Executable)

## بالعربية

### المتطلبات المسبقة
1. تثبيت Python 3.8 أو إصدار أحدث على جهازك
2. تأكد من وجود pip محدث

### خطوات إنشاء الملف التنفيذي
1. افتح سطر الأوامر (Command Prompt) وانتقل إلى مجلد المشروع:
   ```
   cd n:\iptv
   ```

2. قم بتشغيل ملف البناء:
   ```
   build.bat
   ```
   
   أو يمكنك تنفيذ الأوامر يدويًا:
   ```
   pip install pyinstaller
   pip install -r requirements.txt
   python build_exe.py
   ```

3. انتظر حتى تكتمل عملية البناء. سيظهر الملف التنفيذي في مجلد `dist\Modern_IPTV_Player`.

4. يمكنك الآن نسخ المجلد بالكامل ومشاركته مع المستخدمين.

### ملاحظات
- تأكد من وجود جميع الملفات والمجلدات المطلوبة في المشروع (resources, translations, etc.).
- في حالة وجود أي مشاكل، يرجى التحقق من ملفات السجل في مجلد البناء.

## In English

### Prerequisites
1. Install Python 3.8 or newer on your computer
2. Make sure you have an updated pip

### Steps to Create the Executable
1. Open Command Prompt and navigate to the project folder:
   ```
   cd n:\iptv
   ```

2. Run the build file:
   ```
   build.bat
   ```
   
   Or you can run the commands manually:
   ```
   pip install pyinstaller
   pip install -r requirements.txt
   python build_exe.py
   ```

3. Wait for the build process to complete. The executable will appear in the `dist\Modern_IPTV_Player` folder.

4. You can now copy the entire folder and share it with users.

### Notes
- Make sure all required files and folders exist in the project (resources, translations, etc.).
- If you encounter any problems, please check the log files in the build directory.

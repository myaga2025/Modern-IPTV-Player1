# Modern IPTV Player / مشغل IPTV الحديث

[English](#english) | [العربية](#arabic)

<a name="english"></a>
## English

Modern IPTV Player is a sophisticated application built using Python with PyQt6 interface and VLC media player backend.

### Features
#### Windows & Linux App
- Play channels from M3U links/playlists
- Search and categorize channels
- Create custom playlists
- Support for English and Arabic languages
- Modern and elegant user interface

### Version
Current version: 1.0.1

### System Requirements

- Python 3.8 or newer
- PyQt6
- python-vlc
- requests
- VLC Media Player (64-bit version recommended)

### Important: Architecture Compatibility with VLC

For the application to work correctly, the VLC architecture must match your Python architecture:

- **Recommended: Use Python 64-bit with VLC 64-bit** installed in "C:\Program Files\VideoLAN\VLC"
- **Alternative: Use Python 32-bit with VLC 32-bit** installed in "C:\Program Files (x86)\VideoLAN\VLC"

To check your Python architecture, run:
```python
python -c "import sys; print('64-bit' if sys.maxsize > 2**32 else '32-bit')"
```

### Installation

1. Download and install the 64-bit version of VLC from [videolan.org](https://www.videolan.org/vlc/)

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Configure the VLC path:
   ```
   python force_vlc_path.py
   ```
   This will help you select the correct VLC installation.

4. Run the application:
   ```
   python main.py
   ```

### VLC Troubleshooting

If you encounter issues:

1. Install the 64-bit version of VLC in the default path: `C:\Program Files\VideoLAN\VLC`

2. Run the VLC path configuration tool:
   ```
   python force_vlc_path.py
   ```

3. If the problem persists, try:
   ```
   python setup_vlc.py
   ```

### Common Issues

#### Playlist Loading Errors

If you see the error "Detailed error loading URL playlist: 'dict' object has no attribute 'name'":

1. Check the format of your M3U playlist URL
2. Ensure your playlist URL returns a valid M3U format
3. Try with a different playlist to verify if the issue is specific to that playlist
4. Check your network connection
5. If using a local file, verify its format is correct
6. Restart the application after making any changes

### Usage

1. Start the application:
   ```
   python main.py
   ```

2. Load an IPTV playlist:
   - Open local M3U file: File > Open Playlist...
   - Open from URL: File > Open Playlist from URL...

3. Browse channels:
   - Use the search box to find specific channels
   - Filter channels by category using the dropdown menu
   - Double-click on a channel to play it

4. Custom playlists:
   - Click the "+" button in the tabs area
   - Name your playlist
   - Right-click on channels and select "Add to Playlist"

### Creating an Executable

To create a standalone executable (.exe) file:

1. Make sure all requirements are installed:
   ```
   pip install -r requirements.txt
   ```

2. Run the build script:
   ```
   build.bat
   ```

3. Find the executable in the `dist\Modern_IPTV_Player` folder

---

<a name="arabic"></a>
## العربية

مشغل IPTV الحديث هو تطبيق متطور مبني باستخدام Python مع واجهة PyQt6 ومحرك تشغيل VLC.

### الميزات

- تشغيل القنوات من روابط وقوائم تشغيل M3U
- البحث في القنوات وتصنيفها
- إنشاء قوائم تشغيل مخصصة
- دعم اللغتين العربية والإنجليزية
- واجهة مستخدم حديثة وأنيقة

### الإصدار
الإصدار الحالي: 1.0.1

### متطلبات النظام

- Python 3.8 أو أحدث
- PyQt6
- python-vlc
- requests
- VLC Media Player (إصدار 64 بت موصى به)

### هام: توافق البنية مع VLC

لكي يعمل التطبيق بشكل صحيح، يجب أن تتطابق بنية VLC مع بنية Python:

- **ينصح باستخدام Python 64-bit مع VLC 64-bit** المثبت في "C:\Program Files\VideoLAN\VLC"
- **يمكن أيضاً استخدام Python 32-bit مع VLC 32-bit** المثبت في "C:\Program Files (x86)\VideoLAN\VLC"

للتحقق من بنية Python لديك، قم بتشغيل:
```python
python -c "import sys; print('64-bit' if sys.maxsize > 2**32 else '32-bit')"
```

### التثبيت

1. قم بتنزيل وتثبيت إصدار 64 بت من VLC من [videolan.org](https://www.videolan.org/vlc/)

2. قم بتثبيت حزم Python المطلوبة:
   ```
   pip install -r requirements.txt
   ```

3. قم بتكوين مسار VLC:
   ```
   python force_vlc_path.py
   ```
   سيساعدك هذا في اختيار تثبيت VLC الصحيح.

4. قم بتشغيل التطبيق:
   ```
   python main.py
   ```

### استكشاف أخطاء VLC وإصلاحها

إذا واجهت مشكلات:

1. قم بتثبيت إصدار 64 بت من VLC في المسار الافتراضي: `C:\Program Files\VideoLAN\VLC`

2. قم بتشغيل أداة تكوين مسار VLC:
   ```
   python force_vlc_path.py
   ```

3. إذا استمرت المشكلة، جرب:
   ```
   python setup_vlc.py
   ```

### مشكلات شائعة

#### أخطاء تحميل قوائم التشغيل

إذا رأيت الخطأ "Detailed error loading URL playlist: 'dict' object has no attribute 'name'":

1. تحقق من تنسيق رابط قائمة التشغيل M3U
2. تأكد من أن رابط قائمة التشغيل يعيد تنسيق M3U صالح
3. جرب قائمة تشغيل مختلفة للتحقق مما إذا كانت المشكلة خاصة بتلك القائمة
4. تحقق من اتصالك بالإنترنت
5. إذا كنت تستخدم ملفًا محليًا، فتحقق من صحة تنسيقه
6. أعد تشغيل التطبيق بعد إجراء أي تغييرات

### الاستخدام

1. قم بتشغيل التطبيق:
   ```
   python main.py
   ```

2. قم بتحميل قائمة تشغيل IPTV:
   - فتح ملف M3U محلي: File > Open Playlist...
   - فتح من URL: File > Open Playlist from URL...

3. تصفح القنوات:
   - استخدم مربع البحث للعثور على قنوات محددة
   - قم بتصفية القنوات حسب الفئة باستخدام القائمة المنسدلة
   - انقر نقراً مزدوجاً على قناة لتشغيلها

4. قوائم التشغيل المخصصة:
   - انقر على زر "+" في منطقة علامات التبويب
   - قم بتسمية قائمة التشغيل الخاصة بك
   - انقر بزر الماوس الأيمن على القنوات وحدد "Add to Playlist"

### إنشاء ملف تنفيذي

لإنشاء ملف تنفيذي مستقل (exe):

1. تأكد من تثبيت جميع المتطلبات:
   ```
   pip install -r requirements.txt
   ```

2. قم بتشغيل سكريبت البناء:
   ```
   build.bat
   ```

3. ستجد الملف التنفيذي في مجلد `dist\Modern_IPTV_Player`


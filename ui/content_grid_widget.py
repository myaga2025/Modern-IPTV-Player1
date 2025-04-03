from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QLineEdit, QScrollArea, QGridLayout,
                           QFrame, QApplication, QSizePolicy, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QDir, QTimer
from PyQt6.QtGui import QPixmap, QImage
import os
import requests
from io import BytesIO
from threading import Thread
import threading
import hashlib
import time
import traceback
import logging
from functools import partial
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from collections import defaultdict, deque
from core.language_manager import tr
import weakref  # Add weakref support for safer callbacks

# Configure logging for the image loader
logging.basicConfig(level=logging.WARNING)
image_logger = logging.getLogger('ImageLoader')
image_logger.setLevel(logging.WARNING)  # Set to WARNING to reduce console spam

class ImageLoader:
    """Enhanced helper class to load images asynchronously with advanced caching and error handling"""
    
    # Class-level variables for image cache
    _cache = {}  # Memory cache for images
    _cache_lock = threading.Lock()
    _active_threads = {}
    _active_threads_lock = threading.Lock()
    _max_threads = 6  # Reduced maximum concurrent threads to avoid overwhelming connections
    
    # Domain throttling - track requests per domain 
    _domain_requests = defaultdict(int)
    _domain_requests_lock = threading.Lock()
    _domain_max_requests = 2  # Reduced max concurrent requests per domain
    
    # Request queue for delayed loading when all threads are busy
    _request_queue = deque()
    _request_queue_lock = threading.Lock()
    _request_queue_processing = False
    
    # Error tracking to avoid flooding the logs
    _error_domains = set()  # Domains with errors
    _error_count = defaultdict(int)  # Count of errors per domain
    _error_threshold = 3  # Reduced threshold for error suppression
    _failed_domains = set()  # Track persistently failing domains to avoid retries
    
    # Flag to indicate shutdown
    _shutdown = False
    
    @staticmethod
    def setup_cache_dir():
        """Set up the cache directory for downloaded images"""
        cache_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 
                           'Modern-IPTV-Player', 'image_cache')
        os.makedirs(cache_dir, exist_ok=True)
        return cache_dir
    
    @staticmethod
    def get_domain(url):
        """Extract domain from URL for throttling purposes"""
        if not url:
            return None
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return None
    
    @staticmethod
    def get_cache_path(url):
        """Generate a cache file path for a URL"""
        if not url:
            return None
            
        # Create hash of URL for filename
        url_hash = hashlib.md5(url.encode()).hexdigest()
        cache_dir = ImageLoader.setup_cache_dir()
        
        # Extract extension from URL or use .jpg as default
        extension = os.path.splitext(url)[1].lower()
        if not extension or extension not in ['.jpg', '.jpeg', '.png', '.webp', '.gif']:
            extension = '.jpg'
            
        return os.path.join(cache_dir, f"{url_hash}{extension}")
    
    @staticmethod
    def _process_queue():
        """Process the queue of delayed image loading requests"""
        with ImageLoader._request_queue_lock:
            if ImageLoader._request_queue_processing or len(ImageLoader._request_queue) == 0:
                return
            ImageLoader._request_queue_processing = True
        
        try:
            while True:
                # Get the next request from the queue
                with ImageLoader._request_queue_lock:
                    if not ImageLoader._request_queue:
                        ImageLoader._request_queue_processing = False
                        break
                    
                    url, weak_callback, default_image = ImageLoader._request_queue.popleft()
                
                # Check if we can process this request now
                domain = ImageLoader.get_domain(url)
                can_process = True
                
                with ImageLoader._active_threads_lock:
                    if len(ImageLoader._active_threads) >= ImageLoader._max_threads:
                        can_process = False
                
                if domain:
                    with ImageLoader._domain_requests_lock:
                        if ImageLoader._domain_requests[domain] >= ImageLoader._domain_max_requests:
                            can_process = False
                
                # If we can process, load the image, otherwise put it back in the queue
                if can_process:
                    ImageLoader._load_image(url, weak_callback, default_image)
                else:
                    with ImageLoader._request_queue_lock:
                        ImageLoader._request_queue.append((url, weak_callback, default_image))
                        # Prevent processing too many items at once
                        break
        except Exception as e:
            image_logger.error(f"Error processing image queue: {e}")
        finally:
            with ImageLoader._request_queue_lock:
                ImageLoader._request_queue_processing = False
    
    @staticmethod
    def load_image_async(url, callback, default_image=None):
        """Load image from URL asynchronously with caching and error handling"""
        # Create a weak reference to the callback to prevent accessing deleted objects
        weak_callback = weakref.WeakMethod(callback) if hasattr(callback, '__self__') else weakref.ref(callback)
        
        if not url:
            # Execute callback with default image if URL is empty
            try:
                cb = weak_callback()
                if cb is not None:
                    cb(default_image)
            except Exception:
                pass  # Callback might be gone already
            return
        
        # Use http if the URL starts with just //
        if url.startswith('//'):
            url = 'https:' + url
            
        # Check if we already have this image in memory cache
        with ImageLoader._cache_lock:
            if url in ImageLoader._cache:
                pixmap = ImageLoader._cache[url]
                if not pixmap.isNull():
                    try:
                        cb = weak_callback()
                        if cb is not None:
                            cb(pixmap)
                    except Exception:
                        pass  # Callback might be gone
                    return
                else:
                    # Remove invalid pixmap from cache
                    del ImageLoader._cache[url]
        
        # Check if we already have this image in file cache
        cache_path = ImageLoader.get_cache_path(url)
        if cache_path and os.path.exists(cache_path):
            try:
                pixmap = QPixmap(cache_path)
                if not pixmap.isNull() and pixmap.width() > 0 and pixmap.height() > 0:
                    # Store in memory cache and return
                    with ImageLoader._cache_lock:
                        ImageLoader._cache[url] = pixmap
                    try:
                        cb = weak_callback()
                        if cb is not None:
                            cb(pixmap)
                    except Exception:
                        pass  # Callback might be gone
                    return
            except Exception:
                # If loading from cache fails, continue with download
                pass
        
        # Check if we're already downloading this URL
        with ImageLoader._active_threads_lock:
            if url in ImageLoader._active_threads:
                # Add this callback to the existing thread's callbacks
                ImageLoader._active_threads[url].append(weak_callback)
                return
        
        # Check domain throttling limits
        domain = ImageLoader.get_domain(url)
        can_process = True
        
        if domain:
            with ImageLoader._domain_requests_lock:
                if ImageLoader._domain_requests[domain] >= ImageLoader._domain_max_requests:
                    can_process = False
        
        with ImageLoader._active_threads_lock:
            if len(ImageLoader._active_threads) >= ImageLoader._max_threads:
                can_process = False
        
        # If we can't process now, add to queue for later
        if not can_process:
            with ImageLoader._request_queue_lock:
                ImageLoader._request_queue.append((url, weak_callback, default_image))
                
                # Start queue processing if not already running
                if not ImageLoader._request_queue_processing and not ImageLoader._shutdown:
                    thread = Thread(target=ImageLoader._process_queue)
                    thread.daemon = True
                    thread.start()
            
            # Show the default image for now
            if default_image:
                try:
                    cb = weak_callback()
                    if cb is not None:
                        cb(default_image)
                except Exception:
                    pass  # Callback might be gone
            return
        
        # Process the image load now
        ImageLoader._load_image(url, weak_callback, default_image)
    
    @staticmethod
    def _load_image(url, weak_callback, default_image=None):
        """Internal method that handles the actual image loading"""
        domain = ImageLoader.get_domain(url)
        
        # Skip loading if domain is known to fail persistently
        if domain and domain in ImageLoader._failed_domains:
            # Just use the default image immediately
            if default_image:
                try:
                    cb = weak_callback()
                    if cb is not None:
                        cb(default_image)
                except Exception:
                    pass
            return
            
        # Update domain request count and track this thread
        with ImageLoader._domain_requests_lock:
            if domain:
                ImageLoader._domain_requests[domain] += 1
        
        with ImageLoader._active_threads_lock:
            ImageLoader._active_threads[url] = [weak_callback]
        
        def load_task():
            cache_path = ImageLoader.get_cache_path(url)
            try:
                # Skip if shutdown is in progress
                if ImageLoader._shutdown:
                    return
                    
                if url.startswith(("http://", "https://")):
                    # Check if this domain has had repeated failures
                    with ImageLoader._domain_requests_lock:
                        if domain and ImageLoader._error_count[domain] > 5:
                            # Add to failed domains set to avoid future attempts
                            ImageLoader._failed_domains.add(domain)
                            raise Exception(f"Domain {domain} has failed too many times, skipping")
                    
                    # Create a session with retries and timeout settings
                    session = requests.Session()
                    
                    # Configure the session with retries - reduced retries to 1
                    retries = Retry(
                        total=1,
                        backoff_factor=0.2,
                        status_forcelist=[500, 502, 503, 504],
                    )
                    
                    # Mount the adapter to both http and https
                    session.mount('http://', HTTPAdapter(max_retries=retries))
                    session.mount('https://', HTTPAdapter(max_retries=retries))
                    
                    # Disable SSL verification for problematic sites
                    session.verify = False
                    
                    # Make the request with shorter timeout (reduced from 4s to 3s)
                    response = session.get(url, timeout=3, stream=True)
                    response.raise_for_status()
                    
                    # Read image data
                    image_data = response.content
                    image = QImage.fromData(image_data)
                    pixmap = QPixmap.fromImage(image)
                    
                    if not pixmap.isNull() and pixmap.width() > 0 and pixmap.height() > 0:
                        # Save to file cache
                        if cache_path:
                            try:
                                with open(cache_path, 'wb') as f:
                                    f.write(image_data)
                            except Exception as e:
                                if domain not in ImageLoader._error_domains:
                                    image_logger.debug(f"Error saving image to cache: {e}")
                        
                        # Save to memory cache
                        with ImageLoader._cache_lock:
                            ImageLoader._cache[url] = pixmap
                        
                        # Call all callbacks for this URL
                        with ImageLoader._active_threads_lock:
                            weak_callbacks = ImageLoader._active_threads.pop(url, [])
                        
                        # Execute callbacks with appropriate error handling
                        for weak_cb in weak_callbacks:
                            try:
                                cb = weak_cb()
                                if cb is not None:
                                    cb(pixmap)
                            except Exception:
                                # Silently ignore callback errors - widget may be deleted
                                pass
                                
                        return
            except requests.exceptions.Timeout:
                # Don't log every timeout
                with ImageLoader._domain_requests_lock:
                    ImageLoader._error_count[domain] += 1
                    if ImageLoader._error_count[domain] <= ImageLoader._error_threshold:
                        image_logger.debug(f"Timeout loading image from {domain}")
                    elif ImageLoader._error_count[domain] == ImageLoader._error_threshold + 1:
                        image_logger.warning(f"Suppressing further timeout errors from {domain}")
                        ImageLoader._error_domains.add(domain)
                        ImageLoader._failed_domains.add(domain)  # Add to persistent failures
            except requests.exceptions.SSLError:
                # SSL errors are common with certain sites
                with ImageLoader._domain_requests_lock:
                    ImageLoader._error_count[domain] += 1
                    ImageLoader._failed_domains.add(domain)  # Add to persistent failures
            except requests.exceptions.ConnectionError as e:
                # Connection errors including name resolution failures
                with ImageLoader._domain_requests_lock:
                    ImageLoader._error_count[domain] += 1
                    if "NameResolutionError" in str(e) or "getaddrinfo failed" in str(e):
                        # Domain doesn't exist or DNS issues - mark as persistent failure
                        ImageLoader._failed_domains.add(domain)
                    if ImageLoader._error_count[domain] <= ImageLoader._error_threshold:
                        image_logger.debug(f"Connection error for {domain}: {str(e)}")
                    elif ImageLoader._error_count[domain] == ImageLoader._error_threshold + 1:
                        image_logger.warning(f"Suppressing further connection errors from {domain}")
                        ImageLoader._error_domains.add(domain)
            except requests.exceptions.RequestException as e:
                # Handle request exceptions without spamming logs
                with ImageLoader._domain_requests_lock:
                    ImageLoader._error_count[domain] += 1
                    if ImageLoader._error_count[domain] <= ImageLoader._error_threshold:
                        image_logger.debug(f"Request error loading image from {domain}: {str(e)}")
                    elif ImageLoader._error_count[domain] == ImageLoader._error_threshold + 1:
                        image_logger.warning(f"Suppressing further request errors from {domain}")
                        ImageLoader._error_domains.add(domain)
            except Exception as e:
                # General errors
                with ImageLoader._domain_requests_lock:
                    if domain:
                        ImageLoader._error_count[domain] += 1
                        if ImageLoader._error_count[domain] <= ImageLoader._error_threshold:
                            image_logger.debug(f"Unexpected error loading image from {domain}: {str(e)}")
                        elif ImageLoader._error_count[domain] == ImageLoader._error_threshold + 1:
                            image_logger.warning(f"Suppressing further errors from {domain}")
                            ImageLoader._error_domains.add(domain)
            finally:
                # Always update domain request count and cleanup
                if domain:
                    with ImageLoader._domain_requests_lock:
                        ImageLoader._domain_requests[domain] = max(0, ImageLoader._domain_requests[domain] - 1)
                
                # If loading fails, use default image for all callbacks - safely with error handling
                if default_image:
                    with ImageLoader._active_threads_lock:
                        weak_callbacks = ImageLoader._active_threads.pop(url, [])
                    
                    for weak_cb in weak_callbacks:
                        try:
                            cb = weak_cb()
                            if cb is not None:
                                cb(default_image)
                        except Exception:
                            pass  # Ignore errors - widget might be deleted
                else:
                    with ImageLoader._active_threads_lock:
                        ImageLoader._active_threads.pop(url, None)
                
                # Process the next item in the queue if not shutting down
                if not ImageLoader._shutdown:
                    ImageLoader._process_queue()
        
        # Start loading thread
        thread = Thread(target=load_task)
        thread.daemon = True
        thread.start()
    
    @staticmethod
    def shutdown():
        """Signal all threads to stop and clean up resources"""
        ImageLoader._shutdown = True
        
        # Clear the request queue
        with ImageLoader._request_queue_lock:
            ImageLoader._request_queue.clear()
        
        # Clear active threads
        with ImageLoader._active_threads_lock:
            ImageLoader._active_threads.clear()
    
    @staticmethod
    def clear_cache(clear_files=False):
        """Clear the image cache"""
        # Clear memory cache
        with ImageLoader._cache_lock:
            ImageLoader._cache.clear()
        
        # Optionally clear file cache
        if clear_files:
            cache_dir = ImageLoader.setup_cache_dir()
            try:
                for file in os.listdir(cache_dir):
                    file_path = os.path.join(cache_dir, file)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except:
                        pass
            except:
                pass
    
    @staticmethod
    def clear_failed_domains():
        """Clear the list of failed domains to allow retry attempts"""
        ImageLoader._failed_domains.clear()
        ImageLoader._error_domains.clear()
        ImageLoader._error_count.clear()

class ContentItemWidget(QFrame):
    """Widget for displaying a movie or series item"""
    
    clicked = pyqtSignal(dict)  # Signal emitted when item is clicked, containing the item data
    
    def __init__(self, item_data, default_image=None, parent=None):
        super().__init__(parent)
        self.item_data = item_data
        self.default_image = default_image
        self.is_destroyed = False  # Flag to track if widget is destroyed
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the UI components"""
        # Set frame style
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # حجم البطاقة ديناميكي ويعتمد على حجم الأب
        self.setMinimumWidth(160)
        self.setFixedWidth(180)  # الحجم الافتراضي، يمكن تغييره من خارج الفئة
        self.setMinimumHeight(260)
        
        # Get theme colors
        app = QApplication.instance()
        is_dark_theme = app and app.styleSheet() and "background-color: #121212" in app.styleSheet()
        
        # Colors based on theme
        bg_color = "#2A2A2A" if is_dark_theme else "#F0F0F0"
        text_color = "#FFFFFF" if is_dark_theme else "#000000"
        border_color = "#444444" if is_dark_theme else "#CCCCCC"
        
        # تحسين مظهر البطاقة - استخدام خصائص CSS مدعومة فقط
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 8px;
                border: 1px solid {border_color};
            }}
            QFrame:hover {{
                border: 2px solid #0078D7;
            }}
            QLabel {{
                background-color: transparent;
                border: none;
            }}
        """)
        
        # Create layout - تقليل الهامش لملء المساحة بشكل أفضل
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Create poster image label
        self.poster_label = QLabel()
        self.poster_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.poster_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.poster_label.setMinimumHeight(200)  # زيادة ارتفاع الصورة
        
        # إضافة تنسيق للصورة لملء البطاقة
        self.poster_label.setStyleSheet("""
            background-color: transparent;
            border-top-left-radius: 7px;
            border-top-right-radius: 7px;
        """)
        layout.addWidget(self.poster_label, 1)
        
        # إذا كانت هناك صورة افتراضية، يتم ضبطها لملء المساحة بشكل أفضل
        if self.default_image:
            self.poster_label.setPixmap(self.default_image.scaled(
                self.width() - 8, 220, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
        
        # Load the actual image - تحسين طريقة التحميل لملء البطاقة
        poster_url = self.item_data.get('poster', '')
        if poster_url:
            ImageLoader.load_image_async(
                poster_url, 
                self._set_scaled_pixmap,
                self.default_image
            )
        
        # Create title label - تحسين أسلوب العرض
        self.title_label = QLabel(self.item_data.get('name', 'Unknown'))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)
        # تقليل حجم الخط وإضافة إمكانية الإظهار بسطرين فقط
        self.title_label.setStyleSheet(f"""
            font-weight: bold; 
            color: {text_color}; 
            font-size: 12px;
            margin-top: 2px;
            background-color: {bg_color};
        """)
        self.title_label.setMaximumHeight(36)
        layout.addWidget(self.title_label)
        
        # إضافة السنة أو التصنيف في سطر منفصل بتنسيق أفضل
        info_text = ""
        if self.item_data.get('release_date'):
            year = self.item_data.get('release_date', '').split('-')[0] if '-' in self.item_data.get('release_date', '') else ''
            if year and year.isdigit():
                info_text = f"{year}"
        
        # إذا كان هناك تصنيف، نضيفه بعد السنة
        if self.item_data.get('genre'):
            genre = self.item_data.get('genre', '').split(',')[0]
            if genre:
                if info_text:
                    info_text += f" • {genre}"
                else:
                    info_text = genre
        
        self.info_label = QLabel(info_text)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.info_label.setStyleSheet(f"color: {text_color}; font-size: 10px; opacity: 0.7;")
        layout.addWidget(self.info_label)
    
    def _set_scaled_pixmap(self, pixmap):
        """Set scaled pixmap to poster label - safely check if widget still exists"""
        if hasattr(self, 'is_destroyed') and self.is_destroyed:
            return
            
        if hasattr(self, 'poster_label') and self.poster_label and not pixmap.isNull():
            try:
                # تعديل طريقة تحجيم الصورة لملء البطاقة بشكل أفضل
                # استخدام عرض البطاقة الفعلي بدلاً من قيمة ثابتة
                scaled_pixmap = pixmap.scaled(
                    self.width() - 8, 220, 
                    Qt.AspectRatioMode.KeepAspectRatio, 
                    Qt.TransformationMode.SmoothTransformation
                )
                self.poster_label.setPixmap(scaled_pixmap)
            except RuntimeError:
                # Widget might have been deleted between check and execution
                pass
                
    def resizeEvent(self, event):
        """اعتراض حدث تغيير الحجم لإعادة تحجيم الصورة"""
        super().resizeEvent(event)
        # إذا كان هناك صورة بالفعل، أعد تحجيمها
        if hasattr(self, 'poster_label') and self.poster_label and not self.poster_label.pixmap().isNull():
            pixmap = self.poster_label.pixmap().copy()  # نسخة من الصورة الحالية
            scaled_pixmap = pixmap.scaled(
                self.width() - 8, 220, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.poster_label.setPixmap(scaled_pixmap)
    
    def mousePressEvent(self, event):
        """Handle mouse press events"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.item_data)
        super().mousePressEvent(event)
    
    def __del__(self):
        """Handle object destruction - mark as destroyed to prevent callbacks"""
        self.is_destroyed = True


class ContentGridWidget(QWidget):
    """Grid widget for displaying movies or series content"""
    
    item_selected = pyqtSignal(dict)  # Signal emitted when an item is selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_items = []
        self.setup_ui()
        self.destroyed.connect(self.on_destroyed)  # Connect to destroyed signal
        
        # Disable SSL warnings (for requests library)
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    
    def on_destroyed(self):
        """Handle widget destruction - ensure all threads are stopped"""
        # Signal ImageLoader to clean up active threads for this widget
        ImageLoader.shutdown()
        
    def setup_ui(self):
        """Setup the UI components"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # توسيع الجزء العلوي لتضمين شريط البحث وأزرار العرض
        top_bar = QHBoxLayout()
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr("Search..."))
        self.search_input.textChanged.connect(self.filter_content)
        top_bar.addWidget(self.search_input)
        
        # زر عرض المحتوى في نافذة منفصلة
        self.expand_btn = QPushButton(tr("Open in Window"))
        self.expand_btn.setMaximumWidth(150)
        self.expand_btn.clicked.connect(self.open_in_window)
        top_bar.addWidget(self.expand_btn)
        
        # زر تغيير حجم بطاقات العرض
        self.size_btn = QPushButton(tr("Adjust Size"))
        self.size_btn.setMaximumWidth(120)
        self.size_btn.clicked.connect(self.toggle_card_size)
        top_bar.addWidget(self.size_btn)
        
        # Add a refresh/retry button
        self.refresh_btn = QPushButton(tr("Reload Images"))
        self.refresh_btn.setMaximumWidth(120)
        self.refresh_btn.clicked.connect(self.reload_images)
        top_bar.addWidget(self.refresh_btn)
        
        main_layout.addLayout(top_bar)
        
        # Scroll area for content grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Container widget for grid
        self.grid_container = QWidget()
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(5, 5, 5, 5)
        self.grid_layout.setSpacing(10)  # تقليل المسافة بين العناصر
        
        self.scroll_area.setWidget(self.grid_container)
        main_layout.addWidget(self.scroll_area)
        
        # Create default image for use when loading or as fallback
        self.default_image = None
        self.load_default_image()
        
        # حالة حجم البطاقات (عادي أو كبير)
        self.is_large_cards = False
        
        # عدد الأعمدة الافتراضي
        self.columns = 4
    
    def load_default_image(self):
        """Load default image for use when no poster is available"""
        try:
            # Try to load from resources
            image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                     "resources", "icons", "no_poster.png")
            
            if os.path.exists(image_path):
                self.default_image = QPixmap(image_path)
            else:
                # Create a blank image as fallback
                self.default_image = QPixmap(160, 240)
                self.default_image.fill(Qt.GlobalColor.lightGray)
        except Exception as e:
            print(f"Error loading default image: {str(e)}")
            # Create a blank image as fallback
            self.default_image = QPixmap(160, 240)
            self.default_image.fill(Qt.GlobalColor.lightGray)
    
    def set_content(self, items):
        """Set the content items to display in the grid"""
        # Store items for filtering
        self.current_items = items
        
        # Clear the search input
        self.search_input.clear()
        
        # تحميل تدريجي للمحتوى إذا كان كبيراً
        if len(items) > 100:
            self.load_content_progressively(items)
        else:
            # تحديث الشبكة مباشرة للمحتوى الصغير
            self.update_grid(items)
    
    def load_content_progressively(self, items):
        """تحميل المحتوى بشكل تدريجي لتجنب تجميد الواجهة"""
        # عرض رسالة حالة للمستخدم
        status_label = QLabel(tr("Loading {total} items...").format(total=len(items)))
        status_label.setStyleSheet("color: #0078D7; font-weight: bold;")
        status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # أضف أيقونة تحميل أو شريط تقدم إلى واجهة المستخدم
        progress_bar = QProgressBar()
        progress_bar.setRange(0, len(items))
        progress_bar.setValue(0)
        
        # أضف العناصر مؤقتاً إلى التخطيط
        self.layout().addWidget(status_label)
        self.layout().addWidget(progress_bar)
        
        # مسح الشبكة الحالية
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
        
        # حساب الأعمدة - دائماً 4 أعمدة
        columns = 4
        
        # عدد العناصر للمعالجة في كل دفعة
        batch_size = 30
        total_items = len(items)
        
        # استخدام QTimer لتحميل الدفعات في حلقة أحداث Qt
        def process_batch(start_index):
            if start_index >= total_items:
                # إزالة عناصر حالة التقدم
                status_label.setParent(None)
                progress_bar.setParent(None)
                status_label.deleteLater()
                progress_bar.deleteLater()
                return
            
            # تحديث شريط التقدم
            progress_bar.setValue(start_index)
            
            # تحديث رسالة الحالة
            current_percent = int((start_index / total_items) * 100)
            status_label.setText(tr("Loading {current}/{total} items ({percent}%)").format(
                current=start_index,
                total=total_items,
                percent=current_percent
            ))
            
            # عدد العناصر لمعالجتها في هذه الدفعة
            end_index = min(start_index + batch_size, total_items)
            
            # إضافة دفعة من العناصر إلى الشبكة
            for i in range(start_index, end_index):
                row = i // columns
                col = i % columns
                
                item = items[i]
                item_widget = ContentItemWidget(item, self.default_image)
                item_widget.clicked.connect(self.item_selected.emit)
                self.grid_layout.addWidget(item_widget, row, col)
            
            # الانتقال إلى الدفعة التالية
            QTimer.singleShot(10, lambda: process_batch(end_index))
        
        # بدء معالجة الدفعة الأولى
        QTimer.singleShot(0, lambda: process_batch(0))
    
    def filter_content(self, search_text):
        """Filter content based on search text"""
        if not search_text:
            # If search is empty, show all items
            self.update_grid(self.current_items)
            return
            
        # Filter items by name
        filtered_items = [item for item in self.current_items 
                        if search_text.lower() in item.get('name', '').lower()]
        
        # Update the grid with filtered items
        self.update_grid(filtered_items)
    
    def update_grid(self, items):
        """Update the grid with the given items"""
        # Clear existing items from grid
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # حساب العرض المتاح مع مراعاة أشرطة التمرير
        available_width = self.scroll_area.width() - 30  # حساب عرض منطقة التمرير مع هامش
        
        # تحديد حجم البطاقات بناءً على اختيار المستخدم وعرض الشاشة
        item_width = 180  # الحجم الافتراضي
        
        if self.is_large_cards:
            item_width = 240  # بطاقات أكبر
        
        # Add items to grid
        for i, item in enumerate(items):
            row = i // self.columns
            col = i % self.columns
            
            # إنشاء البطاقة بالحجم المناسب
            item_widget = ContentItemWidget(item, self.default_image)
            
            if self.is_large_cards:
                item_widget.setFixedWidth(item_width)  # تعيين عرض ثابت أكبر للبطاقات
                
            item_widget.clicked.connect(self.item_selected.emit)
            self.grid_layout.addWidget(item_widget, row, col)
        
        # Add empty widgets to fill the last row if needed
        item_count = len(items)
        if item_count % self.columns != 0:
            remaining = self.columns - (item_count % self.columns)
            for i in range(remaining):
                spacer = QWidget()
                spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
                self.grid_layout.addWidget(spacer, item_count // self.columns, (item_count % self.columns) + i)
    
    def toggle_card_size(self):
        """تبديل حجم بطاقات العرض بين الحجم العادي والكبير"""
        self.is_large_cards = not self.is_large_cards
        
        if self.is_large_cards:
            self.columns = 3  # عرض 3 أعمدة فقط للبطاقات الكبيرة
            self.size_btn.setText(tr("Normal Size"))
        else:
            self.columns = 4  # العودة إلى 4 أعمدة للبطاقات العادية
            self.size_btn.setText(tr("Larger Cards"))
        
        # تحديث العرض بالحجم الجديد
        if self.current_items:
            self.update_grid(self.current_items)
    
    def resizeEvent(self, event):
        """Handle resize event to adjust grid columns"""
        super().resizeEvent(event)
        
        # فحص ما إذا كان عرض الشاشة قد تغير بشكل كبير يستدعي تعديل عدد الأعمدة
        width = event.size().width()
        
        # تعديل عدد الأعمدة ديناميكيًا بناءً على عرض الشاشة
        old_columns = self.columns
        
        if self.is_large_cards:
            # عدد أعمدة أقل للبطاقات الكبيرة
            if width < 800:
                self.columns = 2
            else:
                self.columns = 3
        else:
            # عدد أعمدة أكثر للبطاقات العادية
            if width < 600:
                self.columns = 2
            elif width < 900:
                self.columns = 3
            elif width < 1200:
                self.columns = 4
            else:
                self.columns = 5
        
        # تحديث العرض فقط إذا تغير عدد الأعمدة
        if old_columns != self.columns and self.current_items:
            self.update_grid(self.current_items)
    
    def open_in_window(self):
        """فتح المحتوى في نافذة منفصلة"""
        try:
            # إنشاء نافذة جديدة لعرض المحتوى
            from PyQt6.QtWidgets import QDialog
            
            dialog = QDialog(self.parent())
            dialog.setWindowTitle(tr("Movies Gallery"))
            dialog.resize(1000, 700)
            
            # إنشاء نسخة جديدة من العرض
            layout = QVBoxLayout(dialog)
            
            # إضافة شريط بحث
            search_layout = QHBoxLayout()
            search_input = QLineEdit()
            search_input.setPlaceholderText(tr("Search..."))
            search_layout.addWidget(search_input)
            layout.addLayout(search_layout)
            
            # إنشاء عارض شبكة جديد
            content_grid = ContentGridWidget()
            layout.addWidget(content_grid)
            
            # نسخ المحتوى الحالي إلى العارض الجديد
            content_grid.set_content(self.current_items)
            
            # ربط وظيفة البحث
            search_input.textChanged.connect(content_grid.filter_content)
            
            # ربط إشارة اختيار العنصر من العارض الجديد
            content_grid.item_selected.connect(self.item_selected.emit)
            content_grid.item_selected.connect(dialog.accept)  # إغلاق النافذة عند اختيار عنصر
            
            # فتح الحوار كنافذة غير مشروطة
            dialog.setModal(False)
            dialog.show()
            
        except Exception as e:
            print(f"Error opening content in window: {e}")
            import traceback
            traceback.print_exc()
    
    def reload_images(self):
        """Force reload of images by resetting failed domains and refreshing the grid"""
        # Clear the failed domains list to allow retries
        ImageLoader.clear_failed_domains()
        
        # Force reload of current items
        current_items = self.current_items
        if current_items:
            self.update_grid(current_items)

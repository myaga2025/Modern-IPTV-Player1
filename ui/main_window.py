import os
import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QTabWidget, QPushButton, QLineEdit, QComboBox,
                           QLabel, QToolBar, QMenu, QMenuBar, QStatusBar,
                           QMessageBox, QFileDialog, QScrollArea, QFrame,
                           QTextEdit, QDialog, QDialogButtonBox, QApplication)
from PyQt6.QtGui import QIcon, QAction, QActionGroup, QFont
from PyQt6.QtCore import Qt, QSize, QTranslator, QEvent, QTimer

# Import our playlist loader
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from playlist_loader import load_playlist_from_url as loader_url
from playlist_loader import load_playlist_from_file as loader_file
from core.playlist_history import PlaylistHistory
from core.theme_manager import ThemeManager

from ui.player_widget import PlayerWidget
from ui.playlist_widget import PlaylistWidget
from ui.dialogs import AddPlaylistDialog, AboutDialog, URLInputDialog
from ui.xtream_dialog import XtreamLoginDialog, XtreamInfoDialog  # Add Xtream dialogs
from core.m3u_parser import M3UParser
from core.playlist import PlaylistManager
from core.language_manager import LanguageManager, tr
from core.url_history import PlaylistURLManager
from ui.content_grid_widget import ContentGridWidget

class MainWindow(QMainWindow):
    """Main application window"""
    
    # Application version
    APP_VERSION = "1.0.1"
    
    def __init__(self, url_manager=None, playlist_history=None, theme_manager=None, language_manager=None, pin_manager=None):
        super().__init__()
        
        # Initialize components
        self.m3u_parser = M3UParser()
        self.playlist_manager = PlaylistManager()
        self.language_manager = language_manager or LanguageManager()
        self.url_manager = url_manager or PlaylistURLManager()
        self.playlist_history = playlist_history or PlaylistHistory()
        self.theme_manager = theme_manager or ThemeManager()
        self.pin_manager = pin_manager
        self.last_loaded_playlist = None  # Track the currently loaded playlist
        self.is_fullscreen = False  # Track fullscreen state
        
        # تعيين أيقونة النافذة
        app_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                  "resources", "icons", "app_icon.png")
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))
        
        # Setup UI
        self.setWindowTitle(tr("Modern IPTV Player"))
        self.setMinimumSize(1200, 800)
        self._setup_ui()
        
        # Apply current theme
        self.apply_theme()
        
        # Connect signals
        self._connect_signals()
        
        # Load the last playlist (delayed to ensure UI is ready)
        QTimer.singleShot(500, self.load_last_playlist)
    
    def apply_theme(self):
        """Apply the current theme stylesheet to the application"""
        try:
            stylesheet_path = self.theme_manager.get_stylesheet_path()
            if os.path.exists(stylesheet_path):
                with open(stylesheet_path, "r", encoding='utf-8') as f:
                    QApplication.instance().setStyleSheet(f.read())
                    print(f"Applied theme: {self.theme_manager.get_current_theme()}")
            else:
                print(f"Theme stylesheet not found: {stylesheet_path}")
        except Exception as e:
            print(f"Error applying theme: {e}")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        new_theme = self.theme_manager.toggle_theme()
        self.apply_theme()
        
        theme_name = "Light" if new_theme == ThemeManager.LIGHT_THEME else "Dark"
        self.statusBar.showMessage(self.tr(f"Switched to {theme_name} theme"), 3000)
    
    def _setup_ui(self):
        """Setup the user interface"""
        # Create central widget and main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        main_layout = QVBoxLayout(self.central_widget)  # Changed to vertical layout
        
        # Create categories scroll area at the top
        self._setup_categories_panel()
        main_layout.addWidget(self.categories_scroll)
        
        # Create horizontal layout for content area
        self.content_layout = QHBoxLayout()  # تخزين مرجع للتخطيط الأفقيout()
        
        # Create left panel (playlists and channels)
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText(tr("Search channels..."))
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)
        
        # Tabs for different playlists
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.TabPosition.North)
        
        # Main playlists tab
        self.all_channels_widget = PlaylistWidget()
        self.tabs.addTab(self.all_channels_widget, tr("All Channels"))
        
        # Connect tab change signal to handle lazy loading of content
        self.tabs.currentChanged.connect(self._on_tab_changed)
        
        # Movies tab (initially hidden)
        self.movies_widget = ContentGridWidget()
        self.movies_tab_index = None  # We'll set this when adding the tab
        self.movies_loaded = False  # Flag to track if movies have been loaded
        
        # Series tab (initially hidden)
        self.series_widget = ContentGridWidget()
        self.series_tab_index = None  # We'll set this when adding the tab
        
        # Add playlists from playlist manager
        for name, playlist in self.playlist_manager.playlists.items():
            playlist_widget = PlaylistWidget()
            playlist_widget.set_channels(playlist.channels)
            self.tabs.addTab(playlist_widget, name)
        
        # Add tab for adding new playlists
        self.add_tab_button = QPushButton("+")
        self.add_tab_button.setFlat(True)
        self.add_tab_button.setMaximumWidth(30)
        self.tabs.setCornerWidget(self.add_tab_button)
        
        left_layout.addWidget(self.tabs)
        
        self.content_layout.addWidget(left_panel, 1)
        
        # Create right panel (player)
        self.player_widget = PlayerWidget()
        self.content_layout.addWidget(self.player_widget, 2)
        
        # إضافة زر لإخفاء/إظهار القائمة الجانبية
        toggle_sidebar_layout = QHBoxLayout()
        
        # زر إظهار/إخفاء القائمة الجانبية
        self.toggle_sidebar_btn = QPushButton()
        self.toggle_sidebar_btn.setObjectName("toggle-sidebar-button")
        icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "icons")
        hide_icon_path = os.path.join(icons_dir, "hide_sidebar.png")
        if os.path.exists(hide_icon_path):
            self.toggle_sidebar_btn.setIcon(QIcon(hide_icon_path))
        else:
            self.toggle_sidebar_btn.setText("«")
        self.toggle_sidebar_btn.setToolTip(tr("Hide/Show Sidebar"))
        self.toggle_sidebar_btn.setMaximumWidth(20)
        self.toggle_sidebar_btn.clicked.connect(self.toggle_sidebar)
        toggle_sidebar_layout.addWidget(self.toggle_sidebar_btn)
        
        # إضافة زر التبديل كعنصر منفصل بين القائمة والمشغل
        self.content_layout.addLayout(toggle_sidebar_layout)
        
        # حفظ مرجع للقائمة الجانبية
        self.sidebar_panel = left_panel
        self.is_sidebar_visible = True
        
        # Add content layout to main layout
        main_layout.addLayout(self.content_layout)
        
        # Setup menu bar
        self._setup_menu_bar()
        
        # Setup status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.statusBar.showMessage(tr("Ready"))
    
    def toggle_sidebar(self):
        """تبديل حالة عرض/إخفاء القائمة الجانبية"""
        if self.is_sidebar_visible:
            # إخفاء القائمة
            self.sidebar_panel.hide()
            self.is_sidebar_visible = False
            
            # تغيير أيقونة الزر
            icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "icons")
            show_icon_path = os.path.join(icons_dir, "show_sidebar.png")
            if os.path.exists(show_icon_path):
                self.toggle_sidebar_btn.setIcon(QIcon(show_icon_path))
            else:
                self.toggle_sidebar_btn.setText("»")
            self.toggle_sidebar_btn.setToolTip(tr("Show Sidebar"))
        else:
            # إظهار القائمة
            self.sidebar_panel.show()
            self.is_sidebar_visible = True
            
            # تغيير أيقونة الزر
            icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "icons")
            hide_icon_path = os.path.join(icons_dir, "hide_sidebar.png")
            if os.path.exists(hide_icon_path):
                self.toggle_sidebar_btn.setIcon(QIcon(hide_icon_path))
            else:
                self.toggle_sidebar_btn.setText("«")
            self.toggle_sidebar_btn.setToolTip(tr("Hide Sidebar"))
    
    def _setup_menu_bar(self):
        """Setup menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu(tr("&File"))
        
        open_action = QAction(tr("&Open Playlist..."), self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_playlist)
        file_menu.addAction(open_action)
        
        open_url_action = QAction(tr("Open Playlist from &URL..."), self)
        open_url_action.triggered.connect(self.open_playlist_url)
        file_menu.addAction(open_url_action)
        
        # Add Xtream option - now enabled
        xtream_action = QAction(tr("Xtream Connection"), self)
        xtream_action.triggered.connect(self.open_xtream_connection)
        file_menu.addAction(xtream_action)
        
        # Add Xtream info option - initially disabled
        self.xtream_info_action = QAction(tr("Xtream Connection Info"), self)
        self.xtream_info_action.triggered.connect(self.show_xtream_info)
        self.xtream_info_action.setEnabled(False)  # Enabled only after connection
        file_menu.addAction(self.xtream_info_action)
        
        # Add Playlist Management menu
        manage_playlists_action = QAction(tr("&Manage Playlists..."), self)
        manage_playlists_action.triggered.connect(self.show_playlist_manager)
        file_menu.addAction(manage_playlists_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction(tr("E&xit"), self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Playback menu
        playback_menu = menu_bar.addMenu(tr("&Playback"))
        
        play_action = QAction(tr("&Play/Pause"), self)
        play_action.setShortcut("Space")
        play_action.triggered.connect(self.player_widget.toggle_play)
        playback_menu.addAction(play_action)
        
        stop_action = QAction(tr("&Stop"), self)
        stop_action.triggered.connect(self.player_widget.stop)
        playback_menu.addAction(stop_action)
        
        # Add fullscreen action to playback menu
        playback_menu.addSeparator()
        self.fullscreen_action = QAction(tr("&Fullscreen"), self)
        self.fullscreen_action.setShortcut("F11")
        self.fullscreen_action.setCheckable(True)
        self.fullscreen_action.triggered.connect(self.toggle_fullscreen)
        playback_menu.addAction(self.fullscreen_action)
        
        # Settings menu
        settings_menu = menu_bar.addMenu(tr("&Settings"))
        
        # إضافة خيار لإدارة شعار التطبيق
        logo_action = QAction(tr("App Logo"), self)
        logo_action.triggered.connect(self.manage_app_logo)
        settings_menu.addAction(logo_action)
        
        # إضافة خيار لإدارة الإعدادات
        manage_settings_action = QAction(tr("Manage Settings"), self)
        manage_settings_action.triggered.connect(self.manage_settings)
        settings_menu.addAction(manage_settings_action)
        
        # إضافة خيار لإدارة قفل التطبيق
        if self.pin_manager:
            pin_lock_action = QAction(tr("App Lock Settings"), self)
            pin_lock_action.triggered.connect(self.manage_pin_lock)
            settings_menu.addAction(pin_lock_action)
        
        # Add theme submenu
        theme_menu = settings_menu.addMenu(tr("Theme"))
        
        # Create action group for themes to make them exclusive
        theme_action_group = QActionGroup(self)
        theme_action_group.setExclusive(True)
        
        # Add theme options
        dark_theme_action = QAction(tr("Dark"), self)
        dark_theme_action.setCheckable(True)
        dark_theme_action.setChecked(self.theme_manager.get_current_theme() == ThemeManager.DARK_THEME)
        dark_theme_action.triggered.connect(lambda: self.change_theme(ThemeManager.DARK_THEME))
        theme_action_group.addAction(dark_theme_action)
        theme_menu.addAction(dark_theme_action)
        
        light_theme_action = QAction(tr("Light"), self)
        light_theme_action.setCheckable(True)
        light_theme_action.setChecked(self.theme_manager.get_current_theme() == ThemeManager.LIGHT_THEME)
        light_theme_action.triggered.connect(lambda: self.change_theme(ThemeManager.LIGHT_THEME))
        theme_action_group.addAction(light_theme_action)
        theme_menu.addAction(light_theme_action)
        
        # Add a theme toggle action
        theme_menu.addSeparator()
        toggle_theme_action = QAction(tr("Toggle Theme"), self)
        toggle_theme_action.setShortcut("Ctrl+T")
        toggle_theme_action.triggered.connect(self.toggle_theme)
        theme_menu.addAction(toggle_theme_action)
        
        # Language submenu
        language_menu = settings_menu.addMenu(tr("Language"))
        
        # Create action group for languages to make them exclusive
        lang_action_group = QActionGroup(self)
        lang_action_group.setExclusive(True)
        
        # Add language options
        english_action = QAction(tr("English"), self)
        english_action.setCheckable(True)
        english_action.setChecked(self.language_manager.current_language == "en")
        english_action.triggered.connect(lambda: self.change_language("en"))
        lang_action_group.addAction(english_action)
        language_menu.addAction(english_action)
        
        arabic_action = QAction(tr("العربية"), self)
        arabic_action.setCheckable(True)
        arabic_action.setChecked(self.language_manager.current_language == "ar")
        arabic_action.triggered.connect(lambda: self.change_language("ar"))
        lang_action_group.addAction(arabic_action)
        language_menu.addAction(arabic_action)
        
        # Help menu
        help_menu = menu_bar.addMenu(tr("&Help"))
        
        # إضافة عناصر القائمة مباشرة إلى قائمة المساعدة
        about_app_action = QAction(tr("About App"), self)
        about_app_action.triggered.connect(self.show_about_app)
        help_menu.addAction(about_app_action)
        
        about_developer_action = QAction(tr("About Developer"), self)
        about_developer_action.triggered.connect(self.show_about_developer)
        help_menu.addAction(about_developer_action)
        
        # إضافة عنصر الترخيص
        license_action = QAction(tr("License"), self)
        license_action.triggered.connect(self.show_license)
        help_menu.addAction(license_action)
        
        check_updates_action = QAction(tr("Check for Updates"), self)
        check_updates_action.triggered.connect(self.check_updates)
        help_menu.addAction(check_updates_action)
    
    def show_license(self):
        """Show license dialog"""
        try:
            # Check for LICENSE.txt first (preferred)
            license_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "LICENSE.txt")
            
            # Fall back to LICENSE.md if LICENSE.txt doesn't exist
            if not os.path.exists(license_path):
                license_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "LICENSE.md")
                
            if os.path.exists(license_path):
                with open(license_path, 'r', encoding='utf-8') as f:
                    license_text = f.read()
                    
                # Remove the filepath comment from the beginning if present
                if license_text.startswith("# filepath:"):
                    license_text = license_text[license_text.find("\n") + 1:]
                    
                dialog = QDialog(self)
                dialog.setWindowTitle(tr("License Agreement"))
                dialog.setMinimumSize(600, 500)
                
                layout = QVBoxLayout(dialog)
                
                text_browser = QTextEdit()
                text_browser.setReadOnly(True)
                text_browser.setMarkdown(license_text)
                layout.addWidget(text_browser)
                
                button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
                button_box.accepted.connect(dialog.accept)
                layout.addWidget(button_box)
                
                dialog.exec()
            else:
                QMessageBox.warning(self, tr("License Not Found"), 
                                   tr("The license file could not be found. Please visit our website for more information."))
        except Exception as e:
            QMessageBox.critical(self, tr("Error"), 
                               tr("An error occurred while trying to display the license: {0}").format(str(e)))
    
    def change_theme(self, theme_name):
        """Change application theme"""
        if self.theme_manager.set_theme(theme_name):
            self.apply_theme()
            
            theme_display_name = "Light" if theme_name == ThemeManager.LIGHT_THEME else "Dark"
            self.statusBar.showMessage(self.tr(f"Changed theme to {theme_display_name}"), 3000)
    
    def _setup_categories_panel(self):
        """Setup the categories panel with horizontal scrolling buttons"""
        # Create a scroll area for category buttons
        self.categories_scroll = QScrollArea()
        self.categories_scroll.setWidgetResizable(True)
        self.categories_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.categories_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.categories_scroll.setMaximumHeight(60)  # Limit the height
        
        # Container widget for buttons
        self.categories_widget = QWidget()
        self.categories_layout = QHBoxLayout(self.categories_widget)
        self.categories_layout.setSpacing(10)  # مسافة بين أزرار الفئات
        self.categories_layout.setContentsMargins(10, 5, 10, 5)  # هوامش مناسبة
        
        # Add an "All" category button
        self.all_category_btn = QPushButton(tr("All"))
        self.all_category_btn.setCheckable(True)
        self.all_category_btn.setChecked(True)  # Checked by default
        self.all_category_btn.setMinimumWidth(100)  # زيادة العرض الأدنى لتجنب قطع النص
        self.all_category_btn.clicked.connect(lambda: self.select_category(self.all_category_btn, "All"))
        self.categories_layout.addWidget(self.all_category_btn)
        
        # Store category buttons for later reference
        self.category_buttons = [self.all_category_btn]
        
        # Add stretch to push buttons to the left
        self.categories_layout.addStretch()
        
        # Add "Contact Us" button on the right
        self.contact_us_button = QPushButton(tr("Contact Us"))
        self.contact_us_button.setObjectName("contact-us-button")
        self.contact_us_button.setMinimumWidth(200)  # زيادة العرض الأدنى
        self.contact_us_button.setMaximumWidth(200)
        self.contact_us_button.clicked.connect(self.show_contact_dialog)
        self.categories_layout.addWidget(self.contact_us_button)
        
        # Set the container as the scroll area widget
        self.categories_scroll.setWidget(self.categories_widget)
        
        # تحسين مظهر لوحة التصنيفات
        self.categories_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #555;
                background-color: #333;
                border-radius: 5px;
            }
            QPushButton {
                padding: 6px 12px;
                border-radius: 15px;
                background-color: #444;
                color: white;
                font-weight: bold;
                min-width: 90px;
            }
            QPushButton:checked {
                background-color: #0078D7;
            }
            QPushButton#contact-us-button {
                background-color: #0078D7;
            }
        """)
    
    def show_contact_dialog(self):
        """عرض نافذة التواصل معنا"""
        from ui.dialogs import ContactDialog
        contact_dialog = ContactDialog(self)
        contact_dialog.exec()
    
    def select_category(self, button, category_name):
        """Handle category button selection"""
        # Uncheck all buttons
        for btn in self.category_buttons:
            if btn != button:
                btn.setChecked(False)
        
        # Ensure the selected button is checked
        button.setChecked(True)
        
        # Filter channels by the selected category
        if category_name == "All":
            self.all_channels_widget.set_channels(self.m3u_parser.channels)
        else:
            filtered = self.m3u_parser.get_channels_by_group(category_name)
            self.all_channels_widget.set_channels(filtered)
    
    def _update_after_playlist_load(self):
        """Update UI after loading a playlist"""
        try:
            # Log the channel count
            print(f"Updating UI after loading playlist: {len(self.m3u_parser.channels)} channels")
            
            # Update channels list
            self.all_channels_widget.set_channels(self.m3u_parser.channels)
            
            # Clear existing category buttons except 'All'
            while len(self.category_buttons) > 1:
                btn = self.category_buttons.pop()
                btn.deleteLater()
            
            # Reset 'All' button to checked state
            self.all_category_btn.setChecked(True)
            
            # تحسين عملية إضافة أزرار الفئات لتفادي التراكب
            max_buttons_without_scroll = 8  # عدد الأزرار التي يمكن عرضها بدون تمرير
            group_count = len(self.m3u_parser.groups)
            
            # تعديل عرض الأزرار بناءً على عدد الفئات
            button_width = min(150, max(95, int(700 / max(1, min(group_count, max_buttons_without_scroll)))))
            
            # أضف أزرار الفئات الجديدة مع مراعاة الحجم المناسب
            for group in sorted(self.m3u_parser.groups):
                category_btn = QPushButton(group)
                category_btn.setCheckable(True)
                category_btn.setMinimumWidth(button_width)
                # استخدام lambda مع معلمة افتراضية لمنع مشاكل الإغلاق
                category_btn.clicked.connect(
                    lambda checked=False, btn=category_btn, cat=group: self.select_category(btn, cat)
                )
                self.categories_layout.insertWidget(len(self.category_buttons), category_btn)
                self.category_buttons.append(category_btn)
            
            # Make sure channels are visible
            self.all_channels_widget.update()
            self.centralWidget().update()
            
            # Status update
            self.statusBar.showMessage(self.tr("Loaded {count} channels").format(count=len(self.m3u_parser.channels)))
            print(f"Updated UI with {len(self.m3u_parser.channels)} channels")
            
            # معالجة حدث التمرير إذا كان هناك عدد كبير من الأقسام
            if group_count > max_buttons_without_scroll:
                # إضافة أسهم تمرير للإشارة إلى وجود المزيد
                scroll_indicator = QLabel("⟩⟩")
                scroll_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
                scroll_indicator.setStyleSheet("background: none; color: #FFFFFF; font-size: 14px; font-weight: bold;")
                self.categories_layout.insertWidget(len(self.category_buttons) + 1, scroll_indicator)
            
            # Force the UI to update by processing events
            QApplication.processEvents()
            
        except Exception as e:
            print(f"Error updating UI after playlist load: {e}")
            import traceback
            traceback.print_exc()
    
    def _connect_signals(self):
        """Connect signals to slots"""
        self.add_tab_button.clicked.connect(self.add_new_playlist)
        self.search_input.textChanged.connect(self.search_channels)
        self.all_channels_widget.channel_selected.connect(self.play_channel)
        
        # Connect player's fullscreen toggle signal to our toggle_fullscreen method
        self.player_widget.fullscreen_toggled.connect(self.toggle_fullscreen)
        
        # Add connection for contact button if not already added in _setup_ui
        if hasattr(self, 'contact_us_btn'):
            self.contact_us_btn.clicked.connect(self.show_contact_dialog)
    
    def change_language(self, language):
        """Change application language"""
        self.language_manager.change_language(language)
        
        # Show a message to inform the user
        QMessageBox.information(
            self, 
            tr("Language Changed"),
            tr("The language has been changed. Please restart the application for the changes to take effect."),
            QMessageBox.StandardButton.Ok
        )
    
    def load_last_playlist(self):
        """Load the last used playlist if available"""
        playlist_info = self.playlist_history.load_last_playlist()
        if not playlist_info:
            return
        
        try:
            if playlist_info.get('type') == 'file' and os.path.exists(playlist_info.get('path', '')):
                file_path = playlist_info.get('path')
                self.statusBar.showMessage(tr("Loading last used playlist: {name}...").format(name=playlist_info.get('name', file_path)))
                self.load_playlist_from_file(file_path)
            elif playlist_info.get('type') == 'url' and playlist_info.get('url'):
                url = playlist_info.get('url')
                self.statusBar.showMessage(tr("Loading last used playlist from URL: {name}...").format(name=playlist_info.get('name', url)))
                self.load_playlist_from_url(url)
        except Exception as e:
            print(f"Error loading last playlist: {e}")
    
    def save_current_playlist_info(self, playlist_type, source, name=None):
        """Save information about the currently loaded playlist"""
        info = {
            'type': playlist_type,  # 'file' or 'url'
            'name': name or (os.path.basename(source) if playlist_type == 'file' else source)
        }
        
        if playlist_type == 'file':
            info['path'] = source
        else:
            info['url'] = source
        
        self.last_loaded_playlist = info
        self.playlist_history.save_last_playlist(info)
    
    def open_playlist(self):
        """Open M3U playlist from file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, tr("Open Playlist"), "", tr("M3U Playlists (*.m3u *.m3u8);;JSON Playlists (*.json);;All Files (*)")
        )
        
        if file_path:
            self.statusBar.showMessage(tr("Loading playlist: {file_path}...").format(file_path=file_path))
            try:
                success = self.load_playlist_from_file(file_path)
                
                if success:
                    # Save this playlist as the last loaded one
                    self.save_current_playlist_info('file', file_path, os.path.basename(file_path))
                else:
                    QMessageBox.critical(self, tr("Error"), tr("Failed to load playlist: {file_path}").format(file_path=file_path))
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    tr("Error"), 
                    tr("Error loading playlist {file_path}: {error}").format(file_path=file_path, error=str(e))
                )
                print(f"Detailed error loading playlist: {e}")
    
    def open_playlist_url(self):
        """Open M3U playlist from URL"""
        dialog = URLInputDialog(self.url_manager.get_urls(), tr("Open Playlist URL"), tr("Enter playlist URL:"), self)
        if dialog.exec():
            url = dialog.get_input()
            if url:
                # إضافة الرابط إلى السجل
                self.url_manager.add_url(url)
                
                self.statusBar.showMessage(tr("Loading playlist from URL..."))
                try:
                    success = self.load_playlist_from_url(url)
                    
                    if success:
                        # Save this URL as the last loaded one
                        self.save_current_playlist_info('url', url)
                    else:
                        QMessageBox.critical(self, tr("Error"), tr("Failed to load playlist from URL"))
                except Exception as e:
                    QMessageBox.critical(
                        self, 
                        tr("Error"), 
                        tr("Error loading playlist from URL: {error}").format(error=str(e))
                    )
                    print(f"Detailed error loading URL playlist: {e}")
    
    def load_playlist_from_url(self, url):
        """Load a playlist from a URL using the new playlist loader"""
        try:
            self.statusBar.showMessage(tr("Loading playlist from URL..."))
            
            # Use the imported function from playlist_loader
            channels = loader_url(url)
            
            if not channels:
                self.statusBar.showMessage(tr("Error: Could not load playlist from URL"), 5000)
                return False
            
            # Store channels in m3u_parser for consistency with the rest of the app
            self.m3u_parser.channels = channels
            
            # Extract unique groups for filtering
            groups = set()
            for channel in channels:
                if 'group' in channel:
                    groups.add(channel['group'])
            self.m3u_parser.groups = list(groups)
                
            # Update UI with loaded channels
            self._update_after_playlist_load()
            self.statusBar.showMessage(tr(f"Loaded {len(channels)} channels from URL"), 5000)
            return True
        except Exception as e:
            self.statusBar.showMessage(tr(f"Error loading playlist: {str(e)}"), 5000)
            print(f"Detailed error loading URL playlist: {str(e)}")
            return False

    def load_playlist_from_file(self, file_path):
        """Load a playlist from a file using the new playlist loader"""
        try:
            self.statusBar.showMessage(tr("Loading playlist..."))
            
            # Use the imported function from playlist_loader
            channels = loader_file(file_path)
            
            if not channels:
                self.statusBar.showMessage(tr("Error: Could not load playlist file"), 5000)
                return False
            
            # Store channels in m3u_parser for consistency with the rest of the app
            self.m3u_parser.channels = channels
            
            # Extract unique groups for filtering
            groups = set()
            for channel in channels:
                if 'group' in channel:
                    groups.add(channel['group'])
            self.m3u_parser.groups = list(groups)
                
            # Update UI with loaded channels
            self._update_after_playlist_load()
            self.statusBar.showMessage(tr(f"Loaded {len(channels)} channels"), 5000)
            return True
        except Exception as e:
            self.statusBar.showMessage(tr(f"Error loading playlist: {str(e)}"), 5000)
            print(f"Detailed error loading playlist file: {str(e)}")
            return False
            
    def add_channels_to_current_playlist(self, channels):
        """Add channels to the current playlist"""
        try:
            # Ensure all channels have required attributes
            validated_channels = []
            
            for channel in channels:
                # Ensure channel is a dictionary and has all required keys
                if isinstance(channel, dict):
                    # Create a validated channel with all required keys
                    valid_channel = {
                        "name": channel.get("name", f"Channel {len(validated_channels) + 1}"),
                        "url": channel.get("url", ""),
                        "group": channel.get("group", "Unknown"),
                        "logo": channel.get("logo", ""),
                        "id": channel.get("id", len(validated_channels))
                    }
                    validated_channels.append(valid_channel)
                else:
                    print(f"Skipping invalid channel: {channel}")
            
            # Store the channels in m3u_parser for proper UI updates
            self.m3u_parser.channels = validated_channels
            
            # Extract unique groups for filtering
            groups = set()
            for channel in validated_channels:
                if 'group' in channel:
                    groups.add(channel['group'])
            self.m3u_parser.groups = list(groups)
            
            # Update UI with loaded channels
            self._update_after_playlist_load()
                
        except Exception as e:
            print(f"Error adding channels to playlist: {e}")
            raise e  # Re-raise to see the detailed error
    
    def search_channels(self, query):
        """Search channels by name"""
        self.all_channels_widget.search(query)
    
    def add_new_playlist(self):
        """Add new custom playlist"""
        dialog = AddPlaylistDialog()
        if dialog.exec():
            name = dialog.get_playlist_name()
            if name:
                playlist = self.playlist_manager.create_playlist(name)
                
                # Add new tab for playlist
                playlist_widget = PlaylistWidget()
                new_tab_index = self.tabs.addTab(playlist_widget, name)
                self.tabs.setCurrentIndex(new_tab_index)
    
    def play_channel(self, channel):
        """Play selected channel"""
        if not channel:
            return
            
        print(f"Playing channel: {channel.name}, URL: {channel.url}")
        self.statusBar.showMessage(tr("Playing: {channel_name}").format(channel_name=channel.name))
        
        # Update active channel in all playlist widgets
        if hasattr(channel, 'id'):
            print(f"Setting active channel ID: {channel.id} in all playlist widgets")
            # Update in main channel list
            self.all_channels_widget.set_active_channel(channel.id)
            
            # Also update in other playlist tabs
            for i in range(self.tabs.count()):
                widget = self.tabs.widget(i)
                if isinstance(widget, PlaylistWidget) and widget != self.all_channels_widget:
                    widget.set_active_channel(channel.id)
        else:
            print("Channel has no ID attribute, cannot set active channel")
        
        # Play the channel
        self.player_widget.play(channel.url, channel.name)
    
    def show_about_app(self):
        """Show information about the app"""
        content = ""
        if self.language_manager.current_language == "ar":
            content = f"Modern IPTV Player v{self.APP_VERSION}\n\n" \
                      "مشغل IPTV حديث ومتطور يدعم قوائم تشغيل M3U وبواجهة رسومية جذابة.\n\n" \
                      "الميزات:\n" \
                      "- دعم قوائم تشغيل M3U المحلية وعبر الإنترنت\n" \
                      "- البحث والتصنيف بالمجموعات\n" \
                      "- إنشاء وإدارة قوائم تشغيل مخصصة\n" \
                      "- واجهة مستخدم عصرية وسهلة الاستخدام\n\n" \
                      "© 2023-2024 جميع الحقوق محفوظة."
        else:
            content = f"Modern IPTV Player v{self.APP_VERSION}\n\n" \
                      "A modern IPTV player supporting M3U playlists with an elegant graphical interface.\n\n" \
                      "Features:\n" \
                      "- Support for local and remote M3U playlists\n" \
                      "- Search and categorization by groups\n" \
                      "- Create and manage custom playlists\n" \
                      "- Modern and user-friendly interface\n\n" \
                      "© 2023-2024 All Rights Reserved."
                      
        dialog = AboutDialog(
            title=tr("About App"),
            content=content
        )
        dialog.exec()
    
    def show_about_developer(self):
        """Show information about the developer"""
        content = ""
        if self.language_manager.current_language == "ar":
            content = "تم تطوير هذا البرنامج بواسطة:\n\n" \
                      " تطوير Mu Dev \n\n" \
                      "للتواصل والدعم الفني:\n" \
                      "البريد الإلكتروني: admin@aljup.com\n" \
                      "الموقع الإلكتروني: www.aljup.com\n\n" \
                      "نرحب بملاحظاتكم واقتراحاتكم لتطوير البرنامج!"
        else:
            content = "This program was developed by:\n\n" \
                      "IPTV Player Development Team\n\n" \
                      "Contact and support information:\n" \
                      "Email: admin@aljup.com\n" \
                      "Website: www.aljup.com\n" \
                      "We welcome your feedback and suggestions!"
                      
        dialog = AboutDialog(
            title=tr("About Developer"),
            content=content
        )
        dialog.exec()
    
    def check_updates(self):
        """Check for application updates and show changelog"""
        # Show the changelog dialog instead of just a simple message
        changelog_dialog = ChangelogDialog(self)
        changelog_dialog.exec()
    
    def show_about(self):
        """Show about dialog - for backwards compatibility"""
        self.show_about_app()
    
    def show_playlist_manager(self):
        """Show the playlist manager dialog"""
        from ui.dialogs import PlaylistManagerDialog
        dialog = PlaylistManagerDialog(self.playlist_manager, self)
        if dialog.exec():
            # Refresh tabs if changes made
            self._refresh_playlist_tabs()
    
    def _refresh_playlist_tabs(self):
        """Refresh playlist tabs"""
        # Get current tab index
        current_index = self.tabs.currentIndex()
        
        # Delete all tabs except the first one (All Channels)
        while self.tabs.count() > 1:
            self.tabs.removeTab(1)
        
        # Re-add all playlists
        for name, playlist in self.playlist_manager.playlists.items():
            playlist_widget = PlaylistWidget()
            playlist_widget.set_channels(playlist.channels)
            playlist_widget.channel_selected.connect(self.play_channel)
            self.tabs.addTab(playlist_widget, name)
        
        # Try to restore the selected tab
        if current_index < self.tabs.count():
            self.tabs.setCurrentIndex(current_index)
    
    def manage_app_logo(self):
        """فتح نافذة إدارة شعار التطبيق"""
        try:
            # استدعاء مدير الشعار
            from logo_manager import LogoManagerWindow
            self.logo_manager = LogoManagerWindow()
            self.logo_manager.show()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء فتح مدير الشعار: {str(e)}")

    def manage_settings(self):
        """فتح نافذة إدارة الإعدادات"""
        try:
            # استدعاء مدير الإعدادات
            from settings_manager import SettingsManager
            self.settings_manager = SettingsManager()
            self.settings_manager.show()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء فتح مدير الإعدادات: {str(e)}")

    def manage_pin_lock(self):
        """فتح نافذة إدارة قفل التطبيق"""
        try:
            # استدعاء مدير قفل التطبيق
            from ui.pin_settings_dialog import PinSettingsDialog
            pin_dialog = PinSettingsDialog(self.pin_manager, self)
            pin_dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء فتح إعدادات قفل التطبيق: {str(e)}")

    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        if self.is_fullscreen:
            self.showNormal()
            self.is_fullscreen = False
            self.fullscreen_action.setChecked(False)
            
            # Show UI elements that should be visible in normal mode
            self.menuBar().show()
            self.statusBar().show()
            self.categories_scroll.show()
            self.tabs.tabBar().show()
            self.search_input.show()
            
            # عرض لوحة القنوات الجانبية إذا كانت مرئية قبل دخول وضع ملء الشاشة
            if hasattr(self, 'is_sidebar_visible_before_fullscreen') and self.is_sidebar_visible_before_fullscreen:
                self.sidebar_panel.show()
                self.is_sidebar_visible = True
            
            # إظهار زر التبديل
            self.toggle_sidebar_btn.show()
        else:
            # حفظ حالة القائمة الجانبية قبل الدخول في وضع ملء الشاشة
            self.is_sidebar_visible_before_fullscreen = self.is_sidebar_visible
            
            self.showFullScreen()
            self.is_fullscreen = True
            self.fullscreen_action.setChecked(True)
            
            # Hide UI elements for a cleaner fullscreen experience
            self.menuBar().hide()
            self.statusBar.hide()
            self.categories_scroll.hide()
            self.tabs.tabBar().hide()
            self.search_input.hide()
            
            # إخفاء القائمة الجانبية
            self.sidebar_panel.hide()
            
            # إخفاء زر التبديل
            self.toggle_sidebar_btn.hide()
        
        # تحديث حالة زر ملء الشاشة في المشغل
        self.player_widget.update_fullscreen_button(self.is_fullscreen)
        
        # Update player widget for fullscreen state
        self.player_widget.on_fullscreen_changed(self.is_fullscreen)
    
    def showEvent(self, event):
        """Handle window show event"""
        super().showEvent(event)
        # تحديث حالة زر ملء الشاشة
        if hasattr(self, 'player_widget'):
            self.player_widget.update_fullscreen_button(self.is_fullscreen)
    
    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key.Key_F11:
            self.toggle_fullscreen()
        # اضافة اختصار للتبديل بين إظهار وإخفاء القائمة الجانبية (Ctrl+B)
        elif event.key() == Qt.Key.Key_B and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            self.toggle_sidebar()
        elif event.key() == Qt.Key.Key_Escape and self.is_fullscreen:
            # Exit fullscreen mode with Escape key
            self.toggle_fullscreen()
        else:
            super().keyPressEvent(event)

    def closeEvent(self, event):
        """Handle window close event"""
        # If we have a loaded playlist, make sure it's saved to history
        if self.last_loaded_playlist:
            self.playlist_history.save_last_playlist(self.last_loaded_playlist)
        
        # Accept the close event
        event.accept()

    def open_xtream_connection(self):
        """Open Xtream connection dialog"""
        try:
            dialog = XtreamLoginDialog(self)
            # ربط إشارة الدفعات الجديدة
            dialog.data_chunk_ready.connect(self.process_xtream_data_chunk)
            dialog.connection_successful.connect(self.on_xtream_connection_successful)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(
                self, 
                tr("Error"), 
                tr("Error connecting to Xtream service: {error}").format(error=str(e))
            )

    def process_xtream_data_chunk(self, chunk):
        """معالجة دفعة بيانات من Xtream وتحديث الواجهة تدريجيًا"""
        # يمكننا هنا تحديث القائمة الجزئية للعرض التدريجي
        try:
            # إذا لم تكن قائمة القنوات موجودة، نقوم بإنشائها
            if not hasattr(self.m3u_parser, 'channels') or self.m3u_parser.channels is None:
                self.m3u_parser.channels = []
            
            # إضافة دفعة القنوات الجديدة
            current_count = len(self.m3u_parser.channels)
            self.m3u_parser.channels.extend(chunk)
            
            # تحديث مجموعات الفئات
            groups_set = set(self.m3u_parser.groups) if hasattr(self.m3u_parser, 'groups') else set()
            for channel in chunk:
                if 'group' in channel and channel['group']:
                    groups_set.add(channel['group'])
            self.m3u_parser.groups = sorted(list(groups_set))
            
            # تحديث حالة العرض
            self.statusBar.showMessage(
                tr("Loading channels: {current}/{total}").format(
                    current=len(self.m3u_parser.channels),
                    total="?"  # لا نعرف العدد الإجمالي بعد
                )
            )
            
            # تحديث الواجهة تدريجيًا كل 500 قناة
            if current_count == 0 or len(self.m3u_parser.channels) % 500 == 0:
                self.all_channels_widget.set_channels(self.m3u_parser.channels)
                self._update_category_buttons()
                QApplication.processEvents()
            
        except Exception as e:
            print(f"Error processing Xtream data chunk: {e}")
    
    def _update_category_buttons(self):
        """تحديث أزرار الفئات بناءً على المحتوى الحالي"""
        # احتفظ بزر "الكل" فقط
        while len(self.category_buttons) > 1:
            btn = self.category_buttons.pop()
            btn.deleteLater()
        
        # أعد تعيين زر "الكل" إلى حالة محددة
        self.all_category_btn.setChecked(True)
        
        # حساب العرض المناسب للأزرار
        max_buttons_without_scroll = 8
        group_count = len(self.m3u_parser.groups)
        button_width = min(140, max(90, int(700 / max(1, min(group_count, max_buttons_without_scroll)))))
        
        # إضافة أزرار الفئات مع الحجم المناسب
        for group in sorted(self.m3u_parser.groups):
            category_btn = QPushButton(group)
            category_btn.setCheckable(True)
            category_btn.setMinimumWidth(button_width)
            category_btn.clicked.connect(
                lambda checked=False, btn=category_btn, cat=group: self.select_category(btn, cat)
            )
            self.categories_layout.insertWidget(len(self.category_buttons), category_btn)
            self.category_buttons.append(category_btn)

    def on_xtream_connection_successful(self, connection_info, channels):
        """Handle successful Xtream connection"""
        try:
            # Store the connection info
            self.xtream_connection = connection_info
            
            # Enable the connection info action
            self.xtream_info_action.setEnabled(True)
            
            # Store channels in m3u_parser for consistency with other methods
            self.m3u_parser.channels = channels
            
            # Extract unique groups for filtering
            groups = set()
            for channel in channels:
                if 'group' in channel:
                    groups.add(channel['group'])
            self.m3u_parser.groups = list(groups)
                
            # Update UI with loaded channels
            self._update_after_playlist_load()
            
            # Update status bar
            self.statusBar.showMessage(
                tr("Connected to Xtream service. Loaded {count} channels.").format(count=len(channels))
            )
            
            # أضف تبويبات الأفلام والمسلسلات ولكن بدون تحميل المحتوى حتى يتم النقر عليها
            self._add_vod_tabs()
            
        except Exception as e:
            QMessageBox.critical(
                self, 
                tr("Error"), 
                tr("Error processing Xtream data: {error}").format(error=str(e))
            )

    def _add_vod_tabs(self):
        """إضافة تبويبات الأفلام والمسلسلات بدون تحميل المحتوى"""
        try:
            # Add movies tab if not already added
            if self.movies_tab_index is None:
                self.movies_tab_index = self.tabs.addTab(self.movies_widget, tr("Movies"))
                # Connect the signal
                self.movies_widget.item_selected.connect(self.play_movie)
                
            # Add series tab (disabled with coming soon widget)
            if self.series_tab_index is None:
                # استخدام واجهة العرض المعطلة للمسلسلات
                from ui.coming_soon_widget import ComingSoonWidget
                self.series_coming_soon_widget = ComingSoonWidget("series")
                self.series_tab_index = self.tabs.addTab(self.series_coming_soon_widget, tr("Series"))
                
                # تحديد نمط لسان التبويبة بلون مختلف
                self.tabs.tabBar().setTabTextColor(self.series_tab_index, Qt.GlobalColor.red)
                
                # إضافة أيقونة معطل إلى لسان التبويبة إذا وجدت
                try:
                    icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                          "resources", "icons", "disabled.png")
                    if os.path.exists(icon_path):
                        self.tabs.tabBar().setTabIcon(self.series_tab_index, QIcon(icon_path))
                except:
                    pass
            
            # Reset loading flags
            self.movies_loaded = False
            
        except Exception as e:
            print(f"Error adding VOD tabs: {e}")
        
    def _load_movies_content(self):
        """تحميل محتوى الأفلام تدريجيًا"""
        # إظهار مؤشر التحميل
        self.statusBar.showMessage(tr("Loading movies..."))
        
        # تحميل الأفلام في خلفية منفصلة لتجنب تجمد واجهة المستخدم
        loading_widget = self._create_loading_overlay(self.movies_widget)
        loading_widget.set_message(tr("جاري تحميل الأفلام..."))
        loading_widget.show()
        
        # استدعاء التحميل بعد فترة قصيرة للسماح لواجهة المستخدم بالتحديث
        QTimer.singleShot(100, lambda: self._start_loading_movies(loading_widget))
    
    def _start_loading_movies(self, loading_widget):
        """بدء تحميل الأفلام فعليًا"""
        try:
            # إنشاء عميل Xtream جديد باستخدام بيانات الاعتماد المخزنة
            from core.xtream_client import XtreamClient
            client = XtreamClient(
                self.xtream_connection.get('server'),
                self.xtream_connection.get('username'),
                self.xtream_connection.get('password', '')
            )
            
            # الاتصال بالخادم
            success, _ = client.connect()
            if not success:
                loading_widget.deleteLater()
                self.statusBar.showMessage(tr("Failed to connect to Xtream server"), 3000)
                return
            
            # الحصول على الأفلام (VOD)
            movies = client.get_vod_streams()
            
            # تم التحميل بنجاح، تحديث الواجهة
            self.statusBar.showMessage(tr("Loaded {count} movies").format(count=len(movies)), 3000)
            
            # تعيين المحتوى في ContentGridWidget
            self.movies_widget.set_content(movies)
            
            # تحديث علم التحميل
            self.movies_loaded = True
            
        except Exception as e:
            self.statusBar.showMessage(tr("Error loading movies: {error}").format(error=str(e)), 5000)
            print(f"Error loading VOD content: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # إزالة مؤشر التحميل
            loading_widget.deleteLater()
    
    def _create_loading_overlay(self, parent):
        """إنشاء واجهة تحميل متراكبة فوق عنصر الأب"""
        from ui.loading_widget import LoadingWidget
        loading = LoadingWidget(parent)
        # جعل الحجم مطابق للأب
        loading.resize(parent.size())
        return loading
    
    def _on_tab_changed(self, index):
        """معالجة تغيير التبويب النشط للتحميل التدريجي"""
        # تحقق مما إذا كان التبويب المحدد هو تبويب الأفلام وأنه لم يتم تحميله بعد
        if self.movies_tab_index is not None and index == self.movies_tab_index and not self.movies_loaded:
            self._load_movies_content()
        
        # إذا تم النقر على تبويبة المسلسلات المعطلة، أظهر رسالة للمستخدم
        elif self.series_tab_index is not None and index == self.series_tab_index:
            QMessageBox.information(
                self,
                tr("Feature Disabled"),
                tr("The Series feature is currently disabled and will be available in a future update."),
                QMessageBox.StandardButton.Ok
            )
            # العودة إلى التبويبة السابقة
            previous_tab = 0 if self.tabs.count() > 0 else self.movies_tab_index
            self.tabs.setCurrentIndex(previous_tab)

    def play_movie(self, movie):
        """Play a movie from the movie grid"""
        if not movie:
            return
            
        print(f"Playing movie: {movie.get('name')}, URL: {movie.get('url')}")
        self.statusBar.showMessage(tr("Playing: {movie_name}").format(movie_name=movie.get('name')))
        
        # Play the movie
        self.player_widget.play(movie.get('url'), movie.get('name'))
    
    def show_series_details(self, series):
        """عرض تفاصيل المسلسل المحدد - معطلة حاليًا"""
        # بما أن ميزة المسلسلات معطلة، نعرض رسالة للمستخدم
        QMessageBox.information(
            self,
            tr("Feature Disabled"),
            tr("The Series feature is currently disabled and will be available in a future update.")
        )
        return

    def show_xtream_info(self):
        """Show dialog with Xtream connection information"""
        if hasattr(self, 'xtream_connection'):
            dialog = XtreamInfoDialog(self.xtream_connection, self)
            dialog.exec()

class ChangelogDialog(QDialog):
    """Dialog for displaying version changelog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Get the application version from MainWindow
        self.app_version = parent.APP_VERSION if hasattr(parent, 'APP_VERSION') else "1.0.3"
        self.setWindowTitle(tr("Updates & Changelog"))
        self.setMinimumSize(500, 400)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Current version info
        current_version_layout = QHBoxLayout()
        current_version_icon = QLabel()
        current_version_icon.setPixmap(QIcon(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                           "resources", "icons", "check.png")).pixmap(32, 32))
        current_version_layout.addWidget(current_version_icon)
        
        current_version_text = QLabel(tr(f"You are using the latest version ({self.app_version})."))
        current_version_text.setStyleSheet("font-size: 14px; font-weight: bold;")
        current_version_layout.addWidget(current_version_text)
        current_version_layout.addStretch()
        
        layout.addLayout(current_version_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Changelog title
        changelog_title = QLabel(tr("Changelog:"))
        changelog_title.setStyleSheet("font-size: 14px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(changelog_title)
        
        # Changelog content in a text edit for scrolling
        self.changelog_text = QTextEdit()
        self.changelog_text.setReadOnly(True)
        self.changelog_text.setStyleSheet("background-color: #2a2a2a; border-radius: 5px;")
        
        # Add the changelog entries - newest first
        changelog = self._get_changelog()
        self.changelog_text.setHtml(changelog)
        
        layout.addWidget(self.changelog_text)
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
    
    def _get_changelog(self):
        """Return the HTML-formatted changelog"""
        # Use different languages based on parent's language setting
        parent = self.parent()
        is_arabic = parent and hasattr(parent, 'language_manager') and parent.language_manager.current_language == "ar"
        
        if is_arabic:
            return """
            <style>
                body { color: #f0f0f0; font-family: Arial, sans-serif; }
                h3 { color: #0078D7; margin-bottom: 5px; }
                ul { margin-top: 5px; }
                .version { color: #0078D7; font-weight: bold; }
                .date { color: #aaa; font-size: small; }
            </style>
            <h3>إصدار <span class="version">1.0.3</span> <span class="date">(03 ابريل 2025)</span></h3>
            <ul>
                <li>إضافة دعم الاتصال بسيرفرات Xtream للحصول على قوائم البث والأفلام</li>
                <li>تحسين معالجة أخطاء تحميل الصور وتقليل رسائل الخطأ المتكررة</li>
                <li>إضافة زر "إعادة تحميل الصور" لمحاولة تحميل الصور الفاشلة</li>
                <li>تحسين واجهة عرض الافلام والمسلسلات</li>
                <li>معالجة مشاكل الاتصال بالانترنت أثناء تحميل الصور</li>
                <li>تحسين أداء العرض مع المحتوى الكبير</li>
                <li>إصلاح مشكلة الاختفاء الجانبي للافلام في شاشات العرض المختلفة</li>
                <li>تعديل عدد الاعمدة ديناميكياً حسب عرض الشاشة</li>
                <li>تقليل استهلاك موارد النظام عند تحميل الصور</li>
            </ul>
            
            <h3>إصدار <span class="version">1.0.2</span> <span class="date">(2 ابريل 2025)</span></h3>
            <ul>
                <li>إضافة قائمة "اتصل بنا" مع خيارات دعم متعددة</li>
                <li>تحسين واجهة المستخدم مع تأثيرات بصرية إضافية</li>
                <li>تعزيز مشغل الفيديو مع دعم المزيد من التنسيقات</li>
                <li>تحسين دعم اللغة العربية</li>
                <li>إصلاح مشاكل تحميل قوائم التشغيل من مصادر مختلفة</li>
                <li>زيادة استقرار وأداء التطبيق</li>
                <li>إضافة المزيد من خيارات إدارة قوائم التشغيل المخصصة</li>
            </ul>
            
            <h3>إصدار <span class="version">1.0.1</span> <span class="date">(01 ابريل 2025)</span></h3>
            <ul>
                <li>إضافة تمييز للقناة النشطة في قائمة القنوات لتسهيل التعرف على القناة الحالية</li>
                <li>إضافة الوضع الفاتح للتطبيق مع إمكانية التبديل بسهولة بين الوضعين</li>
                <li>إضافة لوحة فئات أفقية للتصفية السريعة</li>
                <li>إضافة امكانية حفظ اخر قائمة تشغيل عند اغلاق التطبيق</li>
                <li>تحسين رؤية النص في الوضع الفاتح</li>
                <li>تم إصلاح مشكلة عدم عرض القنوات بعد التحميل</li>
                <li>تم إصلاح مشكلة تحميل الملفات المحلية</li>
                <li>تم إصلاح خطأ 'dict' object has no attribute 'name'</li>
                <li>تحسين عرض قوائم التشغيل</li>
                <li>تحسينات عامة في واجهة المستخدم</li>
            </ul>
            
            <h3>إصدار <span class="version">1.0.0</span> <span class="date">(28 مارس 2025)</span></h3>
            <ul>
                <li>الإصدار الأولي</li>
                <li>دعم قوائم تشغيل M3U المحلية وعبر الإنترنت</li>
                <li>إمكانية البحث والتصنيف حسب المجموعات</li>
                <li>إنشاء وإدارة قوائم تشغيل مخصصة</li>
                <li>دعم اللغتين العربية والإنجليزية</li>
            </ul>
            """
        else:
            return """
            <style>
                body { color: #f0f0f0; font-family: Arial, sans-serif; }
                h3 { color: #0078D7; margin-bottom: 5px; }
                ul { margin-top: 5px; }
                .version { color: #0078D7; font-weight: bold; }
                .date { color: #aaa; font-size: small; }
            </style>
            <h3>Version <span class="version">1.0.3</span> <span class="date">(April 3, 2025)</span></h3>
            <ul>
                <li>Added Xtream servers connection support for streaming lists and movies</li>
                <li>Improved image loading error handling and reduced repetitive error messages</li>
                <li>Added "Reload Images" button to retry failed image loads</li>
                <li>Enhanced movie and series display interface</li>
                <li>Fixed network connectivity issues during image loading</li>
                <li>Improved display performance with large content</li>
                <li>Fixed side cutoff issues for movies on different screen sizes</li>
                <li>Dynamically adjust column count based on screen width</li>
                <li>Reduced system resource usage when loading images</li>
            </ul>
            
            <h3>Version <span class="version">1.0.2</span> <span class="date">(October 15, 2024)</span></h3>
            <ul>
                <li>Added "Contact Us" functionality with multiple support options</li>
                <li>Improved UI with additional visual effects</li>
                <li>Enhanced video player with support for more formats</li>
                <li>Improved Arabic language support</li>
                <li>Fixed issues with playlist loading from various sources</li>
                <li>Increased application stability and performance</li>
                <li>Added more management options for custom playlists</li>
            </ul>
            
            <h3>Version <span class="version">1.0.1</span> <span class="date">(July 1, 2024)</span></h3>
            <ul>
                <li>Added highlighting for active channel in the playlist for better visibility</li>
                <li>Added light theme with easy toggling between dark and light modes</li>
                <li>Fixed text visibility issues in light mode</li>
                <li>Added horizontal category panel for quick filtering</li>
                <li>Added automatic loading of last used playlist on startup</li>
                <li>Fixed issue where channels weren't displayed after loading</li>
                <li>Fixed local file loading issue</li>
                <li>Fixed 'dict' object has no attribute 'name' error</li>
                <li>Improved playlist display</li>
                <li>General UI improvements</li>
            </ul>
            
            <h3>Version <span class="version">1.0.0</span> <span class="date">(March 28, 2024)</span></h3>
            <ul>
                <li>Initial release</li>
                <li>Support for local and remote M3U playlists</li>
                <li>Search and categorization by groups</li>
                <li>Create and manage custom playlists</li>
                <li>Support for English and Arabic languages</li>
            </ul>
            """

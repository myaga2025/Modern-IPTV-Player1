from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                          QTabWidget, QListWidget, QTextEdit, QSplitter, QWidget, 
                          QApplication, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer
from PyQt6.QtGui import QPixmap, QFont, QIcon
import os
from core.language_manager import tr
from ui.loading_widget import LoadingWidget

class SeriesDetailsDialog(QDialog):
    """نافذة عرض تفاصيل المسلسل مع المواسم والحلقات"""
    
    episode_selected = pyqtSignal(dict)  # إشارة عند اختيار حلقة للتشغيل
    
    def __init__(self, series_data, xtream_client, parent=None):
        super().__init__(parent)
        
        self.series_data = series_data
        self.xtream_client = xtream_client
        self.seasons_data = {}  # تخزين بيانات المواسم
        self.episodes_data = {}  # تخزين بيانات الحلقات لكل موسم
        self.current_season_id = None  # تخزين معرف الموسم الحالي
        
        self.setup_ui()
        self.load_series_info()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم للنافذة"""
        # إعدادات النافذة
        self.setWindowTitle(tr("Series Details"))
        self.resize(900, 600)
        
        # تطبيق الأنماط بناءً على سمة التطبيق
        app = QApplication.instance()
        is_dark_theme = app and app.styleSheet() and "background-color: #121212" in app.styleSheet()
        text_color = "#FFFFFF" if is_dark_theme else "#000000"
        bg_color = "#1E1E1E" if is_dark_theme else "#F5F5F5"
        accent_color = "#0078D7"
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # قسم العنوان وصورة المسلسل
        top_section = QHBoxLayout()
        
        # صورة المسلسل (الملصق)
        self.poster_label = QLabel()
        self.poster_label.setFixedSize(180, 270)
        self.poster_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter)
        self.poster_label.setStyleSheet(f"""
            background-color: {bg_color};
            border: 1px solid #555;
            border-radius: 5px;
        """)
        
        # تحميل الصورة الافتراضية
        default_image_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                         "resources", "icons", "no_poster.png")
        if os.path.exists(default_image_path):
            self.poster_label.setPixmap(QPixmap(default_image_path).scaled(
                180, 270, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            ))
        
        top_section.addWidget(self.poster_label)
        
        # معلومات المسلسل
        info_layout = QVBoxLayout()
        
        # عنوان المسلسل
        self.title_label = QLabel(self.series_data.get('name', 'Unknown Series'))
        self.title_label.setStyleSheet(f"""
            font-size: 20px;
            font-weight: bold;
            color: {accent_color};
            padding-bottom: 5px;
        """)
        info_layout.addWidget(self.title_label)
        
        # تصنيف المسلسل والتقييم
        category_year_layout = QHBoxLayout()
        
        self.category_label = QLabel(self.series_data.get('category_name', ''))
        self.category_label.setStyleSheet(f"color: {text_color}; font-size: 12px;")
        category_year_layout.addWidget(self.category_label)
        
        year = ""
        if 'year' in self.series_data:
            year = str(self.series_data['year'])
        elif 'releaseDate' in self.series_data:
            year = self.series_data['releaseDate'].split('-')[0]
            
        if year:
            self.year_label = QLabel(year)
            self.year_label.setStyleSheet(f"color: {text_color}; font-size: 12px;")
            category_year_layout.addWidget(QLabel("•"))
            category_year_layout.addWidget(self.year_label)
        
        rating = self.series_data.get('rating', None)
        if rating:
            self.rating_label = QLabel(f"{rating}/10")
            self.rating_label.setStyleSheet(f"color: gold; font-weight: bold;")
            category_year_layout.addWidget(QLabel("•"))
            category_year_layout.addWidget(self.rating_label)
            
        category_year_layout.addStretch()
        info_layout.addLayout(category_year_layout)
        
        # وصف المسلسل
        self.plot_text = QTextEdit()
        self.plot_text.setReadOnly(True)
        self.plot_text.setText(self.series_data.get('plot', tr('No description available.')))
        self.plot_text.setStyleSheet(f"""
            background-color: {bg_color};
            color: {text_color};
            border: 1px solid #555;
            border-radius: 5px;
        """)
        self.plot_text.setMaximumHeight(100)
        info_layout.addWidget(self.plot_text)
        
        top_section.addLayout(info_layout, 1)
        main_layout.addLayout(top_section)
        
        # مقسم للمساحة بين معلومات السلسلة والمواسم/الحلقات
        splitter = QSplitter(Qt.Orientation.Vertical)
        main_layout.addWidget(splitter, 1)
        
        # منطقة المواسم والحلقات
        content_widget = QWidget()
        content_layout = QHBoxLayout(content_widget)
        
        # قائمة المواسم
        seasons_frame = QFrame()
        seasons_frame.setFrameShape(QFrame.Shape.StyledPanel)
        seasons_frame.setMinimumWidth(200)
        seasons_frame.setMaximumWidth(250)
        seasons_layout = QVBoxLayout(seasons_frame)
        
        seasons_title = QLabel(tr("Seasons"))
        seasons_title.setStyleSheet(f"font-weight: bold; color: {accent_color}; font-size: 14px;")
        seasons_layout.addWidget(seasons_title)
        
        self.seasons_list = QListWidget()
        self.seasons_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {bg_color};
                color: {text_color};
                border: 1px solid #555;
                border-radius: 5px;
            }}
            QListWidget::item:selected {{
                background-color: {accent_color};
                color: white;
            }}
            QListWidget::item:hover {{
                background-color: {accent_color}50;
            }}
        """)
        self.seasons_list.currentRowChanged.connect(self.on_season_selected)
        seasons_layout.addWidget(self.seasons_list)
        
        content_layout.addWidget(seasons_frame)
        
        # تبويبات لعرض حلقات كل موسم
        self.episodes_tabs = QTabWidget()
        self.episodes_tabs.setStyleSheet(f"""
            QTabWidget::pane {{
                border: 1px solid #555;
                border-radius: 5px;
                background-color: {bg_color};
            }}
            QTabBar::tab {{
                background-color: {'#2D2D2D' if is_dark_theme else '#E5E5E5'};
                color: {text_color};
                padding: 8px 12px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            QTabBar::tab:selected {{
                background-color: {accent_color};
                color: white;
            }}
        """)
        content_layout.addWidget(self.episodes_tabs, 1)
        
        splitter.addWidget(content_widget)
        
        # أزرار التحكم
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.close_button = QPushButton(tr("Close"))
        self.close_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.close_button)
        
        main_layout.addLayout(buttons_layout)
    
    def load_series_info(self):
        """تحميل معلومات المسلسل والمواسم"""
        # إظهار مؤشر التحميل
        self.loading_widget = LoadingWidget(self)
        self.loading_widget.set_message(tr("Loading series info..."))
        self.loading_widget.resize(self.size())
        self.loading_widget.show()
        
        try:
            # تحميل صورة المسلسل إذا كانت متوفرة
            poster_url = self.series_data.get('cover', None) or self.series_data.get('poster', None)
            if poster_url:
                from ui.content_grid_widget import ImageLoader
                ImageLoader.load_image_async(
                    poster_url,
                    lambda pixmap: self._set_poster(pixmap)
                )
            
            # تحميل مواسم المسلسل
            series_id = self.series_data.get('series_id')
            if not series_id:
                print("No series_id found in series data")
                self.loading_widget.deleteLater()
                self.loading_widget = None
                return

            # بدلاً من استخدام خيط منفصل، نستخدم QTimer لجدولة التحميل على خيط الواجهة الرئيسي
            QTimer.singleShot(100, lambda: self._load_seasons_direct(series_id))
                
        except Exception as e:
            print(f"Error in load_series_info: {e}")
            import traceback
            traceback.print_exc()
            if hasattr(self, 'loading_widget') and self.loading_widget:
                self.loading_widget.deleteLater()
                self.loading_widget = None
    
    def _load_seasons_direct(self, series_id):
        """تحميل المواسم بشكل مباشر"""
        try:
            print(f"Loading seasons for series ID: {series_id}")
            # تحميل معلومات المسلسل كاملة 
            series_info = self.xtream_client.get_series_info(series_id)
            print(f"Series info loaded: {len(series_info)} keys")

            # استخراج المواسم من معلومات المسلسل
            seasons = []
            if 'info' in series_info and 'seasons' in series_info['info']:
                seasons = series_info['info']['seasons']
                print(f"Found {len(seasons)} seasons in series info")
            else:
                print(f"No seasons found in series info. Keys: {series_info.keys()}")
            
            # تحديث قائمة المواسم
            self._update_seasons_list(seasons)
            
            # تخزين بيانات الحلقات من معلومات المسلسل لتسريع التحميل لاحقاً
            if 'episodes' in series_info:
                self.all_episodes = series_info['episodes']
                print(f"Stored {len(self.all_episodes)} episodes for faster loading")
            else:
                self.all_episodes = []
                print("No episodes found in series info")
            
        except Exception as e:
            print(f"Error loading seasons directly: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # إزالة مؤشر التحميل بعد الانتهاء
            if hasattr(self, 'loading_widget') and self.loading_widget:
                self.loading_widget.deleteLater()
                self.loading_widget = None
    
    def _set_poster(self, pixmap):
        """تعيين صورة الملصق من تحميل غير متزامن"""
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(
                180, 270, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            self.poster_label.setPixmap(scaled_pixmap)
    
    def _update_seasons_list(self, seasons):
        """تحديث قائمة المواسم"""
        self.seasons_data = {}
        self.seasons_list.clear()
        
        if not seasons:
            self.seasons_list.addItem(tr("No seasons available"))
            return
            
        # ترتيب المواسم تصاعدياً
        sorted_seasons = sorted(seasons, key=lambda s: int(s.get('season_number', 0)))
        
        for season in sorted_seasons:
            season_num = season.get('season_number', 'Unknown')
            item_text = f"{tr('Season')} {season_num}"
            self.seasons_list.addItem(item_text)
            
            # تخزين بيانات الموسم للرجوع إليها لاحقاً
            self.seasons_data[item_text] = season
        
        # تحديد الموسم الأول تلقائياً
        if self.seasons_list.count() > 0:
            self.seasons_list.setCurrentRow(0)
    
    def on_season_selected(self, row):
        """التعامل مع تحديد موسم من القائمة"""
        if row < 0:
            return
            
        # الحصول على بيانات الموسم المحدد
        selected_text = self.seasons_list.item(row).text()
        season_data = self.seasons_data.get(selected_text)
        
        if not season_data:
            print(f"No season data found for '{selected_text}'")
            return
        
        # حفظ معرف الموسم الحالي
        season_id = season_data.get('season_id')
        if not season_id:
            print("No season_id found in season data")
            return
            
        self.current_season_id = season_id
        print(f"Selected season ID: {season_id}")
        
        # إظهار مؤشر التحميل
        self.loading_widget = LoadingWidget(self)
        self.loading_widget.set_message(tr("Loading episodes..."))
        self.loading_widget.resize(self.size())
        self.loading_widget.show()
        
        # استخدام QTimer بدلاً من الخيوط للتحميل في خيط الواجهة الرئيسي
        QTimer.singleShot(100, lambda: self._load_episodes_direct(season_data))
    
    def _load_episodes_direct(self, season_data):
        """تحميل الحلقات مباشرة بدون خيوط"""
        try:
            season_id = season_data.get('season_id')
            season_number = season_data.get('season_number')
            print(f"Loading episodes for season ID: {season_id} (Season {season_number})")
            
            # التحقق ما إذا كان لدينا الحلقات مخزنة مسبقاً
            if hasattr(self, 'all_episodes') and self.all_episodes:
                # استخدام الحلقات المخزنة مسبقاً وتصفيتها للموسم الحالي
                episodes = [ep for ep in self.all_episodes if str(ep.get('season_id', '')) == str(season_id)]
                print(f"Using stored episodes: found {len(episodes)} episodes for season {season_number}")
                
                # إضافة URLs للتشغيل لكل حلقة
                for episode in episodes:
                    episode_id = episode.get('id', '')
                    stream_url = f"{self.xtream_client.base_url}/series/{self.xtream_client.username}/{self.xtream_client.password}/{episode_id}.{episode.get('container_extension', 'mp4')}"
                    episode['stream_url'] = stream_url
            else:
                # تحميل الحلقات من API
                episodes = self.xtream_client.get_series_episodes(self.series_data.get('series_id'), season_id)
                print(f"Loaded episodes from API: found {len(episodes)} episodes for season {season_number}")
            
            # عرض الحلقات
            self._display_episodes(season_data.get('season_number', ''), episodes)
            
        except Exception as e:
            print(f"Error loading episodes directly: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # إزالة مؤشر التحميل
            if hasattr(self, 'loading_widget') and self.loading_widget:
                self.loading_widget.deleteLater()
                self.loading_widget = None
    
    def _display_episodes(self, season_number, episodes):
        """عرض حلقات الموسم المحدد في تبويبة"""
        # إزالة التبويبات السابقة
        while self.episodes_tabs.count() > 0:
            self.episodes_tabs.removeTab(0)
            
        if not episodes:
            # إضافة تبويبة فارغة إذا لم تكن هناك حلقات
            empty_tab = QWidget()
            empty_layout = QVBoxLayout(empty_tab)
            empty_label = QLabel(tr("No episodes available for this season."))
            empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            empty_layout.addWidget(empty_label)
            self.episodes_tabs.addTab(empty_tab, tr("Episodes"))
            return
            
        # ترتيب الحلقات تصاعدياً
        sorted_episodes = sorted(episodes, key=lambda e: int(e.get('episode_num', 0)))
        
        # إنشاء تبويبة للحلقات
        episodes_widget = QWidget()
        episodes_layout = QVBoxLayout(episodes_widget)
        
        # قائمة للحلقات مع التمرير
        episodes_scroll = QScrollArea()
        episodes_scroll.setWidgetResizable(True)
        
        episodes_content = QWidget()
        episodes_grid = QVBoxLayout(episodes_content)
        episodes_grid.setAlignment(Qt.AlignmentFlag.AlignTop)
        episodes_grid.setSpacing(10)
        episodes_grid.setContentsMargins(10, 10, 10, 10)
        
        # إضافة كل حلقة إلى القائمة
        for episode in sorted_episodes:
            episode_widget = self._create_episode_item(episode)
            episodes_grid.addWidget(episode_widget)
            
        episodes_scroll.setWidget(episodes_content)
        episodes_layout.addWidget(episodes_scroll)
        
        # إضافة التبويبة
        tab_title = f"{tr('Season')} {season_number} - {tr('Episodes')}"
        self.episodes_tabs.addTab(episodes_widget, tab_title)
    
    def _create_episode_item(self, episode_data):
        """إنشاء عنصر واجهة لكل حلقة"""
        app = QApplication.instance()
        is_dark_theme = app and app.styleSheet() and "background-color: #121212" in app.styleSheet()
        text_color = "#FFFFFF" if is_dark_theme else "#000000"
        bg_color = "#2A2A2A" if is_dark_theme else "#F5F5F5"
        border_color = "#444444" if is_dark_theme else "#DDDDDD"
        
        # إنشاء إطار للحلقة
        episode_frame = QFrame()
        episode_frame.setFrameShape(QFrame.Shape.StyledPanel)
        episode_frame.setCursor(Qt.CursorShape.PointingHandCursor)
        episode_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 5px;
            }}
            QFrame:hover {{
                border: 1px solid #0078D7;
                background-color: {'#3A3A3A' if is_dark_theme else '#E5E5E5'};
            }}
        """)
        
        # تخطيط أفقي للحلقة
        episode_layout = QHBoxLayout(episode_frame)
        episode_layout.setContentsMargins(10, 10, 10, 10)
        
        # رقم الحلقة
        episode_num = episode_data.get('episode_num', '?')
        episode_num_label = QLabel(f"#{episode_num}")
        episode_num_label.setStyleSheet(f"""
            font-weight: bold;
            color: #0078D7;
            font-size: 18px;
            min-width: 40px;
        """)
        episode_layout.addWidget(episode_num_label)
        
        # معلومات الحلقة (العنوان والمدة)
        info_layout = QVBoxLayout()
        
        title = episode_data.get('title', f"{tr('Episode')} {episode_num}")
        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-weight: bold; color: {text_color}; font-size: 14px;")
        info_layout.addWidget(title_label)
        
        # مدة الحلقة والتاريخ إن وجد
        container_duration = episode_data.get('container_extension', '')
        added = episode_data.get('added', '')
        info_text = ""
        
        if container_duration:
            info_text += f"{container_duration.upper()}"
        
        if added:
            if info_text:
                info_text += " • "
            info_text += added
        
        if info_text:
            info_label = QLabel(info_text)
            info_label.setStyleSheet(f"color: {'#AAAAAA' if is_dark_theme else '#555555'}; font-size: 12px;")
            info_layout.addWidget(info_label)
        
        episode_layout.addLayout(info_layout)
        episode_layout.addStretch()
        
        # زر التشغيل
        play_button = QPushButton()
        play_button.setToolTip(tr("Play Episode"))
        play_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # محاولة تحميل أيقونة التشغيل
        play_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                     "resources", "icons", "play.png")
        if os.path.exists(play_icon_path):
            play_button.setIcon(QIcon(play_icon_path))
        else:
            play_button.setText("▶")
            
        play_button.setFixedSize(36, 36)
        play_button.setStyleSheet(f"""
            QPushButton {{
                background-color: #0078D7;
                border-radius: 18px;
                border: none;
                color: white;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: #0086F0;
            }}
        """)
        
        # ربط زر التشغيل بالحدث
        play_button.clicked.connect(lambda: self.play_episode(episode_data))
        episode_layout.addWidget(play_button)
        
        return episode_frame
    
    def play_episode(self, episode_data):
        """تشغيل الحلقة المحددة"""
        # إعداد بيانات الحلقة للإرسال
        episode_info = {
            'id': episode_data.get('id'),
            'name': episode_data.get('title', tr('Episode')),
            'url': episode_data.get('stream_url', ''),
            'episode_num': episode_data.get('episode_num'),
            'season_num': episode_data.get('season'),
            'series_name': self.series_data.get('name')
        }
        
        # إرسال الإشارة لتشغيل الحلقة
        self.episode_selected.emit(episode_info)
        self.accept()  # إغلاق النافذة بعد اختيار حلقة للتشغيل
    
    def resizeEvent(self, event):
        """معالجة تغيير حجم النافذة"""
        super().resizeEvent(event)
        # التأكد من أن مؤشر التحميل يغطي كامل النافذة
        if hasattr(self, 'loading_widget') and self.loading_widget:
            self.loading_widget.resize(self.size())

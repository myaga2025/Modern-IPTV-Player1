import os
import json
from PyQt6.QtCore import QObject

class ThemeManager(QObject):
    """Manages application themes and user theme preference"""
    
    DARK_THEME = "dark"
    LIGHT_THEME = "light"
    
    def __init__(self, data_dir=None, parent=None):
        # Fixed parameter order - parent comes first for QObject
        super().__init__(parent)
        
        # استخدام المسار المُمرر أو الاعتماد على المسار الافتراضي
        if data_dir:
            self.data_dir = data_dir
        else:
            # استخدام مسار AppData للمستخدم كمسار افتراضي
            self.data_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')),
                                      'Modern-IPTV-Player', 'data')
        
        # التأكد من وجود المجلد
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.settings_file = os.path.join(self.data_dir, 'theme_settings.json')
        self._current_theme = self.DARK_THEME  # Default theme
        self._load_settings()
        
    def _load_settings(self):
        """Load theme settings from file"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self._current_theme = settings.get("theme", self.DARK_THEME)
        except Exception as e:
            print(f"Error loading theme settings: {e}")
            self._current_theme = self.DARK_THEME
    
    def _save_settings(self):
        """Save theme settings to file"""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump({"theme": self._current_theme}, f, indent=2)
        except Exception as e:
            print(f"Error saving theme settings: {e}")
    
    def get_current_theme(self):
        """Get the current theme name"""
        return self._current_theme
    
    def set_theme(self, theme_name):
        """Set the theme by name"""
        if theme_name in (self.DARK_THEME, self.LIGHT_THEME):
            self._current_theme = theme_name
            self._save_settings()
            return True
        return False
    
    def get_stylesheet_path(self):
        """Get the path to the current theme's stylesheet"""
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        if self._current_theme == self.LIGHT_THEME:
            return os.path.join(base_path, "resources", "styles", "light_theme.qss")
        else:
            return os.path.join(base_path, "resources", "styles", "dark_theme.qss")
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        new_theme = self.LIGHT_THEME if self._current_theme == self.DARK_THEME else self.DARK_THEME
        self.set_theme(new_theme)
        return new_theme

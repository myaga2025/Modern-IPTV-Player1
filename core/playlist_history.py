import os
import json
import logging

logger = logging.getLogger(__name__)

class PlaylistHistory:
    """Manages playlist history"""
    
    def __init__(self, data_dir=None):
        # استخدام المسار المُمرر أو الاعتماد على المسار الافتراضي
        if data_dir:
            self.data_dir = data_dir
        else:
            # استخدام مسار AppData للمستخدم كمسار افتراضي
            self.data_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')),
                                      'Modern-IPTV-Player', 'data')
        
        # التأكد من وجود المجلد
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.history_file = os.path.join(self.data_dir, 'playlist_history.json')
    
    def save_last_playlist(self, playlist_info):
        """Save information about the last used playlist
        
        Args:
            playlist_info: Dictionary with 'type' ('file' or 'url'), 'path' or 'url', and 'name'
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(playlist_info, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved last playlist info: {playlist_info.get('name', 'Unknown')}")
            return True
        except Exception as e:
            logger.error(f"Failed to save playlist history: {e}")
            return False
    
    def load_last_playlist(self):
        """Load information about the last used playlist
        
        Returns:
            Dictionary with playlist info or None if no history exists
        """
        try:
            if not os.path.exists(self.history_file):
                logger.info("No playlist history file found")
                return None
                
            with open(self.history_file, 'r', encoding='utf-8') as f:
                playlist_info = json.load(f)
            
            logger.info(f"Loaded last playlist info: {playlist_info.get('name', 'Unknown')}")
            return playlist_info
        except Exception as e:
            logger.error(f"Failed to load playlist history: {e}")
            return None

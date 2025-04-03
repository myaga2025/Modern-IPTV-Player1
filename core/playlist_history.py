import os
import json
import logging
import datetime
import shutil

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',
    filemode='a'
)
logger = logging.getLogger('PlaylistHistory')

class PlaylistHistory:
    """Class for managing playlist loading history"""
    
    def __init__(self, data_dir=None):
        """
        Initialize playlist history manager
        
        Args:
            data_dir: Optional directory to store history files.
                      If None, default AppData directory is used.
        """
        self.data_dir = data_dir
        self.history_file = self._get_history_file_path()
        self.history = []
        self._load_history()
    
    def _get_history_file_path(self):
        """Get the path to the history file"""
        if self.data_dir is None:
            # Use default location if data_dir was not provided
            self.data_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 
                             'Modern-IPTV-Player', 'data')
        
        # Create directory if it doesn't exist
        os.makedirs(self.data_dir, exist_ok=True)
        return os.path.join(self.data_dir, 'playlist_history.json')
    
    def _load_history(self):
        """Load playlist history from file"""
        try:
            if os.path.exists(self.history_file):
                # Check if file is empty
                if os.path.getsize(self.history_file) == 0:
                    logger.warning("Playlist history file is empty, initializing with empty list")
                    self.history = []
                    # Write a valid empty JSON array to the file
                    with open(self.history_file, 'w', encoding='utf-8') as f:
                        json.dump([], f)
                    return
                
                # Read the file and attempt to parse it
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        # File contains only whitespace
                        logger.warning("Playlist history file contains only whitespace")
                        self.history = []
                        # Write a valid empty JSON array to the file
                        with open(self.history_file, 'w', encoding='utf-8') as f:
                            json.dump([], f)
                        return
                    
                    # Try to parse the content
                    try:
                        self.history = json.loads(content)
                        # Validate that it's a list
                        if not isinstance(self.history, list):
                            logger.warning("Playlist history file didn't contain a list, resetting")
                            self.history = []
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse playlist history JSON: {e}")
                        self._backup_and_reset_history_file()
            else:
                # File doesn't exist, create it with an empty list
                logger.info("No playlist history file found, creating new one")
                self.history = []
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump([], f)
        except Exception as e:
            logger.error(f"Error loading playlist history: {e}")
            self._backup_and_reset_history_file()
    
    def _backup_and_reset_history_file(self):
        """Backup corrupted history file and create a new empty one"""
        try:
            if os.path.exists(self.history_file):
                # Create backup filename with timestamp
                timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                backup_file = f"{self.history_file}.bak.{timestamp}"
                
                # Copy the file instead of renaming to preserve the original
                shutil.copy2(self.history_file, backup_file)
                logger.info(f"Backed up corrupted history file to {backup_file}")
                
                # Create new empty file
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                logger.info("Created new empty history file")
            
            # Reset history to empty list
            self.history = []
        except Exception as e:
            logger.error(f"Error during history file backup and reset: {e}")
            # Last resort: try to just create an empty file
            try:
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump([], f)
                self.history = []
            except:
                pass
    
    def save_history(self):
        """Save playlist history to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving playlist history: {e}")
            return False
    
    def add_playlist(self, playlist_info):
        """Add a playlist to the history"""
        # Add timestamp to the playlist info
        playlist_info['timestamp'] = datetime.datetime.now().isoformat()
        
        # Check if this playlist already exists in history
        for i, item in enumerate(self.history):
            if self._is_same_playlist(item, playlist_info):
                # Remove existing entry (we'll add an updated one)
                self.history.pop(i)
                break
        
        # Add to history (at the beginning)
        self.history.insert(0, playlist_info)
        
        # Keep only the last 20 entries
        if len(self.history) > 20:
            self.history = self.history[:20]
        
        # Save to file
        return self.save_history()
    
    def _is_same_playlist(self, item1, item2):
        """Check if two playlist entries refer to the same playlist"""
        if item1.get('type') != item2.get('type'):
            return False
            
        if item1.get('type') == 'file':
            return item1.get('path') == item2.get('path')
        elif item1.get('type') == 'url':
            return item1.get('url') == item2.get('url')
        elif item1.get('type') == 'xtream':
            return (item1.get('server') == item2.get('server') and 
                   item1.get('username') == item2.get('username'))
        
        return False
    
    def save_last_playlist(self, playlist_info):
        """Save the last used playlist"""
        try:
            last_playlist_file = os.path.join(self.data_dir, 'last_playlist.json')
            with open(last_playlist_file, 'w', encoding='utf-8') as f:
                json.dump(playlist_info, f, indent=2)
            
            # Also add to history
            self.add_playlist(playlist_info)
            return True
        except Exception as e:
            logger.error(f"Error saving last playlist: {e}")
            return False
    
    def load_last_playlist(self):
        """Load the last used playlist"""
        try:
            last_playlist_file = os.path.join(self.data_dir, 'last_playlist.json')
            if os.path.exists(last_playlist_file):
                # Check if file is empty
                if os.path.getsize(last_playlist_file) == 0:
                    logger.warning("Last playlist file is empty")
                    return None
                
                try:
                    with open(last_playlist_file, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if not content:
                            logger.warning("Last playlist file contains only whitespace")
                            return None
                        
                        # Try to parse the content
                        try:
                            return json.loads(content)
                        except json.JSONDecodeError as e:
                            logger.error(f"Failed to parse last playlist JSON: {e}")
                            # Backup and reset the file
                            try:
                                timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                                backup_file = f"{last_playlist_file}.bak.{timestamp}"
                                shutil.copy2(last_playlist_file, backup_file)
                                with open(last_playlist_file, 'w', encoding='utf-8') as f:
                                    json.dump({}, f)
                            except Exception as backup_err:
                                logger.error(f"Error backing up last playlist file: {backup_err}")
                except Exception as e:
                    logger.error(f"Error reading last playlist file: {e}")
            return None
        except Exception as e:
            logger.error(f"Error loading last playlist: {e}")
            return None
    
    def get_history(self):
        """Get the playlist history"""
        return self.history
    
    def clear_history(self):
        """Clear the playlist history"""
        self.history = []
        return self.save_history()

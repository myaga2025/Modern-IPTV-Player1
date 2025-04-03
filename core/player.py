import os
import sys
import platform
from PyQt6.QtCore import QTimer, pyqtSignal, QObject

class Player(QObject):
    """VLC-based media player wrapper"""
    
    # Signals
    time_changed = pyqtSignal(int)
    position_changed = pyqtSignal(float)
    media_state_changed = pyqtSignal(int)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Don't set up VLC path here - it should be handled in main.py before import
        self._vlc_available = False
        
        # Clear problematic environment variables that might cause issues
        if 'PYTHON_VLC_MODULE_PATH' in os.environ:
            del os.environ['PYTHON_VLC_MODULE_PATH']
        if 'PYTHON_VLC_LIB_PATH' in os.environ:
            del os.environ['PYTHON_VLC_LIB_PATH']
        
        try:
            # Attempt to import and initialize VLC
            import vlc
            
            # Get VLC version for debugging
            try:
                vlc_version = vlc.libvlc_get_version().decode()
                print(f"Using VLC version: {vlc_version}")
            except:
                print("Could not determine VLC version")
            
            # Try with direct initialization with more options to handle various issues
            try:
                # Use minimal options to avoid X11 issues
                if platform.system() == "Linux":
                    self.instance = vlc.Instance('--no-xlib', '--quiet')
                else:
                    self.instance = vlc.Instance('--quiet')
                
                self.media_player = self.instance.media_player_new()
                
                # Create timer for updating position
                self.update_timer = QTimer()
                self.update_timer.setInterval(1000)  # Update every second
                self.update_timer.timeout.connect(self._update_status)
                
                self._vlc_available = True
                print("VLC initialized successfully")
            except Exception as e:
                self.error_occurred.emit(f"Error creating VLC instance: {str(e)}")
                print(f"Error creating VLC instance: {e}")
        except Exception as e:
            self.error_occurred.emit(f"Error importing VLC: {str(e)}")
            print(f"Error importing VLC: {e}")
    
    def set_widget(self, widget):
        """Set window handle for rendering video"""
        if not hasattr(self, '_vlc_available') or not self._vlc_available:
            return False
            
        try:
            if platform.system() == "Linux":
                self.media_player.set_xwindow(widget.winId())
            elif platform.system() == "Windows":
                self.media_player.set_hwnd(int(widget.winId()))
            elif platform.system() == "Darwin":
                self.media_player.set_nsobject(int(widget.winId()))
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error setting video widget: {str(e)}")
            print(f"Error setting video widget: {e}")
            return False
    
    def play(self, url, name=""):
        """Play media from URL"""
        if not hasattr(self, '_vlc_available') or not self._vlc_available:
            self.error_occurred.emit("VLC is not available")
            return False
            
        try:
            import vlc
            media = self.instance.media_new(url)
            self.media_player.set_media(media)
            self.media_player.play()
            self.update_timer.start()
            return True
        except Exception as e:
            self.error_occurred.emit(str(e))
            return False
    
    def pause(self):
        """Toggle pause/play"""
        if not hasattr(self, '_vlc_available') or not self._vlc_available:
            return
        self.media_player.pause()
    
    def stop(self):
        """Stop playback"""
        if not hasattr(self, '_vlc_available') or not self._vlc_available:
            return
        self.media_player.stop()
        self.update_timer.stop()
    
    def set_volume(self, volume):
        """Set volume (0-100)"""
        if not hasattr(self, '_vlc_available') or not self._vlc_available:
            return
        self.media_player.audio_set_volume(volume)
    
    def get_volume(self):
        """Get current volume"""
        if not hasattr(self, '_vlc_available') or not self._vlc_available:
            return 0
        return self.media_player.audio_get_volume()
    
    def is_playing(self):
        """Check if player is currently playing"""
        if not hasattr(self, '_vlc_available') or not self._vlc_available:
            return False
        return self.media_player.is_playing()
    
    def get_length(self):
        """Get media length in ms"""
        if not hasattr(self, '_vlc_available') or not self._vlc_available:
            return 0
        return self.media_player.get_length()
    
    def get_time(self):
        """Get current time in ms"""
        if not hasattr(self, '_vlc_available') or not self._vlc_available:
            return 0
        return self.media_player.get_time()
    
    def set_time(self, ms):
        """Set current time in ms"""
        if not hasattr(self, '_vlc_available') or not self._vlc_available:
            return
        self.media_player.set_time(ms)
    
    def get_position(self):
        """Get current position as float 0.0-1.0"""
        if not hasattr(self, '_vlc_available') or not self._vlc_available:
            return 0.0
        return self.media_player.get_position()
    
    def set_position(self, position):
        """Set position as float 0.0-1.0"""
        if not hasattr(self, '_vlc_available') or not self._vlc_available:
            return
        self.media_player.set_position(position)
    
    def set_fullscreen(self, fullscreen):
        """Set fullscreen mode for the player"""
        try:
            if not hasattr(self, '_vlc_available') or not self._vlc_available:
                return False
                
            # Use direct media player instance instead of _player which doesn't exist
            self.media_player.set_fullscreen(fullscreen)
            return True
        except Exception as e:
            print(f"Error setting fullscreen mode: {e}")
            return False
    
    def _update_status(self):
        """Update time and position"""
        if not hasattr(self, '_vlc_available') or not self._vlc_available:
            return
            
        current_time = self.get_time()
        self.time_changed.emit(current_time)
        
        current_pos = self.get_position()
        self.position_changed.emit(current_pos)

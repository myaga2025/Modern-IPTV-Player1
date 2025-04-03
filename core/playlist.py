import json
import os
from datetime import datetime
from core.language_manager import tr

class Playlist:
    """Custom playlist manager"""
    
    def __init__(self, name="", channels=None):
        self.name = name
        self.channels = channels or []
        self.created = datetime.now().isoformat()
        self.last_updated = self.created
    
    def add_channel(self, channel):
        """Add channel to playlist"""
        # Avoid duplicates by URL
        if not any(ch.url == channel.url for ch in self.channels):
            self.channels.append(channel)
            self.last_updated = datetime.now().isoformat()
            return True
        return False
    
    def remove_channel(self, channel):
        """Remove channel from playlist"""
        for i, ch in enumerate(self.channels):
            if ch.url == channel.url:
                self.channels.pop(i)
                self.last_updated = datetime.now().isoformat()
                return True
        return False
    
    def to_dict(self):
        """Convert playlist to dictionary"""
        return {
            'name': self.name,
            'created': self.created,
            'last_updated': self.last_updated,
            'channels': [ch.__dict__ for ch in self.channels]
        }

class PlaylistManager:
    """Manage multiple playlists"""
    
    def __init__(self, save_dir="playlists"):
        self.save_dir = save_dir
        self.playlists = {}
        
        # Create save directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
        
        # Load existing playlists
        self.load_playlists()
    
    def load_playlists(self):
        """Load playlists from disk"""
        if not os.path.exists(self.save_dir):
            return
        
        for filename in os.listdir(self.save_dir):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.save_dir, filename), 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    playlist = Playlist(name=data['name'])
                    playlist.created = data['created']
                    playlist.last_updated = data['last_updated']
                    
                    from core.m3u_parser import Channel
                    for ch_data in data['channels']:
                        channel = Channel(
                            name=ch_data['name'],
                            url=ch_data['url'],
                            logo=ch_data['logo'],
                            group=ch_data.get('group', ''),
                            quality=ch_data.get('quality', '')
                        )
                        playlist.channels.append(channel)
                    
                    self.playlists[playlist.name] = playlist
                except Exception as e:
                    print(f"Error loading playlist {filename}: {e}")
    
    def save_playlist(self, playlist):
        """Save playlist to disk"""
        filename = f"{playlist.name.replace(' ', '_')}.json"
        filepath = os.path.join(self.save_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(playlist.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Update memory copy
        self.playlists[playlist.name] = playlist
        
        return filepath
    
    def create_playlist(self, name):
        """Create a new empty playlist"""
        if name in self.playlists:
            return self.playlists[name]
        
        playlist = Playlist(name=name)
        self.playlists[name] = playlist
        self.save_playlist(playlist)
        return playlist
    
    def delete_playlist(self, name):
        """Delete playlist"""
        if name not in self.playlists:
            return False
        
        # Remove from memory
        del self.playlists[name]
        
        # Remove from disk
        filename = f"{name.replace(' ', '_')}.json"
        filepath = os.path.join(self.save_dir, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return True
    
    def rename_playlist(self, old_name, new_name):
        """Rename a playlist"""
        if old_name not in self.playlists or new_name in self.playlists:
            return False
        
        # Get the playlist
        playlist = self.playlists[old_name]
        
        # Remove old file
        old_filename = f"{old_name.replace(' ', '_')}.json"
        old_filepath = os.path.join(self.save_dir, old_filename)
        if os.path.exists(old_filepath):
            os.remove(old_filepath)
        
        # Update playlist name
        playlist.name = new_name
        
        # Remove from dictionary with old name
        del self.playlists[old_name]
        
        # Add with new name
        self.playlists[new_name] = playlist
        
        # Save with new name
        self.save_playlist(playlist)
        
        return True
    
    def add_channel_to_playlist(self, playlist_name, channel):
        """Add channel to specified playlist"""
        if playlist_name not in self.playlists:
            return False
        
        if self.playlists[playlist_name].add_channel(channel):
            self.save_playlist(self.playlists[playlist_name])
            return True
        return False
    
    def remove_channel_from_playlist(self, playlist_name, channel):
        """Remove channel from specified playlist"""
        if playlist_name not in self.playlists:
            return False
        
        if self.playlists[playlist_name].remove_channel(channel):
            self.save_playlist(self.playlists[playlist_name])
            return True
        return False
    
    def get_playlist_history(self):
        """Get list of playlists with metadata"""
        history = []
        for name, playlist in self.playlists.items():
            history.append({
                'name': name,
                'created': playlist.created,
                'last_updated': playlist.last_updated,
                'channel_count': len(playlist.channels)
            })
        
        # Sort by last updated (newest first)
        history.sort(key=lambda x: x['last_updated'], reverse=True)
        return history

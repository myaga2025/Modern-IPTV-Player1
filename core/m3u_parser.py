import re
import requests
from urllib.parse import urlparse

# Add Channel class definition to fix import issues
class Channel:
    """Class to represent a channel with all its attributes"""
    
    def __init__(self, channel_dict=None):
        """Initialize a Channel object from dictionary or with default values"""
        if channel_dict is None:
            channel_dict = {}
            
        self.id = channel_dict.get('id', 0)
        self.name = channel_dict.get('name', 'Unknown Channel')
        self.url = channel_dict.get('url', '')
        self.group = channel_dict.get('group', 'Unknown')
        self.logo = channel_dict.get('logo', '')
        self.epg_id = channel_dict.get('epg_id', '')
        self.language = channel_dict.get('language', '')
        self.country = channel_dict.get('country', '')
        self.category = channel_dict.get('category', '')
        self.stream_id = channel_dict.get('stream_id', '')
        
        # Add any additional attributes from the dictionary
        for key, value in channel_dict.items():
            if not hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert Channel object to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'group': self.group,
            'logo': self.logo,
            'epg_id': self.epg_id,
            'language': self.language,
            'country': self.country,
            'category': self.category,
            'stream_id': self.stream_id
        }
    
    def __str__(self):
        return f"Channel({self.name}, {self.group})"

class M3UParser:
    """Parser for M3U playlists"""
    
    def __init__(self):
        self.channels = []
        self.groups = []
        self.file_path = None
    
    def load_from_file(self, file_path):
        """Load and parse M3U file from local path"""
        self.file_path = file_path
        try:
            if file_path.lower().endswith(('.json')):
                # Handle JSON playlist
                import json
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = json.load(file)
                    
                # Convert JSON to channels
                self.channels = self._parse_json(content)
            else:
                # Handle M3U playlist
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                self.channels = self.parse_content(content)
                
            # Build groups list after parsing
            self._build_groups_list()
            return True
        except Exception as e:
            print(f"Error loading playlist {file_path}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_from_url(self, url):
        """Load and parse M3U from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            content = response.text
            
            if url.lower().endswith('.json'):
                # Handle JSON playlist from URL
                import json
                content_json = response.json()
                self.channels = self._parse_json(content_json)
            else:
                # Handle M3U playlist from URL
                self.channels = self.parse_content(content)
                
            # Build groups list after parsing
            self._build_groups_list()
            return True
        except Exception as e:
            print(f"Error loading playlist from URL: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _parse_json(self, content):
        """Parse JSON playlist content and convert to channels"""
        channels = []
        
        if isinstance(content, list):
            # List of channel objects
            for i, item in enumerate(content):
                if isinstance(item, dict):
                    item['id'] = i
                    channels.append(item)
        elif isinstance(content, dict):
            # Dictionary with channels
            if 'channels' in content and isinstance(content['channels'], list):
                for i, item in enumerate(content['channels']):
                    if isinstance(item, dict):
                        item['id'] = i
                        channels.append(item)
        
        return channels
    
    def _build_groups_list(self):
        """Build list of unique groups from parsed channels"""
        groups_set = set()
        for channel in self.channels:
            if 'group' in channel and channel['group']:
                groups_set.add(channel['group'])
        
        self.groups = sorted(list(groups_set))
    
    def parse_file(self, file_path):
        """Parse M3U file from local path (legacy method)"""
        return self.load_from_file(file_path)
    
    def parse_url(self, url):
        """Parse M3U file from URL (legacy method)"""
        return self.load_from_url(url)
    
    def parse_content(self, content):
        """Parse M3U content"""
        if not content or not content.strip():
            raise ValueError("Empty playlist content")
            
        if not content.strip().startswith("#EXTM3U"):
            raise ValueError("Invalid M3U format")
        
        channels = []
        groups_set = set()
        
        lines = content.strip().split("\n")
        
        # Parse all lines
        channel = {}
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("#EXTINF:"):
                # Parse channel info
                channel = self._parse_extinf(line, i)
            elif not line.startswith('#') and channel:
                # URL line after #EXTINF
                channel['url'] = line
                channel['id'] = len(channels)
                channels.append(channel)
                
                if 'group' in channel and channel['group']:
                    groups_set.add(channel['group'])
                    
                channel = {}
        
        # Update groups list
        self.groups = sorted(list(groups_set))
        
        return channels
    
    def _parse_extinf(self, line, index):
        """Parse EXTINF line to extract channel details"""
        channel = {
            'name': f"Channel {index}",
            'group': 'Unknown',
            'logo': ''
        }
        
        # Extract name
        name_match = re.search(r',\s*([^,]+)$', line)
        if name_match:
            channel['name'] = name_match.group(1).strip()
        
        # Extract group/category
        group_match = re.search(r'group-title="([^"]*)"', line)
        if group_match:
            channel['group'] = group_match.group(1)
        
        # Extract logo URL
        logo_match = re.search(r'tvg-logo="([^"]*)"', line)
        if logo_match:
            channel['logo'] = logo_match.group(1)
        
        # Extract EPG ID if available
        epg_match = re.search(r'tvg-id="([^"]*)"', line)
        if epg_match:
            channel['epg_id'] = epg_match.group(1)
        
        return channel
    
    def get_channels_by_group(self, group):
        """Get channels filtered by group"""
        return [ch for ch in self.channels if ch.get('group', 'Unknown') == group]
    
    def search_channels(self, query):
        """Search channels by name"""
        query = query.lower()
        return [ch for ch in self.channels if query in ch.get('name', '').lower()]
    
    def create_channel_object(self, channel_dict):
        """Create a Channel object from a dictionary"""
        return Channel(channel_dict)

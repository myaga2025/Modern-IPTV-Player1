import re
import requests
from urllib.parse import urlparse

class M3UParser:
    """Parser for M3U playlists"""
    
    def __init__(self):
        self.channels = []
        self.groups = []
        self.file_path = None
    
    def parse_file(self, file_path):
        """Parse M3U file from local path"""
        self.file_path = file_path
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            return self.parse_content(content)
        except Exception as e:
            print(f"Error parsing M3U file: {e}")
            raise
    
    def parse_url(self, url):
        """Parse M3U file from URL"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            content = response.text
            return self.parse_content(content)
        except Exception as e:
            print(f"Error downloading M3U file: {e}")
            raise
    
    def parse_content(self, content):
        """Parse M3U content"""
        if not content or not content.strip():
            raise ValueError("Empty playlist content")
            
        if not content.strip().startswith("#EXTM3U"):
            raise ValueError("Invalid M3U format")
        
        self.channels = []
        self.groups = []
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
                channel['id'] = len(self.channels)
                self.channels.append(channel)
                
                if 'group' in channel and channel['group']:
                    groups_set.add(channel['group'])
                    
                channel = {}
        
        # Update groups list
        self.groups = sorted(list(groups_set))
        
        return self.channels
    
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
        
        return channel
    
    def get_channels_by_group(self, group):
        """Get channels filtered by group"""
        return [ch for ch in self.channels if ch.get('group', 'Unknown') == group]
    
    def search_channels(self, query):
        """Search channels by name"""
        query = query.lower()
        return [ch for ch in self.channels if query in ch.get('name', '').lower()]

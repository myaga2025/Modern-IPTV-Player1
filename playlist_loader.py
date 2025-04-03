import requests
import re
import os
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PlaylistLoader:
    def __init__(self):
        self.channels = []
    
    def load_from_url(self, url):
        """Load an M3U playlist from a URL with proper error handling"""
        try:
            logger.info(f"Attempting to load playlist from URL: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()  # Raise exception for HTTP errors
            content = response.text
            
            # Check if response is JSON
            if response.headers.get('Content-Type', '').startswith('application/json'):
                logger.info("Detected JSON response, parsing as JSON")
                return self.parse_json_content(content)
            else:
                logger.info("Parsing as M3U content")
                return self.parse_m3u_content(content)
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error when loading playlist: {e}")
            raise ValueError(f"Failed to load playlist: {e}")
        except Exception as e:
            logger.error(f"Error parsing playlist: {e}")
            raise ValueError(f"Failed to parse playlist: {e}")
    
    def load_from_file(self, file_path):
        """Load an M3U playlist from a local file"""
        try:
            logger.info(f"Attempting to load playlist from file: {file_path}")
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Playlist file not found: {file_path}")
                
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
            return self.parse_m3u_content(content)
        except Exception as e:
            logger.error(f"Error loading file: {e}")
            raise ValueError(f"Failed to load playlist file: {e}")
    
    def parse_m3u_content(self, content):
        """Parse M3U content into a structured format"""
        if not content or not content.strip():
            raise ValueError("Empty playlist content")
            
        if not content.strip().startswith("#EXTM3U"):
            raise ValueError("Invalid M3U format - missing #EXTM3U header")
        
        channels = []
        lines = content.strip().split("\n")
        
        # Simple state machine for parsing
        current_info = {}
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith("#EXTINF:"):
                # Parse channel info line
                try:
                    current_info = self._parse_extinf_line(line)
                except Exception as e:
                    logger.warning(f"Error parsing EXTINF line {i+1}: {e}, skipping")
                    current_info = {"name": f"Unknown Channel {i}", "group": "Unknown"}
            
            elif not line.startswith('#') and current_info:
                # This should be a URL line following an EXTINF line
                if "name" not in current_info:
                    current_info["name"] = f"Channel {len(channels) + 1}"
                    
                channel = {
                    "name": current_info.get("name", f"Channel {len(channels) + 1}"),
                    "url": line,
                    "group": current_info.get("group", "Unknown"),
                    "logo": current_info.get("logo", ""),
                    "id": len(channels)
                }
                channels.append(channel)
                current_info = {}
        
        logger.info(f"Successfully parsed {len(channels)} channels")
        return channels
    
    def parse_json_content(self, content):
        """Parse JSON playlist content"""
        try:
            data = json.loads(content)
            channels = []
            
            # Log the JSON structure to help debug
            logger.debug(f"JSON structure: {json.dumps(data)[:500]}...")
            
            # Handle different JSON formats
            if isinstance(data, list):
                # Direct list of channels
                for i, item in enumerate(data):
                    channel = self._normalize_channel(item, i)
                    channels.append(channel)
            elif isinstance(data, dict):
                # Handle nested structures
                if "channels" in data:
                    for i, item in enumerate(data["channels"]):
                        channel = self._normalize_channel(item, i)
                        channels.append(channel)
                else:
                    # Try to extract channels from other properties
                    for key, value in data.items():
                        if isinstance(value, list):
                            for i, item in enumerate(value):
                                if isinstance(item, dict) and "url" in item:
                                    channel = self._normalize_channel(item, len(channels))
                                    channels.append(channel)
            
            logger.info(f"Successfully parsed {len(channels)} channels from JSON")
            return channels
        except Exception as e:
            logger.error(f"Error parsing JSON content: {e}")
            raise ValueError(f"Failed to parse JSON playlist: {e}")
    
    def _normalize_channel(self, item, index):
        """Normalize a channel object to ensure it has all required fields"""
        if not isinstance(item, dict):
            # Convert non-dict items to dict if possible
            if isinstance(item, str) and item.startswith('http'):
                return {
                    "name": f"Channel {index + 1}",
                    "url": item,
                    "group": "Unknown",
                    "logo": "",
                    "id": index
                }
            # If not convertible, create a placeholder
            return {
                "name": f"Channel {index + 1}",
                "url": "",
                "group": "Unknown",
                "logo": "",
                "id": index
            }
        
        # For dictionaries, ensure all required fields
        return {
            "name": item.get("name", item.get("title", f"Channel {index + 1}")),
            "url": item.get("url", item.get("stream", "")),
            "group": item.get("group", item.get("category", "Unknown")),
            "logo": item.get("logo", item.get("thumbnail", item.get("icon", ""))),
            "id": item.get("id", index)
        }
    
    def _parse_extinf_line(self, line):
        """Parse an EXTINF line to extract channel metadata"""
        info = {}
        
        # Extract channel name
        name_match = re.search(r',\s*([^,]+)$', line)
        if name_match:
            info["name"] = name_match.group(1).strip()
        else:
            info["name"] = "Unknown Channel"
            
        # Extract group
        group_match = re.search(r'group-title="([^"]*)"', line)
        if group_match:
            info["group"] = group_match.group(1)
        else:
            info["group"] = "Unknown"
            
        # Extract logo URL
        logo_match = re.search(r'tvg-logo="([^"]*)"', line)
        if logo_match:
            info["logo"] = logo_match.group(1)
                
        return info

# Helper function for external use
def load_playlist_from_url(url):
    """Load playlist from URL with additional error handling"""
    loader = PlaylistLoader()
    try:
        return loader.load_from_url(url)
    except Exception as e:
        logger.error(f"Failed to load URL playlist: {e}")
        # Return empty list instead of raising exception
        return []

def load_playlist_from_file(file_path):
    """Load playlist from file with additional error handling"""
    loader = PlaylistLoader()
    try:
        return loader.load_from_file(file_path)
    except Exception as e:
        logger.error(f"Failed to load file playlist: {e}")
        # Return empty list instead of raising exception
        return []

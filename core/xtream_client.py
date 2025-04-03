import requests
import json
import logging
import os
from urllib.parse import urljoin
from datetime import datetime

# Configure logging
log_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'Modern-IPTV-Player', 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'xtream_api.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('XtreamClient')

class XtreamClient:
    """Client for Xtream API connection and data retrieval"""
    
    def __init__(self, server_url, username, password):
        """Initialize the Xtream client with server details"""
        self.server_url = self._normalize_url(server_url)
        self.username = username
        self.password = password
        self.categories = []
        self.movie_categories = []  # New: Movie categories
        self.series_categories = []  # New: Series categories
        self.channels = []
        self.movies = []  # New: Movies list
        self.series = []  # New: Series list
        self.server_info = {}
        self.user_info = {}
        self.connection_successful = False
        logger.info(f"Initialized Xtream client for server: {self.server_url}")
    
    def _normalize_url(self, url):
        """Ensure URL has proper format and ends with a slash"""
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        if not url.endswith('/'):
            url += '/'
        return url
    
    def connect(self):
        """Connect to Xtream API and get user information"""
        try:
            logger.info(f"Connecting to Xtream server: {self.server_url}")
            # Perform API request for user authentication
            auth_url = f"{self.server_url}player_api.php?username={self.username}&password={self.password}"
            response = requests.get(auth_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "user_info" in data:
                    self.user_info = data.get("user_info", {})
                    self.server_info = data.get("server_info", {})
                    self.connection_successful = True
                    
                    logger.info(f"Connected successfully. User: {self.username}, Status: {self.user_info.get('status', 'Unknown')}")
                    logger.info(f"Expiration date: {self.user_info.get('exp_date', 'N/A')}")
                    
                    # If connection was successful, also fetch VOD and Series categories
                    self.get_vod_categories()
                    self.get_series_categories()
                    
                    return True, "Connected successfully"
                else:
                    error_msg = "Invalid username or password"
                    logger.error(error_msg)
                    return False, error_msg
            else:
                error_msg = f"Connection failed with status code: {response.status_code}"
                logger.error(error_msg)
                return False, error_msg
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Error connecting to Xtream server: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def get_live_categories(self):
        """Get list of live TV categories"""
        if not self.connection_successful:
            logger.warning("Cannot get categories: No active connection")
            return []
        
        try:
            url = f"{self.server_url}player_api.php?username={self.username}&password={self.password}&action=get_live_categories"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                categories = response.json()
                self.categories = categories
                logger.info(f"Retrieved {len(categories)} live categories")
                return categories
            else:
                logger.error(f"Failed to get categories. Status code: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting live categories: {str(e)}")
            return []
    
    def get_live_streams(self, category_id=None):
        """Get list of live streams, optionally filtered by category ID"""
        if not self.connection_successful:
            logger.warning("Cannot get streams: No active connection")
            return []
            
        try:
            # Set API URL based on whether we're filtering by category
            if category_id:
                url = f"{self.server_url}player_api.php?username={self.username}&password={self.password}&action=get_live_streams&category_id={category_id}"
            else:
                url = f"{self.server_url}player_api.php?username={self.username}&password={self.password}&action=get_live_streams"
                
            response = requests.get(url, timeout=15)  # Longer timeout for potentially large lists
            
            if response.status_code == 200:
                streams = response.json()
                
                # If we fetched all streams, store them
                if not category_id:
                    self.channels = self._convert_to_channel_format(streams)
                    logger.info(f"Retrieved {len(streams)} live streams")
                
                return streams if category_id else self.channels
            else:
                logger.error(f"Failed to get streams. Status code: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting live streams: {str(e)}")
            return []
    
    def get_vod_categories(self):
        """Get list of VOD (movie) categories"""
        if not self.connection_successful:
            logger.warning("Cannot get VOD categories: No active connection")
            return []
        
        try:
            url = f"{self.server_url}player_api.php?username={self.username}&password={self.password}&action=get_vod_categories"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                categories = response.json()
                self.movie_categories = categories
                logger.info(f"Retrieved {len(categories)} VOD categories")
                return categories
            else:
                logger.error(f"Failed to get VOD categories. Status code: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting VOD categories: {str(e)}")
            return []
    
    def get_series_categories(self):
        """Get list of series categories"""
        if not self.connection_successful:
            logger.warning("Cannot get series categories: No active connection")
            return []
        
        try:
            url = f"{self.server_url}player_api.php?username={self.username}&password={self.password}&action=get_series_categories"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                categories = response.json()
                self.series_categories = categories
                logger.info(f"Retrieved {len(categories)} series categories")
                return categories
            else:
                logger.error(f"Failed to get series categories. Status code: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting series categories: {str(e)}")
            return []
    
    def get_vod_streams(self, category_id=None):
        """Get list of VOD (movie) streams, optionally filtered by category ID"""
        if not self.connection_successful:
            logger.warning("Cannot get VOD streams: No active connection")
            return []
            
        try:
            # Set API URL based on whether we're filtering by category
            if category_id:
                url = f"{self.server_url}player_api.php?username={self.username}&password={self.password}&action=get_vod_streams&category_id={category_id}"
            else:
                url = f"{self.server_url}player_api.php?username={self.username}&password={self.password}&action=get_vod_streams"
                
            response = requests.get(url, timeout=20)  # Longer timeout for VOD lists
            
            if response.status_code == 200:
                streams = response.json()
                
                # If we fetched all streams, store them
                if not category_id:
                    self.movies = self._convert_to_movie_format(streams)
                    logger.info(f"Retrieved {len(streams)} VOD streams")
                
                return streams if category_id else self.movies
            else:
                logger.error(f"Failed to get VOD streams. Status code: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting VOD streams: {str(e)}")
            return []
    
    def get_series(self, category_id=None):
        """Get list of series, optionally filtered by category ID"""
        if not self.connection_successful:
            logger.warning("Cannot get series: No active connection")
            return []
            
        try:
            # Set API URL based on whether we're filtering by category
            if category_id:
                url = f"{self.server_url}player_api.php?username={self.username}&password={self.password}&action=get_series&category_id={category_id}"
            else:
                url = f"{self.server_url}player_api.php?username={self.username}&password={self.password}&action=get_series"
                
            response = requests.get(url, timeout=20)  # Longer timeout for series lists
            
            if response.status_code == 200:
                series_list = response.json()
                
                # If we fetched all series, store them
                if not category_id:
                    self.series = self._convert_to_series_format(series_list)
                    logger.info(f"Retrieved {len(series_list)} series")
                
                return series_list if category_id else self.series
            else:
                logger.error(f"Failed to get series. Status code: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting series: {str(e)}")
            return []
    
    def get_series_info(self, series_id):
        """Get detailed information about a specific series including episodes"""
        if not self.connection_successful:
            logger.warning("Cannot get series info: No active connection")
            return {}
            
        try:
            logger.info(f"Retrieving series info for series ID: {series_id}")
            
            url = f"{self.server_url}player_api.php?username={self.username}&password={self.password}&action=get_series_info&series_id={series_id}"
            response = requests.get(url, timeout=20)  # زيادة مهلة الانتظار لتجنب مشاكل التوقيف
            
            if response.status_code == 200:
                series_info = response.json()
                logger.info(f"Retrieved info for series ID {series_id}")
                
                # طباعة معلومات التصحيح للمساعدة في تحديد المشكلات
                if 'info' in series_info:
                    logger.info(f"Series info contains information section")
                    if 'seasons' in series_info['info']:
                        logger.info(f"Found {len(series_info['info']['seasons'])} seasons")
                
                if 'episodes' in series_info:
                    logger.info(f"Found {len(series_info['episodes'])} episodes")
                else:
                    logger.warning("No episodes found in series info")
                
                return series_info
            else:
                logger.error(f"Failed to get series info. Status code: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting series info: {str(e)}")
            return {}
    
    def get_series_seasons(self, series_id):
        """Get seasons for a series by ID"""
        if not self.connection_successful:
            logger.warning("Cannot get series seasons: No active connection")
            return []
        
        try:
            logger.info(f"Retrieving seasons for series ID: {series_id}")
            
            # Get complete series info which includes seasons
            series_info = self.get_series_info(series_id)
            
            if 'info' in series_info and 'seasons' in series_info['info']:
                seasons = series_info['info']['seasons']
                logger.info(f"Retrieved {len(seasons)} seasons for series ID {series_id}")
                return seasons
            else:
                logger.warning(f"No seasons found for series ID {series_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching series seasons: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def get_series_episodes(self, series_id, season_id):
        """Get episodes for a specific season of a series"""
        if not self.connection_successful:
            logger.warning("Cannot get series episodes: No active connection")
            return []
        
        try:
            logger.info(f"Retrieving episodes for series ID {series_id}, season ID {season_id}")
            
            # Get complete series info which includes episodes
            series_info = self.get_series_info(series_id)
            
            if 'episodes' in series_info:
                # Filter episodes for the requested season only
                all_episodes = series_info['episodes']
                season_episodes = [ep for ep in all_episodes 
                                 if str(ep.get('season_id', '')) == str(season_id)]
                
                # Add stream URL for each episode
                for episode in season_episodes:
                    episode_id = episode.get('id', '')
                    
                    # Build stream URL for the episode
                    stream_url = f"{self.server_url}series/{self.username}/{self.password}/{episode_id}.{episode.get('container_extension', 'mp4')}"
                    episode['stream_url'] = stream_url
                
                # ترتيب الحلقات حسب الرقم
                season_episodes.sort(key=lambda ep: int(ep.get('episode_num', 0)))
                
                logger.info(f"Retrieved {len(season_episodes)} episodes for series ID {series_id}, season ID {season_id}")
                return season_episodes
            else:
                logger.warning(f"No episodes found for series ID {series_id}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching series episodes: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []

    def _convert_to_channel_format(self, xtream_streams):
        """Convert Xtream API stream format to our channel format"""
        channels = []
        
        for idx, stream in enumerate(xtream_streams):
            try:
                # Get category name
                category_name = "Unknown"
                for category in self.categories:
                    if category.get('category_id') == stream.get('category_id'):
                        category_name = category.get('category_name', 'Unknown')
                        break
                
                # Build channel object
                channel = {
                    "id": idx,
                    "name": stream.get('name', f"Channel {idx}"),
                    "url": self._build_stream_url(stream.get('stream_id')),
                    "group": category_name,
                    "logo": stream.get('stream_icon', ''),
                    "epg_channel_id": stream.get('epg_channel_id', ''),
                    "stream_id": stream.get('stream_id', '')
                }
                channels.append(channel)
            except Exception as e:
                logger.error(f"Error converting stream {stream.get('name', 'Unknown')}: {str(e)}")
                continue
                
        return channels
    
    def _convert_to_movie_format(self, vod_streams):
        """Convert Xtream API VOD stream format to our movie format"""
        movies = []
        
        for idx, stream in enumerate(vod_streams):
            try:
                # Get category name
                category_name = "Unknown"
                for category in self.movie_categories:
                    if category.get('category_id') == stream.get('category_id'):
                        category_name = category.get('category_name', 'Unknown')
                        break
                
                # Build movie object
                movie = {
                    "id": idx,
                    "stream_id": stream.get('stream_id', ''),
                    "name": stream.get('name', f"Movie {idx}"),
                    "url": self._build_movie_url(stream.get('stream_id')),
                    "group": category_name,
                    "poster": stream.get('stream_icon', ''),
                    "cover": stream.get('cover', ''),
                    "plot": stream.get('plot', ''),
                    "cast": stream.get('cast', ''),
                    "director": stream.get('director', ''),
                    "genre": stream.get('genre', ''),
                    "release_date": stream.get('releasedate', ''),
                    "rating": stream.get('rating', ''),
                    "duration": stream.get('duration', ''),
                    "type": "movie"  # To distinguish from channels and series
                }
                movies.append(movie)
            except Exception as e:
                logger.error(f"Error converting VOD stream {stream.get('name', 'Unknown')}: {str(e)}")
                continue
                
        return movies
    
    def _convert_to_series_format(self, series_list):
        """Convert Xtream API series format to our series format"""
        series_items = []
        
        for idx, series in enumerate(series_list):
            try:
                # Get category name
                category_name = "Unknown"
                for category in self.series_categories:
                    if category.get('category_id') == series.get('category_id'):
                        category_name = category.get('category_name', 'Unknown')
                        break
                
                # Build series object
                series_item = {
                    "id": idx,
                    "series_id": series.get('series_id', ''),
                    "name": series.get('name', f"Series {idx}"),
                    "group": category_name,
                    "poster": series.get('cover', ''),
                    "cover": series.get('backdrop_path', ''),
                    "plot": series.get('plot', ''),
                    "cast": series.get('cast', ''),
                    "director": series.get('director', ''),
                    "genre": series.get('genre', ''),
                    "release_date": series.get('releaseDate', ''),
                    "rating": series.get('rating', ''),
                    "episodes": {},  # Will be populated when viewing the series
                    "type": "series"  # To distinguish from channels and movies
                }
                series_items.append(series_item)
            except Exception as e:
                logger.error(f"Error converting series {series.get('name', 'Unknown')}: {str(e)}")
                continue
                
        return series_items
    
    def _build_stream_url(self, stream_id):
        """Build the playable stream URL for a given stream_id"""
        return f"{self.server_url}live/{self.username}/{self.password}/{stream_id}.ts"
    
    def _build_movie_url(self, stream_id):
        """Build the playable VOD URL for a given stream_id"""
        return f"{self.server_url}movie/{self.username}/{self.password}/{stream_id}.mp4"
    
    def _build_series_url(self, series_id, season, episode):
        """Build the playable series URL for a given episode"""
        return f"{self.server_url}series/{self.username}/{self.password}/{series_id}/{season}/{episode}.mp4"
    
    def get_account_status(self):
        """Get current account status information"""
        if not self.user_info:
            return {}
            
        # Calculate days remaining if expiration date exists
        days_remaining = None
        if self.user_info.get('exp_date'):
            try:
                exp_timestamp = int(self.user_info.get('exp_date', 0))
                if exp_timestamp > 0:
                    exp_date = datetime.fromtimestamp(exp_timestamp)
                    days_remaining = (exp_date - datetime.now()).days
            except Exception:
                pass
                
        return {
            "username": self.username,
            "status": self.user_info.get('status', 'Unknown'),
            "max_connections": self.user_info.get('max_connections', 'Unknown'),
            "expiration_date": self.user_info.get('exp_date', 'Never'),
            "days_remaining": days_remaining,
            "active_connections": self.user_info.get('active_cons', 0),
            "created_at": self.user_info.get('created_at', 'Unknown')
        }

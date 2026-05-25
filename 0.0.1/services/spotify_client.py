import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import Config
from models.track import Track
from utils.logger import logger
from typing import List, Dict, Any, Optional


class SpotifyClient:
    def __init__(self):
        if not Config.CLIENT_ID or not Config.CLIENT_SECRET:
            logger.error("Spotify credentials not found in .env")
            self.sp = None
            return

        scope = "playlist-modify-public playlist-modify-private user-library-modify"
        auth_manager = SpotifyOAuth(
            client_id=Config.CLIENT_ID,
            client_secret=Config.CLIENT_SECRET,
            redirect_uri=Config.REDIRECT_URI,
            scope=scope,
        )
        self.sp = spotipy.Spotify(auth_manager=auth_manager)

    def create_playlist(self, name: str, tracks: List[str]):
        """
        Creates a new playlist and adds tracks by their IDs
        """
        if not self.sp:
            return
        try:
            user_id = self.sp.current_user()["id"]
            playlist = self.sp.user_playlist_create(user_id, name)
            self.sp.playlist_add_items(playlist["id"], tracks)
            logger.info(f"Created playlist {name} with {len(tracks)} tracks")
            return playlist
        except Exception as e:
            logger.error(f"Error creating playlist: {e}")
            return None

    def get_track_info(self, url: str) -> List[Track]:
        if not self.sp:
            return []

        try:
            if "track" in url:
                return [self._parse_track(self.sp.track(url))]
            elif "album" in url:
                album = self.sp.album(url)
                return [self._parse_track(t, album) for t in album["tracks"]["items"]]
            elif "playlist" in url:
                results = self.sp.playlist_tracks(url)
                tracks = results["items"]
                while results["next"]:
                    results = self.sp.next(results)
                    tracks.extend(results["items"])
                return [self._parse_track(t["track"]) for t in tracks if t["track"]]
        except Exception as e:
            logger.error(f"Error fetching Spotify data: {e}")
        return []

    def _parse_track(
        self, data: Dict[str, Any], album_data: Optional[Dict[str, Any]] = None
    ) -> Track:
        album = album_data or data.get("album", {})
        return Track(
            id=data["id"],
            title=data["name"],
            artist=data["artists"][0]["name"],
            album=album.get("name", "Unknown Album"),
            duration_ms=data["duration_ms"],
            cover_url=album.get("images", [{}])[0].get("url", ""),
            release_date=album.get("release_date", "Unknown"),
            spotify_url=data["external_urls"]["spotify"],
            track_number=data["track_number"],
            disc_number=data["disc_number"],
        )

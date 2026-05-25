import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Spotify
    CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
    CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
    REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI", "http://localhost:8888/callback")

    # Paths
    BASE_DIR = Path(__file__).parent
    DEFAULT_DOWNLOAD_DIR = Path(
        os.getenv("DEFAULT_DOWNLOAD_PATH", BASE_DIR / "downloads")
    )
    DATABASE_PATH = BASE_DIR / "library.db"
    LOG_FILE = BASE_DIR / "app.log"

    # Defaults
    QUALITY = os.getenv("DEFAULT_QUALITY", "320")
    FORMAT = os.getenv("DEFAULT_FORMAT", "mp3")
    DOWNLOAD_COVERS = os.getenv("DOWNLOAD_COVERS", "True").lower() == "true"
    SAVE_LYRICS = os.getenv("SAVE_LYRICS", "True").lower() == "true"
    SAVE_METADATA = os.getenv("SAVE_METADATA", "True").lower() == "true"
    THEME = os.getenv("THEME", "dark")

    @classmethod
    def ensure_dirs(cls):
        cls.DEFAULT_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

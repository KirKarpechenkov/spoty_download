import sqlite3
from config import Config
from models.track import Track
from utils.logger import logger


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DATABASE_PATH, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id TEXT PRIMARY KEY,
                title TEXT,
                artist TEXT,
                album TEXT,
                duration_ms INTEGER,
                cover_url TEXT,
                release_date TEXT,
                spotify_url TEXT,
                file_path TEXT,
                download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def add_track(self, track: Track):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO history 
                (id, title, artist, album, duration_ms, cover_url, release_date, spotify_url, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    track.id,
                    track.title,
                    track.artist,
                    track.album,
                    track.duration_ms,
                    track.cover_url,
                    track.release_date,
                    track.spotify_url,
                    track.file_path,
                ),
            )
            self.conn.commit()
        except Exception as e:
            logger.error(f"Database error: {e}")

    def get_history(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM history ORDER BY download_date DESC")
        return cursor.fetchall()

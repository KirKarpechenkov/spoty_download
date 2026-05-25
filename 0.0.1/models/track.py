from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Track:
    id: str
    title: str
    artist: str
    album: str
    duration_ms: int
    cover_url: str
    release_date: str
    spotify_url: str
    track_number: int = 1
    disc_number: int = 1
    genre: Optional[str] = None
    lyrics: Optional[str] = None
    file_path: Optional[str] = None
    status: str = "pending"  # pending, downloading, completed, error
    progress: int = 0

    @property
    def duration_str(self) -> str:
        seconds = self.duration_ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"

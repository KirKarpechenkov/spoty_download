from mutagen.id3 import ID3, TIT2, TPE1, TALB, TYER, TRCK, APIC, USLT
from mutagen.mp3 import MP3
from mutagen.flac import FLAC, Picture
import requests
from models.track import Track
from utils.logger import logger
import os


class MetadataManager:
    @staticmethod
    def apply_metadata(file_path: str, track: Track):
        try:
            if file_path.endswith(".mp3"):
                MetadataManager._apply_mp3_metadata(file_path, track)
            elif file_path.endswith(".flac"):
                MetadataManager._apply_flac_metadata(file_path, track)
        except Exception as e:
            logger.error(f"Error applying metadata to {file_path}: {e}")

    @staticmethod
    def _apply_mp3_metadata(file_path: str, track: Track):
        audio = MP3(file_path, ID3=ID3)
        try:
            audio.add_tags()
        except:
            pass

        audio.tags.add(TIT2(encoding=3, text=track.title))
        audio.tags.add(TPE1(encoding=3, text=track.artist))
        audio.tags.add(TALB(encoding=3, text=track.album))
        audio.tags.add(TYER(encoding=3, text=track.release_date[:4]))
        audio.tags.add(TRCK(encoding=3, text=str(track.track_number)))

        if track.cover_url:
            response = requests.get(track.cover_url)
            if response.status_code == 200:
                audio.tags.add(
                    APIC(
                        encoding=3,
                        mime="image/jpeg",
                        type=3,
                        desc="Cover",
                        data=response.content,
                    )
                )

        if track.lyrics:
            audio.tags.add(
                USLT(encoding=3, lang="eng", desc="pdesc", text=track.lyrics)
            )

        audio.save()

    @staticmethod
    def _apply_flac_metadata(file_path: str, track: Track):
        audio = FLAC(file_path)
        audio["title"] = track.title
        audio["artist"] = track.artist
        audio["album"] = track.album
        audio["date"] = track.release_date[:4]
        audio["tracknumber"] = str(track.track_number)

        if track.cover_url:
            response = requests.get(track.cover_url)
            if response.status_code == 200:
                image = Picture()
                image.type = 3
                image.mime = "image/jpeg"
                image.desc = "Cover"
                image.data = response.content
                audio.add_picture(image)

        audio.save()

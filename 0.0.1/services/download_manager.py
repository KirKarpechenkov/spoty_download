import asyncio
import yt_dlp
import os
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Optional
from models.track import Track
from services.ffmpeg_manager import FFmpegManager
from services.metadata_manager import MetadataManager
from utils.logger import logger


class DownloadManager:
    def __init__(self, status_callback: Optional[Callable] = None):
        self.status_callback = status_callback
        self.executor = ThreadPoolExecutor(max_workers=5)
        self._is_cancelled = False

    async def download_track(
        self, track: Track, download_dir: str, quality: str, format: str
    ):
        if self._is_cancelled:
            return

        loop = asyncio.get_running_loop()

        # Используем стандартный ytsearch, но с жестким уточнением для музыкальной библиотеки
        # "Topic" и "YouTube Music" гарантируют поиск официальных треков
        search_query = f"{track.artist} - {track.title} YouTube Music Topic"

        os.makedirs(download_dir, exist_ok=True)
        temp_filename = f"temp_{track.id}"
        temp_path_template = os.path.join(download_dir, f"{temp_filename}.%(ext)s")

        ydl_opts = {
            "format": "bestaudio/best",
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "outtmpl": temp_path_template,
            "noplaylist": True,
            # Ограничиваем поиск только 1 результатом
            "extract_flat": False,
        }

        try:
            logger.info(f"Searching for official audio: {search_query}")
            track.status = "downloading"
            if self.status_callback:
                self.status_callback(track)

            def _extract_and_download():
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Используем ytsearch1: как самый стабильный префикс
                    info = ydl.extract_info(f"ytsearch1:{search_query}", download=True)

                    if not info or not info.get("entries"):
                        raise Exception("No results found in official music library")

                    target = info["entries"][0]
                    return ydl.prepare_filename(target)

            downloaded_temp_file = await loop.run_in_executor(
                self.executor, _extract_and_download
            )

            if not os.path.exists(downloaded_temp_file):
                # Иногда yt-dlp может изменить расширение (например на .m4a)
                # Пробуем найти файл по шаблону если точный путь не найден
                base_temp = os.path.join(download_dir, f"{temp_filename}")
                for ext in [".webm", ".m4a", ".mp3", ".opus"]:
                    if os.path.exists(base_temp + ext):
                        downloaded_temp_file = base_temp + ext
                        break

            # Очистка имени для финального файла
            clean_name = "".join(
                [
                    c
                    for c in f"{track.artist} - {track.title}"
                    if c.isalnum() or c in (" ", "-", ".", "_")
                ]
            ).strip()
            final_file = os.path.join(download_dir, f"{clean_name}.{format}")

            # Конвертация
            logger.info(f"Converting to {format}...")
            success = await loop.run_in_executor(
                self.executor,
                lambda: FFmpegManager.convert(
                    downloaded_temp_file, final_file, f"{quality}k"
                ),
            )

            if success:
                logger.info("Applying metadata...")
                MetadataManager.apply_metadata(final_file, track)
                track.file_path = final_file
                track.status = "completed"
                track.progress = 100
                if os.path.exists(downloaded_temp_file):
                    os.remove(downloaded_temp_file)
            else:
                track.status = "error"

        except Exception as e:
            logger.error(f"Download error for {track.title}: {e}")
            track.status = "error"

        finally:
            if self.status_callback:
                self.status_callback(track)

    def cancel(self):
        self._is_cancelled = True

import subprocess
import os
import shutil
from utils.logger import logger


class FFmpegManager:
    @classmethod
    def get_ffmpeg_executable(cls):
        # 1. Проверяем PATH
        path = shutil.which("ffmpeg")
        if path:
            return path

        # 2. Проверяем локальную папку bin/ffmpeg.exe (если пользователь положил его туда)
        local_exe = os.path.join(os.getcwd(), "bin", "ffmpeg.exe")
        if os.name == "nt" and not local_exe.endswith(".exe"):
            local_exe += ".exe"

        if os.path.exists(local_exe):
            return local_exe

        return None

    @classmethod
    def convert(cls, input_path: str, output_path: str, quality: str = "320k"):
        ffmpeg_exe = cls.get_ffmpeg_executable()
        if not ffmpeg_exe:
            logger.error("FFmpeg executable not found in PATH or ./bin/")
            return False

        try:
            # Базовая команда
            command = [
                ffmpeg_exe,
                "-y",
                "-i",
                input_path,
                "-vn",
                "-ar",
                "44100",
                "-ac",
                "2",
                "-b:a",
                quality,
                output_path,
            ]

            # Настройки для специфичных форматов
            if output_path.endswith(".wav"):
                command = [ffmpeg_exe, "-y", "-i", input_path, output_path]
            elif output_path.endswith(".flac"):
                command = [
                    ffmpeg_exe,
                    "-y",
                    "-i",
                    input_path,
                    "-compression_level",
                    "5",
                    output_path,
                ]

            # На Windows используем creationflags, чтобы не мелькало консольное окно
            creation_flags = 0
            if os.name == "nt":
                creation_flags = subprocess.CREATE_NO_WINDOW

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                creationflags=creation_flags,
            )
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                logger.error(f"FFmpeg error (code {process.returncode}): {stderr}")
                return False

            logger.info(f"Successfully converted to {output_path}")
            return True
        except Exception as e:
            logger.error(f"FFmpeg exception during conversion: {e}")
            return False

    @staticmethod
    def is_ffmpeg_available():
        path = shutil.which("ffmpeg")
        if path:
            return True
        local_exe = os.path.join(os.getcwd(), "bin", "ffmpeg.exe")
        return os.path.exists(local_exe)

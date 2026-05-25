<h1 align="center">Spoty Download</h1>

<p align="center">
  <strong>Современное desktop-приложение на Python, написанное с помощью Command Center, для импорта и экспорта плейлистов и альбомов Spotify, управления музыкальной библиотекой и загрузки аудио из легальных открытых источников.</strong>
</p>





## Возможности
  Импорт Spotify playlist / album / track URL
  Получение metadata через Spotify Web API
  Автоматический поиск доступных аудиоисточников
  Загрузка музыки в различных форматах:
  MP3 128 kbps
  MP3 320 kbps
  FLAC
  WAV
## Автоматическая загрузка:
  cover art
  metadata
  lyrics
## Конвертация аудио через FFmpeg
  ID3 tagging через Mutagen
  Современный минималистичный GUI на PySide6 / PyQt6
  Очередь загрузок
  Progress tracking
  Retry system
  История загрузок (SQLite)
## Dark / Light Theme
  Drag & Drop поддержка
## Технологии:
  Python 3.12+
  PySide6 / PyQt6
  Spotify Web API
  Spotipy
  yt-dlp
  FFmpeg
  Mutagen
  SQLite
  Asyncio
## Особенности:
  Чистая модульная архитектура
  Асинхронная обработка задач
  Production-ready структура проекта
  Современный UI/UX
  Полная типизация и логирование
  Кроссплатформенная поддержка

--
  
## Важно

Проект использует только легальные и открытые источники аудио и не предназначен для обхода DRM или нарушения правил Spotify.

## Запуск
```bash
git clone https://github.com/KirKarpechenkov/spoty_download
cd spotify-library-manager
```

```bash
pip install -r requirements.txt
python main.py
```

## Настройка

Создайте .env файл и укажите:
```bash
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

## Интерфейс

Минималистичный desktop UI в стиле Spotify / Apple Music с поддержкой:

  playlists
  albums
  tracks
  quality selection
  download queue
  metadata management
  Статус проекта

В активной разработке.

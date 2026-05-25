import sys
import asyncio
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QFileDialog,
    QComboBox,
    QCheckBox,
    QLabel,
    QFrame,
)
from PySide6.QtCore import Qt, QThread, Signal, Slot
from gui.components.track_item import TrackItem
from services.spotify_client import SpotifyClient
from services.download_manager import DownloadManager
from config import Config
from models.track import Track
from utils.logger import logger


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SpotyDownload - Premium Music Downloader")
        self.resize(1000, 700)

        self.spotify = SpotifyClient()
        self.download_manager = DownloadManager(self.on_download_progress)
        self.tracks = []

        self.init_ui()
        self.apply_styles()

    def init_ui(self):
        self.setAcceptDrops(True)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header: URL Input
        header_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(
            "Paste Spotify track, album, or playlist URL here..."
        )
        self.url_input.setObjectName("urlInput")

        self.analyze_btn = QPushButton("Analyze")
        self.analyze_btn.setObjectName("primaryButton")
        self.analyze_btn.clicked.connect(self.analyze_url)

        header_layout.addWidget(self.url_input)
        header_layout.addWidget(self.analyze_btn)
        main_layout.addLayout(header_layout)

        # Settings bar
        settings_layout = QHBoxLayout()

        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["128", "320"])
        self.quality_combo.setCurrentText(Config.QUALITY)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp3", "flac", "wav"])
        self.format_combo.setCurrentText(Config.FORMAT)

        self.cover_cb = QCheckBox("Download Covers")
        self.cover_cb.setChecked(Config.DOWNLOAD_COVERS)

        self.metadata_cb = QCheckBox("Save Metadata")
        self.metadata_cb.setChecked(Config.SAVE_METADATA)

        self.dir_btn = QPushButton("Select Folder")
        self.dir_btn.clicked.connect(self.select_directory)

        settings_layout.addWidget(QLabel("Quality (kbps):"))
        settings_layout.addWidget(self.quality_combo)
        settings_layout.addWidget(QLabel("Format:"))
        settings_layout.addWidget(self.format_combo)
        settings_layout.addSpacing(20)
        settings_layout.addWidget(self.cover_cb)
        settings_layout.addWidget(self.metadata_cb)
        settings_layout.addStretch()
        settings_layout.addWidget(self.dir_btn)

        main_layout.addLayout(settings_layout)

        # Tracks list
        self.track_list = QListWidget()
        self.track_list.setObjectName("trackList")
        main_layout.addWidget(self.track_list)

        # Footer: Actions
        footer_layout = QHBoxLayout()
        self.download_btn = QPushButton("Download All")
        self.download_btn.setObjectName("downloadButton")
        self.download_btn.clicked.connect(self.start_downloads)

        self.clear_btn = QPushButton("Clear")
        self.clear_btn.clicked.connect(self.clear_list)

        footer_layout.addWidget(self.clear_btn)
        footer_layout.addStretch()
        footer_layout.addWidget(self.download_btn)
        main_layout.addLayout(footer_layout)

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow { background-color: #121212; }
            QWidget { color: #FFFFFF; font-family: 'Segoe UI', sans-serif; }
            QLineEdit#urlInput {
                background-color: #282828;
                border: 1px solid #3E3E3E;
                border-radius: 20px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton#primaryButton {
                background-color: #1DB954;
                color: black;
                border-radius: 20px;
                padding: 10px 30px;
                font-weight: bold;
            }
            QPushButton#downloadButton {
                background-color: #1DB954;
                color: black;
                border-radius: 25px;
                padding: 15px 50px;
                font-size: 16px;
                font-weight: bold;
            }
            QListWidget {
                background-color: #181818;
                border: none;
                border-radius: 10px;
                outline: none;
            }
            QCheckBox, QLabel { font-size: 12px; }
        """)

    def analyze_url(self):
        url = self.url_input.text().strip()
        if not url:
            return

        self.analyze_btn.setEnabled(False)
        self.analyze_btn.setText("Analyzing...")

        # In a real app, this should be in a separate thread
        tracks = self.spotify.get_track_info(url)
        for track in tracks:
            self.add_track_to_list(track)

        self.analyze_btn.setEnabled(True)
        self.analyze_btn.setText("Analyze")

    def add_track_to_list(self, track: Track):
        self.tracks.append(track)
        item = QListWidgetItem(self.track_list)
        item_widget = TrackItem(track)
        item.setSizeHint(item_widget.sizeHint())
        self.track_list.addItem(item)
        self.track_list.setItemWidget(item, item_widget)

    def select_directory(self):
        path = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if path:
            Config.DEFAULT_DOWNLOAD_DIR = path

    def clear_list(self):
        self.track_list.clear()
        self.tracks = []

    def start_downloads(self):
        quality = self.quality_combo.currentText()
        fmt = self.format_combo.currentText()
        download_dir = str(Config.DEFAULT_DOWNLOAD_DIR)

        asyncio.create_task(self._run_downloads(download_dir, quality, fmt))

    async def _run_downloads(self, download_dir, quality, fmt):
        for track in self.tracks:
            if track.status == "completed":
                continue
            await self.download_manager.download_track(
                track, download_dir, quality, fmt
            )

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        url = event.mimeData().text()
        self.url_input.setText(url)
        self.analyze_url()

    def on_download_progress(self, track: Track):
        # Find the widget and update it
        for i in range(self.track_list.count()):
            item = self.track_list.item(i)
            widget = self.track_list.itemWidget(item)
            if widget.track.id == track.id:
                widget.update_status()
                break

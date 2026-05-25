import requests
import threading
from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QImage
from models.track import Track


class TrackItem(QFrame):
    def __init__(self, track: Track, parent=None):
        super().__init__(parent)
        self.track = track
        self.init_ui()
        # Фоновая загрузка обложки
        threading.Thread(target=self.load_cover, daemon=True).start()

    def init_ui(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setObjectName("trackItem")
        self.setFixedHeight(80)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)

        # Обложка
        self.cover_label = QLabel()
        self.cover_label.setFixedSize(60, 60)
        self.cover_label.setStyleSheet("background-color: #282828; border-radius: 4px;")
        self.cover_label.setScaledContents(True)
        layout.addWidget(self.cover_label)

        # Инфо
        info_layout = QVBoxLayout()
        self.title_label = QLabel(self.track.title)
        self.title_label.setStyleSheet("font-weight: bold; color: white;")

        self.artist_label = QLabel(f"{self.track.artist} • {self.track.album}")
        self.artist_label.setStyleSheet("font-size: 11px; color: #b3b3b3;")

        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.artist_label)
        layout.addLayout(info_layout, 1)

        # Статус
        self.status_label = QLabel(self.track.status.capitalize())
        self.status_label.setStyleSheet("font-size: 11px; color: #1DB954;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setVisible(False)
        self.progress_bar.setTextVisible(False)

        status_layout = QVBoxLayout()
        status_layout.setAlignment(Qt.AlignCenter)
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.progress_bar)
        layout.addLayout(status_layout)

    def load_cover(self):
        if not self.track.cover_url:
            return
        try:
            response = requests.get(self.track.cover_url, timeout=5)
            if response.status_code == 200:
                image = QImage()
                image.loadFromData(response.content)
                pixmap = QPixmap.fromImage(image)
                # В PySide6 обновление UI из потока лучше делать через сигналы,
                # но для простоты и обложек setPixmap часто работает.
                self.cover_label.setPixmap(pixmap)
        except:
            pass

    def update_status(self):
        self.status_label.setText(self.track.status.capitalize())
        if self.track.status == "downloading":
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(self.track.progress)
        elif self.track.status == "completed":
            self.progress_bar.setVisible(False)
            self.status_label.setText("✓ Ready")
            self.status_label.setStyleSheet("color: #1DB954;")
        elif self.track.status == "error":
            self.progress_bar.setVisible(False)
            self.status_label.setText("✕ Failed")
            self.status_label.setStyleSheet("color: #FF4444;")

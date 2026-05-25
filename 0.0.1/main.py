import sys
import asyncio
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop
from gui.main_window import MainWindow
from config import Config
from utils.logger import logger


def main():
    # Обеспечиваем наличие директорий
    Config.ensure_dirs()

    app = QApplication(sys.argv)
    app.setApplicationName("SpotyDownload")

    # Интегрируем asyncio в цикл событий Qt
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    logger.info("Application started successfully")

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.error(f"Critical crash: {e}")
        sys.exit(1)

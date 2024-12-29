import logging
from pathlib import Path
import signal
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QLabel
from PyQt6.QtGui import QIcon, QAction


class SystrayApp:
    log: logging.Logger

    app: QApplication
    tray_icon: QSystemTrayIcon
    menu: QMenu
    menu_battery_status: QLabel

    def __init__(self, app: QApplication, log_level: int):
        self.setup_logger(log_level)

        self.app = app
        self.tray_icon = QSystemTrayIcon(QIcon(
            # TODO: change it depending on the theme lightness
            str(Path(__file__).parent.joinpath('images', 'steelseries_logo_white.png').absolute().as_posix())
        ), parent=self.app)

        self.menu = QMenu()
        self.menu_battery_status = QAction('Battery status: ...')
        self.menu.addAction(self.menu_battery_status)
        self.tray_icon.setContextMenu(self.menu)

    def setup_logger(self, log_level: int):
        self.log = logging.getLogger('SystrayApp')
        self.log.setLevel(log_level)

    async def start(self):
        self.log.info('Starting Systray app.')
        self.tray_icon.show()

        self.app.exec_()

    def stop(self):
        self.log.debug('Received shutdown signal, shutting down.')
        self.app.quit()

import json
import logging
from pathlib import Path
from typing import Any, Callable
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QLabel
from PyQt6.QtGui import QIcon, QAction

from arctis_chatmix.device_manager import DeviceStatus


class SystrayApp:
    log: logging.Logger

    app: QApplication
    tray_icon: QSystemTrayIcon
    menu: QMenu
    menu_entries: dict[str, QAction]

    translations: dict

    def __init__(self, app: QApplication, log_level: int):
        self.setup_logger(log_level)

        self.app = app
        self.tray_icon = QSystemTrayIcon(QIcon(
            # TODO: change it depending on the theme lightness
            str(Path(__file__).parent.joinpath('images', 'steelseries_logo.svg').absolute().as_posix())
        ), parent=self.app)
        self.tray_icon.setToolTip('Arctis ChatMix')

        self.menu_entries = {}

        # TODO: dynamically get the language, defaulting to "en"
        self.translations = json.load(Path(__file__).parent.joinpath('lang', 'en.json').open('r'))

        self.menu = QMenu()
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

    def on_device_status_update(self, status: DeviceStatus) -> None:
        if status is None:
            return

        sections = [
            {
                'headset_power_status': {'format': {'status': self.translations['menu']['headset_power_status_status'][status.headset_power_status]}},
                'headset_battery_charge': {'format': {'status': int(status.headset_battery_charge*100)}},
                'charge_slot_battery_charge': {'format': {'status': int(status.charge_slot_battery_charge*100)}},
            },
            {
                'mic_status': {'format': {'status': self.translations['menu']['mic_status_status'][status.mic_status]}},
                'mic_led_brightness': {'format': {'status': int(status.mic_led_brightness * 100)}},
            },
            {
                'noise_cancelling': {'format': {'status': self.translations['menu']['noise_cancelling_status'][status.noise_cancelling]}},
                'transparent_noise_cancelling_level': {'format': {'status': int(status.transparent_noise_cancelling_level*100)}},
            },
            {
                'wireless_pairing': {'format': {'status': self.translations['menu']['wireless_pairing_status'][status.wireless_pairing]}},
                'wireless_mode': {'format': {'mode': self.translations['menu']['wireless_mode_status'][status.wireless_mode]}},
            },
            {
                'bluetooth_powerup_state': {'format': {'status': self.translations['menu']['on_off_state'][status.bluetooth_powerup_state]}},
                'bluetooth_power_status': {'format': {'status': self.translations['menu']['on_off_state'][status.bluetooth_power_status]}},
                'bluetooth_auto_mute': {'format': {'status': self.translations['menu']['bluetooth_auto_mute_status'][status.bluetooth_auto_mute]}},
                'bluetooth_connection': {'format': {'status': self.translations['menu']['on_off_state'][status.bluetooth_connection]}},
            }
        ]

        for i, section in enumerate(sections):
            if i > 0:
                if any((val for key, val in section.items() if getattr(status, key) is not None)):
                    self.menu.addSeparator()
            for key, attrs in section.items():
                if getattr(status, key) is not None:
                    self.add_menu_entry(key, attrs['format'])

        for entry in status.__annotations__.keys():
            if getattr(status, entry) is None:
                self.remove_menu_entry(entry)

    def add_menu_entry(self, entry: str, format: dict[str, Any], callback: Callable[[], None] = None):
        if entry not in self.menu_entries:
            self.menu_entries[entry] = QAction('')
            self.menu_entries[entry].setDisabled(callback is None)
            if callback is not None:
                self.menu_entries[entry].triggered.connect(callback)
            self.menu.addAction(self.menu_entries[entry])

        self.menu_entries[entry].setText(
            self.translations['menu'][f'{entry}_label'].format(**format)
        )

    def remove_menu_entry(self, entry: str):
        if entry in self.menu_entries:
            self.menu.removeAction(self.menu_entries[entry])
            del self.menu_entries[entry]

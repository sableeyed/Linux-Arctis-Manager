import json
import locale
import logging
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any, Callable

from PyQt6 import QtSvg
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon, QImage, QPainter, QPixmap, QPalette
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from arctis_chatmix.device_manager import DeviceStatus


class SystrayApp:
    log: logging.Logger

    app: QApplication
    tray_icon: QSystemTrayIcon
    menu: QMenu
    menu_entries: dict[str, QAction]

    translations: dict

    def get_systray_icon_pixmap(self, path: Path) -> QPixmap:
        brush_color = QApplication.palette().color(QPalette.ColorRole.Text)
        # brush_color_argb = f'#{hex(brush_color.alpha())[2:]}{hex(brush_color.red())[2:]}{
        #     hex(brush_color.green())[2:]}{hex(brush_color.blue())[2:]}'

        xml_tree = ET.parse(path.absolute().as_posix())
        xml_root = xml_tree.getroot()

        for path in xml_root.findall('.//{http://www.w3.org/2000/svg}path'):
            path.set('fill', brush_color.name())

        xml_str = ET.tostring(xml_root)

        svg_renderer = QtSvg.QSvgRenderer(xml_str)

        # Create the empty image
        image = QImage(64, 64, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)

        # Initialize the painter
        painter = QPainter(image)
        painter.setBrush(brush_color)
        painter.setPen(Qt.PenStyle.NoPen)

        # Render the image on the QImage
        svg_renderer.render(painter)

        # Rendering end
        painter.end()

        pixmap = QPixmap.fromImage(image)

        return pixmap

    def __init__(self, app: QApplication, log_level: int):
        self.setup_logger(log_level)
        self.app = app

        svg_path = Path(__file__).parent.joinpath('images', 'steelseries_logo.svg')
        pixmap = self.get_systray_icon_pixmap(svg_path)

        self.tray_icon = QSystemTrayIcon(QIcon(pixmap), parent=self.app)
        self.tray_icon.setToolTip('Arctis ChatMix')

        self.menu_entries = {}

        lang_code, _ = locale.getdefaultlocale()
        lang_code = lang_code.split('_')[0]

        translation_json_path = Path(__file__).parent.joinpath('lang', f'{lang_code}.json')
        if not translation_json_path.is_file():
            translation_json_path = Path(__file__).parent.joinpath('lang', 'en.json')
        self.translations = json.load(translation_json_path.open('r'))

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

    def get_translation(self, dot_notation_key: str, to_translate: str) -> str:
        keys = dot_notation_key.split('.')
        node = self.translations

        for key in keys:
            if node.get(key, None) is None:
                return to_translate
            node = node[key]

        return node[to_translate]

    def on_device_status_update(self, status: DeviceStatus) -> None:
        if status is None:
            return

        sections = [
            {
                'headset_power_status': {'format': {'status': self.get_translation('menu.headset_power_status_status', status.headset_power_status)}},
                'headset_battery_charge': {'format': {'status': int(status.headset_battery_charge*100)}},
                'charge_slot_battery_charge': {'format': {'status': int(status.charge_slot_battery_charge*100)}},
            },
            {
                'mic_status': {'format': {'status': self.get_translation('menu.mic_status_status', status.mic_status)}},
                'mic_led_brightness': {'format': {'status': int(status.mic_led_brightness * 100)}},
            },
            {
                'noise_cancelling': {'format': {'status': self.get_translation('menu.noise_cancelling_status', status.noise_cancelling)}},
                'transparent_noise_cancelling_level': {'format': {'status': int(status.transparent_noise_cancelling_level*100)}},
            },
            {
                'wireless_pairing': {'format': {'status': self.get_translation('menu.wireless_pairing_status', status.wireless_pairing)}},
                'wireless_mode': {'format': {'mode': self.get_translation('menu.wireless_mode_status', status.wireless_mode)}},
            },
            {
                'bluetooth_powerup_state': {'format': {'status': self.get_translation('menu.on_off_state', status.bluetooth_powerup_state)}},
                'bluetooth_power_status': {'format': {'status': self.get_translation('menu.on_off_state', status.bluetooth_power_status)}},
                'bluetooth_auto_mute': {'format': {'status': self.get_translation('menu.bluetooth_auto_mute_status', status.bluetooth_auto_mute)}},
                'bluetooth_connection': {'format': {'status': self.get_translation('menu.on_off_state', status.bluetooth_connection)}},
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

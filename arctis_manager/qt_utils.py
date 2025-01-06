import xml.etree.ElementTree as ET
from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter, QPalette, QPixmap
from PyQt6 import QtSvg
from PyQt6.QtWidgets import QApplication

ICON_PATH = Path(__file__).parent.joinpath('images', 'steelseries_logo.svg')


def get_icon_pixmap(path: Path = ICON_PATH, color: QPalette.ColorRole = QPalette.ColorRole.Text) -> QPixmap:
    brush_color = QApplication.palette().color(color)

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

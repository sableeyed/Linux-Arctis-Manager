from typing import Callable, Optional

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (QFormLayout, QHBoxLayout, QLabel, QLayout,
                             QListWidget, QMainWindow, QSlider, QStackedWidget,
                             QWidget)

from arctis_chatmix.custom_widgets.q_toggle import QToggle
from arctis_chatmix.device_manager.device_settings import (DeviceSetting,
                                                           SliderSetting,
                                                           ToggleSetting)
from arctis_chatmix.qt_utils import get_icon_pixmap
from arctis_chatmix.translations import Translations


class SettingsWindow(QMainWindow):
    def __init__(self, sections: dict[str, list[DeviceSetting]]):
        super().__init__()

        i18n = Translations.get_instance()

        self.setWindowTitle(i18n.get_translation('app.settings_window_title'))
        # Note: Wayland does not support window icons (yet?)
        self.setWindowIcon(QIcon(get_icon_pixmap()))

        # Set the minimum size and adjust to screen geometry
        self.setMinimumSize(800, 600)
        available_geometry = self.screen().availableGeometry()
        self.resize(min(800, available_geometry.width()), min(600, available_geometry.height()))

        # Create a list widget for sections on the left
        section_list = QListWidget()
        section_list.addItems([i18n.get_translation('sections', section) for section in sections.keys()])
        section_list.setFixedWidth(max(section_list.sizeHintForColumn(0), 200))
        section_list.currentRowChanged.connect(self.change_panel)

        # Create a stacked widget for panels on the right
        panel_stack = QStackedWidget()

        # Create and add panels to the stacked widget
        for settings in sections.values():
            panel = QWidget()
            layout = QFormLayout()
            layout.setAlignment(Qt.AlignmentFlag.AlignTop)

            for setting in settings:
                widget_layout = QWidget()
                w_layout = QHBoxLayout()
                widget_layout.setLayout(w_layout)
                w_layout.addWidget(QLabel(f'{setting.name}: '))

                widget_layout: QLayout = None

                if isinstance(setting, SliderSetting):
                    widget_layout = self.get_slider_configuration_widget(
                        setting.min_value, setting.max_value, setting.step,
                        setting.current_state, setting.min_label, setting.max_label,
                        setting.on_value_change
                    )
                elif isinstance(setting, ToggleSetting):
                    widget_layout = self.get_checkbox_configuration_widget(
                        setting.untoggled_label, setting.toggled_label, setting.current_state,
                        setting.on_value_change
                    )

                if widget_layout is not None:
                    layout.addRow(setting.name, widget_layout)
            panel.setLayout(layout)

            panel_stack.addWidget(panel)

        # Create a central widget and set up the layout
        central_widget = QWidget()
        layout = QHBoxLayout()
        layout.addWidget(section_list)
        layout.addWidget(panel_stack)
        central_widget.setLayout(layout)

        self.setCentralWidget(central_widget)

    def change_panel(self, index):
        # Change the panel based on the selected section
        self.centralWidget().findChild(QStackedWidget).setCurrentIndex(index)

    def get_slider_configuration_widget(
        self, min: int, max: int, step: int, default_value: int, min_label: str, max_label: str, on_value_changed: Optional[Callable[[int], None]]
    ) -> QLayout:
        layout = QHBoxLayout()

        controller = QSlider(orientation=Qt.Orientation.Horizontal)
        controller.setMinimum(min)
        controller.setMaximum(max)
        controller.setSingleStep(step)
        controller.setValue(default_value)

        # layout.addWidget(QLabel(f'{name}: '))
        layout.addWidget(QLabel(min_label))
        layout.addWidget(controller)
        layout.addWidget(QLabel(max_label))

        if on_value_changed is not None:
            controller.sliderReleased.connect(lambda: on_value_changed(controller.value()))

        return layout

    def get_checkbox_configuration_widget(
        self, off_label: str, on_label: str, toggled: bool, on_value_changed: Optional[Callable[[int], None]]
    ) -> QLayout:
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        controller = QToggle()
        controller.setChecked(toggled)

        layout.addWidget(QLabel(off_label))
        layout.addWidget(controller)
        layout.addWidget(QLabel(on_label))

        if on_value_changed is not None:
            controller.stateChanged.connect(lambda: on_value_changed(controller.isChecked()))

        return layout

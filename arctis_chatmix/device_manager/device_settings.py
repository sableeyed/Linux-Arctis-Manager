
from abc import ABC, abstractmethod
from typing import Any, Callable

from arctis_chatmix.translations import Translations


class DeviceSetting(ABC):
    setting_key: str
    name: str

    def __init__(self, setting_key: str):
        self.setting_key = setting_key
        self.name = Translations.get_instance().get_translation('settings', setting_key)

    @abstractmethod
    def possible_values() -> dict[Any, str]:
        pass

    @abstractmethod
    def on_value_change(self, value: Any) -> None:
        pass

    @abstractmethod
    def to_settings_dict(self) -> dict[str, Any]:
        pass


class ToggleSetting(DeviceSetting):
    def __init__(
            self, setting_key: str, toggled_translation_key: str, untoggled_translation_key: str,
            current_state: bool, on_value_toggle: Callable[[bool], None]
    ):
        super().__init__(setting_key)

        self.toggled_label = Translations.get_instance().get_translation('setting_values', toggled_translation_key)
        self.untoggled_label = Translations.get_instance().get_translation('setting_values', untoggled_translation_key)
        self.current_state = current_state
        self.callback = on_value_toggle

    def possible_values(self) -> dict[bool, str]:
        return {
            True: self.toggled_label,
            False: self.untoggled_label,
        }

    def on_value_change(self, value) -> None:
        self.callback(value)

    def to_settings_dict(self):
        return {
            'type': 'toggle',
            'configuration': {
                'off_label': self.untoggled_label,
                'on_label': self.toggled_label,
                'toggled': self.current_state
            }
        }


class SliderSertting(DeviceSetting):
    pass

from dataclasses import dataclass, field
from typing import Any, Callable, Generic, Optional, TypeVar

from arctis_chatmix.translations import Translations

T = TypeVar('T')


@dataclass(frozen=True)
class DeviceStatusValue(Generic[T]):
    value: T
    value_translation_key: Optional[str] = field(default=None)  # Relative to device_status_values
    mapped_val: Optional[Callable[[T], str]] = field(default=None)  # Optional string value conversion, if decoding is requried

    def __str__(self) -> T:
        return self.mapped_val(self.value) if self.mapped_val is not None \
            else Translations.get_instance().get_translation('device_status_values', self.value_translation_key) \
            if self.value_translation_key is not None \
            else str(self.value)

    def __mul__(self, other) -> int | float:
        val = self.mapped_val(self.value) if self.mapped_val is not None else None

        if type(val) in [int, float]:
            return val * other

        return 0


@dataclass(frozen=True)
class DeviceStatus:
    # Bluetooth
    bluetooth_powerup_state: Optional[DeviceStatusValue] = field(default=None)
    bluetooth_auto_mute: Optional[DeviceStatusValue] = field(default=None)
    bluetooth_power_status: Optional[DeviceStatusValue] = field(default=None)
    bluetooth_connection: Optional[DeviceStatusValue] = field(default=None)

    # Wireless
    wireless_mode: Optional[DeviceStatusValue] = field(default=None)
    wireless_pairing: Optional[DeviceStatusValue] = field(default=None)

    # Battery / power status
    '''Value between 0 and 1, percentage'''
    headset_battery_charge: Optional[DeviceStatusValue[float]] = field(default=None)
    '''Value between 0 and 1, percentage'''
    charge_slot_battery_charge: Optional[DeviceStatusValue[float]] = field(default=None)
    headset_power_status: Optional[DeviceStatusValue] = field(default=None)

    # ANC
    '''Value between 0 and 1, percentage'''
    transparent_noise_cancelling_level: Optional[DeviceStatusValue[float]] = field(default=None)
    noise_cancelling: Optional[DeviceStatusValue] = field(default=None)

    # Microphone
    mic_status: Optional[DeviceStatusValue] = field(default=None)
    '''Value between 0 and 1, percentage'''
    mic_led_brightness: Optional[DeviceStatusValue[float]] = field(default=None)

    # Advanced features
    auto_off_time_minutes: Optional[DeviceStatusValue[int]] = field(default=None)

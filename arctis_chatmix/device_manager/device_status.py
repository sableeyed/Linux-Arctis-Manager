from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Literal, Optional


@dataclass(frozen=True)
class DeviceStatus(ABC):
    # Bluetooth
    bluetooth_powerup_state: Optional[str] = field(default=None)
    bluetooth_auto_mute: Optional[str] = field(default=None)
    bluetooth_power_status: Optional[str] = field(default=None)
    bluetooth_connection: Optional[str] = field(default=None)

    # Wireless
    wireless_mode: Optional[str] = field(default=None)
    wireless_pairing: Optional[str] = field(default=None)

    # Battery / power status
    '''Value between 0 and 1, percentage'''
    headset_battery_charge: Optional[float] = field(default=None)
    '''Value between 0 and 1, percentage'''
    charge_slot_battery_charge: Optional[float] = field(default=None)
    headset_power_status: Optional[str] = field(default=None)

    # ANC
    '''Value between 0 and 1, percentage'''
    transparent_noise_cancelling_level: Optional[float] = field(default=None)
    noise_cancelling: Optional[str] = field(default=None)

    # Microphone
    mic_status: Optional[str] = field(default=None)
    '''Value between 0 and 1, percentage'''
    mic_led_brightness: Optional[float] = field(default=None)

    # Advanced features
    auto_off_time_minutes: Optional[int] = field(default=None)

    @abstractmethod
    def validation_dict(self) -> dict[str, list[str] | dict[Literal['between'], list[int]] | dict[Literal['gt', 'lt'], int | float] | Literal['any', 'any_str', 'any_int', 'any_float']]:
        '''
        Returns the validation dictionary. This might and should limit the options set by the device itself.
        None values are always acceptable and won't be listed in the contextual menu.

        Possible attribute / value combinations:

        'attribute_name': 'any'                    # any value is acceptable (any type). SHOULD NOT BE USED IF NOT NECESSARY.
        'attribute_name': 'any_str'                # any str value is acceptable
        'attribute_name': 'any_int'                # any int value is acceptable
        'attribute_name': 'any_float'              # any float value is acceptable
        'attribute_name': [possible values]        # fixed list of values
        'attribute_name': {'between': [min, max]}  # value between min, max (for example 0, 1 for percentages)
        'attribute_name': {'gt': value}            # value greater than
        'attribute_name': {'gte': value}           # value greater than or equal
        'attribute_name': {'lt': value}            # value less than
        'attribute_name': {'lte': value}           # value less than or equal
        '''

        pass

    def __post_init__(self):
        validation_dict = self.validation_dict()
        for attr in self.__annotations__:
            attr_value = getattr(self, attr)

            # Attribute defined in the validation dictionary
            if attr in validation_dict:
                values = validation_dict[attr]
                if attr_value is None:
                    continue

                if isinstance(values, list):
                    if attr_value not in values:
                        raise Exception(f"{attr} must be one of {values}")
                elif values == 'any':
                    continue
                elif values == 'any_str' and not isinstance(attr_value, str):
                    raise Exception(f"{attr} must be a str")
                elif values == 'any_int' and not isinstance(attr_value, int):
                    raise Exception(f"{attr} must be an int")
                elif values == 'any_float' and not isinstance(attr_value, float):
                    raise Exception(f"{attr} must be a float")
                elif isinstance(values, dict):
                    if 'between' in values and (attr_value < values['between'][0] or attr_value > values['between'][1]):
                        raise Exception(f"{attr} must be between {values['between'][0]} and {values['between'][1]}")
                    elif 'gt' in values and attr_value <= values['gt']:
                        raise Exception(f"{attr} must be greater than {values['gt']}")
                    elif 'gte' in values and attr_value <= values['gte']:
                        raise Exception(f"{attr} must be greater than or equal {values['gte']}")
                    elif 'lt' in values and attr_value >= values['lt']:
                        raise Exception(f"{attr} must be lesser than {values['lt']}")
                    elif 'lte' in values and attr_value >= values['lte']:
                        raise Exception(f"{attr} must be lesser than or equal {values['lte']}")
            # Attribute not defined in the validation dictionary, but not None
            elif values is not None:
                raise Exception(f'Unexpected attribute {attr}')

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import logging
from typing import Literal, Optional

import usb.core
import usb.util


@dataclass(frozen=True)
class InterfaceEndpoint:
    '''Address of the interface and the endpoint to listen to'''

    '''0-based index of the interface to listen to'''
    interface: int
    '''0-based index of the endpoint to listen to'''
    endpoint: int

    def __eq__(self, other: 'InterfaceEndpoint') -> bool:
        return self.interface == other.interface and self.endpoint == other.endpoint


class ChannelPosition(Enum):
    # Standard positions
    FRONT_LEFT = 'FL'
    FRONT_RIGHT = 'FR'
    # Might have positions
    FRONT_CENTRAL = 'FC'
    LOW_FREQUENCY_EFFECTS = 'LFE'
    SIDE_LEFT = 'SL'
    SIDE_RIGHT = 'SR'
    REAR_LEFT = 'RL'
    REAR_RIGHT = 'RR'
    # Advanced positions
    REAR_LEFT_CENTER = 'RLC'
    REAR_RIGHT_CENTER = 'RRC'
    FRONT_LEFT_CENTER = 'FLC'
    FRONT_RIGHT_CENTER = 'FRC'


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


@dataclass(frozen=True)
class ChatMixState:
    '''Status of the chat mix'''

    '''Volume of the Game channel (0.0 to 1.0)'''
    game_volume: float
    '''Volume of the Chat channel (0.0 to 1.0)'''
    chat_volume: float

    '''Mix of the Game channel (0.0 to 1.0)'''
    game_mix: float
    '''Mix of the Chat channel (0.0 to 1.0)'''
    chat_mix: float

    '''The device status (advanced features)'''
    device_status: DeviceStatus

    def __post_init__(self):
        for attr in ['game_volume', 'chat_volume', 'game_mix', 'chat_mix']:
            value = getattr(self, attr)
            if not isinstance(value, float) and not isinstance(value, int):
                raise Exception(f"{attr} must be a float")
            if value < 0.0 or value > 1.0:
                raise Exception(f"{attr} must be between 0.0 and 1.0")


class DeviceManager(ABC):
    device: usb.core.Device
    log: logging.Logger

    def __init__(self, log_level: int = logging.INFO):
        self.log = logging.getLogger('Device')
        self.log.level = log_level

    def set_device(self, device: usb.core.Device):
        '''
        Called by the daemon before init_device
        '''
        self.device = device

    def kernel_detach(self, ie: Optional[InterfaceEndpoint] = None) -> None:
        '''
        Ensure that the kernel driver is detached for all the interfaces we need to access in I/O
        '''

        if ie is not None:
            interfaces = [ie.interface]
        else:
            interfaces = list(set([ie.interface for ie in self.get_endpoint_addresses_to_listen()]))

        for interface in interfaces:
            interface = self.device[0].interfaces()[interface]
            interface_num = interface.bInterfaceNumber

            if self.device.is_kernel_driver_active(interface_num):
                self.device.detach_kernel_driver(interface_num)

    def init_device(self) -> None:
        '''
        Initialize the device. Overwrite when needed.
        '''
        pass

    def get_device_vendor_id(self) -> int:
        '''
        Get the vendor's identifier (should always be SteelSerie's)
        '''
        return 0x1038

    @abstractmethod
    def get_device_product_id(self) -> int:
        '''
        Get the product's identifier
        '''
        pass

    @abstractmethod
    def get_device_name(self) -> str:
        '''
        Get the device's friendly name (for example "Arctis Nova Pro Wireless")
        '''
        pass

    def get_audio_position(self) -> list[ChannelPosition]:
        '''
        Get the list of channel positions, defaulting to FL, FR.
        Override when different.
        '''
        return [ChannelPosition.FRONT_LEFT, ChannelPosition.FRONT_RIGHT]

    @abstractmethod
    def get_endpoint_addresses_to_listen(self) -> list[InterfaceEndpoint]:
        '''
        Get the list of endpoint addresses to listen.
        '''
        pass

    def get_request_device_status(self) -> tuple[Optional[InterfaceEndpoint], Optional[list[int]]]:
        '''
        If the device supports the device status, define the interface/endpoint and the request status message here.
        It will be read by the manage_input_data function.
        '''

        return None, None

    def utility_guess_endpoint(self, interface_index: int, direction_out: Literal['out', 'in']) -> Optional[InterfaceEndpoint]:
        '''
        Guess the endpoint index based on the interface index and the direction.
        out: host-to-device
        in: device-to-host
        '''

        if getattr(self, '_endpoint_cache', None) is None:
            self._endpoint_cache = {}

        index = f'{self.get_device_product_id()}::{interface_index}::{direction_out}'
        if index in self._endpoint_cache:
            return self._endpoint_cache[index]

        if self.device is None:
            self.log.debug('Device is not initialized yet.')

            return None

        interface = self.device[0].interfaces()[interface_index]
        for endpoint_index, endpoint in enumerate(interface.endpoints()):
            if usb.util.endpoint_direction(endpoint.bEndpointAddress) == usb.util.ENDPOINT_OUT if direction_out == 'out' else usb.util.ENDPOINT_IN:
                result = InterfaceEndpoint(interface_index, endpoint_index)
                self._endpoint_cache[index] = result

                return result

        return None

    @abstractmethod
    def manage_input_data(self, data: list[int], endpoint: InterfaceEndpoint) -> ChatMixState:
        '''
        Manage the data received from the device at the given endpoint, returning the new state.
        '''
        pass

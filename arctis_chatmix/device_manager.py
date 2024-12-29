from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
import logging
from typing import Literal, Optional

import usb.core


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
class DeviceStatus:
    # Bluetooth
    bluetooth_powerup_state: Optional[Literal['on', 'off']] = field(default=None)
    bluetooth_auto_mute: Optional[Literal['on', 'off', 'half']] = field(default=None)
    bluetooth_power_status: Optional[Literal['on', 'off']] = field(default=None)
    bluetooth_connection: Optional[Literal['off', 'connected', 'disconnected']] = field(default=None)

    # Wireless
    wireless_mode: Optional[Literal['speed', 'range']] = field(default=None)
    wireless_pairing: Optional[Literal['not_paired', 'paired_offline', 'connected']] = field(default=None)

    # Battery / power status
    '''Value between 0 and 1, percentage'''
    headset_battery_charge: Optional[float] = field(default=None)
    '''Value between 0 and 1, percentage'''
    charge_slot_battery_charge: Optional[float] = field(default=None)
    headset_power_status: Optional[Literal['offline', 'cable_charging', 'online']] = field(default=None)

    # ANC
    '''Value between 0 and 1, percentage'''
    transparent_noise_cancelling_level: Optional[float] = field(default=None)
    noise_cancelling: Optional[Literal['on', 'transparent', 'off']] = field(default=None)

    # Microphone
    mic_status: Optional[Literal['muted', 'unmuted']] = field(default=None)
    '''Value between 0 and 1, percentage'''
    mic_led_brightness: Optional[float] = field(default=None)

    # Advanced features
    auto_off_time_minutes: Optional[int] = field(default=None)  # No checks on this (might vary from device to device)

    def __post_init__(self):
        attrs = {
            'bluetooth_powerup_state': ['on', 'off'],
            'bluetooth_auto_mute': ['on', 'off', 'half'],
            'bluetooth_power_status': ['on', 'off'],
            'bluetooth_connection': ['on', 'off'],

            'wireless_mode': ['speed', 'range'],
            'wireless_pairing': ['not_paired', 'paired_offline', 'connected'],

            'headset_battery_charge': {'between': [0, 1]},
            'charge_slot_battery_charge': {'between': [0, 1]},
            'headset_power_status': ['offline', 'cable_charging', 'online'],

            'transparent_noise_cancelling_level': {'between': [0, 1]},
            'noise_cancelling': ['on', 'transparent', 'off'],

            'mic_status': ['muted', 'unmuted'],
            'mic_led_brightness': {'between': [0, 1]},

            'auto_off_time_minutes': {'gt': 0},
        }

        for attr, values in attrs.items():
            attr_value = getattr(self, attr)
            if attr_value is None:
                continue

            if isinstance(values, list):
                if attr_value not in values:
                    raise Exception(f"{attr} must be one of {values}")
            elif isinstance(values, dict):
                if 'between' in values and (attr_value < values['between'][0] or attr_value > values['between'][1]):
                    raise Exception(f"{attr} must be between {values['between'][0]} and {values['between'][1]}")
                elif 'gt' in values and attr_value <= values['gt']:
                    raise Exception(f"{attr} must be greater than {values['gt']}")


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

    def get_request_device_status(self) -> tuple[Optional[InterfaceEndpoint], Optional[list[int]]]:
        '''
        If the device supports the device status, define the interface/endpoint and the request status message here.
        It will be read by the manage_input_data function.
        '''

        return None, None

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

    @abstractmethod
    def manage_input_data(self, data: list[int], endpoint: InterfaceEndpoint) -> ChatMixState:
        '''
        Manage the data received from the device at the given endpoint, returning the new state.
        '''
        pass

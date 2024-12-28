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


@dataclass(frozen=True)
class DeviceStatus:
    '''Value between 0 and 1, percentage'''
    headset_battery_charge: float

    '''Whether the headset is connected or not'''
    headset_state: bool

    def __post_init__(self):
        if self.headset_battery_charge < 0 or self.headset_battery_charge > 1:
            raise Exception("Headset battery charge must be between 0 and 1")


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

    '''Whether the headset is connected or not'''
    headset_online_status: bool = field(default=True)  # Not all devices might have this feature, so setting it default to True (active)

    def __post_init__(self):
        if self.game_volume < 0.0 or self.game_volume > 1.0:
            raise Exception("Game volume must be between 0.0 and 1.0")
        if self.chat_volume < 0.0 or self.chat_volume > 1.0:
            raise Exception("Chat volume must be between 0.0 and 1.0")
        if self.game_mix < 0.0 or self.game_mix > 1.0:
            raise Exception("Game mix must be between 0.0 and 1.0")
        if self.chat_mix < 0.0 or self.chat_mix > 1.0:
            raise Exception("Chat mix must be between 0.0 and 1.0")


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

    def kernel_detach(self) -> None:
        '''
        Ensure that the kernel driver is detached for all the interfaces we need to access in I/O
        '''
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

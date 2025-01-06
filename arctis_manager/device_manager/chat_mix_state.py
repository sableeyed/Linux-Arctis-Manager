from dataclasses import dataclass

from arctis_manager.device_manager.device_status import DeviceStatus


@dataclass(frozen=True)
class DeviceState:
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

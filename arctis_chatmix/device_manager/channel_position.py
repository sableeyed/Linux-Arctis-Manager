from enum import Enum


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

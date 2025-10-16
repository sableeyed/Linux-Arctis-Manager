# side tone
# off = c6 00 00
# low = c6 00 01
# medium = c6 80 01
# high = c6 00 04

# The following data fragments are sent when changing the sidetone from Off -> High
# Data Fragment: 04400212c600040000000000000000000000000000000000000000000000000000000000000000
# Data Fragment: 04400111549b000000000000000000000000000000000000000000000000000000000000000000
# Data Fragment: 2101
# Data Fragment: 068a4200200900000000000000000000000000000000000000000000000000000000000000
# Data Fragment: 068a4200200900000000000000000000000000000000000000000000000000000000000000
# Data Fragment: 06814301230000000000000000000000000000000000000000000000000000000000000000
# Data Fragment: 06814301220000000000000000000000000000000000000000000000000000000000000000

# The following data fragments are sent when changing the sidetone from High -> Off
# Data Fragment: 04400212c600000000000000000000000000000000000000000000000000000000000000000000
# Data Fragment: 04400111549b000000000000000000000000000000000000000000000000000000000000000000
# Data Fragment: 2101
# Data Fragment: 068a4200200900000000000000000000000000000000000000000000000000000000000000
# Data Fragment: 068a4200200900000000000000000000000000000000000000000000000000000000000000
# Data Fragment: 06814301230000000000000000000000000000000000000000000000000000000000000000
# Data Fragment: 06814301220000000000000000000000000000000000000000000000000000000000000000

from typing import Optional

from arctis_manager.config_manager import ConfigManager
from arctis_manager.device_manager import (DeviceState, DeviceManager,
                                           DeviceStatus, InterfaceEndpoint)
from arctis_manager.device_manager.device_settings import (DeviceSetting,
                                                           SliderSetting,
                                                           ToggleSetting)
from arctis_manager.device_manager.device_status import DeviceStatusValue


class ArctisProWiredDevice(DeviceManager):

    def get_device_name(self):
        return 'Arctis Pro'
    
    def get_device_product_id(self):
        return 0x1252
    
    def get_device_vendor_id(self):
        return 0x1038


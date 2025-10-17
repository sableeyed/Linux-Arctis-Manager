# side tone
# off = c6 00 00
# low = c6 00 01
# medium = c6 80 01
# high = c6 00 04

# Endpoint 0 = Audio Control
# Presumably to set the sidetone to low (from off) we need to send the following bytes
# 0x21 0x09 0x0204 0x005 04400212c600010000000000000000000000000000000000000000000000000000000000000000
# 0x21 = Host-to-device Request, class 0x1, recipient interface 0x1 (where does this come from -> 0x21 = 00100001)
# 0x09 = SET_REPORT
# 0x0204 = ReportID 4, ReportType 2 (output)
# 0x005 = wIndex
# wLength always seems to be 39 (includes padding)

from typing import Optional

from arctis_manager.config_manager import ConfigManager
from arctis_manager.device_manager import (DeviceState, DeviceManager,
                                           DeviceStatus, InterfaceEndpoint)
from arctis_manager.device_manager.device_settings import (DeviceSetting,
                                                           SliderSetting,
                                                           ToggleSetting)
from arctis_manager.device_manager.device_status import DeviceStatusValue


class ArctisProWiredDevice(DeviceManager):
    game_mix: int = None
    chat_mix: int = None

    def get_local_settings(self) -> dict[str, int]:

        self._local_config = ConfigManager.get_instance().get_config(self.get_device_vendor_id(), self.get_device_product_id()) or {
            'mic_side_tone': 0x00, #off
        }

        return self._local_config

    def get_device_name(self):
        return 'Arctis Pro'
    
    def get_device_product_id(self):
        return 0x1252
    
    def get_device_vendor_id(self):
        return 0x1038


from arctis_manager.device_manager.device_manager import device_manager_factory
from arctis_manager.devices.device_arctis_7_plus import Arctis7PlusDevice


@device_manager_factory(0x2212, 'Arctis 7+ (PS5)')
class Arctis7PlusDevicePS5(Arctis7PlusDevice):
    pass


@device_manager_factory(0x2216, 'Arctis 7+ (Xbox)')
class Arctis7PlusDeviceXBOX(Arctis7PlusDevice):
    pass


@device_manager_factory(0x2236, 'Arctis 7+ (Destiny)')
class Arctis7PlusDeviceDestiny(Arctis7PlusDevice):
    pass

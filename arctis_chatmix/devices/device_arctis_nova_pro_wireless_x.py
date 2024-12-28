from arctis_chatmix.devices.device_arctis_7_plus import ArctisNovaProWirelessDevice


class ArctisNovaProWirelessDeviceX(ArctisNovaProWirelessDevice):
    '''
    Essentially a copy of ArctisNovaProWirelessDevice, but with a different product ID and name.
    '''

    def get_device_product_id(self):
        return 0x12e5

    def get_device_name(self):
        return 'Arctis Nova Pro Wireless X'

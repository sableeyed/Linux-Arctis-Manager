from arctis_chatmix.device_manager import ChatMixState, DeviceManager, InterfaceEndpoint


class ArctisNovaProWirelessDevice(DeviceManager):
    def get_device_product_id(self) -> int:
        return 0x220e

    def get_device_name(self) -> str:
        return 'Arctis 7+'

    def get_endpoint_addresses_to_listen(self) -> list[InterfaceEndpoint]:
        return [InterfaceEndpoint(7, 0)]

    def manage_input_data(self, data: list[int], endpoint: InterfaceEndpoint) -> ChatMixState:
        if endpoint == InterfaceEndpoint(7, 0):
            return ChatMixState(data[1] / 100, data[2] / 100, 1, 1)

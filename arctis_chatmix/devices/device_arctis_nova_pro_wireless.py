from arctis_chatmix.device_manager import ChatMixState, DeviceManager, InterfaceEndpoint


class ArctisNovaProWirelessDevice(DeviceManager):
    game_mix: int = None
    chat_mix: int = None

    def get_device_name(self):
        return 'Arctis Nova Pro Wireless'

    def get_device_product_id(self):
        return 0x12e0

    def get_endpoint_addresses_to_listen(self) -> list[InterfaceEndpoint]:
        return [
            InterfaceEndpoint(6, 0),
            InterfaceEndpoint(7, 0),
            InterfaceEndpoint(7, 1),
        ]

    def init_device(self):
        '''
        Initializes the GameDAC Gen2, enabling the mixer.
        Kinda obscure, but seems to work on my machine (tm).
        (Packets and sequence taken from the Arctis Nova Pro Wireless via Wireshark)
        '''

        commands = [
            # Command, expects response

            # Series of queries / responses
            ([0x06, 0xb0], True),
            ([0x06, 0xb0], True),
            ([0x06, 0x20], True),
            ([0x06, 0x20], True),
            ([0x06, 0x10], True),
            ([0x06, 0x10], True),
            ([0x06, 0xb0], True),
            ([0x06, 0xb0], True),
            ([0x06, 0x10], True),
            ([0x06, 0x3b], False),  # Correction?
            ([0x06, 0xb0], True),
            ([0x06, 0x8d, 0x01], True),
            ([0x06, 0x20], True),
            ([0x06, 0x20], True),
            ([0x06, 0x20], True),
            ([0x06, 0x80], True),
            ([0x06, 0x3b], False),  # Correction?
            ([0x06, 0xb0], True),
            # Burst of commands (device init?)
            ([0x06, 0x8d, 0x01], False),
            ([0x06, 0x33, 0x14, 0x14, 0x14], False),
            ([0x06, 0xc3], False),
            ([0x06, 0x2e], False),
            ([0x06, 0xc1, 0x05], False),
            ([0x06, 0x85, 0x0a], False),
            ([0x06, 0x37, 0x0a], False),
            ([0x06, 0xb2], False),
            ([0x06, 0x47, 0x64, 0x00, 0x64], False),
            ([0x06, 0x83, 0x01], False),
            ([0x06, 0x89, 0x00], False),
            ([0x06, 0x27, 0x02], False),
            ([0x06, 0xb3], False),
            ([0x06, 0x39], False),
            ([0x06, 0xbf, 0x0a], False),
            ([0x06, 0x43, 0x01], False),
            ([0x06, 0x69, 0x00], False),
            ([0x06, 0x3b, 0x00], False),
            ([0x06, 0x8d, 0x01], False),
            ([0x06, 0x49, 0x01], False),
            ([0x06, 0xb7, 0x00], False),
            # Another series of queries (perhaps for confirmation?)
            ([0x06, 0xb7, 0x00], True),
            ([0x06, 0xb0, 0x00], True),
            ([0x06, 0xb7, 0x00], True),
            ([0x06, 0xb0, 0x00], True),
            ([0x06, 0x20, 0x00], True),
            ([0x06, 0xb7, 0x00], True),
            ([0x06, 0xb0, 0x00], True),
        ]

        # 8th interface, 2nd endpoint. The 1st one is for receiving data from the DAC
        commands_endpoint_address = self.device[0].interfaces()[7].endpoints()[1].bEndpointAddress

        if self.device.is_kernel_driver_active(commands_endpoint_address):
            self.device.detach_kernel_driver(commands_endpoint_address)

        for command in commands:
            self.device.write(commands_endpoint_address, self.packet_0_filler(command[0], 91))
            # Ignore the responses for now, as I haven't figured out yet their significance.

    def manage_input_data(self, data: list[int], endpoint: InterfaceEndpoint) -> ChatMixState:
        volume = 1
        device_connected = True  # TODO get it from GameDAC

        if endpoint == InterfaceEndpoint(7, 0):
            # Volume control is managed by the GameDAC
            if data[0] == 0x07 and data[1] == 0x25:
                # Volume is data[2]. If needed for any other purpose, it ranges between -56 (0%) and 0 (100%).
                pass

            elif data[0] == 0x07 and data[1] == 0x45:
                self.game_mix = data[2] / 100  # Ranges from 0 to 100
                self.chat_mix = data[3] / 100  # Ranges from 0 to 100
            else:
                self.log.debug(f'Incoming data from {endpoint.interface}, {endpoint.endpoint}: {data}')
        else:
            # TODO find out a way to know if the device is connected
            self.log.debug(f'Incoming data from {endpoint.interface}, {endpoint.endpoint}: {data}')

        return ChatMixState(volume, volume, self.game_mix if self.game_mix is not None else 1, self.chat_mix if self.chat_mix is not None else 1, device_connected)

    @staticmethod
    def packet_0_filler(packet: list[int], size: int):
        return [*packet, *[0 for _ in range(size - len(packet))]]

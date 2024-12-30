from arctis_chatmix.device_manager import ChatMixState, DeviceManager, DeviceStatus, InterfaceEndpoint

inactive_time_minutes_decode_dict = {
    0: 0,
    1: 1,
    2: 5,
    3: 10,
    4: 15,
    5: 30,
    6: 60,
}


class ArctisNovaProWirelessDevice(DeviceManager):
    game_mix: int = None
    chat_mix: int = None

    def get_device_name(self):
        return 'Arctis Nova Pro Wireless'

    def get_device_product_id(self):
        return 0x12e0

    def get_endpoint_addresses_to_listen(self) -> list[InterfaceEndpoint]:
        return [self.utility_guess_endpoint(7, 'in')]
        # return [InterfaceEndpoint(7, 0)]  # The same interface/endpoint is used for both volume / mixer and device state

    def get_request_device_status(self):
        # return InterfaceEndpoint(7, 1), [0x06, 0xb0]
        return self.utility_guess_endpoint(7, 'out'), [0x06, 0xb0]

    def init_device(self):
        '''
        Initializes the GameDAC Gen2, enabling the mixer.
        Kinda obscure, but seems to work on my machine (tm).
        (Packets and sequence taken from the Arctis Nova Pro Wireless via Wireshark)
        '''

        commands = [
            # Command, expects response

            # Series of queries / responses
            ([0x06, 0x20], True),
            ([0x06, 0x20], True),
            ([0x06, 0x10], True),
            ([0x06, 0x10], True),
            ([0x06, 0x10], True),
            ([0x06, 0x3b], False),  # Correction?
            ([0x06, 0x8d, 0x01], True),
            ([0x06, 0x20], True),
            ([0x06, 0x20], True),
            ([0x06, 0x20], True),
            ([0x06, 0x80], True),
            ([0x06, 0x3b], False),  # Correction?
            # Burst of commands (device init?)
            ([0x06, 0x8d, 0x01], False),
            ([0x06, 0x33, 0x14, 0x14, 0x14], False),  # Equalizer with 3 bands
            ([0x06, 0xc3], False),
            ([0x06, 0x2e, 0x00], False),  # Set equalizer preset (0)
            ([0x06, 0xc1, 0x05], False),  # Set inactive time (to 30 minutes, see inactive_time_minutes_decode_dict)
            ([0x06, 0x85, 0x0a], False),
            ([0x06, 0x37, 0x0a], False),
            ([0x06, 0xb2], False),
            ([0x06, 0x47, 0x64, 0x00, 0x64], False),
            ([0x06, 0x83, 0x01], False),
            ([0x06, 0x89, 0x00], False),
            ([0x06, 0x27, 0x02], False),
            ([0x06, 0xb3], False),
            ([0x06, 0x39, 0x00], False),  # Set the sidetone to 0 (off) -> possible values: 0 (off), 1 (low), 2 (medium), 3 (high)
            ([0x06, 0xbf, 0x0a], False),  # Set lights to 10 (out of 10)
            ([0x06, 0x43, 0x01], False),
            ([0x06, 0x69, 0x00], False),
            ([0x06, 0x3b, 0x00], False),
            ([0x06, 0x8d, 0x01], False),
            ([0x06, 0x49, 0x01], False),
            ([0x06, 0xb7, 0x00], False),
            # Another series of queries (perhaps for confirmation?)
            ([0x06, 0xb7, 0x00], True),
            ([0x06, 0xb7, 0x00], True),
            ([0x06, 0xb0, 0x00], True),  # Get device status
            ([0x06, 0x20, 0x00], True),
            ([0x06, 0xb7, 0x00], True),
        ]

        endpoint, _ = self.get_request_device_status()
        commands_endpoint_address = self.device[0].interfaces()[endpoint.interface].endpoints()[endpoint.endpoint].bEndpointAddress
        self.kernel_detach(endpoint)

        for command in commands:
            self.device.write(commands_endpoint_address, self.packet_0_filler(command[0], 91))
            # Ignore the responses for now, as I haven't figured out yet their significance.

    def manage_input_data(self, data: list[int], endpoint: InterfaceEndpoint) -> ChatMixState:
        volume = 1
        device_status = None

        if endpoint == InterfaceEndpoint(7, 0):
            # Volume control is managed by the GameDAC
            if len(data) >= 2 and data[0] == 0x07 and data[1] == 0x25:
                # Volume is data[2]. If needed for any other purpose, it ranges between -56 (0%) and 0 (100%).
                pass

            elif len(data) >= 4 and data[0] == 0x07 and data[1] == 0x45:
                self.log.debug('Received volume control data.')
                self.game_mix = data[2] / 100  # Ranges from 0 to 100
                self.chat_mix = data[3] / 100  # Ranges from 0 to 100
            elif len(data) >= 16 and data[0] == 0x06 and data[1] == 0xb0:
                # https://github.com/Sapd/HeadsetControl/blob/master/src/devices/steelseries_arctis_nova_pro_wireless.c#L242
                device_status = DeviceStatus(
                    bluetooth_powerup_state='off' if data[2] == 0x00 else 'on',
                    bluetooth_auto_mute='off' if data[3] == 0x00 else 'half' if data[3] == 0x01 else 'on',
                    bluetooth_power_status='off' if data[4] == 0x01 else 'on',
                    bluetooth_connection='off' if data[5] == 0x00 else 'connected' if data[5] == 0x01 else 'disconnected',
                    headset_battery_charge=float(round(data[6] / 8, 2)),
                    charge_slot_battery_charge=float(round(data[7] / 8, 2)),
                    transparent_noise_cancelling_level=data[8] / 10,
                    mic_status='unmuted' if data[9] == 0x00 else 'muted',
                    noise_cancelling='off' if data[10] == 0x00 else 'transparent' if data[10] == 0x01 else 'on',
                    mic_led_brightness=data[11] / 10,
                    auto_off_time_minutes=inactive_time_minutes_decode_dict[data[12]],
                    wireless_mode='speed' if data[13] == 0x00 else 'range',
                    wireless_pairing='not_paired' if data[14] == 0x01 else 'paired_offline' if data[13] == 0x04 else 'connected',
                    headset_power_status='offline' if data[15] == 0x01 else 'cable_charging' if data[14] == 0x02 else 'online',
                )
            else:
                self.log.debug(f'Incoming data from {endpoint.interface}, {endpoint.endpoint}: [{':'.join(hex(x)[2:] for x in data)}]')
        else:
            self.log.debug(f'Incoming data from {endpoint.interface}, {endpoint.endpoint}: [{':'.join(hex(x)[2:] for x in data)}]')

        return ChatMixState(
            game_volume=volume,
            chat_volume=volume,
            game_mix=self.game_mix if self.game_mix is not None else 1,
            chat_mix=self.chat_mix if self.chat_mix is not None else 1,
            device_status=device_status,
        )

    @staticmethod
    def packet_0_filler(packet: list[int], size: int):
        return [*packet, *[0 for _ in range(size - len(packet))]]

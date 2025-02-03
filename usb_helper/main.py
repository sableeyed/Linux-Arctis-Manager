import asyncio
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
import re
import subprocess
from typing import Optional
import pyuac

from tshark_packet import TSharkPacket

def get_tshark_path() -> Path:
    try:
        via_path = subprocess.check_output(['where', 'tshark'], universal_newlines=True)
        return Path(via_path)
    except subprocess.CalledProcessError:
        pass

    via_std_path = Path('C:\\Program Files\\Wireshark\\tshark.exe')
    if via_std_path.exists():
        return via_std_path

    raise Exception('Could not find tshark')

def get_usbpcap_devices() -> list[str]:
    tshark_path = get_tshark_path()
    cmd = subprocess.Popen([tshark_path.name, '-D'], cwd=str(tshark_path.parent), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    out, err = cmd.communicate()
 
    if err:
        raise Exception(err.decode('utf-8'))

    devices = []
    name_re = re.compile(r'^.+\((.+)\)$')
    for line in out.decode('utf-8').split('\n'):
        if 'USBPcap' in line:
            devices.append(name_re.match(line.strip())[1])
    
    return devices

async def read_usbpcap_device(device: str):
    tshark = get_tshark_path()
    json_decoder = json.JSONDecoder()

    process = await asyncio.create_subprocess_exec(str(tshark), '-i', device, '-Y', 'usb.transfer_type == 0x01', '-x', '-T', 'json',
        stdout=subprocess.PIPE,
        cwd=str(tshark.parent),
    )

    buffer = ''
    try:
        while buffer.strip() != ']':
            chunk = await process.stdout.read(4096)
            if not chunk:
                continue

            buffer += chunk.decode('utf-8')
            if buffer[0] in ['[', ',']:
                buffer = buffer[1:]
            buffer = buffer.lstrip()

            try:
                packet_data, idx = json_decoder.raw_decode(buffer)
                yield packet_data

                buffer = buffer[idx:].lstrip()
            except json.decoder.JSONDecodeError as ex:
                # Not enough data (yet)
                continue
    finally:
        process.terminate()
        await process.wait()

async def read_consumer(generator, callback):
    async for packet_data in generator:
        callback(packet_data)

def filter_packets_by_ignore_list(packets: list[TSharkPacket], ignore_list: list[str]):
    return [packet for packet in packets if packet.usb.source not in ignore_list or packet.usb.dest not in ignore_list]

async def detect_init_packets(usbpcap_devices: list[str], devices_ignore_list: list[str]) -> list[TSharkPacket]:
    init_packets: list[TSharkPacket] = []

    print('The application will now try to detect device initialization traffic.')
    print('')
    print('ATTACH YOUR DEVICE ONLY WHEN YOU HIT ENTER AND SEE "Capturing on \'USBPcap*\' MESSAGES!')
    print('')
    input('Please press [Enter] to continue, then connect the Arctis device. This will take 20 seconds.')
    logging.debug('Creating listening tasks to detect init traffic...')
    tasks = [asyncio.create_task(read_consumer(
        read_usbpcap_device(device),
        lambda packet_data: init_packets.append(TSharkPacket(**packet_data['_source']['layers'])),
    )) for device in usbpcap_devices]
    
    try:
        await asyncio.sleep(20)
    except asyncio.CancelledError:
        print('Listening was cancelled')

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)

    init_packets = filter_packets_by_ignore_list(init_packets, devices_ignore_list)
    init_packets = [packet for packet in init_packets if 'usbhid' in packet.frame.protocols]

    print('Detected the following packets:')
    for packet in init_packets:
        print(packet)
    
    print('')
    src_packets = list(set([packet.usb.source for packet in init_packets if packet.usb.source != 'host']))
    if len(src_packets) == 1:
        target_device = src_packets[0]
    if len(src_packets) > 1:
        print('Multiple USB devices found during the initialization phase. Please specify which device to analyze (it will probably the one with the most traffic).')
        for idx, src in enumerate(src_packets):
            print(f'{idx+1}. {src}')
        choice = int(input('Input number: ')) - 1
        target_device = src_packets[choice]
        init_packets = [packet for packet in init_packets if packet.usb.source == target_device or packet.usb.dest == target_device]

        for packet in init_packets:
            print(packet)
    print('')

    return init_packets

async def detect_packets_and_return_packets(device: Optional[str], interfaces: list[str]) -> list[TSharkPacket]:
    tasks = []
    packets: list[TSharkPacket] = []

    def store_packet(packet_data: dict):
        packet = TSharkPacket(**packet_data['_source']['layers'])

        if device and (packet.usb.source == device or packet.usb.dest == device):
            print(f'{device} - {packet.usb.source} -> {packet.usb.dest}', flush=True)
            packets.append(packet)

    if device:
        dev_interface = re.compile(r'(\d+).\d+.\d+').match(device)[1]
        interfaces = [f'USBPcap{dev_interface}']
    tasks = [asyncio.create_task(read_consumer(read_usbpcap_device(dev), store_packet)) for dev in interfaces]

    while True:
        if len(packets) > 0 and (packets[-1].timestamp + timedelta(seconds=5)) < datetime.now():
            break

        print('.', end='', flush=True)
        await asyncio.sleep(1)
    print('', flush=True)

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)

    return packets

async def main():
    target_device: str = None
    init_packets: list[TSharkPacket] = []
    devices_ignore_list: list[str] = []

    logging.debug('Getting USBPcap devices...')
    devices = get_usbpcap_devices()
    if len(devices) == 0:
        logging.error('No USBPcap devices found. Have you installed the USBPcap driver?')
        return

    # Devices to ignore.
    # NOTE: if put in a dedicated async function, it will freeze for some reason!

    print('')    
    print('IF THE ARCTIS DEVICE IS CONNECTED, PLEASE DISCONNECT IT NOW.')
    print('If possible, detach any other USB devices not strictly needed (like keyboard and mouse).')
    print('')
    input('Press [Enter] to continue...')

    print('')
    print('The application will try to filter out all current USB traffic.')
    print('Please use your mouse, keyboard and other USB attached devices.')
    print('This process will take 10 seconds.')
    print('')
    print('DETACH YOUR ARCTIS DEVICE NOW.')
    print('')
    input('Press [Enter] to continue...')

    print('')
    logging.debug('Creating listening tasks to detect USB devices to ignore...')
    tasks = [asyncio.create_task(read_consumer(
        read_usbpcap_device(device),
        lambda packet_data: devices_ignore_list.append(TSharkPacket(**packet_data['_source']['layers']).usb.source),
    )) for device in devices]
    
    try:
        await asyncio.sleep(10)
    except asyncio.CancelledError:
        print('Listening was cancelled')

    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)

    devices_ignore_list = list(set(devices_ignore_list))
    try:
        devices_ignore_list.remove('host')
    except:
        pass

    print(f'Detected {len(devices_ignore_list)} devices to ignore: {", ".join(devices_ignore_list)}')
    print('')

    init_packets = await detect_init_packets(devices, devices_ignore_list)
    target_device = next((p.usb.dest for p in init_packets if p.usb.dest != 'host'), None)

    if target_device is None:
        print('No device detected. Continuing with program (the device might not need initialization).')
        print('')
    
    print('The application will now attempt to capture the USB traffic specific for settings change.')
    print('')
    
    print('Open the GG software -> Engine -> [your device] and go under the device settings.')
    print('For each setting, name it here in the console, then change it and click on the save button.')
    print('After saving it, name the setting value in the console, then repeat the process for all possible values of the same setting.')
    print('')
    print('In any case, follow the instructions on-screen.')
    print('')
    input('Press [Enter] to continue...')

    features = []
    while func_name := input('Please enter a setting name (or press [Enter] to finish): '):
        while True:
            packets = await detect_packets_and_return_packets(target_device, devices)
            while func_value := input(f'{func_name}: which value have you set (i.e. on/off, 10%, high, low, etc.)? ') == '':
                pass

            features.append({'function': func_name, 'value_label': func_value, 'packets': packets})

            while (finished := input('Have you tried all possible values of this setting? [Y/n] ').lower()) not in ['y', 'n', '']:
                pass
            
            if finished in ['y', '']:
                print(features)
                # TODO save feature info
                break

    input('To be continued...')

async def run():
    try:
        await main()
    except asyncio.CancelledError:
        logging.debug('Program cancelled and succesfully closed.')
    except KeyboardInterrupt:
        logging.debug('Program exiting due to user input.')
    finally:
        logging.debug('Program exited.')

if __name__ == '__main__':
    if not pyuac.isUserAdmin():
        print('Run this program with admin privileges.')
        pyuac.runAsAdmin()
    else:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()],
        )
        try:
            asyncio.run(run())
        except KeyboardInterrupt:
            logging.debug('Program exiting due to user input.')
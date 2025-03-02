import asyncio
from datetime import datetime, timedelta
from os import environ
from pathlib import Path
from typing import Optional

import pyuac

from asyncio_helpers import Waiter
from cli_helpers import print_loading
from models import Feature, FeatureValue
from tshark import get_usbpcap_interfaces, read_usbpcap_interface
from tshark_packet import TSharkPacket

def print_banner():
    print('''
    _          _   _                    _       _                _  __  __         
   /_\\  _ _ __| |_(_)___  _ __  __ _ __| |_____| |_ ___  ____ _ (_)/ _|/ _|___ _ _ 
  / _ \\| '_/ _|  _| (_-< | '_ \\/ _` / _| / / -_)  _(_-< (_-< ' \\| |  _|  _/ -_) '_|
 /_/ \\_\\_| \\__|\\__|_/__/ | .__/\\__,_\\__|_\\_\\___|\\__/__/ /__/_||_|_|_| |_| \\___|_|  
                         |_|                                                       
''')
    print('')


def print_step(step: int, message: str):
    print(f'[{step}] {message}')
    print('')

def should_break_after_wait(start: datetime, packets: list, wait_from_last_packet_seconds: int, timeout_seconds: int) -> bool:
    if len(packets) > 0:
        if (datetime.now() > (packets[-1].timestamp + timedelta(seconds=wait_from_last_packet_seconds))):
            return True
    elif (start + timedelta(seconds=timeout_seconds)) < datetime.now():
        return True

    return False

async def wait_and_cancel_tasks(
        wait_message: str,
        start_time: datetime,
        tasks: list[asyncio.Task],
        packets: list[TSharkPacket],
        wait_from_last_packet_seconds: int = 3,
        timeout_seconds: int = 10
    ):

    idx = 0
    while True:
        idx += 1
        await print_loading(idx, wait_message)
        if should_break_after_wait(start_time, packets, wait_from_last_packet_seconds, timeout_seconds):
            print('')
            break
    for task in tasks:
        task.cancel()
    
    await asyncio.gather(*tasks)

async def capture_packets(usbpcap_interfaces: list[str], wait_message: str, timeout: int, hard_timeout: int, *filters: list[str]) -> list[TSharkPacket]:
    packets: list[TSharkPacket] = []
    tasks: list[asyncio.Task] = []
    waiters: list[Waiter] = []
    for iface in usbpcap_interfaces:
        waiters.append(Waiter())
        tasks.append(asyncio.create_task(
            read_usbpcap_interface(iface, lambda packet: packets.append(packet), 'frame.protocols contains "usbhid"', *filters, waiter=waiters[-1])
        ))
    
    for waiter in waiters:
        await waiter

    start_time = datetime.now()
    await wait_and_cancel_tasks(wait_message, start_time, tasks, packets, timeout, hard_timeout)
    print('')

    return packets

async def build_devices_blacklist(usbpcap_interfaces: list[str]) -> list[str]:
    print('Please disconnect your Arctis device and any other USB device not strictly required.')
    print('When the application will be ready, press some keyboard keys (i.e. CTRL, ALT or SHIFT) and move your mouse.')
    print('This will exclude those devices from the next steps.')
    print('')

    input('Press [Enter] to continue...')

    packets = await capture_packets(usbpcap_interfaces, 'Move your mouse, press some keys then wait...', 3, 10)

    blacklist = []
    for packet in packets:
        blacklist.extend([packet.usb.source, packet.usb.dest])
    blacklist = list(set(blacklist))
    try:
        blacklist.remove('host')
    except:
        pass

    return blacklist

async def get_init_packets(usbpcap_interfaces: list[str], blacklist: list[str]) -> list[TSharkPacket]:
    print('When all the USBPcap interfaces are ready, plug your Arctis device in and wait a couple of seconds.')
    input('Press [Enter] to continue...')

    packets = await capture_packets(
        usbpcap_interfaces,
        'Plug your Arctis device in and wait...',
        5, 15,
        *[f'usb.addr != {dev}' for dev in blacklist]
    )

    return packets

async def get_features_set(usbpcap_interfaces: list[str], device_id: Optional[str], blacklist: list[str], features: list[Feature] = []) -> list[Feature]:
    if not features:
        print('In this part, the application will attempt to detect the configuration packets sent by the GG software.')
        print('First of all, open the SteelSeries GG software, enter the Engine section and then the Arctis device\'s settings.')
        print('Remember to try the physical wheels, too (like the volume up / down (down to minimum, up to maximum etc).)')
        print('')
        input('Press [Enter] to continue...')
    
    while (feature_name := input('Enter the name of the feature (e.g. "Microphone volume"): ')) == '':
        pass

    filters = []
    if device_id:
        filters.append(f'usb.addr == {device_id}')
    else:
        # In case of missing previously missed init packets (that might not exist)
        filters.extend([f'usb.addr != "{id}"' for id in blacklist])
    
    feature = next((f for f in features if f.name == feature_name), None)
    if feature is None:
        feature = Feature(feature_name, [])
        features.append(feature)

    while True:
        packets = await capture_packets(
            usbpcap_interfaces, f'Change the "{feature_name}" value and hit the "Save" button, then wait...',
            5, 15,
            *filters
        )

        if not packets:
            if input('No packets captured. Do you want to try again? (Y/n): ').lower() in ['n', 'no']:
                break
            else:
                continue
        
        while (value := input('Insert the value you set (for example 0%, on, off, enabled, disabled, high, medium, low, ...): ')) == '':
            pass
                
        feature.values.append(FeatureValue(value, packets))

        print(f'Catalogued values for this feature are: {", ".join([fv.value for fv in feature.values])}.')
        if input('Do you have any other value for this feature you want to catalog? (y/N): ').lower() in ['n', 'no', '']:
            break
    
    if input('Do you have any other feature you want to catalog? (y/N): ').lower() in ['n', 'no', '']:
        return features
    
    return await get_features_set(usbpcap_interfaces, device_id, blacklist, features)

def markdown_page(device_name: str, init_packets: list[TSharkPacket], features: list[Feature]) -> str:
    md = f'# {device_name}\n\n'
    md += '## Initialization sequence\n\n'
    md += '| Datetime | Source | Destination | Data Length | Payload |\n'
    md += '|---------|--------|-------------|-------------|---------|\n'
    for packet in init_packets:
        md += f'| {packet.timestamp} | {packet.usb.source} | {packet.usb.dest} | {packet.usb.data_length} | {packet.hid_data} |\n'
    md += '\n'
    md += '## Features\n\n'
    for feature in features:
        md += f'### {feature.name}\n\n'
        md += '| Value | Packet #n | Datetime | Source | Dest | Payload |\n'
        md += '|-------|-----------|-----------|--------|------|---------|\n'
        for value in feature.values:
            for i, packet in enumerate(value.packets[1:]):
                md += f'| {value.value} | {i + 1} | {packet.timestamp} | {packet.usb.source} | {packet.usb.dest} | {packet.hid_data} |\n'
        md += '\n'
    
    return md

async def main():
    print_banner()

    print_step(1, 'Getting USBPcap interfaces...')
    usbpcap_interfaces = get_usbpcap_interfaces()
    
    print_step(2, 'Filtering out current USB traffic...')
    blacklist = await build_devices_blacklist(usbpcap_interfaces)

    print_step(3, 'Capturing device initialization traffic...')
    init_packets = await get_init_packets(usbpcap_interfaces, blacklist)

    device_src = [p.usb.source for p in init_packets if p.usb.source != 'host']
    device_dest = [p.usb.dest for p in init_packets if p.usb.dest != 'host']
    device_id = list(set(device_src + device_dest))

    if len(init_packets) > 0:
        print(f'Init sequence captured ({len(init_packets)} packets).')
        
        if len(device_id) > 1:
            print('Multiple devices detected. Please choose one of the identifiers (the one with the most packets should be the correct one):')
            src_packets = list(set([packet.usb.source for packet in init_packets if packet.usb.source != 'host']))
            for idx, src in enumerate(init_packets):
                print(f'{idx+1}. {src}')
            choice = int(input('Input number: ')) - 1
            device_id = src_packets[choice]
            init_packets = [packet for packet in init_packets if packet.usb.source == device_id or packet.usb.dest == device_id]
        elif len(device_id) == 1:
            device_id = device_id[0]
        else:
            device_id = None
    else:
        print('Cannot detect device initialization traffic. This might not be an error, as the device might not need to be initialized.')
        if input('Do you want to continue? (Y/n) ').lower() not in ('yes', 'y', ''):
            return
        device_id = None
    
    if device_id is not None:
        print(f'Detected device ID: {device_id} (you can use this as a Wireshark filter: usb.addr == "{device_id}").')

    print_step(4, 'Device-specific setting configurations.')
    features = await get_features_set(usbpcap_interfaces, device_id, blacklist)

    device_name = input('Enter the device name (e.g. "Arctis 7"): ')

    output_path = Path(f'{device_name}_{datetime.now().strftime('%Y_%m_%d_%H_%M')}.md')
    with output_path.open('w') as f:
        f.write(markdown_page(device_name, init_packets, features))
        print(f'Data exported to "{output_path.absolute()}".')

    input('Press [Enter] to close.')
    
if __name__ == '__main__':
    if not pyuac.isUserAdmin():
        print('Run this program with admin privileges.')
        pyuac.runAsAdmin()
    else:
        asyncio.run(main())

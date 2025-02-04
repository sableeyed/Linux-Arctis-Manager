import asyncio
from datetime import datetime, timedelta
from os import environ

import pyuac

from cli_helpers import print_loading
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

async def build_devices_blacklist(usbpcap_interfaces: list[str]) -> list[str]:
    print('Please disconnect your Arctis device and any other USB device not strictly required.')
    print('When the application will be ready, press some keyboard keys (i.e. CTRL, ALT or SHIFT) and move your mouse.')
    print('This will exclude those devices from the next steps.')
    print('')

    input('Press [Enter] to continue...')

    packets: list[TSharkPacket] = []
    tasks: list[asyncio.Task] = []
    for iface in usbpcap_interfaces:
        tasks.append(asyncio.create_task(
            read_usbpcap_interface(iface, lambda packet: packets.append(packet), 'frame.protocols contains "usbhid"')
        ))

    await asyncio.sleep(2)
    start_time = datetime.now()
    await wait_and_cancel_tasks('Move your mouse, press some keys then wait...', start_time, tasks, packets, 3)
    print('')
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

    packets: list[TSharkPacket] = []
    tasks: list[asyncio.Task] = []
    for iface in usbpcap_interfaces:
        tasks.append(asyncio.create_task(
            read_usbpcap_interface(iface, lambda packet: packets.append(packet), 'frame.protocols contains "usbhid"', *[f'usb.addr != {dev}' for dev in blacklist])
        ))
    
    await asyncio.sleep(2)
    start_time = datetime.now()
    await wait_and_cancel_tasks('Plug your Arctis device in and wait...', start_time, tasks, packets, 5)
    print('')

    return packets

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
        print('Init sequence captured.')
        for packet in init_packets:
            print(packet)
        
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
    
if __name__ == '__main__':
    if not pyuac.isUserAdmin():
        print('Run this program with admin privileges.')
        pyuac.runAsAdmin()
    else:
        asyncio.run(main())
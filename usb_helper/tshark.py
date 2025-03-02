import asyncio
import json
from os import environ
import os
from pathlib import Path
import re
import subprocess
from typing import AsyncGenerator, Callable, Optional

from asyncio_helpers import Waiter
from cli_helpers import print_loading
from tshark_packet import TSharkPacket


def get_tshark_path() -> Path:
    try:
        via_path = subprocess.check_output(['where', 'tshark'], stderr=subprocess.DEVNULL, universal_newlines=True)
        return Path(via_path)
    except subprocess.CalledProcessError:
        pass

    via_std_path = Path('C:\\Program Files\\Wireshark\\tshark.exe')
    if via_std_path.exists():
        return via_std_path

    raise Exception('Could not find tshark')

def get_usbpcap_interfaces() -> list[str]:
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

async def read_usbpcap_interface(interface: str, callback: Callable[[TSharkPacket], None], *filters: list[str], waiter: Optional[Waiter] = None) -> None:
    async for packet in read_usbpcap_interface_generator(interface, *filters, waiter=waiter):
        callback(packet)

async def read_usbpcap_interface_generator(interface: str, *filters: list[str], waiter: Optional[Waiter] = None) -> AsyncGenerator[TSharkPacket, None]:
    tshark = get_tshark_path()
    json_decoder = json.JSONDecoder()

    process = await asyncio.create_subprocess_exec(
        str(tshark.absolute()),
        '-i', interface,
        '-Y', ' && '.join(['usb.transfer_type == 0x01', *filters]),
        '-x',
        '-T', 'json',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for tshark to start
    idx = 0
    buffer_stderr = ''
    while True:
        buffer_stderr += (await process.stderr.read(4096)).decode('utf-8')

        if f"Capturing on '{interface}'" in buffer_stderr:
            break

        await print_loading(idx, f'Waiting for {interface} listening to start...')
        idx += 1
    
    print(f'Capturing on {interface}')

    if waiter:
        waiter.set() 
   
    try:
        buffer = ''
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

                yield TSharkPacket(**packet_data['_source']['layers'])

                buffer = buffer[idx:].lstrip()
            except json.decoder.JSONDecodeError as ex:
                # Not enough data (yet)
                continue
    except asyncio.CancelledError:
        pass
    finally:
        process.terminate()
        await process.wait()


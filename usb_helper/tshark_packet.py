from datetime import datetime
import re


class TSharkUSBLayer:
    source: str
    dest: str
    data_length: int

    def __init__(self, **kwargs):
        self.source = kwargs['usb.src']
        self.dest = kwargs['usb.dst']
        self.data_length = int(kwargs['usb.data_len'])

class TSharkFrame:
    interface: str
    time_epoch: float
    protocols: str
    frame_number: int

    def __init__(self, **kwargs):
        self.interface = kwargs['frame.interface_id_tree']['frame.interface_description']
        self.time_epoch = float(kwargs['frame.time_epoch'])
        self.protocols = kwargs['frame.protocols']
        self.frame_number = int(kwargs['frame.number'])

class TSharkPacket:
    usb: TSharkUSBLayer
    frame: TSharkFrame
    hid_data: str

    def __init__(self, usb, frame, **kwargs):
        self.usb = TSharkUSBLayer(**usb)
        self.frame = TSharkFrame(**frame)
        self.hid_data = kwargs['usbhid.data'] if 'usbhid.data' in kwargs else ''

    @property
    def timestamp(self):
        return datetime.fromtimestamp(int(self.frame.time_epoch))
    
    def __str__(self):
        return f'{self.timestamp} | {self.frame.protocols} | {self.usb.source} -> {self.usb.dest} ({self.usb.data_length}) | {self.hid_data}'
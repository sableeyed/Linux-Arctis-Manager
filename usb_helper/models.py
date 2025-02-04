from dataclasses import dataclass
from tshark_packet import TSharkPacket

@dataclass
class FeatureValue:
    value: str
    packets: list[TSharkPacket]

@dataclass
class Feature:
    name: str
    values: list[FeatureValue]
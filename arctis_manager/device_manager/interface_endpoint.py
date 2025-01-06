from dataclasses import dataclass


@dataclass(frozen=True)
class InterfaceEndpoint:
    '''Address of the interface and the endpoint to listen to'''

    '''0-based index of the interface to listen to'''
    interface: int
    '''0-based index of the endpoint to listen to'''
    endpoint: int

    def __eq__(self, other: 'InterfaceEndpoint') -> bool:
        return self.interface == other.interface and self.endpoint == other.endpoint

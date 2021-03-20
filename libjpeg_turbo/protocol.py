from ctypes import *


class DatagramHeader(Structure):
    _fields_ = [
        ('seq', c_uint),
        ('frm', c_uint),
        ('last', c_bool),
        ('fn', c_byte),
        ('timestamp', c_uint),
        ('pairity', c_bool),
    ]


def get_payload(datagram: bytes):
    return datagram[sizeof(DatagramHeader):]


def create_datagram(**kwargs):
    return bytes(DatagramHeader(kwargs['seq'], kwargs['frm'], kwargs['last'], kwargs['fn'],
                                kwargs['timestamp'], kwargs['parity'])) + kwargs['payload']

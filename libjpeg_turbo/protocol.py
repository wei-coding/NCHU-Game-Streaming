from ctypes import *


class GSCPHeader(Structure):
    _fields_ = [
        ('seq', c_uint),
        ('type', c_char),
        ('fn', c_char),
        ('timestamp', c_double)
    ]


class GSPHeader(Structure):
    _fields_ = [
        ('seq', c_uint8),
        ('frm', c_uint),
        ('last', c_bool),
        ('timestamp', c_double)
    ]


def get_payload(datagram: bytes):
    return datagram[sizeof(DatagramHeader):]


def create_datagram(**kwargs):
    return bytes(DatagramHeader(kwargs['seq'], kwargs['frm'], kwargs['last'], kwargs['fn'],
                                kwargs['timestamp'], kwargs['parity'])) + kwargs['payload']

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

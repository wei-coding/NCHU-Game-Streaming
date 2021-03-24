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
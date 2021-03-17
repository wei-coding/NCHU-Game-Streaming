import struct
from ctypes import *


class DatagramHeader(Structure):
    _fields_ = [
        ('seq', c_uint),
        ('last', c_bool),
        ('timestamp', c_uint),
    ]


class DatagramBuilder:
    def __init__(self, _packstr):
        self.packstr = _packstr
        self.packsize = struct.calcsize(self.packstr)

    def pack(self, seq, last):
        d = DatagramHeader()
        d.seq = seq
        d.last = last
        byte_string = struct.pack(self.packstr, d.seq, d.last)
        return byte_string

    def unpack(self, datagram):
        data = struct.unpack(self.packstr, datagram[0:struct.calcsize(self.packstr)])
        return data

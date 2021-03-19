from ctypes import *
import struct

format_ = '!I?I'

class DatagramHeader(Structure):
    _fields_ = [
        ('seq', c_uint),
        ('last', c_bool),
        ('timestamp', c_long),
    ]


class DatagramBuilder():
    def __init__(self):
        pass
    def pack(self,seq,last,timestamp):
        d = DatagramHeader()
        d.seq = seq
        d.last = last
        d.timestamp = timestamp
        byte_string = struct.pack('!I?I',d.seq,d.last,d.timestamp)
        return byte_string
    def unpack(self,datagram):
        data = struct.unpack('!I?I',datagram[0:struct.calcsize('!I?I')])
        return data
from ctypes import *
import struct
class DatagramHeader(Structure):
    _fields_ = [
        ('seq',c_uint),
        ('last',c_bool),
        ('timestamp',c_uint),
    ]
class DatagramBuilder():
    def __init__(self):
        pass
    def pack(self,seq,last,timestamp,payload):
        d = DatagramHeader()
        d.seq = seq
        d.last = last
        d.timestamp = timestamp
        byte_string = struct.pack('!I?I',d.seq,d.last,d.timestamp) + payload
        return byte_string
    def unpack(self,datagram):
        data = struct.unpack('!I?I',datagram[:struct.calcsize('!I?I')])
        return (*data, datagram[struct.calcsize('!I?I'):])
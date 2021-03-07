from ctypes import *
import struct
PACKET_SIZE = 2**15
class Datagram(Structure):
    _fields_ = [
        ('seq',c_uint),
        ('last',c_bool),
        ('timestamp',c_uint),
        ('payload',c_char_p),
        ('end',c_ubyte)
    ]
class DatagramBuilder():
    def __init__(self):
        pass
    def pack(self,seq,last,timestamp,payload):
        d = Datagram()
        d.seq = seq
        d.last = last
        d.timestamp = timestamp
        d.payload = payload
        d.end = 0x88
        byte_string = struct.pack('!I?I%dpB'%(2**7 - 64),d.seq,d.last,d.timestamp,d.payload,d.end)
        return byte_string
    def unpack(self,datagram):
        data = struct.unpack('!I?I%dpB'%(2**7 - 64),datagram)
        return data
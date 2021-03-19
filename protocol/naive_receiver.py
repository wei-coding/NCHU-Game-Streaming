import socket
import protocol
import ctypes

MAX_DGRAM = 2**16

def dump_buffer(s):
    """ Emptying buffer frame """
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        data = protocol.DatagramHeader.from_buffer_copy(seg)
        print(data.last)
        if data.last:
            print("finish emptying buffer")
            break

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('127.0.0.1', 12345))
dat = b''
#dump_buffer(s)

try:
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        data = protocol.DatagramHeader.from_buffer_copy(seg)
        if not data.last:
            dat += seg[ctypes.sizeof(protocol.DatagramHeader):]
        else:
            dat += seg[ctypes.sizeof(protocol.DatagramHeader):]
            print(dat)
except KeyboardInterrupt:
    s.close()
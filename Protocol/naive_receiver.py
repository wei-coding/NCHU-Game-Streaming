import socket
from Protocol import *

MAX_DGRAM = 65546
datagram_builder = DatagramBuilder()

def dump_buffer(s):
    """ Emptying buffer frame """
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        (seq,last,timestamp,payload,end) = datagram_builder.unpack(seg)
        print(last)
        if last:
            print("finish emptying buffer")
            break

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('192.168.56.101', 12345))
dat = b''
dump_buffer(s)

seg, addr = s.recvfrom(MAX_DGRAM)
while seq is not None:
    (seq,last,timestamp,payload,end) = datagram_builder.unpack(seg)
    if not last:
        dat += payload
    else:
        dat += payload
        print(dat)
s.close()
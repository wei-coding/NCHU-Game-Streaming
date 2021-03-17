import socket
import protocol
import time

MAX_DGRAM = 2**16
MAX_DATA_DGRAM = 2

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = '192.168.56.101'
port = 12345

p = protocol.DatagramBuilder()

message = b'15613864965'
seq = 0

partition = []
i = 0
while i < len(message):
    partition.append(message[i:i+MAX_DATA_DGRAM])
    i += MAX_DATA_DGRAM
print(partition)


for i in range(len(partition)):
    last = False if i != len(partition) - 1 else True
    dat = p.pack(seq,last,time.time_ns(),partition[i])
    print(last,dat,seq)
    s.sendto(dat,(addr,port))
    seq += 1

s.close()
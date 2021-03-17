import protocol
import struct
import time
import ctypes
d = protocol.Datagram()
d.seq = 0
d.last = True
d.timestamp = time.time_ns()
message = b'test message'
d.payload = message
d.end = 0x88
byte_string = struct.pack('!I?I%dp'%(20),d.seq,d.last,d.timestamp,d.payload)
print(byte_string)
print(struct.calcsize('!I?I%dp'%(10)))
string = struct.unpack('!I?I%dp'%(20),byte_string)
print(string)
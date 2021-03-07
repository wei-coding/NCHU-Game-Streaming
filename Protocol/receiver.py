#!/usr/bin/env python

from __future__ import division
import cv2
import numpy as np
import socket
import struct
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

def main():
    """ Getting image udp frame &
    concate before decode and output image """
    
    # Set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('192.168.56.101', 12345))
    dat = b''
    dump_buffer(s)

    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        (seq,last,timestamp,payload,end) = datagram_builder.unpack(seg)
        if not last:
            dat += payload
        else:
            dat += payload
            img = cv2.imdecode(np.fromstring(dat, dtype=np.uint8), 1)
            cv2.imshow('frame', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            dat = b''

    # cap.release()
    cv2.destroyAllWindows()
    s.close()

if __name__ == "__main__":
    
    main()

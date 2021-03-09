#!/usr/bin/env python

from __future__ import division
import cv2
import numpy as np
import socket
import struct
from Protocol import *
import threading
import time

MAX_DGRAM = 2**16
datagram_builder = DatagramBuilder()

img_buffer = []

def dump_buffer(s):
    """ Emptying buffer frame """
    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        (seq,last,timestamp) = datagram_builder.unpack(seg)
        #print(last)
        if last:
            print("finish emptying buffer")
            break

def main():
    """ Getting image udp frame &
    concate before decode and output image """
    
    # Set up socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('192.168.56.102', 12345))
    dat = b''
    dump_buffer(s)

    while True:
        seg, addr = s.recvfrom(MAX_DGRAM)
        (seq,last,timestamp) = datagram_builder.unpack(seg)
        payload = seg[struct.calcsize('!I?I'):]
        #print(seq,last,timestamp,payload)
        if not last:
            dat += payload
        else:
            dat += payload
            img = cv2.imdecode(np.fromstring(dat, dtype=np.uint8), 1)
            if img is not None:
                now = time.time()
                dif = timestamp - int(now - int(now))
                print(dif)
                if dif < 500000:
                    cv2.imshow('frame', img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            dat = b''

    # cap.release()
    cv2.destroyAllWindows()
    s.close()
def show_img():
    while True:
        if(len(img_buffer)):
            img = img_buffer.pop(0)
            if img is not None:
                cv2.imshow('frame',img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
if __name__ == "__main__":
    main_thread = threading.Thread(target=main)
    #show_thread = threading.Thread(target=show_img)
    main_thread.start()
    #show_thread.start()

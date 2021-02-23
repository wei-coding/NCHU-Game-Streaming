#!/usr/bin/env python

from __future__ import division
import cv2
import numpy as np
import socket
import struct
import math
import time
import threading
from mss import mss
from PIL import Image


class FrameSegment(threading.Thread):
    """
    Object to break down image frame segment
    if the size of image exceed maximum datagram size
    """
    MAX_DGRAM = 2**16
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64  # extract 64 bytes in case UDP frame overflown

    def __init__(self, sock, port, addr="127.0.0.1"):
        threading.Thread.__init__(self)
        self.s = sock
        self.port = port
        self.addr = addr
        self.buffer = []

    def run(self):
        """
        Compress image and Break down
        into data segments
        """
        while(True):
            if(len(self.buffer) != 0):
                img = self.buffer.pop()
                compress_img = cv2.imencode('.jpg', img)[1]
                dat = compress_img.tostring()
                size = len(dat)
                count = math.ceil(size/(self.MAX_IMAGE_DGRAM))
                array_pos_start = 0
                while count:
                    array_pos_end = min(size, array_pos_start + self.MAX_IMAGE_DGRAM)
                    self.s.sendto(struct.pack("B", count) +
                        dat[array_pos_start:array_pos_end],
                        (self.addr, self.port)
                        )
                    array_pos_start = array_pos_end
                    count -= 1
            else:
                time.sleep(10)
    def add_buffer(self,img):
        self.buffer.insert(0,img)
def main():
    """ Top level main function """
    # Set up UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 12345

    fs = FrameSegment(s, port)

    mon = {'top':0,'left':0,'width':500,'height':500}
    sct = mss()
    fs.start()
    while True:
        sct_img = sct.grab(mon)
        img = Image.frombytes('RGB',sct_img.size,sct_img.bgra,'raw','BGRX')
        img = cv2.cvtColor(np.asarray(img),cv2.COLOR_RGB2BGR)
        fs.add_buffer(img)
    s.close()


if __name__ == "__main__":
    main()

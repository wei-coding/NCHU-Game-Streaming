#!/usr/bin/env python

from __future__ import division
import cv2
import numpy as np
import socket
import struct
import math
import time
import threading
#import pyautogui as pg
from mss import mss
from PIL import Image


class FrameSegment(threading.Thread):
    """
    Object to break down image frame segment
    if the size of image exceed maximum datagram size
    """
    MAX_DGRAM = 2**16
    MAX_IMAGE_DGRAM = MAX_DGRAM - 64  # extract 64 bytes in case UDP frame overflown

    def __init__(self, sock, port, addr="192.168.56.101"):
        threading.Thread.__init__(self)
        self.s = sock
        self.port = port
        self.addr = addr
        self.buffer = []
        self.flag = True
        self.die = False

    def run(self):
        """
        Compress image and Break down
        into data segments
        """
        while(self.flag):
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
                print("Sleeping...")
                time.sleep(0.01)
    def add_buffer(self,img):
        self.buffer.insert(0,img)
        print(len(self.buffer))
        if(len(self.buffer) >= 10):
            time.sleep(0.1)
    def join(self):
        self.die = True
        super().join()
class ScreenShot(threading.Thread):
    def __init__(self,fs_,w_=1920,h_=1080):
        threading.Thread.__init__(self)
        self.w = w_
        self.h = h_
        self.sct = mss()
        self.fs = fs_
        self.die = False
    def run(self):
        mon = {'top':0,'left':0,'width':self.w,'height':self.h}
        while(True):
            sct_img = self.sct.grab(mon)
            img = Image.frombytes('RGB',sct_img.size,sct_img.bgra,'raw','BGRX')
            img = cv2.cvtColor(np.asarray(img),cv2.COLOR_RGB2BGR)
            self.fs.add_buffer(img)
    def join(self):
        self.die = True
        super().join()
def main():
    """ Top level main function """
    # Set up UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = 12345

    fs = FrameSegment(s, port)

    '''cap = cv2.VideoCapture(2)
    while (cap.isOpened()):
        _, frame = cap.read()
        fs.udp_frame(frame)
    cap.release()
    cv2.destroyAllWindows()
    s.close()
    '''
    #(w,h) = pg.size()
    ss = ScreenShot(fs)
    fs.start()
    ss.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        fs.join()
        ss.join()
    s.close()


if __name__ == "__main__":
    main()
